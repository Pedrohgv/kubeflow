FROM python:slim-buster

COPY ./src /src

RUN pip install requests

CMD python ./src/download_zip_file.py