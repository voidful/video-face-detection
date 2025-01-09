FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu20.04

LABEL authors="voidful"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y \
        ffmpeg \
        git \
        cmake \
        libsm6 \
        libxext6 \
        libxrender-dev \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-numpy \
        gcc \
        g++ \
        build-essential \
        gfortran \
        wget \
        curl \
        libprotobuf-dev \
        protobuf-compiler && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install face_recognition \
    scipy \
    opencv-python \
    numpy \
    tqdm \
    soundfile \
    silero-vad \
    moviepy \
    onnxruntime \
    spleeter \
    pycld3

WORKDIR /app

CMD ["bash"]
