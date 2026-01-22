# 1. Base image
FROM python:3.11-slim

# 2. Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set work directory
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

# 5. Copy requirements first (for caching)
COPY requirements.txt /app/

# 6. Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 7. Copy project files
COPY . /app/

# 8. Expose Django port
EXPOSE 8000

# 9. Run server
CMD ["gunicorn", "jiomart_clone.wsgi:application", "--bind", "0.0.0.0:8000"]
