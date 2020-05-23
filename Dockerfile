FROM tiangolo/meinheld-gunicorn:python3.8-alpine3.11
COPY . /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
