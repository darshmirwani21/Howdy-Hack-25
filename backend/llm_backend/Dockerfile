FROM python:3.14.0-slim-bookworm

EXPOSE 443
WORKDIR /app
COPY . .
RUN apt-get update
RUN apt-get install -y gcc
RUN pip install -r requirements.txt

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "443"]