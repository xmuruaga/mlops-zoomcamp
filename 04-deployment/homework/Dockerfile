FROM python:3.12-slim

# Update OS packages and apply security patches
RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy model file(s) into the image
COPY model.bin ./

COPY batch.py ./

ENTRYPOINT [ "python", "batch.py" ]