FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
COPY . .
RUN [ "python", "-m", "unittest", "-v" ]
HEALTHCHECK CMD curl --fail http://localhost:8080/ || exit 1
CMD [ "python", "./app.py" ]
