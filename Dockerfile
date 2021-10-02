FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
COPY . .
RUN [ "python", "-m", "unittest", "-v" ]
CMD [ "waitress-serve", "app:app" ]