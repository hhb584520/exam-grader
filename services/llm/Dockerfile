FROM intel/intel-optimization-notebook:py3.11-torch2.4.0-ipex-2.4.0

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV VLLM_TARGET_DEVICE=cpu
ENV VLLM_CPU_KVCACHE_SPACE=40
ENV VLLM_CPU_AVX512BF16=1

WORKDIR /app

RUN pip install --no-cache-dir \
    vllm==0.6.6 \
    fastapi==0.115.0 \
    uvicorn==0.30.6 \
    transformers==4.44.0 \
    accelerate==0.34.0 \
    pydantic==2.9.0

COPY llm_service.py /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["python", "/app/llm_service.py"]
