FROM python:3.12-slim

# Update OS packages and apply security patches
RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY predict.py ./

ENV MLFLOW_TRACKING_URI=http://host.docker.internal:5000

EXPOSE 9696

ENTRYPOINT [ "uvicorn", "predict:app", "--host=0.0.0.0", "--port=9696" ]