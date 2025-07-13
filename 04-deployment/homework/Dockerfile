FROM python:3.10.13-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy model file(s) into the image
COPY model.bin ./

COPY batch.py ./

ENTRYPOINT [ "python", "batch.py" ]