FROM python:3.10

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY .. .

#ENV PYTHONPATH=/app
#ENV APP_ENV=production

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]