FROM nvidia/cuda:12.2.2-devel-ubuntu22.04

# Set non-interactive installation mode and configure timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Environment variables for Llama library and other purposes
ENV LLAMA_CUBLAS=1
ENV CMAKE_ARGS=-DLLAMA_CUBLAS=on
ENV FORCE_CMAKE=1

# Set working directory
WORKDIR /workspace

# Install Python and various dependencies needed for both environments
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    libblas-dev \
    liblapack-dev \
    gfortran \
    git \
    ffmpeg \
    tesseract-ocr && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --upgrade pip wheel setuptools

# Install file_processing with options based on build args
ARG DEV=false
ARG FULL=false
COPY dist/file_processing-0.0.0-py3-none-any.whl .
RUN if [ "${DEV}" = "true" ] && [ "${FULL}" = "true" ]; then \
        pip install file_processing-0.0.0-py3-none-any.whl[developer,full] --no-cache-dir; \
    elif [ "${DEV}" = "true" ]; then \
        pip install file_processing-0.0.0-py3-none-any.whl[developer] --no-cache-dir; \
    elif [ "${FULL}" = "true" ]; then \
        pip install file_processing-0.0.0-py3-none-any.whl[full] --no-cache-dir; \
    else \
        pip install file_processing-0.0.0-py3-none-any.whl --no-cache-dir; \
    fi

# Install requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir

# Special installation for llama-cpp-python with GPU support
RUN pip install llama-cpp-python==0.2.55 --no-cache-dir --force-reinstall --verbose

# Clean up to reduce the image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache/pip

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
