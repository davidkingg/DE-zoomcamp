FROM python:3.10



WORKDIR /app

COPY pipeline.py pipeline.py
COPY postgres_data_loading.py postgres_data_loading.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

#ENTRYPOINT [ "bash" ]
ENTRYPOINT [ "python","postgres_data_loading.py" ]
