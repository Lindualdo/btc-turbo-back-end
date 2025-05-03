# Dockerfile

FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia todos os arquivos do projeto para dentro da imagem
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Define a variável de ambiente para evitar warnings
ENV PYTHONUNBUFFERED=1

# Comando para rodar o app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

ARG CACHEBUST=1
