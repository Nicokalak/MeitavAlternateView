FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
COPY . .
RUN [ "python", "-m", "unittest", "-v" ]
RUN useradd -g users appuser
USER appuser

HEALTHCHECK CMD python ./healthcheck.py || exit 1
CMD [ "python", "./app.py" ]
