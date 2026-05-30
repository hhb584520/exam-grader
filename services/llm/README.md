# LLM Service with Intel AMX Optimization

This service provides LLM inference using vLLM with Intel hardware optimizations.

## Intel Hardware Support

| Feature | CPU Requirement | Description |
|---------|---------------|-------------|
| AVX-512 | Intel Skylake-X (2017)+ | 512-bit vector operations |
| AVX-512 BF16 | Intel Cascade Lake (2019)+ | BF16 data type support |
| AMX | Intel Sapphire Rapids (2023)+ | 6-14x faster matrix operations |

## AMX Configuration

### Environment Variables

```env
# Device Configuration
VLLM_TARGET_DEVICE=cpu              # Use CPU backend
VLLM_CPU_AVX512BF16=1               # Enable AVX-512 BF16 (required for AMX)
VLLM_CPU_KVCACHE_SPACE=40           # KV cache size in GB

# Thread Configuration
VLLM_CPU_OMP_THREADS_BIND=0-31     # Bind to CPU cores 0-31
OMP_NUM_THREADS=32                  # OpenMP threads
MKL_NUM_THREADS=32                  # Intel MKL threads

# Intel Extension for PyTorch (IPEX)
USE_IPEX=1                          # Enable IPEX
BF16_MODE=1                         # Use BF16 computation
```

## Building

```bash
cd services/llm
docker build -t exam-grader-llm .
```

## Running

```bash
# Via docker-compose
docker-compose up -d llm

# Direct
docker run -p 8001:8000 \
  --env-file services/llm/.env \
  exam-grader-llm
```

## Health Check

```bash
curl http://localhost:8001/health

# Response includes optimization info
{
  "status": "healthy",
  "model": "Qwen/Qwen2-7B-Instruct",
  "device": "cpu",
  "amx_enabled": true,
  "optimizations": ["AMX-BF16", "AVX-512", "oneDNN"]
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with optimization info |
| `/v1/models` | GET | List available models |
| `/v1/completions` | POST | Text completion |
| `/v1/chat/completions` | POST | Chat completion |

## Performance Notes

- **AMX-BF16**: Requires Intel Sapphire Rapids or newer CPU
- **AVX-512 BF16**: Requires Intel Cascade Lake or newer CPU
- Without AMX support, falls back to AVX-512 optimizations
- BF16 provides 2x speedup vs FP32 with minimal accuracy loss
