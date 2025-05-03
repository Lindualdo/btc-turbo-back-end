FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ARG CACHEBUST=1

RUN apt-get update && apt-get install -y build-essential git curl && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir git+https://github.com/rongardF/tvdatafeed.git

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY . .

# cache bust


