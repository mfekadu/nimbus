FROM python:3.6

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# initialize models
RUN python -c "from model_utils import get_tfhub_sent_encoder; get_tfhub_sent_encoder()"

CMD [ "python", "app.py" ]
