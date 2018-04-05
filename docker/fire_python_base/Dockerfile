FROM python:3.5

WORKDIR /usr/src/fire

RUN apt update \
    && apt install -y cmake

ENV TZ=GST-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
