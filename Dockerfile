FROM python:3.8.6-buster

WORKDIR /app

COPY ./ /app

COPY conf/app.conf.example /app/syncmemo.conf

RUN pip install --upgrade pip && \
pip install -r /app/requirements.txt

ENV MEMO_CONF=/app/syncmemo.conf

CMD ["gunicorn", "--workers=1", "--bind=0.0.0.0:80", "flaskr:create_app()"]