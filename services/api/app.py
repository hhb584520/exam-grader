# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import os
from typing import List, Optional, Union

import aiohttp
import asyncpg
import httpx
import tiktoken
from docarray import BaseDoc
from dotenv import load_dotenv
from fastapi import File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter

from comps import (
    DocPath,
    ServiceType,
    opea_microservices,
    opea_telemetry,
    register_microservice,
)

openai_tokenizer = tiktoken.get_encoding("o200k_base")

load_dotenv()
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8008/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
embedding_enpoint = os.getenv("EMBEDDING_ENDPOINT", "")
pg_host = os.getenv("PG_HOST", "")
pg_port = os.getenv("PG_PORT", "5432")
pg_user = os.getenv("PG_USER", "")
pg_pwd = os.getenv("PG_PWD", "")
pg_db = os.getenv("PG_DB", "")

GRADER_AGENT_ENDPOINT = os.getenv(
    "GRADER_AGENT_ENDPOINT", "http://localhost:9095/v1/chat/completions"
)

assert embedding_enpoint != "", "EMBEDDING_ENDPOINT is not set"
assert pg_host != "", "PG_HOST is not set"
assert pg_user != "", "PG_USER is not set"
assert pg_pwd != "", "PG_PWD is not set"
assert pg_db != "", "PG_DB is not set"

upload_folder = "./uploaded_files/"
os.makedirs(upload_folder, exist_ok=True)

CHUNK_STORAGE = dict()


class ChatParams(BaseDoc):
    messages: list
    streaming: bool = True


class StepAnalysis(BaseDoc):
    question_id: str
    student_id: str
    steps: list
    error_step_index: int
    error_reason: str
    error_type: str
    correct_method: str
    suggested_steps: list
    common_mistakes: list
    teaching_suggestions: str
    learning_tips: str


class StudentProfile(BaseDoc):
    student_id: str
    weak_topics: list
    error_patterns: dict
    learning_style: str
    improvement_suggestions: list
    recommended_resources: list


class TeachingInsight(BaseDoc):
    subject: str
    topic: str
    common_errors: list
    teaching_focus: list
    activity_suggestions: list
    assessment_methods: list


@opea_telemetry
def post_process_text(text: str):
    if text == " ":
        return "data: @#$\n\n"
    if text == "\n":
        return "data: <br/>\n\n"
    if text.isspace():
        return None
    new_text = text.replace(" ", "@#$")
    return f"data: {new_text}\n\n"


def encode_filename(filename: str) -> str:
    import hashlib
    return hashlib.md5(filename.encode()).hexdigest()


async def save_content_to_local_disk(save_path: str, file: UploadFile):
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)


def document_loader(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


async def init_db():
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS exam_papers (
            paper_id TEXT PRIMARY KEY,
            title TEXT,
            subject TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS student_answers (
            id SERIAL PRIMARY KEY,
            paper_id TEXT,
            student_id TEXT,
            answers TEXT,
            score FLOAT,
            graded BOOLEAN DEFAULT FALSE,
            graded_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS wrong_questions (
            id SERIAL PRIMARY KEY,
            question_id TEXT,
            student_id TEXT,
            paper_id TEXT,
            question_content TEXT,
            student_answer TEXT,
            correct_answer TEXT,
            knowledge_points TEXT,
            difficulty TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            step_analysis TEXT,
            correct_steps TEXT,
            common_mistakes TEXT,
            teaching_suggestions TEXT
        );
    """)
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_points (
            id SERIAL PRIMARY KEY,
            point_id TEXT,
            subject TEXT,
            topic TEXT,
            description TEXT,
            correct_methods TEXT,
            common_errors TEXT,
            teaching_tips TEXT,
            embedding vector(1024)
        );
    """)
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS step_templates (
            id SERIAL PRIMARY KEY,
            subject TEXT,
            topic TEXT,
            method_name TEXT,
            steps TEXT,
            examples TEXT,
            embedding vector(1024)
        );
    """)
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS student_analysis (
            id SERIAL PRIMARY KEY,
            student_id TEXT,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            weak_topics TEXT,
            error_patterns TEXT,
            learning_style TEXT,
            improvement_suggestions TEXT
        );
    """)
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS class_analysis (
            id SERIAL PRIMARY KEY,
            class_id TEXT,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            overall_performance TEXT,
            common_errors TEXT,
            teaching_focus TEXT,
            student_progress TEXT
        );
    """)
    
    await conn.close()


@register_microservice(
    name="opea_service@api",
    service_type=ServiceType.LLM,
    endpoint="/grade",
    host="0.0.0.0",
    port=9000,
)
async def grade_exam(params: dict):
    """批改试卷（含步骤级分析）"""
    paper_id = params.get("paper_id")
    student_id = params.get("student_id")
    student_answers = params.get("answers")
    
    if not paper_id or not student_id or not student_answers:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "grade_with_steps",
                        "paper_id": paper_id,
                        "student_id": student_id,
                        "answers": student_answers
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/upload_paper", host="0.0.0.0", port=9000
)
async def upload_paper(
    file: UploadFile = File(...),
    paper_id: str = Form(...),
    title: str = Form(...),
    subject: str = Form(...),
):
    """上传试卷"""
    try:
        save_path = upload_folder + encode_filename(file.filename)
        await save_content_to_local_disk(save_path, file)
        content = document_loader(save_path)
        
        conn = await asyncpg.connect(
            user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
        )
        
        await conn.execute(
            """
            INSERT INTO exam_papers (paper_id, title, subject, content)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (paper_id) DO UPDATE SET content = $4, title = $2;
            """,
            paper_id, title, subject, content
        )
        
        await conn.close()
        
        return {"status": 200, "message": "Paper uploaded successfully", "paper_id": paper_id}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


@register_microservice(
    name="opea_service@api", endpoint="/upload_answers", host="0.0.0.0", port=9000
)
async def upload_answers(
    paper_id: str = Form(...),
    student_id: str = Form(...),
    answers: str = Form(...),
):
    """上传学生答卷"""
    try:
        conn = await asyncpg.connect(
            user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
        )
        
        await conn.execute(
            """
            INSERT INTO student_answers (paper_id, student_id, answers)
            VALUES ($1, $2, $3);
            """,
            paper_id, student_id, answers
        )
        
        await conn.close()
        
        return {"status": 200, "message": "Answers uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


@register_microservice(
    name="opea_service@api", endpoint="/wrong_questions", host="0.0.0.0", port=9000
)
async def get_wrong_questions(student_id: str = Form(...)):
    """获取学生错题列表（含步骤分析）"""
    try:
        conn = await asyncpg.connect(
            user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
        )
        
        results = await conn.fetch(
            """
            SELECT * FROM wrong_questions WHERE student_id = $1 ORDER BY timestamp DESC;
            """,
            student_id
        )
        
        await conn.close()
        
        wrong_questions = []
        for row in results:
            wrong_questions.append({
                "id": row["id"],
                "question_id": row["question_id"],
                "paper_id": row["paper_id"],
                "question_content": row["question_content"],
                "student_answer": row["student_answer"],
                "correct_answer": row["correct_answer"],
                "knowledge_points": json.loads(row["knowledge_points"]) if row["knowledge_points"] else [],
                "difficulty": row["difficulty"],
                "timestamp": row["timestamp"].isoformat(),
                "step_analysis": json.loads(row["step_analysis"]) if row["step_analysis"] else None,
                "correct_steps": json.loads(row["correct_steps"]) if row["correct_steps"] else None,
                "common_mistakes": json.loads(row["common_mistakes"]) if row["common_mistakes"] else None,
                "teaching_suggestions": row["teaching_suggestions"]
            })
        
        return {"status": 200, "data": wrong_questions}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")


@register_microservice(
    name="opea_service@api", endpoint="/review_suggestion", host="0.0.0.0", port=9000
)
async def get_review_suggestion(student_id: str = Form(...)):
    """获取复习建议"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "review_suggestion",
                        "student_id": student_id
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/generate_quiz", host="0.0.0.0", port=9000
)
async def generate_quiz(student_id: str = Form(...), question_count: int = Form(10)):
    """生成个性化检查卷"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "generate_quiz",
                        "student_id": student_id,
                        "question_count": question_count
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/step_analysis", host="0.0.0.0", port=9000
)
async def get_step_analysis(question_id: str = Form(...), student_id: str = Form(...)):
    """获取单题步骤分析"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "step_analysis",
                        "question_id": question_id,
                        "student_id": student_id
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/student_analysis", host="0.0.0.0", port=9000
)
async def get_student_analysis(student_id: str = Form(...)):
    """获取学生综合分析报告"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "student_analysis",
                        "student_id": student_id
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/class_analysis", host="0.0.0.0", port=9000
)
async def get_class_analysis(class_id: str = Form(...)):
    """获取班级分析报告（供老师使用）"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "class_analysis",
                        "class_id": class_id
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/teaching_suggestions", host="0.0.0.0", port=9000
)
async def get_teaching_suggestions(subject: str = Form(...), topic: str = Form("")):
    """获取教学建议（供老师使用）"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "teaching_suggestions",
                        "subject": subject,
                        "topic": topic
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/recommend_materials", host="0.0.0.0", port=9000
)
async def recommend_learning_materials(
    student_id: str = Form(...),
    material_type: str = Form(None)
):
    """推荐学习资料（基于薄弱知识点）"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "recommend_materials",
                        "student_id": student_id,
                        "material_type": material_type
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/rate_material", host="0.0.0.0", port=9000
)
async def rate_learning_material(
    material_id: str = Form(...),
    student_id: str = Form(...),
    rating: int = Form(...),
    effectiveness_score: float = Form(0.0),
    learning_outcome: str = Form(""),
    time_spent: int = Form(0),
    completed: bool = Form(True),
    feedback: str = Form(None)
):
    """评价学习资料"""
    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "rate_material",
                        "material_id": material_id,
                        "student_id": student_id,
                        "rating": rating,
                        "effectiveness_score": effectiveness_score,
                        "learning_outcome": learning_outcome,
                        "time_spent": time_spent,
                        "completed": completed,
                        "feedback": feedback
                    })
                }
            )
            result = response.json()
            return {"status": 200, "message": "Rating saved successfully", "data": result}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Rating failed: {str(e)}")


@register_microservice(
    name="opea_service@api", endpoint="/exam_analysis", host="0.0.0.0", port=9000
)
async def analyze_exam_papers(
    student_id: str = Form(...),
    subject: str = Form("数学"),
    years: str = Form("2023,2022,2021")
):
    """高考真题分析（对比学生掌握情况）"""
    years_list = [int(y.strip()) for y in years.split(",")]
    
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "exam_analysis",
                        "student_id": student_id,
                        "subject": subject,
                        "years": years_list
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/create_review_plan", host="0.0.0.0", port=9000
)
async def create_exam_review_plan(
    student_id: str = Form(...),
    exam_date: str = Form(...),
    available_time_per_day: int = Form(120)
):
    """创建考前复习计划"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "create_review_plan",
                        "student_id": student_id,
                        "exam_date": exam_date,
                        "available_time_per_day": available_time_per_day
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/evaluate_material", host="0.0.0.0", port=9000
)
async def evaluate_learning_material(material_id: str = Form(...)):
    """评估学习资料有效性"""
    async def event_stream():
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "evaluate_material",
                        "material_id": material_id
                    }),
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@register_microservice(
    name="opea_service@api", endpoint="/update_mastery", host="0.0.0.0", port=9000
)
async def update_knowledge_mastery(
    student_id: str = Form(...),
    knowledge_point_id: str = Form(...),
    is_correct: bool = Form(...)
):
    """更新知识点掌握度"""
    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "update_mastery",
                        "student_id": student_id,
                        "knowledge_point_id": knowledge_point_id,
                        "is_correct": is_correct
                    })
                }
            )
            result = response.json()
            return {"status": 200, "message": "Mastery updated successfully", "data": result}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")


@register_microservice(
    name="opea_service@api", endpoint="/get_weak_points", host="0.0.0.0", port=9000
)
async def get_weak_knowledge_points(
    student_id: str = Form(...),
    threshold: float = Form(0.6)
):
    """获取学生薄弱知识点"""
    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                GRADER_AGENT_ENDPOINT,
                json={
                    "messages": json.dumps({
                        "action": "get_weak_points",
                        "student_id": student_id,
                        "threshold": threshold
                    })
                }
            )
            result = response.json()
            return {"status": 200, "data": result}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")


@register_microservice(
    name="opea_service@api", endpoint="/upload_material", host="0.0.0.0", port=9000
)
async def upload_learning_material(
    material_id: str = Form(...),
    title: str = Form(...),
    material_type: str = Form(...),
    subject: str = Form(...),
    topic: str = Form(...),
    knowledge_points: str = Form(...),
    description: str = Form(""),
    url: str = Form(""),
    duration_minutes: int = Form(0),
    difficulty_level: str = Form("中等"),
    target_audience: str = Form(""),
    tags: str = Form(""),
    author: str = Form(""),
    source: str = Form("")
):
    """上传学习资料（供老师使用）"""
    try:
        conn = await asyncpg.connect(
            user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
        )
        
        await conn.execute(
            """
            INSERT INTO learning_materials (
                material_id, title, material_type, subject, topic,
                knowledge_points, description, url, duration_minutes,
                difficulty_level, target_audience, tags, author, source
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            ON CONFLICT (material_id) DO UPDATE SET
                title = $2, material_type = $3, subject = $4, topic = $5,
                knowledge_points = $6, description = $7, url = $8, duration_minutes = $9,
                difficulty_level = $10, target_audience = $11, tags = $12, author = $13, source = $14;
            """,
            material_id, title, material_type, subject, topic,
            knowledge_points, description, url, duration_minutes,
            difficulty_level, target_audience, tags, author, source
        )
        
        await conn.close()
        
        return {"status": 200, "message": "Material uploaded successfully", "material_id": material_id}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


@register_microservice(
    name="opea_service@api", endpoint="/upload_exam_archive", host="0.0.0.0", port=9000
)
async def upload_exam_paper_archive(
    year: int = Form(...),
    province: str = Form(...),
    subject: str = Form(...),
    paper_type: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    knowledge_points: str = Form(""),
    difficulty_distribution: str = Form(""),
    total_score: int = Form(150)
):
    """上传高考真题（供管理员使用）"""
    try:
        conn = await asyncpg.connect(
            user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
        )
        
        await conn.execute(
            """
            INSERT INTO exam_papers_archive (
                year, province, subject, paper_type, title,
                content, knowledge_points, difficulty_distribution, total_score
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
            """,
            year, province, subject, paper_type, title,
            content, knowledge_points, difficulty_distribution, total_score
        )
        
        await conn.close()
        
        return {"status": 200, "message": "Exam paper archived successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(init_db())
    opea_microservices["opea_service@api"].start()
