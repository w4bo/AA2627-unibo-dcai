FROM w4bo/python:1.0.7

WORKDIR /lab

COPY requirements.txt .
RUN pip install --no-cache-dir --ignore-requires-python -r requirements.txt

COPY mlzero_chat.py ollama_chat.yaml prepare_data.py ./
RUN python prepare_data.py               # bakes data/adult.csv into the image

# Ollama service from docker-compose.yml; override with -e OLLAMA_URL=... or --ollama-url
ENV OLLAMA_URL=http://ollama:11434

CMD ["python", "mlzero_chat.py", "-i", "data/adult.csv"]
