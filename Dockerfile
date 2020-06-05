FROM tiangolo/meinheld-gunicorn:latest
COPY . /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
