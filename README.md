# Project: Reviving an Old Pipeline with Docker Integration

The purpose of this project is to **rescue and modernize an old pipeline** by creating a robust and versatile Docker container. The container is built upon a foundation of **Ubuntu 20.04**, **MINC ToolBox 1.9**, and the **Volgenmodel-Nipype pipeline**. With this repository, you can breathe new life into pipelines that may no longer have access to their original software environment.

---

## Features

### 1. **Docker-Based Flexibility**
- The Docker container provided in this repository ensures a smooth and reliable execution environment.
- You can:
  - **Manually build** the container using the included `Dockerfile`.
  - **Download** a prebuilt container directly from Docker Hub (ideal when the original software is no longer available).

### 2. **Support for NIfTI Format Files**
This repository introduces compatibility with the more widely used **NIfTI (.nii)** file format. For users working with these files:
- Input NIfTI files are automatically **converted to MINC (.mnc)** format.
- After processing, the resulting templates are **converted back to NIfTI**, ensuring full interoperability.

### 3. **Full-Permutation Pipeline Mode**
A standout feature of this repository is its ability to **run the pipeline in a full-permutation mode**. This means:
- Any combination of base files can be used to generate templates.
- For instance, if you provide files `00`, `01`, and `02`, the pipeline will:
  - Create templates for combinations such as `00-01`, `01-02`, and `00-01-02`.
  - Note: The **order of the files does not matter** in these permutations.

### 4. **Integrated Jupyter Notebook**
The container is designed to start a **Jupyter Notebook server**, allowing an intuitive and interactive environment for managing the pipeline:
- Simply open your browser and navigate to `localhost:8888` to access the server.
- The main code for creating templates, performing file conversions, and generating permutations is located in the `create_template_from_mnc.ipynb` file.
- There's **nothing else to install**—everything you need is preinstalled in the Docker container.

### 5. **Workflow Automation**
The pipeline includes source code to:
1. **Convert NIfTI files to MINC format.**
2. Build all possible **permutations** of input base files.
3. Calculate templates using the **Volgenmodel-Nipype pipeline**.
4. Convert the output templates back to the NIfTI format for broader compatibility.

---

## How to Get Started

### Build the Docker Container Manually
To manually build the Docker container, use the following command in the root directory of the repository:
```bash
docker build -t volgenmodel-pipeline .
```

### Start the Prebuilt Container from Docker Hub
Alternatively, you can download the prebuilt container from Docker Hub and start it directly:
```bash
docker pull <dockerhub-username>/volgenmodel-pipeline:latest
docker run -it <dockerhub-username>/volgenmodel-pipeline
```
- Check out the volume mount defined in the "docker-compose.yml" option mounts the `/data` folder from your local repository into the container. This ensures that **all processing steps and outputs are saved outside the container**, making them easily accessible and persistent.

---

## Important Notes

### Accessing the Jupyter Notebook
- Once the container is running, a **Jupyter Notebook server** will be available at `localhost:8888`.
- Use this interface to execute the notebook file `create_template_from_mnc.ipynb`. This file provides the code to:
  - Convert NIfTI files to MINC format.
  - Perform full permutations of input files.
  - Generate templates with the Volgenmodel-Nipype pipeline.
  - Convert the resulting templates back to the NIfTI format.

### CPU Usage Configuration
- You can customize the number of CPUs used during processing with the `ncpus` parameter. However, be cautious:
  - **Excessive CPU allocation** may overload your system, potentially causing it to crash.
  - A **safe and recommended estimate** is to set `ncpus` to the number of **physical cores** on your machine. For example, if your computer has 8 cores, set `ncpus=8` for optimal performance.

---

## Why This Repository?
This project is a **lifeline** for researchers and users who want to:
- Maintain compatibility with legacy pipelines.
- Transition to modern file formats.
- Harness the power of Docker for a consistent and portable environment.

Feel free to clone the repository, explore the code, and contribute to its growth. Your feedback and collaboration are always welcome! 🚀
//////////////////////////////////////////////////////////////////////////////
// README from OG repo as backup copy
# volgenmodel-nipype

This is the original development repo from 2014.

Official repository: [https://github.com/NIF-au/volgenmodel-nipype](https://github.com/NIF-au/volgenmodel-nipype)

Active fork at CAI-UQ: [https://github.com/CAIsr/volgenmodel-nipype](https://github.com/CAIsr/volgenmodel-nipype)

volgenmodel-nipype is the port of [volgenmodel](https://github.com/andrewjanke/volgenmodel) to [Nipype](https://github.com/nipy/nipype). It creates nonlinear models from a series of input MINC files.

## Quickstart on Ubuntu 20 with MINC Toolkit 1.9.18-20200813

### Ubuntu packages

```bash
sudo apt-get install git octave python3-pip imagemagick
```

### minc-toolkit

From [https://bic-mni.github.io/#installing](https://bic-mni.github.io/#installing):

```bash
wget http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/minc-toolkit-1.9.18-20200813-Ubuntu_20.04-x86_64.deb
sudo dpkg -i minc-toolkit-1.9.18-20200813-Ubuntu_20.04-x86_64.deb
```

### nipype

```bash
pip install nipype
```

### Run the fast example

```bash
git clone https://github.com/carlohamalainen/volgenmodel-nipype
git clone https://github.com/carlohamalainen/volgenmodel-fast-example.git

cd volgenmodel-nipype
export PYTHONPATH=`pwd`
export PATH=$PATH:`pwd`/extra-scripts:/opt/minc/1.9.18/bin
export PERL5LIB=/opt/minc/1.9.18/perl

python3 volgenmodel.py --run=MultiProc --ncpus=2 --fit_stages=lin,1,3 --input_dir=../volgenmodel-fast-example
```

Check the output:

```bash
$ find workflow_output_workflowMultiProc2/ -type f
workflow_output_workflowMultiProc2/stdev/mouse00_volcentre_norm_resample_bigaverage_stdev_vol_symm.mnc
workflow_output_workflowMultiProc2/model/mouse00_volcentre_norm_resample_bigaverage_reshape_vol_symm.mnc
```

## Install for Windows Subsystem for Linux or Ubuntu 16.04
Install minc: https://bic-mni.github.io
```bash
    wget http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/minc-toolkit-1.9.16-20180117-Ubuntu_16.04-x86_64.deb
    sudo apt-get install libc6 libstdc++6 imagemagick perl octave
    sudo dpkg -i minc-toolkit-1.9.16-20180117-Ubuntu_16.04-x86_64.deb
    sudo apt-get install libgl1-mesa-glx libglu1-mesa
    rm minc-toolkit-1.9.16-20180117-Ubuntu_16.04-x86_64.deb

    vi .bashrc
    source /opt/minc/1.9.16/minc-toolkit-config.sh
    export PERL5LIB=/opt/minc/1.9.16/perl
```

Clone code and test-data:    
```bash
git clone https://github.com/CAIsr/volgenmodel-nipype.git
git clone https://github.com/CAIsr/volgenmodel-fast-example.git
```

install miniconda:
```bash
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

start new terminal and install packages required:
```bash
conda install --channel conda-forge nipype
pip install pydot
```

add additonal scripts to PATH
```bash
cd volgenmodel-nipype/extra-scripts
echo "export PATH="`pwd -P`":\$PATH" >> ~/.bashrc
```

you need a working octave installed. Somehow the minc libs break octave. Sometimes this fixes it:
select /usr/lib/lapack/liblapack.so.3
```bash
sudo update-alternatives --config liblapack.so.3
```
or load octave using a module:
```bash
module load octave/4.2.1
```

start new temrinal and run volgenmodel with the test data:
```bash
cd volgenmodel-nipype/
python3 volgenmodel.py --input_dir ../volgenmodel-fast-example
```



The final model should look like this:

![mouse model triplanar](https://raw.githubusercontent.com/carlohamalainen/volgenmodel-fast-example/master/model-2016-01-09.png)

# Citation
This method is an implementation of the technique described in this paper:

   http://www.ncbi.nlm.nih.gov/pubmed/25620005

If you use it in a publication please cite:

   Janke AL, Ullmann JF, Robust methods to create ex vivo minimum
deformation atlases for brain mapping.
   Methods. 2015 Feb;73:18-26. doi: [10.1016/j.ymeth.2015.01.005](http://dx.doi.org/10.1016/j.ymeth.2015.01.005)
