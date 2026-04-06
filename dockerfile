FROM python:3.12-slim

WORKDIR /app

# Copy source
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH để import src
ENV PYTHONPATH=/app

# Run app
CMD ["python", "-m", "src.tools.buildagent"]