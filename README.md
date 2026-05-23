# ExamGrader - Intelligent Exam Grading System

ExamGrader is an innovative AI-driven solution that enables automated grading of exams and assignments, collects wrong questions into a question bank, provides intelligent analysis based on wrong questions, generates personalized knowledge point analysis and check papers for each student, and completes the learning closed loop.

## Core Features

1. **Exam Grading** - Automatically grade student exams and assignments, supporting multiple question types (multiple choice, fill-in-the-blank, essay questions, etc.)
2. **Wrong Question Collection** - Automatically collect students' wrong questions into the database, building personal wrong question notebooks
3. **Intelligent Analysis** - Analyze knowledge points associated with wrong questions, identifying learning weak areas
4. **Review Suggestions** - Generate personalized review suggestions based on wrong question analysis results
5. **Check Paper Generation** - One student, one paper - generate targeted check papers based on weak knowledge points

## Technical Architecture

```
├── services/
│   ├── api/                # API Microservice (FastAPI)
│   ├── agent/              # Agent Service (OPEA comps)
│   ├── db/                 # Database Configuration (PostgreSQL + pgvector)
│   ├── embedding/          # Embedding Service
│   └── llm/                # LLM Service (vLLM)
├── web/                    # Frontend Interface (React + TypeScript)
├── README.md
└── PPT.md
```

## Test Environment

- **Processor**: Intel(R) Xeon(R) Gold 6252N
- **Operating System**: Ubuntu 22.04.1 / Windows 10+
- **Software**: Docker, Python 3.10+, Node.js 18+

## Running Instructions

### Step 1: Run LLM Service

Directory: [./services/llm/](./services/llm/)

Start the vLLM docker container using OPEA's `comps/llms/text-generation/vllm/langchain`.

After startup, the default endpoint is `http://${vLLM_HOST_IP}:8008/v1`

### Step 2: Run Embedding Service

Directory: [./services/embedding/](./services/embedding/)

Start the container using OPEA's `comps/embeddings`.

After startup, the default endpoint is `http://localhost:8009/v1/embeddings`

### Step 3: Run Vector Database

Directory: [./services/db/](./services/db/)

Start the PostgreSQL + pgvector container.

### Step 4: Run Agent Service

Directory: [./services/agent/](./services/agent/)

Use the OPEA `comps/agent` framework, loading custom strategy.

### Step 5: Run API Microservice

Directory: [./services/api/](./services/api/)

The API microservice includes endpoints for exam upload, grading, wrong question queries, etc.

After startup, the default endpoint is `http://${API_HOST_IP}:9000/`

### Step 6: Run Web UI

Directory [./web/](./web/)

The Web UI provides an interactive interface for teachers and students.

## Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Agent**: OPEA comps framework
- **Database**: PostgreSQL + pgvector
- **LLM**: vLLM
- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: SCSS
- **State Management**: Redux Toolkit

## Contributors

- Team ExamGrader
