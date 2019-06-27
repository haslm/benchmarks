FROM ubuntu:16.04

RUN apt-get update

# Install python3 
RUN apt-get install -y python3 

# Install pip
RUN python3 /get-pip.py
RUN pip install --upgrade pip

#Install requirements
RUN pip install opencv-python

RUN mkdir /project
COPY ./* /project/

WORKDIR /project

CMD ["/bin/bash"]