FROM python:3.8

#[ERROR] An error occurred during execution of command [app-deploy]
RUN pip install --upgrade pip

RUN mkdir /code
WORKDIR /code
COPY . /code/


RUN apt-get update && apt-get -y install cmake protobuf-compiler
RUN pip install -r requirements.txt
RUN apt-get install -y libgl1-mesa-dev

EXPOSE 8080
ENV PYTHONPATH="${PYTHONPATH}:/code/apps/pysot"

CMD python application.py