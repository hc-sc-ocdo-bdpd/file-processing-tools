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
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    libblas-dev \
    liblapack-dev \
    gfortran \
    git \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Update pip and install wheel, setuptools
RUN python3 -m pip install --upgrade pip wheel setuptools

COPY dist/file_processing-0.0.0-py3-none-any.whl .

# Install file_processing with options based on build args
ARG DEV=false
ARG FULL=false
RUN if [ "${DEV}" = "true" ] && [ "${FULL}" = "true" ]; then \
        pip install file_processing-0.0.0-py3-none-any.whl[developer,full]; \
    elif [ "${DEV}" = "true" ]; then \
        pip install file_processing-0.0.0-py3-none-any.whl[developer]; \
    elif [ "${FULL}" = "true" ]; then \
        pip install file_processing-0.0.0-py3-none-any.whl[full]; \
    else \
        pip install file_processing-0.0.0-py3-none-any.whl; \
    fi

# Install requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Special installation for llama-cpp-python with GPU support
RUN pip install llama-cpp-python==0.2.55 --no-cache-dir --force-reinstall --verbose

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
