FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Disable SSL verification (only for dev/testing)
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
