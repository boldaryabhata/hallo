FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

WORKDIR /app

RUN apt update \
    && apt -y install python3.10 python3-pip python3.10-venv libglu1-mesa-dev libglib2.0-0 git netcat curl wget vim unzip cmake build-essential ffmpeg \
    && ln -s /usr/bin/python3 /usr/local/bin/python \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log} \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# RUN git clone https://github.com/boldaryabhata/hallo.git

WORKDIR /app/hallo

COPY configs                  ./configs
COPY hallo                    ./hallo
COPY scripts                  ./scripts
COPY .pre-commit-config.yaml  .
COPY accelerate_config.yaml   .
COPY requirements.txt         .
COPY setup.py                 .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install .

RUN pip install --no-cache-dir gunicorn

WORKDIR /app/hallo/scripts

ENTRYPOINT ["python", "httpserver.py"]

# ENTRYPOINT ["gunicorn"]
# CMD ["--workers", "3", "--bind", "0.0.0.0:19000", "httpserver:app"]