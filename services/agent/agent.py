# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import os
from typing import Any, Dict, List

import asyncpg
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from comps import ServiceType, opea_microservices, register_microservice

load_dotenv()

LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8008/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
pg_host = os.getenv("PG_HOST", "")
pg_port = os.getenv("PG_PORT", "5432")
pg_user = os.getenv("PG_USER", "")
pg_pwd = os.getenv("PG_PWD", "")
pg_db = os.getenv("PG_DB", "")

llm = ChatOpenAI(
    model=LLM_MODEL,
    openai_api_key="dummy",
    openai_api_base=LLM_ENDPOINT,
    temperature=0.01,
)


async def get_paper_content(paper_id: str) -> str:
    """获取试卷内容"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    result = await conn.fetchrow(
        "SELECT content FROM exam_papers WHERE paper_id = $1;", paper_id
    )
    await conn.close()
    return result["content"] if result else ""


async def save_wrong_question(
    question_id: str,
    student_id: str,
    paper_id: str,
    question_content: str,
    student_answer: str,
    correct_answer: str,
    knowledge_points: List[str],
    difficulty: str,
    step_analysis: Dict = None,
    correct_steps: List[str] = None,
    common_mistakes: List[str] = None,
    teaching_suggestions: str = None,
):
    """保存错题到数据库（含步骤分析）"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    await conn.execute(
        """
        INSERT INTO wrong_questions (
            question_id, student_id, paper_id, question_content,
            student_answer, correct_answer, knowledge_points, difficulty,
            step_analysis, correct_steps, common_mistakes, teaching_suggestions
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);
        """,
        question_id, student_id, paper_id, question_content,
        student_answer, correct_answer, json.dumps(knowledge_points), difficulty,
        json.dumps(step_analysis) if step_analysis else None,
        json.dumps(correct_steps) if correct_steps else None,
        json.dumps(common_mistakes) if common_mistakes else None,
        teaching_suggestions
    )
    await conn.close()


async def get_student_wrong_questions(student_id: str) -> List[Dict[str, Any]]:
    """获取学生错题"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    results = await conn.fetch(
        "SELECT * FROM wrong_questions WHERE student_id = $1 ORDER BY timestamp DESC;",
        student_id
    )
    await conn.close()
    return [dict(row) for row in results]


async def get_knowledge_point_methods(subject: str, topic: str = "") -> Dict[str, Any]:
    """从RAG系统获取知识点的正确方法"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    if topic:
        result = await conn.fetchrow(
            """
            SELECT correct_methods, common_errors, teaching_tips 
            FROM knowledge_points 
            WHERE subject = $1 AND topic = $2;
            """,
            subject, topic
        )
    else:
        results = await conn.fetch(
            """
            SELECT topic, correct_methods, common_errors, teaching_tips 
            FROM knowledge_points 
            WHERE subject = $1;
            """,
            subject
        )
        await conn.close()
        return [dict(row) for row in results]
    
    await conn.close()
    return dict(result) if result else {}


async def get_step_template(subject: str, topic: str) -> Dict[str, Any]:
    """从RAG系统获取解题步骤模板"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    result = await conn.fetchrow(
        """
        SELECT method_name, steps, examples 
        FROM step_templates 
        WHERE subject = $1 AND topic = $2;
        """,
        subject, topic
    )
    await conn.close()
    return dict(result) if result else {}


def generate_grading_prompt_with_steps(paper_content: str, student_answers: str) -> str:
    """生成带步骤分析的批改提示词"""
    prompt = f"""
    你是一名专业的数学老师，请根据以下试卷内容和学生答案进行详细批改：

    ## 试卷内容：
    {paper_content}

    ## 学生答案：
    {student_answers}

    ## 批改要求：
    1. 仔细分析每道题目的解答过程
    2. 识别学生在哪个步骤出错
    3. 分析错误原因和类型
    4. 提供正确的解题步骤
    5. 列出该知识点的常见错误
    6. 给出教学建议

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - score: 总分
    - total_score: 试卷满分
    - results: 每道题的批改结果数组，包含：
        - question_id: 题目ID
        - question_type: 题型
        - student_answer: 学生答案
        - correct_answer: 正确答案
        - score: 得分
        - max_score: 满分
        - is_correct: 是否正确
        - error_reason: 错误原因
        - knowledge_points: 知识点列表
        - difficulty: 难度等级（简单/中等/困难）
        - step_analysis: 步骤分析对象，包含：
            - student_steps: 学生的解题步骤列表
            - error_step_index: 出错步骤索引（-1表示正确）
            - error_step_desc: 错误步骤描述
            - error_type: 错误类型（概念错误/计算错误/步骤遗漏/逻辑错误）
        - correct_steps: 正确解题步骤列表
        - common_mistakes: 该知识点常见错误列表
        - teaching_suggestions: 针对本题的教学建议
    """
    return prompt


def generate_step_analysis_prompt(question_content: str, student_answer: str, rag_methods: str = "", rag_steps: str = "", rag_common_mistakes: str = "", rag_troubleshooting: str = "", rag_alternative_methods: str = "", rag_shortcuts: str = "") -> str:
    """生成步骤分析提示词（结合RAG系统，包含优化方法）"""
    rag_context = ""
    if rag_methods:
        rag_context += f"\n## RAG知识库 - 正确方法：\n{rag_methods}"
    if rag_steps:
        rag_context += f"\n## RAG知识库 - 标准步骤：\n{rag_steps}"
    if rag_common_mistakes:
        rag_context += f"\n## RAG知识库 - 常见错误：\n{rag_common_mistakes}"
    if rag_troubleshooting:
        rag_context += f"\n## RAG知识库 - 错误排查指南：\n{rag_troubleshooting}"
    if rag_alternative_methods:
        rag_context += f"\n## RAG知识库 - 替代方法：\n{rag_alternative_methods}"
    if rag_shortcuts:
        rag_context += f"\n## RAG知识库 - 快捷技巧：\n{rag_shortcuts}"
    
    prompt = f"""
    你是一名专业的学科老师，请对以下题目和学生答案进行详细的步骤分析，并推荐更优的解题方法：

    ## 题目：
    {question_content}

    ## 学生答案：
    {student_answer}

    {rag_context}

    ## 分析要求：
    1. 将学生的解答过程分解为具体步骤，列出每一步的具体内容和目的
    2. 指出在哪个步骤出错，为什么出错，错误的具体位置和表现形式
    3. 分析错误类型（概念错误、计算错误、步骤遗漏、逻辑错误、粗心错误、审题错误、方法选择错误）
    4. 参考知识库中的正确方法和步骤，提供完整的正确解题步骤
    5. 分析该知识点的常见错误类型和原因，结合知识库中的信息
    6. **重点：推荐更优的解题方法，帮助学生拓展思维，掌握更简单的方法**
    7. 提供解题技巧和快捷方法，帮助学生提高解题效率
    8. 为教师提供针对性的教学建议，包括教学方法、练习设计、重点关注内容
    9. 为学生提供具体的学习建议和改进方法，包括学习策略、练习重点、复习计划

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - question_type: 题型（选择题/填空题/解答题/证明题/计算题）
    - knowledge_points: 涉及的知识点列表
    - difficulty_level: 题目难度等级（简单/中等/困难）
    - student_steps: 学生解题步骤列表（每个步骤包含step_number, content, purpose, is_correct, correctness_reason）
    - error_step_index: 出错步骤索引（-1表示全部正确）
    - error_step_content: 错误步骤的具体内容
    - error_reason: 详细的错误原因分析
    - error_type: 错误类型（概念错误/计算错误/步骤遗漏/逻辑错误/粗心错误/审题错误/方法选择错误）
    - error_severity: 错误严重程度（轻微/中等/严重/致命）
    - correct_steps: 正确解题步骤列表（详细步骤，每个步骤包含step_number, content, purpose, key_points）
    - correct_method: 正确解题方法名称
    - method_description: 方法详细说明
    
    # 新增：优化方法推荐
    - optimized_methods: 更优解题方法列表，包含：
        - method_name: 方法名称
        - method_description: 方法详细说明
        - steps: 优化后的解题步骤
        - advantages: 相比原方法的优势（更简单/更快/更直观）
        -适用场景: 何时使用此方法
        - examples: 使用示例
    - shortcut_techniques: 快捷技巧列表，包含：
        - technique_name: 技巧名称
        - description: 技巧说明
        - when_to_use: 使用时机
        - example: 示例
    - comparison_with_student_method: 与学生方法的对比，包含：
        - student_method: 学生使用的方法
        - optimized_method: 优化后的方法
        - improvement_points: 改进点列表
        - efficiency_gain: 效率提升说明
    
    - common_mistakes: 该知识点常见错误列表（包含mistake_description, mistake_reason, frequency）
    - mistake_pattern: 错误模式分析（学生常犯错误的规律）
    - teaching_suggestions: 针对教师的教学建议对象，包含：
        - key_concepts: 重点讲解的概念
        - teaching_methods: 推荐的教学方法列表
        - practice_design: 练习设计建议
        - common_errors_to_watch: 需要关注的常见错误
        - student_groups_to_focus: 需要重点关注的学生群体
    - learning_tips: 针对学生的学习建议对象，包含：
        - key_practices: 关键练习要点
        - learning_strategies: 学习策略建议
        - common_pitfalls: 需要避免的常见陷阱
        - review_schedule: 复习计划建议
        - self_check_methods: 自我检查方法
    - related_resources: 推荐的学习资源列表（书籍、视频、练习册等）
    - next_practice_suggestions: 下一步练习建议
    """
    return prompt


def generate_student_analysis_prompt(wrong_questions: List[Dict[str, Any]]) -> str:
    """生成学生综合分析提示词"""
    questions_str = json.dumps(wrong_questions, ensure_ascii=False)
    prompt = f"""
    你是一名专业的教育分析师，请根据学生的错题记录进行综合分析：

    ## 学生错题记录：
    {questions_str}

    ## 分析要求：
    1. 分析学生的薄弱知识点分布
    2. 识别学生的错误模式和习惯
    3. 判断学生的学习风格
    4. 给出针对性的改进建议

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - weak_topics: 薄弱知识点列表
    - error_patterns: 错误模式分析
    - learning_style: 学习风格描述
    - common_error_types: 常见错误类型分布
    - improvement_suggestions: 改进建议列表
    - recommended_resources: 推荐学习资源
    """
    return prompt


def generate_class_analysis_prompt(class_wrong_questions: List[Dict[str, Any]]) -> str:
    """生成班级分析提示词（供老师使用）"""
    questions_str = json.dumps(class_wrong_questions, ensure_ascii=False)
    prompt = f"""
    你是一名教学督导专家，请根据班级错题记录进行教学分析：

    ## 班级错题记录：
    {questions_str}

    ## 分析要求：
    1. 分析班级整体表现
    2. 识别班级普遍存在的错误
    3. 确定教学重点和难点
    4. 给出教学改进建议

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - overall_performance: 整体表现分析
    - common_errors: 常见错误列表
    - teaching_focus: 教学重点建议
    - student_progress: 学生进步建议
    - teaching_methods: 教学方法改进建议
    - recommended_activities: 推荐教学活动
    """
    return prompt


def generate_teaching_suggestions_prompt(subject: str, topic: str) -> str:
    """生成教学建议提示词"""
    prompt = f"""
    你是一名资深教师，请提供以下学科和知识点的教学建议：

    ## 学科：{subject}
    ## 知识点：{topic if topic else '全部'}

    ## 建议要求：
    1. 教学目标和重点
    2. 教学方法和策略
    3. 常见错误及应对
    4. 练习设计建议
    5. 评价方式建议

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - subject: 学科
    - topic: 知识点
    - teaching_objectives: 教学目标
    - key_points: 教学重点
    - teaching_methods: 教学方法列表
    - common_student_errors: 学生常见错误
    - error_prevention: 错误预防策略
    - practice_design: 练习设计建议
    - assessment_methods: 评价方式建议
    - extension_activities: 拓展活动建议
    """
    return prompt


async def get_learning_materials(knowledge_points: List[str], material_type: str = None) -> List[Dict[str, Any]]:
    """从RAG系统获取学习资料"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    query = """
        SELECT * FROM learning_materials 
        WHERE knowledge_points && $1
        ORDER BY effectiveness_score DESC, avg_rating DESC
        LIMIT 10;
    """
    
    if material_type:
        query = """
            SELECT * FROM learning_materials 
            WHERE knowledge_points && $1 AND material_type = $2
            ORDER BY effectiveness_score DESC, avg_rating DESC
            LIMIT 10;
        """
        results = await conn.fetch(query, knowledge_points, material_type)
    else:
        results = await conn.fetch(query, knowledge_points)
    
    await conn.close()
    return [dict(row) for row in results]


async def save_material_rating(
    material_id: str,
    student_id: str,
    rating: int,
    effectiveness_score: float,
    learning_outcome: str,
    time_spent: int,
    completed: bool,
    feedback: str = None
):
    """保存资料评分"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    await conn.execute(
        """
        INSERT INTO material_ratings (
            material_id, student_id, rating, effectiveness_score,
            learning_outcome, time_spent_minutes, completed, feedback
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
        """,
        material_id, student_id, rating, effectiveness_score,
        learning_outcome, time_spent, completed, feedback
    )
    
    avg_result = await conn.fetchrow(
        """
        SELECT AVG(rating) as avg_rating, AVG(effectiveness_score) as avg_effect
        FROM material_ratings WHERE material_id = $1;
        """,
        material_id
    )
    
    if avg_result:
        await conn.execute(
            """
            UPDATE learning_materials 
            SET avg_rating = $1, effectiveness_score = $2, usage_count = usage_count + 1
            WHERE material_id = $3;
            """,
            avg_result['avg_rating'], avg_result['avg_effect'], material_id
        )
    
    await conn.close()


async def get_exam_papers_archive(year: int = None, subject: str = None, province: str = None) -> List[Dict[str, Any]]:
    """获取历年高考真题"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    conditions = []
    params = []
    param_idx = 1
    
    if year:
        conditions.append(f"year = ${param_idx}")
        params.append(year)
        param_idx += 1
    if subject:
        conditions.append(f"subject = ${param_idx}")
        params.append(subject)
        param_idx += 1
    if province:
        conditions.append(f"province = ${param_idx}")
        params.append(province)
        param_idx += 1
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM exam_papers_archive WHERE {where_clause} ORDER BY year DESC;"
    
    results = await conn.fetch(query, *params)
    await conn.close()
    return [dict(row) for row in results]


async def update_knowledge_mastery(student_id: str, knowledge_point_id: str, is_correct: bool):
    """更新知识点掌握度"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    existing = await conn.fetchrow(
        """
        SELECT * FROM knowledge_mastery 
        WHERE student_id = $1 AND knowledge_point_id = $2;
        """,
        student_id, knowledge_point_id
    )
    
    if existing:
        new_practice_count = existing['practice_count'] + 1
        new_correct_count = existing['correct_count'] + (1 if is_correct else 0)
        new_mastery = new_correct_count / new_practice_count
        
        await conn.execute(
            """
            UPDATE knowledge_mastery 
            SET practice_count = $1, correct_count = $2, mastery_level = $3,
                last_practice_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE student_id = $4 AND knowledge_point_id = $5;
            """,
            new_practice_count, new_correct_count, new_mastery,
            student_id, knowledge_point_id
        )
    else:
        await conn.execute(
            """
            INSERT INTO knowledge_mastery (
                student_id, knowledge_point_id, mastery_level, 
                practice_count, correct_count, last_practice_at
            ) VALUES ($1, $2, $3, 4, $5, CURRENT_TIMESTAMP);
            """,
            student_id, knowledge_point_id, 
            1.0 if is_correct else 0.0,
            1, 1 if is_correct else 0
        )
    
    await conn.close()


async def get_student_weak_knowledge_points(student_id: str, threshold: float = 0.6) -> List[Dict[str, Any]]:
    """获取学生薄弱知识点"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    results = await conn.fetch(
        """
        SELECT km.*, kp.topic, kp.description 
        FROM knowledge_mastery km
        JOIN knowledge_points kp ON km.knowledge_point_id = kp.point_id
        WHERE km.student_id = $1 AND km.mastery_level < $2
        ORDER BY km.mastery_level ASC;
        """,
        student_id, threshold
    )
    
    await conn.close()
    return [dict(row) for row in results]


async def get_student_knowledge_mastery(student_id: str) -> List[Dict[str, Any]]:
    """获取学生所有知识点掌握度"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    results = await conn.fetch(
        """
        SELECT km.*, kp.topic, kp.description 
        FROM knowledge_mastery km
        JOIN knowledge_points kp ON km.knowledge_point_id = kp.point_id
        WHERE km.student_id = $1
        ORDER BY km.mastery_level ASC;
        """,
        student_id
    )
    
    await conn.close()
    return [dict(row) for row in results]


async def create_review_plan(
    student_id: str,
    plan_type: str,
    start_date: str,
    end_date: str,
    target_knowledge_points: List[str],
    daily_tasks: List[Dict]
):
    """创建考前复习计划"""
    conn = await asyncpg.connect(
        user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
    )
    
    await conn.execute(
        """
        INSERT INTO review_plans (
            student_id, plan_type, start_date, end_date,
            target_knowledge_points, daily_tasks
        ) VALUES ($1, $2, $3, $4, $5, $6);
        """,
        student_id, plan_type, start_date, end_date,
        json.dumps(target_knowledge_points), json.dumps(daily_tasks)
    )
    
    await conn.close()


def generate_material_recommendation_prompt(
    student_id: str,
    weak_knowledge_points: List[Dict],
    available_materials: List[Dict]
) -> str:
    """生成学习资料推荐提示词"""
    prompt = f"""
    你是一名专业的教育顾问，请根据学生的薄弱知识点和可用学习资料，推荐最适合的学习资料：

    ## 学生ID：{student_id}

    ## 薄弱知识点：
    {json.dumps(weak_knowledge_points, ensure_ascii=False, indent=2)}

    ## 可用学习资料：
    {json.dumps(available_materials, ensure_ascii=False, indent=2)}

    ## 推荐要求：
    1. 优先推荐针对薄弱知识点的资料
    2. 考虑资料的类型（视频、动画、文档等）适合学生
    3. 考虑资料的难度和时长
    4. 提供学习顺序建议

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - recommended_materials: 推荐资料列表，每个包含：
        - material_id: 资料ID
        - title: 资料标题
        - reason: 推荐理由
        - priority: 优先级（1-5）
        - expected_outcome: 预期学习效果
    - learning_sequence: 学习顺序建议
    - estimated_total_time: 预计总学习时长（分钟）
    - tips: 学习建议
    """
    return prompt


def generate_exam_analysis_prompt(
    exam_papers: List[Dict],
    student_knowledge_points: List[str],
    student_mastery: List[Dict]
) -> str:
    """生成高考真题分析提示词"""
    prompt = f"""
    你是一名高考研究专家，请分析历年高考真题，并为学生提供针对性的复习建议：

    ## 历年高考真题：
    {json.dumps(exam_papers, ensure_ascii=False, indent=2)}

    ## 学生已掌握知识点：
    {json.dumps(student_knowledge_points, ensure_ascii=False, indent=2)}

    ## 学生知识点掌握度：
    {json.dumps(student_mastery, ensure_ascii=False, indent=2)}

    ## 分析要求：
    1. 提取历年高考高频知识点
    2. 分析知识点考查频率和难度
    3. 对比学生掌握情况，找出差距
    4. 生成针对性复习题建议

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - high_frequency_points: 高频知识点列表，包含：
        - point_id: 知识点ID
        - topic: 知识点名称
        - frequency: 考查频率
        - avg_difficulty: 平均难度
        - question_types: 常见题型
    - gap_analysis: 差距分析，包含：
        - mastered_points: 已掌握的高频点
        - weak_points: 薄弱的高频点
        - missing_points: 未学习的高频点
    - review_priorities: 复习优先级列表
    - suggested_practice_questions: 建议练习题目类型
    - exam_strategy: 考试策略建议
    """
    return prompt


def generate_review_plan_prompt(
    student_id: str,
    weak_points: List[Dict],
    exam_date: str,
    available_time_per_day: int
) -> str:
    """生成考前复习计划提示词"""
    prompt = f"""
    你是一名专业的学习规划师，请为学生制定考前复习计划：

    ## 学生ID：{student_id}

    ## 薄弱知识点：
    {json.dumps(weak_points, ensure_ascii=False, indent=2)}

    ## 考试日期：{exam_date}

    ## 每天可用学习时间：{available_time_per_day}分钟

    ## 计划要求：
    1. 合理分配复习时间
    2. 重点攻克薄弱知识点
    3. 安排适当的练习和测试
    4. 预留复习和巩固时间

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - plan_overview: 计划概览
    - daily_schedule: 每日计划列表，每个包含：
        - date: 日期
        - tasks: 任务列表
        - time_allocation: 时间分配
        - expected_outcome: 预期成果
    - milestones: 里程碑节点
    - checkpoints: 检查点安排
    - adjustment_suggestions: 调整建议
    """
    return prompt


def generate_material_evaluation_prompt(
    material_info: Dict,
    student_feedbacks: List[Dict]
) -> str:
    """生成资料评估提示词"""
    prompt = f"""
    你是一名教育评估专家，请评估学习资料的有效性：

    ## 资料信息：
    {json.dumps(material_info, ensure_ascii=False, indent=2)}

    ## 学生反馈：
    {json.dumps(student_feedbacks, ensure_ascii=False, indent=2)}

    ## 评估要求：
    1. 分析资料对学生学习的帮助程度
    2. 评估资料的适用性
    3. 识别资料的优缺点
    4. 给出改进建议

    ## 输出格式：
    请以JSON格式输出，包含以下字段：
    - overall_score: 总体评分（1-10）
    - effectiveness_analysis: 有效性分析
    - suitability_analysis: 适用性分析
    - strengths: 优点列表
    - weaknesses: 不足列表
    - improvement_suggestions: 改进建议
    - recommended_audience: 推荐适用人群
    - usage_tips: 使用建议
    """
    return prompt


@register_microservice(
    name="opea_service@grader_agent",
    service_type=ServiceType.LLM,
    endpoint="/v1/chat/completions",
    host="0.0.0.0",
    port=9095,
)
async def grader_agent(params: Dict[str, Any]):
    """批改Agent主入口"""
    messages = params.get("messages", "{}")
    
    try:
        data = json.loads(messages)
    except json.JSONDecodeError:
        data = {}
    
    action = data.get("action", "grade_with_steps")
    
    if action == "grade_with_steps" or "paper_id" in data:
        paper_id = data.get("paper_id")
        student_id = data.get("student_id")
        student_answers = data.get("answers", "")
        
        paper_content = await get_paper_content(paper_id)
        if not paper_content:
            return {"error": "Paper not found"}
        
        prompt = generate_grading_prompt_with_steps(paper_content, student_answers)
        response = llm.invoke(prompt)
        
        try:
            result = json.loads(response.content)
            
            for question_result in result.get("results", []):
                if not question_result.get("is_correct", True):
                    await save_wrong_question(
                        question_id=question_result.get("question_id", ""),
                        student_id=student_id,
                        paper_id=paper_id,
                        question_content=question_result.get("question_content", ""),
                        student_answer=question_result.get("student_answer", ""),
                        correct_answer=question_result.get("correct_answer", ""),
                        knowledge_points=question_result.get("knowledge_points", []),
                        difficulty=question_result.get("difficulty", "中等"),
                        step_analysis=question_result.get("step_analysis"),
                        correct_steps=question_result.get("correct_steps"),
                        common_mistakes=question_result.get("common_mistakes"),
                        teaching_suggestions=question_result.get("teaching_suggestions")
                    )
            
            return result
        except json.JSONDecodeError:
            return {"score": 0, "error": "Failed to parse grading result"}
    
    elif action == "step_analysis":
        question_id = data.get("question_id")
        student_id = data.get("student_id")
        
        wrong_questions = await get_student_wrong_questions(student_id)
        question = next((q for q in wrong_questions if q["question_id"] == question_id), None)
        
        if not question:
            return {"error": "Question not found"}
        
        # 从RAG系统获取知识点的完整信息，包括优化方法
        rag_methods = ""
        rag_steps = ""
        rag_common_mistakes = ""
        rag_troubleshooting = ""
        rag_alternative_methods = ""
        rag_shortcuts = ""
        
        knowledge_points = question.get("knowledge_points", "")
        if knowledge_points:
            try:
                kp_list = json.loads(knowledge_points)
                for kp in kp_list:
                    # 获取知识点的完整信息
                    method_info = await get_knowledge_point_methods("数学", kp)
                    if method_info and isinstance(method_info, dict):
                        rag_methods += f"\n- 知识点: {kp}\n  正确方法: {method_info.get('correct_methods', '')}\n  教学要点: {method_info.get('teaching_tips', '')}"
                        if method_info.get('common_errors'):
                            rag_common_mistakes += f"\n- {kp}: {method_info.get('common_errors')}"
                        if method_info.get('troubleshooting_guide'):
                            rag_troubleshooting += f"\n- {kp}: {method_info.get('troubleshooting_guide')}"
                        if method_info.get('alternative_methods'):
                            rag_alternative_methods += f"\n- {kp}替代方法: {method_info.get('alternative_methods')}"
                        if method_info.get('shortcut_techniques'):
                            rag_shortcuts += f"\n- {kp}快捷技巧: {method_info.get('shortcut_techniques')}"
                    
                    # 获取步骤模板的完整信息
                    step_template = await get_step_template("数学", kp)
                    if step_template:
                        rag_steps += f"\n- 方法: {step_template.get('method_name', '')}\n  标准步骤: {step_template.get('steps', '')}\n  示例: {step_template.get('examples', '')}"
                        if step_template.get('common_mistakes'):
                            rag_common_mistakes += f"\n- {kp}常见错误: {step_template.get('common_mistakes')}"
            except Exception as e:
                print(f"Error loading RAG data: {e}")
        
        prompt = generate_step_analysis_prompt(
            question.get("question_content", ""),
            question.get("student_answer", ""),
            rag_methods,
            rag_steps,
            rag_common_mistakes,
            rag_troubleshooting,
            rag_alternative_methods,
            rag_shortcuts
        )
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"analysis": response.content}
    
    elif action == "review_suggestion":
        student_id = data.get("student_id")
        wrong_questions = await get_student_wrong_questions(student_id)
        
        if not wrong_questions:
            return {"message": "No wrong questions found"}
        
        prompt = generate_step_analysis_prompt(
            str([q["question_content"] for q in wrong_questions]),
            str([q["student_answer"] for q in wrong_questions])
        )
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"suggestion": response.content}
    
    elif action == "student_analysis":
        student_id = data.get("student_id")
        wrong_questions = await get_student_wrong_questions(student_id)
        
        if not wrong_questions:
            return {"message": "No wrong questions found"}
        
        prompt = generate_student_analysis_prompt(wrong_questions)
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"analysis": response.content}
    
    elif action == "class_analysis":
        class_id = data.get("class_id")
        all_wrong_questions = []
        
        conn = await asyncpg.connect(
            user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
        )
        results = await conn.fetch(
            "SELECT * FROM wrong_questions ORDER BY timestamp DESC LIMIT 100;"
        )
        await conn.close()
        
        all_wrong_questions = [dict(row) for row in results]
        
        if not all_wrong_questions:
            return {"message": "No data available"}
        
        prompt = generate_class_analysis_prompt(all_wrong_questions)
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"analysis": response.content}
    
    elif action == "teaching_suggestions":
        subject = data.get("subject", "")
        topic = data.get("topic", "")
        
        prompt = generate_teaching_suggestions_prompt(subject, topic)
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"suggestions": response.content}
    
    elif action == "generate_quiz":
        student_id = data.get("student_id")
        count = data.get("question_count", 10)
        wrong_questions = await get_student_wrong_questions(student_id)
        
        if not wrong_questions:
            return {"message": "No wrong questions found to generate quiz"}
        
        questions_str = json.dumps(wrong_questions, ensure_ascii=False)
        prompt = f"""
        你是一名专业的出题老师，请根据学生的错题记录生成针对性的检查卷。

        ## 学生错题记录：
        {questions_str}

        ## 出题要求：
        1. 根据错题涉及的知识点生成新题目
        2. 题目类型应多样化
        3. 难度适中，重点考察薄弱知识点
        4. 生成{count}道题目
        5. 每道题需提供参考答案和评分标准

        ## 输出格式：
        请以JSON格式输出，包含以下字段：
        - title: 检查卷标题
        - subject: 科目
        - total_score: 总分
        - questions: 题目数组，包含：
            - question_id: 题目ID
            - question_type: 题型
            - content: 题目内容
            - options: 选项（选择题）
            - correct_answer: 正确答案
            - score: 分值
            - knowledge_points: 考察知识点
            - difficulty: 难度等级
            - solving_steps: 解题步骤提示
        """
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"quiz": response.content}
    
    elif action == "recommend_materials":
        student_id = data.get("student_id")
        material_type = data.get("material_type", None)
        
        weak_points = await get_student_weak_knowledge_points(student_id)
        
        if not weak_points:
            return {"message": "No weak knowledge points found"}
        
        knowledge_point_ids = [wp['knowledge_point_id'] for wp in weak_points]
        available_materials = await get_learning_materials(knowledge_point_ids, material_type)
        
        if not available_materials:
            return {"message": "No suitable materials found"}
        
        prompt = generate_material_recommendation_prompt(student_id, weak_points, available_materials)
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"recommendations": response.content}
    
    elif action == "rate_material":
        material_id = data.get("material_id")
        student_id = data.get("student_id")
        rating = data.get("rating")
        effectiveness_score = data.get("effectiveness_score", 0.0)
        learning_outcome = data.get("learning_outcome", "")
        time_spent = data.get("time_spent", 0)
        completed = data.get("completed", True)
        feedback = data.get("feedback", None)
        
        await save_material_rating(
            material_id, student_id, rating, effectiveness_score,
            learning_outcome, time_spent, completed, feedback
        )
        
        return {"message": "Rating saved successfully", "material_id": material_id}
    
    elif action == "exam_analysis":
        student_id = data.get("student_id")
        subject = data.get("subject", "数学")
        years = data.get("years", [2023, 2022, 2021])
        
        exam_papers = []
        for year in years:
            papers = await get_exam_papers_archive(year=year, subject=subject)
            exam_papers.extend(papers)
        
        if not exam_papers:
            return {"message": "No exam papers found"}
        
        weak_points = await get_student_weak_knowledge_points(student_id)
        student_mastery = await get_student_knowledge_mastery(student_id)
        student_knowledge_points = [wm['knowledge_point_id'] for wm in student_mastery]
        
        prompt = generate_exam_analysis_prompt(exam_papers, student_knowledge_points, student_mastery)
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"analysis": response.content}
    
    elif action == "create_review_plan":
        student_id = data.get("student_id")
        exam_date = data.get("exam_date")
        available_time_per_day = data.get("available_time_per_day", 120)
        
        weak_points = await get_student_weak_knowledge_points(student_id)
        
        if not weak_points:
            return {"message": "No weak knowledge points found"}
        
        prompt = generate_review_plan_prompt(student_id, weak_points, exam_date, available_time_per_day)
        response = llm.invoke(prompt)
        
        try:
            plan = json.loads(response.content)
            
            target_points = [wp['knowledge_point_id'] for wp in weak_points]
            daily_tasks = plan.get("daily_schedule", [])
            
            await create_review_plan(
                student_id, "考前复习", 
                plan.get("start_date", ""), 
                plan.get("end_date", ""),
                target_points, daily_tasks
            )
            
            return plan
        except json.JSONDecodeError:
            return {"plan": response.content}
    
    elif action == "evaluate_material":
        material_id = data.get("material_id")
        
        conn = await asyncpg.connect(
            user=pg_user, password=pg_pwd, database=pg_db, host=pg_host, port=pg_port
        )
        
        material_info = await conn.fetchrow(
            "SELECT * FROM learning_materials WHERE material_id = $1;", material_id
        )
        
        feedbacks = await conn.fetch(
            "SELECT * FROM material_ratings WHERE material_id = $1;", material_id
        )
        
        await conn.close()
        
        if not material_info:
            return {"error": "Material not found"}
        
        prompt = generate_material_evaluation_prompt(dict(material_info), [dict(f) for f in feedbacks])
        response = llm.invoke(prompt)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"evaluation": response.content}
    
    elif action == "update_mastery":
        student_id = data.get("student_id")
        knowledge_point_id = data.get("knowledge_point_id")
        is_correct = data.get("is_correct", False)
        
        await update_knowledge_mastery(student_id, knowledge_point_id, is_correct)
        
        return {"message": "Mastery updated successfully"}
    
    elif action == "get_weak_points":
        student_id = data.get("student_id")
        threshold = data.get("threshold", 0.6)
        
        weak_points = await get_student_weak_knowledge_points(student_id, threshold)
        
        return {
            "student_id": student_id,
            "weak_points": weak_points,
            "count": len(weak_points)
        }
    
    else:
        return {"error": "Unknown action"}


if __name__ == "__main__":
    opea_microservices["opea_service@grader_agent"].start()
