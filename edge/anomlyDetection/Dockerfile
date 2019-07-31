FROM ubuntu:16.04

RUN apt-get update

# Install python3 
RUN apt-get install -y python3 

# Install pip
COPY docker_utils/* /
RUN python3 /get-pip.py
# RUN pip install --upgrade pip

#Install requirements
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple  -r /requirements.txt

RUN mkdir /project
COPY ./* /project/

WORKDIR /project

CMD ["/bin/bash"]

