# ExamGrader - Intelligent Exam Grading System

![ExamGrader Logo](https://img.shields.io/badge/ExamGrader-AI%20Powered-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

An intelligent exam grading system that integrates **AI-powered grading**, **step-level error analysis**, and **personalized learning recommendations** to form a complete learning loop.

---

## 🌟 System Overview

ExamGrader is an AI-powered education platform designed to address key pain points in education:

| Pain Point | Solution |
|------------|----------|
| Heavy grading workload for teachers | AI-powered automated grading |
| Ineffective wrong question organization | Smart collection and analysis |
| Lack of focused review | Personalized review suggestions |
| No targeted weakness improvement | Custom check papers and material recommendations |

### Core Features

1. **AI Intelligent Grading** - Automatically grade exams with high accuracy
2. **Step-Level Error Analysis** - Identify mistakes at each problem-solving step
3. **RAG Knowledge System** - Retrieve correct methods and optimized solutions
4. **Wrong Question Collection** - Personalized wrong question notebook
5. **Smart Review Suggestions** - Targeted review plans based on weak points
6. **Teacher Dashboard** - Class performance analysis and teaching recommendations
7. **Material Recommendation** - Personalized learning resources with effectiveness tracking
8. **College Entrance Exam Analysis** - Compare mastery with high-frequency exam points

---

## 🚀 Quick Start

### One-Click Deployment

```powershell
# Clone the repository
git clone https://github.com/examgrader/exam-grader.git
cd exam-grader

# Run the deployment script
.\deploy.ps1
```

The script will:
1. Check system requirements
2. Download necessary AI models
3. Start all services using Docker Compose

### Manual Deployment

```powershell
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Access Services

| Service | URL |
|---------|-----|
| Web UI | http://localhost:5173 |
| API | http://localhost:8000 |
| LLM Service | http://localhost:8001 |
| Embedding Service | http://localhost:8002 |
| Agent Service | http://localhost:8003 |

---

## 🛠️ Hardware/Software Requirements

### Minimum Requirements

| Component | Specification |
|-----------|---------------|
| CPU | 4 cores (Intel i5 or equivalent) |
| RAM | 16 GB |
| GPU | NVIDIA GPU with 8GB VRAM (for LLM) |
| Storage | 50 GB free space |
| Network | Stable internet connection |

### Software Dependencies

| Software | Version | Purpose |
|----------|---------|---------|
| Docker Desktop | >= 24.0 | Container orchestration |
| Docker Compose | >= 2.0 | Multi-container deployment |
| NVIDIA Docker | >= 2.0 | GPU acceleration |
| WSL2 | Latest | Linux subsystem (Windows) |

### Recommended Requirements

| Component | Specification |
|-----------|---------------|
| CPU | 8 cores (Intel i7 or equivalent) |
| RAM | 32 GB |
| GPU | NVIDIA RTX 3090/4090 (24GB VRAM) |
| Storage | 100 GB SSD |

---

## 📁 Project Structure

```
exam-grader/
├── api/                    # FastAPI backend service
│   ├── app/               # Application code
│   ├── tests/             # Unit tests
│   └── Dockerfile
├── agent/                 # OPEA-based agent service
│   ├── agents/            # AI agents
│   └── Dockerfile
├── embedding/             # Embedding service
│   └── Dockerfile
├── web/                   # React frontend
│   ├── src/              # Source code
│   └── Dockerfile
├── scripts/              # Database initialization
│   └── init.sql
├── docker-compose.yml    # Docker Compose configuration
├── deploy.ps1           # One-click deployment script
└── README.md            # This file
```

---

## 🔧 Configuration

### Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://examgrader:examgrader123@postgres:5432/examgrader

# Redis Configuration
REDIS_URL=redis://redis:6379

# Service URLs
LLM_SERVICE_URL=http://llm:8000
EMBEDDING_SERVICE_URL=http://embedding:8000
AGENT_SERVICE_URL=http://agent:8000

# Model Configuration
LLM_MODEL=Qwen/Qwen2-7B-Instruct
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Deployment Modes

| Mode | Services Started | Use Case |
|------|-----------------|----------|
| full | All services | Production environment |
| lite | API + Web only | Development/testing |
| api-only | API only | Backend testing |

```powershell
# Start in lite mode
.\deploy.ps1 -Action start -Mode lite

# Start API only
.\deploy.ps1 -Action start -Mode api-only
```

---

## 📋 Expected Outcomes

After successful deployment, you can expect:

### For Teachers

1. **Automated Grading** - Reduce grading time by 80%
2. **Class Analytics** - View comprehensive performance reports
3. **Teaching Recommendations** - Get targeted improvement suggestions
4. **Custom Check Papers** - Generate personalized assessments

### For Students

1. **Instant Feedback** - Get detailed analysis of wrong answers
2. **Step-by-Step Guidance** - Understand exactly where mistakes occurred
3. **Optimized Methods** - Learn alternative problem-solving approaches
4. **Personalized Review** - Focus on weak areas with targeted practice

### System Metrics

| Metric | Expected Value |
|--------|---------------|
| Grading Accuracy | > 95% |
| Response Time | < 5 seconds |
| Step Analysis Coverage | 100% of math problems |
| Recommendation Relevance | > 90% |

---

## 🔌 API Endpoints

### Exam Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/exams` | POST | Upload exam paper |
| `/api/exams/{id}` | GET | Get exam details |
| `/api/exams/{id}` | PUT | Update exam |
| `/api/exams/{id}` | DELETE | Delete exam |

### Grading

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/grading` | POST | Grade student answers |
| `/api/grading/{id}` | GET | Get grading results |
| `/api/grading/step-analysis` | POST | Analyze problem-solving steps |

### Wrong Questions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/wrong-questions` | GET | Get wrong questions for student |
| `/api/wrong-questions/{id}` | DELETE | Remove wrong question |

### Recommendations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/recommendations` | GET | Get review suggestions |
| `/api/check-paper` | POST | Generate check paper |
| `/api/materials` | GET | Get learning material recommendations |

---

## 🧪 Testing

### Run Tests

```powershell
# Run API tests
cd api
docker-compose run api pytest

# Run integration tests
docker-compose run api pytest tests/integration
```

### Health Checks

```powershell
# Check API health
curl http://localhost:8000/health

# Check LLM service
curl http://localhost:8001/v1/models

# Check embedding service
curl http://localhost:8002/health
```

---

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📞 Support

For support, please open an issue on GitHub or contact us at support@examgrader.ai.

---

**Built with ❤️ by the ExamGrader Team**