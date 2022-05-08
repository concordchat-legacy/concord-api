FROM python:3.10.4-alpine

# Used because of cchardet requiring GCC to work.
RUN apk add --no-cache build-base libffi-dev

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "run.py" ]
