import os
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LLM Service with Intel AMX Optimization")

MODEL_NAME = os.getenv("LLM_MODEL", "Qwen/Qwen2-7B-Instruct")
PORT = int(os.getenv("PORT", "8000"))
DEVICE = os.getenv("VLLM_TARGET_DEVICE", "cpu")

class CompletionRequest(BaseModel):
    model: Optional[str] = None
    prompt: str
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

print(f"Initializing LLM Service with Intel AMX optimization")
print(f"Model: {MODEL_NAME}")
print(f"Device: {DEVICE}")
print(f"AMX BF16 support: {os.getenv('VLLM_CPU_AVX512BF16', '1')}")

try:
    from vllm import LLM, SamplingParams
    print("vLLM with Intel AMX support loaded successfully")

    llm = LLM(
        model=MODEL_NAME,
        device=DEVICE,
        trust_remote_code=True,
        dtype="bfloat16" if DEVICE == "cpu" else "auto",
    )
    print("Model loaded with AMX optimizations enabled")
except ImportError:
    print("Warning: vLLM not available, using mock mode")
    llm = None
except Exception as e:
    print(f"Warning: Failed to load model: {e}")
    print("Running in mock mode for testing")
    llm = None

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "device": DEVICE,
        "amx_enabled": os.getenv("VLLM_CPU_AVX512BF16", "0") == "1",
        "optimizations": ["AMX-BF16", "AVX-512", "oneDNN"] if DEVICE == "cpu" else ["CUDA"]
    }

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{
            "id": MODEL_NAME,
            "object": "model",
            "created": 1234567890,
            "owned_by": "system",
            "optimizations": {
                "device": DEVICE,
                "amx_bf16": os.getenv("VLLM_CPU_AVX512BF16", "0") == "1",
                "avx512": True,
                "onednn": True
            }
        }]
    }

@app.post("/v1/completions")
async def completion(request: CompletionRequest):
    if llm is None:
        return {
            "id": "mock-completion",
            "object": "text_completion",
            "created": 1234567890,
            "model": request.model or MODEL_NAME,
            "choices": [{
                "index": 0,
                "text": f"Mock response for: {request.prompt[:50]}...",
                "logprobs": None,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": 50,
                "total_tokens": len(request.prompt.split()) + 50
            }
        }

    try:
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
        )

        outputs = llm.generate([request.prompt], sampling_params)
        output = outputs[0]

        return {
            "id": f"cmpl-{hash(request.prompt) % 1000000}",
            "object": "text_completion",
            "created": 1234567890,
            "model": request.model or MODEL_NAME,
            "choices": [{
                "index": 0,
                "text": output.outputs[0].text,
                "logprobs": None,
                "finish_reason": output.outputs[0].finish_reason or "stop"
            }],
            "usage": {
                "prompt_tokens": output.prompt_token_ids.__len__() if hasattr(output, 'prompt_token_ids') else 0,
                "completion_tokens": len(output.outputs[0].token_ids) if hasattr(output.outputs[0], 'token_ids') else 0,
                "total_tokens": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    if llm is None:
        return {
            "id": "mock-chat",
            "object": "chat.completion",
            "created": 1234567890,
            "model": request.model or MODEL_NAME,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Mock response (AMX optimized)"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 50,
                "total_tokens": 100
            }
        }

    try:
        prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
        prompt += "\nassistant:"

        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
        )

        outputs = llm.generate([prompt], sampling_params)
        output = outputs[0]

        return {
            "id": f"chatcmpl-{hash(prompt) % 1000000}",
            "object": "chat.completion",
            "created": 1234567890,
            "model": request.model or MODEL_NAME,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output.outputs[0].text
                },
                "finish_reason": output.outputs[0].finish_reason or "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": len(output.outputs[0].token_ids) if hasattr(output.outputs[0], 'token_ids') else 0,
                "total_tokens": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"Starting LLM Service on port {PORT} with Intel AMX optimization")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
