FROM python:3.10.4-alpine

FROM prantlf/alpine-make-gcc:latest as builder

COPY --from=builder /root/sources/binary /usr/bin/

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "run.py" ]
