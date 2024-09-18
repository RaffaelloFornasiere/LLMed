FROM python:3.10

RUN mkdir -p /workspace/
WORKDIR /workspace/
COPY requirements.txt /workspace/
RUN apt-get update
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN yes | apt-get install apt-utils build-essential libpoppler-cpp-dev pkg-config
RUN yes | apt-get install cmake git
RUN pip install --upgrade -r requirements.txt
ENTRYPOINT ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5003", "--reload"]
