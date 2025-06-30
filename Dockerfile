# Use the official Ubuntu 20.04 as a parent image
FROM ubuntu:20.04

# Set environment variables to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages including curl
RUN apt-get update && apt-get install -y \
    git \
    octave \
    python3.8 \
    python3.8-venv \
    python3-pip \
    imagemagick \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda using curl
RUN curl -sSL -k https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

# Add Miniconda to PATH
ENV PATH="/opt/conda/bin:${PATH}"

# Configure Conda
RUN conda config --set ssl_verify False && \
    conda update -y conda && \
    conda clean --all

# Create a new Conda environment and install dependencies
RUN conda create -y --name myenv python=3.8 jupyter simpleitk -c simpleitk && \
    echo "source activate myenv" >> ~/.bashrc

# Use Miniconda's activation method directly instead of `source ~/.bashrc`
SHELL ["/bin/bash", "-c"]

# Install the Minc toolkit
RUN wget --no-check-certificate -q http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/minc-toolkit-1.9.18-20200813-Ubuntu_20.04-x86_64.deb && \
    dpkg -i minc-toolkit-1.9.18-20200813-Ubuntu_20.04-x86_64.deb && \
    rm minc-toolkit-1.9.18-20200813-Ubuntu_20.04-x86_64.deb

# Install nipype and other necessary Python packages
RUN conda run -n myenv pip install nipype h5py tifffile tqdm

# Clone the required Git repositories
RUN git -c http.sslVerify=false clone https://github.com/carlohamalainen/volgenmodel-nipype.git && \
    git -c http.sslVerify=false clone https://github.com/carlohamalainen/volgenmodel-fast-example.git

# Set environment variables
ENV PYTHONPATH=/volgenmodel-nipype
ENV PATH="${PATH}:/volgenmodel-nipype/extra-scripts:/opt/minc/1.9.18/bin"
ENV PERL5LIB=/opt/minc/1.9.18/perl

# Expose the port for Jupyter Notebook
EXPOSE 8888

# Start Jupyter Notebook when the container launches
CMD ["conda", "run", "-n", "myenv", "jupyter", "notebook", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]

