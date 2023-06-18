FROM ubuntu:20.04

# Non-interactive mode to prevent user input requests
ARG DEBIAN_FRONTEND=noninteractive

# Switch to bash (instead of /bin/sh)
SHELL ["/bin/bash", "-c"]

# Install dependencies
RUN apt-get -y update --fix-missing
#RUN apt-get -y upgrade
RUN apt-get install -y build-essential git wget ffmpeg libsm6 libxext6 software-properties-common
RUN apt-get install -y cmake unzip pkg-config
RUN apt-get install -y libjpeg-dev libpng-dev libtiff-dev
RUN apt-get install -y libavcodec-dev libavformat-dev libswscale-dev
RUN apt-get install -y libv4l-dev libxvidcore-dev libx264-dev
RUN apt-get install -y libgtk-3-dev
RUN apt-get install -y libatlas-base-dev gfortran
RUN apt-get install -y python3-dev python3-pip
# testresources

# Get CUDA sources
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
RUN add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"

RUN apt-get -y update
RUN apt-get -y install cuda-11-4 libcudnn8 libcudnn8-dev
# nvidia-cuda-toolkit

# Get OpenCV sources
WORKDIR /home
RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/refs/tags/4.6.0.zip
RUN wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/refs/tags/4.6.0.zip
RUN unzip opencv.zip
RUN unzip opencv_contrib.zip
RUN mv opencv-4.6.0 opencv
RUN mv opencv_contrib-4.6.0 opencv_contrib

# Build OpenCV
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-11.4/lib64
ENV PATH=$PATH:/usr/local/cuda-11.4/bin
ENV CUDA_HOME=/usr/local/cuda-11.4

WORKDIR /home/opencv
RUN mkdir build
WORKDIR /home/opencv/build
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D INSTALL_C_EXAMPLES=OFF \
	-D OPENCV_ENABLE_NONFREE=ON \
	-D WITH_CUDA=ON \
	-D WITH_CUDNN=ON \
	-D OPENCV_DNN_CUDA=ON \
	-D ENABLE_FAST_MATH=1 \
	-D CUDA_FAST_MATH=1 \
    # Get your architecture version (i.e., Compute Capability) from https://developer.nvidia.com/cuda-gpus for your model (via nvidia-smi)
	-D CUDA_ARCH_BIN=8.6 \      
	-D WITH_CUBLAS=1 \
	-D OPENCV_EXTRA_MODULES_PATH=/home/opencv_contrib/modules \
	#-D PYTHON_EXECUTABLE=~/.virtualenvs/opencv_cuda/bin/python \
	-D HAVE_opencv_python3=ON \
	-D BUILD_EXAMPLES=ON \
    ..
RUN make -j
RUN make install
RUN ldconfig

# Use virtual environment
#RUN virtualenv --python=/usr/bin/python3.7 /opt/tf_venv
#ENV VIRTUAL_ENV=/opt/tf_venv
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python requirements
WORKDIR /home
ADD ./python_requirements.txt .
RUN pip3 install --no-cache-dir -r python_requirements.txt
RUN pip3 install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113

# Copy custom files
WORKDIR /home/
ADD . .

# Prepare neural network for object detection
WORKDIR /home/traffic-sign-detector-yolov4-main

# Launch application
CMD ["python3","yolov4.py"]
