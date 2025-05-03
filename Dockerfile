# Dockerfile

FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências de sistema (inclui git)
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos para dentro do container
COPY . .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Evita buffering em logs
ENV PYTHONUNBUFFERED=1

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
