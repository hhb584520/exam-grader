# ExamGrader - Intelligent Exam Grading System

![ExamGrader Logo](https://img.shields.io/badge/ExamGrader-AI%20Powered-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-green)
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
9. **OPEA Guardrails** - Enterprise-grade data protection and content safety

---

## 🚀 Quick Start

### One-Click Deployment

```bash
# Clone the repository
git clone https://github.com/examgrader/exam-grader.git
cd exam-grader

# Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Check system requirements
2. Download necessary AI models
3. Start all services using Docker Compose

### Manual Deployment

```bash
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
| Guardrails Service | http://localhost:9090 |

---

## 🛡️ OPEA Guardrails - Data Protection

ExamGrader implements OPEA Guardrails to protect all data flowing through the system. This provides enterprise-grade security with:

### PII Detection & Redaction

Automatically detects and redacts personally identifiable information:

| PII Type | Examples |
|----------|----------|
| Email | user@example.com |
| Phone | 123-456-7890, (123) 456-7890 |
| SSN | 123-45-6789 |
| Credit Card | 1234-5678-9012-3456 |
| Student ID | S123456, ID: ABC123 |
| Address | 123 Main Street, City, State |

### Content Safety

Prevents harmful, violent, or inappropriate content:

| Category | Description |
|----------|-------------|
| `pii` | Personally Identifiable Information |
| `harmful_content` | Potentially harmful or dangerous content |
| `violence` | Violence-related content |
| `hate_speech` | Hateful or discriminatory content |
| `adult_content` | Adult or explicit content |
| `illegal_content` | Illegal activities or content |
| `self_harm` | Self-harm related content |
| `spam` | Spam or promotional content |

### Guardrails API

```bash
# Check content for PII and safety
curl -X POST http://localhost:9090/v1/guardrail \
  -H "Content-Type: application/json" \
  -d '{"text": "Student john@example.com scored 85"}'

# Response
{
  "original_text": "Student john@example.com scored 85",
  "redacted_text": "Student [EMAIL_REDACTED] scored 85",
  "action": "redact",
  "risk_categories": ["pii"],
  "risk_score": 0.5,
  "detected_entities": {"email": ["john@example.com"]},
  "suggestions": ["Please remove or mask PII"],
  "timestamp": "2024-01-15T10:30:00"
}
```

### Risk Score Actions

| Score Range | Action | Description |
|-------------|--------|-------------|
| 0.0 - 0.49 | PASS | Content is safe |
| 0.5 - 0.79 | REDACT | Content needs redaction |
| 0.8 - 1.0 | BLOCK | Content is blocked |

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
├── services/
│   ├── api/                    # FastAPI backend service
│   ├── agent/                 # OPEA-based agent service
│   ├── embedding/              # Embedding service
│   └── guardrails/             # OPEA Guardrails service
├── web/                       # React frontend
├── scripts/                   # Database initialization
├── docker-compose.yml         # Docker Compose configuration
├── deploy.sh                  # One-click deployment script
└── README.md                  # This file
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
GUARDRAIL_SERVICE_URL=http://guardrails:9090

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

```bash
# Start in lite mode
./deploy.sh start lite

# Start API only
./deploy.sh start api-only
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
| Data Protection | 100% PII redaction |

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

### Guardrails

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/guardrail` | POST | Check content for PII/safety |
| `/v1/guardrail/input` | POST | Check user input |
| `/v1/guardrail/output` | POST | Check AI output |
| `/v1/guardrail/batch` | POST | Batch check |
| `/v1/categories` | GET | Get risk categories |

---

## 🧪 Testing

### Run Tests

```bash
# Run API tests
cd api
docker-compose run api pytest

# Run integration tests
docker-compose run api pytest tests/integration
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check LLM service
curl http://localhost:8001/v1/models

# Check embedding service
curl http://localhost:8002/health

# Check guardrails service
curl http://localhost:9090/health
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
