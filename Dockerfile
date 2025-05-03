# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# ✅ Instala git para permitir instalação via repositório remoto
RUN apt-get update && apt-get install -y git

# Copia os arquivos da aplicação
COPY . .

# Instala as dependências com suporte ao tvdatafeed via GitHub
RUN pip install --no-cache-dir -r requirements.txt

# Evita buffering de logs no container
ENV PYTHONUNBUFFERED=1

# Comando para rodar o FastAPI com Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
