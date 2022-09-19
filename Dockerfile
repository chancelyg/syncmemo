FROM python:3.8-slim-buster
WORKDIR /app
COPY ./ /app/syncmemo
COPY conf/app.conf.example /app/syncmemo.conf
RUN  pip3 install -r /app/syncmemo/requirements.txt
ENV FLASK_APP=/app/syncmemo/src/flaskr 
ENV MEMO_CONF=/app/syncmemo.conf

CMD ["flask","run","--host=0.0.0.0","--port=7900"]
