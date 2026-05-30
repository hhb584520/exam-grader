# ExamGrader Guardrails Service

OPEA Guardrails Microservice for Data Protection and Content Safety

## Overview

This service implements OPEA (Open Platform for Enterprise AI) Guardrails to protect all data flowing through the ExamGrader system. It provides:

- **PII Detection & Redaction**: Automatically detects and redacts personally identifiable information
- **Content Safety**: Prevents harmful, violent, or inappropriate content
- **Input Validation**: Validates all user inputs before processing
- **Output Sanitization**: Ensures AI-generated content is safe before delivery

## Features

### Supported PII Types

| Type | Examples |
|------|----------|
| Email | user@example.com |
| Phone | 123-456-7890, (123) 456-7890 |
| SSN | 123-45-6789 |
| Credit Card | 1234-5678-9012-3456 |
| IP Address | 192.168.1.1 |
| Date of Birth | DOB: 01/15/1990 |
| Passport | Passport: AB1234567 |
| Driver License | DL: D1234567 |
| Student ID | Student ID: S123456 |
| Address | 123 Main Street |

### Supported Risk Categories

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

## API Endpoints

### Health Check

```
GET /health
```

### Check Content

```
POST /v1/guardrail
```

Request:
```json
{
  "text": "Text to check",
  "check_pii": true,
  "check_safety": true,
  "redact_pii": true,
  "return_redacted": true
}
```

Response:
```json
{
  "original_text": "Student john@example.com scored 85",
  "redacted_text": "Student [EMAIL_REDACTED] scored 85",
  "action": "redact",
  "risk_categories": ["pii"],
  "risk_score": 0.5,
  "detected_entities": {
    "email": ["john@example.com"]
  },
  "suggestions": ["Please remove or mask personally identifiable information"],
  "timestamp": "2024-01-15T10:30:00"
}
```

### Batch Check

```
POST /v1/guardrail/batch
```

### Check Input

```
POST /v1/guardrail/input
```

### Check Output

```
POST /v1/guardrail/output
```

### Get Risk Categories

```
GET /v1/categories
```

## Usage

### Docker Deployment

The guardrails service is automatically started with the main deployment:

```bash
./deploy.sh start
```

### Manual Start

```bash
cd services/guardrails
pip install -r requirements.txt
python guardrails_service.py
```

### Direct API Usage

```python
import httpx

async def check_content():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9090/v1/guardrail",
            json={
                "text": "Student john@example.com phone: 123-456-7890",
                "check_pii": True,
                "check_safety": True,
                "redact_pii": True,
                "return_redacted": True
            }
        )
        return response.json()
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  API Service │────▶│   LLM/      │
│             │◀────│  + Guardrail │◀────│   Agent     │
└─────────────┘     │   Middleware │     └─────────────┘
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Guardrails  │
                    │  Service     │
                    │  (Port 9090) │
                    └──────────────┘
```

## Middleware Integration

The API service uses guardrails middleware to automatically:

1. Check all incoming requests for PII and safety issues
2. Validate AI outputs before returning to users
3. Log security events for audit

## Risk Score

The risk score ranges from 0.0 to 1.0:

| Score Range | Action | Description |
|-------------|--------|-------------|
| 0.0 - 0.49 | PASS | Content is safe |
| 0.5 - 0.79 | REDACT | Content needs redaction |
| 0.8 - 1.0 | BLOCK | Content is blocked |

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GUARDRAIL_PORT` | 9090 | Service port |
| `GUARDRAILS_ENABLED` | true | Enable/disable guardrails |

## License

Apache License 2.0
