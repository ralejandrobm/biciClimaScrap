FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*


ENV DISPLAY=:99

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN touch /var/log/cron.log
COPY . .

