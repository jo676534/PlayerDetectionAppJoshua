FROM python:3.8

RUN pip install --upgrade pip

# Create working directory and copy all the files to it
WORKDIR /var/app
COPY . /var/app

# Install all libraries required for the application
RUN apt-get update && apt-get -y install cmake protobuf-compiler
RUN pip install -r requirements.txt
RUN apt-get install -y libgl1-mesa-dev

# Exposes port from application.py
EXPOSE 8080
# Creates environment path for pysot
ENV PYTHONPATH="${PYTHONPATH}:/var/app/apps/pysot"

CMD python application.py
