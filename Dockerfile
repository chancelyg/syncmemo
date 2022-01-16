# Compile python3.9.1
FROM ubuntu:18.04 AS compile-python  
WORKDIR /app
RUN apt-get update && \
apt-get install -y git libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev zlib1g-dev make gcc

ADD https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz ./
RUN tar -zxvf Python-3.9.1.tgz && \
./Python-3.9.1/configure --prefix=/usr/local/python3.9.1 && \
make && make install && \
git clone https://github.com/chancelyg/syncmemo.git && \
/usr/local/python3.9.1/bin/pip3 install -r syncmemo/requirements.txt -i https://pypi.doubanio.com/simple

FROM ubuntu:18.04
WORKDIR /app/
COPY --from=compile-python /root /root
COPY --from=compile-python /usr/local/python3.9.1 /usr/local/python3.9.1
COPY --from=compile-python /app/syncmemo /app/syncmemo
COPY app.conf /app/syncmemo/conf/app.conf
EXPOSE 7900
CMD ["/usr/local/python3.9.1/bin/python3","/app/syncmemo/src/main.py","--config=/app/syncmemo/conf/app.conf"]