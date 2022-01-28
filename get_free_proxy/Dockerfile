FROM python:3.9


RUN apt-get -y update

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt ./

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "./proxy.py"]

ENTRYPOINT ["python", "proxy.py"]