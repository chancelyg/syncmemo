FROM python:3.8.6-buster

WORKDIR /app

COPY ./flaskr /app/flaskr
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip -i https://pypi.doubanio.com/simple && \
pip install -i https://pypi.doubanio.com/simple -r /app/requirements.txt

ENV CONFIG=/app/config.yaml

CMD ["gunicorn", "--workers=1", "--bind=0.0.0.0:80", "flaskr:app"]