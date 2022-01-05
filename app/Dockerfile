FROM python:3-alpine

EXPOSE 8848
WORKDIR /app

COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "./promTinkoff.sh"]
