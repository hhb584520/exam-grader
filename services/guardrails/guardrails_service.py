#!/usr/bin/env python3

"""
OPEA Guardrails Microservice for ExamGrader

This microservice provides data protection and content safety for all inputs and outputs.
It implements:
- PII (Personally Identifiable Information) detection and redaction
- Content safety checks (harmful content, violence, etc.)
- Input validation for all user data
- Output sanitization before returning results

Based on OPEA Guardrails Framework:
https://opea-project.github.io/1.3/GenAIComps/comps/guardrails/src/guardrails/README.html
"""

import os
import re
import json
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ExamGrader Guardrails",
    description="OPEA Guardrails Microservice for Data Protection and Content Safety",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GuardrailAction(str, Enum):
    PASS = "pass"
    BLOCK = "block"
    REDACT = "redact"
    FLAG = "flag"

class RiskCategory(str, Enum):
    PII = "pii"
    HARMFUL_CONTENT = "harmful_content"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    ADULT_CONTENT = "adult_content"
    ILLEGAL_CONTENT = "illegal_content"
    SELF_HARM = "self_harm"
    SPAM = "spam"

class GuardrailRequest(BaseModel):
    text: str = Field(..., description="Text content to check")
    check_pii: bool = Field(default=True, description="Enable PII detection")
    check_safety: bool = Field(default=True, description="Enable content safety check")
    redact_pii: bool = Field(default=True, description="Automatically redact PII")
    return_redacted: bool = Field(default=True, description="Return redacted text")

class GuardrailResponse(BaseModel):
    original_text: str = Field(..., description="Original input text")
    redacted_text: Optional[str] = Field(None, description="Redacted text if applicable")
    action: GuardrailAction = Field(..., description="Action taken by guardrail")
    risk_categories: List[RiskCategory] = Field(default_factory=list, description="Detected risk categories")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score 0-1")
    detected_entities: Optional[Dict[str, List[str]]] = Field(None, description="Detected PII entities")
    suggestions: List[str] = Field(default_factory=list, description="Safety suggestions")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class BatchGuardrailRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to check")
    check_pii: bool = Field(default=True)
    check_safety: bool = Field(default=True)
    redact_pii: bool = Field(default=True)

class BatchGuardrailResponse(BaseModel):
    results: List[GuardrailResponse]
    total_checked: int
    risky_count: int
    safe_count: int

class DataHashRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Data to hash for integrity checking")

class DataHashResponse(BaseModel):
    hash: str = Field(..., description="SHA-256 hash of the data")
    timestamp: str

PII_PATTERNS = {
    "email": [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b'
    ],
    "phone": [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
        r'\b\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        r'\b\d{10,11}\b'
    ],
    "ssn": [
        r'\b\d{3}-\d{2}-\d{4}\b',
        r'\b\d{9}\b',
        r'\bSSN[:\s]*\d{3}-\d{2}-\d{4}\b'
    ],
    "credit_card": [
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        r'\b\d{15,16}\b'
    ],
    "ip_address": [
        r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    ],
    "date_of_birth": [
        r'\b(DOB|Date of Birth|Birthday)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'
    ],
    "passport": [
        r'\b(Passport|Passport Number)[:\s]*([A-Z]{1,2}\d{6,9})\b',
        r'\b[A-Z]{1,2}\d{6,9}\b'
    ],
    "driver_license": [
        r'\b(Driver License|DL)[:\s]*(\w{5,20})\b'
    ],
    "student_id": [
        r'\b(Student ID|Student Number|SID)[:\s]*([A-Z0-9]{6,12})\b',
        r'\bID[:\s]*([A-Z0-9]{6,12})\b'
    ],
    "address": [
        r'\b\d{1,5}\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Place|Pl)\.?\b',
        r'\b\d{1,5}\s+[\w\s]+,\s*[\w\s]+,\s*[A-Z]{2}\s*\d{5}\b'
    ]
}

HARMFUL_KEYWORDS = {
    RiskCategory.HARMFUL_CONTENT: [
        "bomb", "explosive", "kill", "murder", "attack", "harm", "destroy",
        "weapon", "gun", "knife", "blade"
    ],
    RiskCategory.VIOLENCE: [
        "violence", "violent", "abuse", "torture", "assault", "fight",
        "blood", "injure", "wound", "victim"
    ],
    RiskCategory.HATE_SPEECH: [
        "hate", "racist", "sexist", "discriminate", "slur", "bigot",
        "nazi", "supremacist"
    ],
    RiskCategory.ADULT_CONTENT: [
        "porn", "xxx", "nude", "naked", "sexual", "erotic"
    ],
    RiskCategory.SELF_HARM: [
        "suicide", "self-harm", "cut myself", "kill myself", "end my life",
        "overdose", "hang myself"
    ],
    RiskCategory.ILLEGAL_CONTENT: [
        "drug", "marijuana", "cocaine", "heroin", "meth", "illegal weapon",
        "fraud", "scam", "phishing", "hack"
    ]
}

class GuardrailEngine:
    """Core guardrail engine for content analysis and PII detection"""

    def __init__(self):
        self.pii_patterns = PII_PATTERNS
        self.harmful_keywords = HARMFUL_KEYWORDS

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect PII entities in text"""
        detected = {}

        for pii_type, patterns in self.pii_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
            if matches:
                detected[pii_type] = list(set(matches))

        return detected

    def redact_pii(self, text: str, detected: Dict[str, List[str]]) -> str:
        """Redact PII entities in text"""
        redacted = text

        for pii_type, values in detected.items():
            for value in values:
                if isinstance(value, tuple):
                    value = value[0] if len(value) > 0 else str(value)
                placeholder = f"[{pii_type.upper()}_REDACTED]"
                redacted = redacted.replace(str(value), placeholder)

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        redacted = re.sub(email_pattern, '[EMAIL_REDACTED]', redacted)

        return redacted

    def check_content_safety(self, text: str) -> tuple[List[RiskCategory], float]:
        """Check content for safety issues"""
        detected_risks = []
        text_lower = text.lower()
        risk_score = 0.0

        for category, keywords in self.harmful_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                detected_risks.append(category)
                risk_score += min(matches * 0.2, 0.4)

        spam_patterns = [
            r'(click here|act now|limited time|offer expires)',
            r'(free money|make \$\d+|earn \$\d+)',
            r'(congratulations you won|you have won)',
            r'(urgent action required|immediate response)'
        ]

        for pattern in spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_risks.append(RiskCategory.SPAM)
                risk_score += 0.3
                break

        risk_score = min(risk_score, 1.0)
        return detected_risks, risk_score

    def analyze(self, text: str, check_pii: bool = True, check_safety: bool = True,
                redact_pii: bool = True) -> GuardrailResponse:
        """Perform complete guardrail analysis"""

        detected_entities = {}
        risk_categories = []
        risk_score = 0.0
        redacted_text = text

        if check_pii:
            detected_entities = self.detect_pii(text)
            if detected_entities:
                risk_categories.append(RiskCategory.PII)
                risk_score += 0.5
                if redact_pii:
                    redacted_text = self.redact_pii(text, detected_entities)

        if check_safety:
            safety_risks, safety_score = self.check_content_safety(text)
            risk_categories.extend(safety_risks)
            risk_score += safety_score

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.8:
            action = GuardrailAction.BLOCK
        elif risk_score >= 0.5:
            action = GuardrailAction.FLAG
        elif risk_categories or detected_entities:
            action = GuardrailAction.REDACT
        else:
            action = GuardrailAction.PASS

        suggestions = self._generate_suggestions(risk_categories)

        return GuardrailResponse(
            original_text=text,
            redacted_text=redacted_text if redact_pii else None,
            action=action,
            risk_categories=risk_categories,
            risk_score=risk_score,
            detected_entities=detected_entities if detected_entities else None,
            suggestions=suggestions
        )

    def _generate_suggestions(self, risk_categories: List[RiskCategory]) -> List[str]:
        """Generate safety suggestions based on detected risks"""
        suggestions = []

        if RiskCategory.PII in risk_categories:
            suggestions.append("Please remove or mask personally identifiable information before submitting.")

        if RiskCategory.HARMFUL_CONTENT in risk_categories:
            suggestions.append("Content contains potentially harmful material. Please revise.")

        if RiskCategory.VIOLENCE in risk_categories:
            suggestions.append("Violence-related content detected. Please ensure appropriate language.")

        if RiskCategory.HATE_SPEECH in risk_categories:
            suggestions.append("Hateful content is not allowed. Please use respectful language.")

        if RiskCategory.SELF_HARM in risk_categories:
            suggestions.append("If you're experiencing thoughts of self-harm, please seek help from a trusted adult or crisis line.")

        if RiskCategory.ILLEGAL_CONTENT in risk_categories:
            suggestions.append("Illegal content is not permitted. Please comply with all applicable laws.")

        return suggestions

guardrail_engine = GuardrailEngine()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "guardrails",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/v1/guardrail", response_model=GuardrailResponse)
async def check_guardrail(request: GuardrailRequest):
    """
    Check text content for PII and safety issues.

    This endpoint performs:
    - PII detection and redaction
    - Content safety analysis
    - Risk scoring
    - Action recommendation
    """
    try:
        result = guardrail_engine.analyze(
            text=request.text,
            check_pii=request.check_pii,
            check_safety=request.check_safety,
            redact_pii=request.redact_pii
        )
        return result
    except Exception as e:
        logger.error(f"Guardrail check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Guardrail analysis failed: {str(e)}")

@app.post("/v1/guardrail/batch", response_model=BatchGuardrailResponse)
async def batch_guardrail_check(request: BatchGuardrailRequest):
    """Check multiple texts in a single request"""
    try:
        results = []
        risky_count = 0
        safe_count = 0

        for text in request.texts:
            result = guardrail_engine.analyze(
                text=text,
                check_pii=request.check_pii,
                check_safety=request.check_safety,
                redact_pii=request.redact_pii
            )
            results.append(result)
            if result.action in [GuardrailAction.BLOCK, GuardrailAction.FLAG]:
                risky_count += 1
            else:
                safe_count += 1

        return BatchGuardrailResponse(
            results=results,
            total_checked=len(results),
            risky_count=risky_count,
            safe_count=safe_count
        )
    except Exception as e:
        logger.error(f"Batch guardrail check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.post("/v1/guardrail/input", response_model=GuardrailResponse)
async def check_input_guardrail(request: GuardrailRequest):
    """
    Check input content (user submitted data).

    This is the primary endpoint for validating user inputs before
    they are processed by the system.
    """
    return await check_guardrail(request)

@app.post("/v1/guardrail/output", response_model=GuardrailResponse)
async def check_output_guardrail(request: GuardrailRequest):
    """
    Check output content (AI generated responses).

    This endpoint validates AI-generated content before it is
    returned to the user.
    """
    request.check_safety = True
    return await check_guardrail(request)

@app.post("/v1/hash", response_model=DataHashResponse)
async def generate_data_hash(request: DataHashRequest):
    """
    Generate SHA-256 hash of data for integrity verification.

    This can be used to verify that data has not been tampered with.
    """
    try:
        data_str = json.dumps(request.data, sort_keys=True)
        hash_value = hashlib.sha256(data_str.encode()).hexdigest()
        return DataHashResponse(
            hash=hash_value,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Hash generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hash generation failed: {str(e)}")

@app.get("/v1/categories")
async def get_risk_categories():
    """Get list of supported risk categories"""
    return {
        "categories": [cat.value for cat in RiskCategory],
        "descriptions": {
            "pii": "Personally Identifiable Information (emails, phones, SSN, etc.)",
            "harmful_content": "Potentially harmful or dangerous content",
            "violence": "Violence-related content",
            "hate_speech": "Hateful or discriminatory content",
            "adult_content": "Adult or explicit content",
            "illegal_content": "Illegal activities or content",
            "self_harm": "Self-harm related content",
            "spam": "Spam or promotional content"
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ExamGrader Guardrails",
        "description": "OPEA Guardrails Microservice for Data Protection",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "check": "POST /v1/guardrail",
            "batch_check": "POST /v1/guardrail/batch",
            "input_check": "POST /v1/guardrail/input",
            "output_check": "POST /v1/guardrail/output",
            "hash": "POST /v1/hash",
            "categories": "GET /v1/categories"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("GUARDRAIL_PORT", "9090"))
    uvicorn.run(app, host="0.0.0.0", port=port)
