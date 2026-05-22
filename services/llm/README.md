# LLM Service

This service provides LLM inference using vLLM.

## Running

Use OPEA's `comps/llms/text-generation/vllm/langchain` to start the vLLM docker container.

### Example command:

```bash
docker run -p 8008:80 -v "/path/to/model":/data --name vllm-service --shm-size 128g opea/vllm:latest --model /data --host 0.0.0.0 --port 80
```

## Endpoint

- Default: `http://localhost:8008/v1`

## Environment Variables

- `LLM_ENDPOINT`: LLM service endpoint
- `LLM_MODEL`: Model name
