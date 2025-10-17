FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install uv && uv pip install --system --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

# Copy and make startup scripts executable
COPY scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.sh
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# The command to run when the container starts
CMD ["/app/entrypoint.sh"]