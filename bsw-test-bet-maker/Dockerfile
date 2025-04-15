FROM python:3.10

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    libyaml-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel cython

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#ENV PYTHONPATH=/app
#ENV APP_ENV=production

COPY .. .

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]