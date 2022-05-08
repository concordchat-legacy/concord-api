FROM python:3.10.4-alpine

# Used because of cchardet requiring GCC to work.
FROM frolvlad/alpine-gcc:latest as gcc

COPY --from=gcc /root/sources/binary /usr/bin/

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "run.py" ]
