FROM ubuntu:16.04

RUN apt-get update

# Install python3 
RUN apt-get update
RUN apt-get install --fix-missing  -y python3 libglib2.0-dev libsm6 libxrender1 libxext-dev

# Install pip
COPY docker_utils/* /
RUN python3 /get-pip.py
# RUN pip install --upgrade pip

#Install requirements
RUN pip install opencv-python

RUN mkdir /project
COPY . /project
WORKDIR /project

CMD ["/bin/bash"]
# CMD [""]
# CMD ["python3 main.py"]