FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install uv && uv pip install --system --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

# The command to run when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]