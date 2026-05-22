## ExamGrader - 智能试卷批改系统

ExamGrader是一个创新的AI驱动解决方案，实现试卷和作业的自动批改，并将错题收集入题库，根据错题进行智能分析，为每位学生生成个性化的知识点分析和检查卷，完成学习闭环。

### 核心功能

1. **试卷批改** - 自动批改学生试卷和作业，支持多种题型（选择题、填空题、问答题等）
2. **错题收集** - 将学生的错题自动收集入库，建立个人错题本
3. **智能分析** - 分析错题对应的知识点，识别学习薄弱环节
4. **复习建议** - 根据错题分析结果，生成个性化复习建议
5. **检查卷生成** - 一学生一卷，根据薄弱知识点生成针对性检查卷

### 技术架构

```
├── services/
│   ├── api/                # API 微服务 (FastAPI)
│   ├── agent/              # Agent 服务 (OPEA comps)
│   ├── db/                 # 数据库配置 (PostgreSQL + pgvector)
│   ├── embedding/          # Embedding 服务
│   └── llm/                # LLM 服务 (vLLM)
├── web/                    # 前端界面 (React + TypeScript)
├── README.md
└── PPT演讲稿.md
```

### 测试环境

- 处理器：Intel(R) Xeon(R) Gold 6252N
- 操作系统：Ubuntu 22.04.1 / Windows 10+
- 软件：Docker, Python 3.10+, Node.js 18+

### 运行说明

#### 步骤1: 运行LLM service

目录：[./services/llm/](./services/llm/)

使用OPEA的`comps/llms/text-generation/vllm/langchain`启动vLLM docker容器。

启动后默认的Endpoint是`http://${vLLM_HOST_IP}:8008/v1`

#### 步骤2: 运行Embedding service

目录：[./services/embedding/](./services/embedding/)

使用OPEA的`comps/embeddings`启动容器。

启动后默认的Endpoint是`http://localhost:8009/v1/embeddings`

#### 步骤3: 运行向量数据库

目录: [./services/db/](./services/db/)

启动PostgreSQL + pgvector容器。

#### 步骤4: 运行Agent service

目录: [./services/agent/](./services/agent/)

使用OPEA的`comps/agent`框架，载入custom strategy。

#### 步骤5: 运行API microservice

目录：[./services/api/](./services/api/)

API microservice包括试卷上传、批改、错题查询等接口。

启动后默认的Endpoint是`http://${API_HOST_IP}:9000/`

#### 步骤6：运行Web UI

目录 [./web/](./web/)

Web UI提供了教师和学生的交互界面。

### 技术栈

- **后端**: FastAPI, Python 3.10+
- **Agent**: OPEA comps framework
- **数据库**: PostgreSQL + pgvector
- **LLM**: vLLM
- **前端**: React 18 + TypeScript + Vite
- **样式**: SCSS
- **状态管理**: Redux Toolkit

### 协作者

- Team ExamGrader
