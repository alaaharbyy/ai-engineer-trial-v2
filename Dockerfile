FROM python:latest

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV OPENAI_API_KEY=sk-replace-me
ENV INDEX_DIR=/var/lib/app/index

EXPOSE 8000

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
