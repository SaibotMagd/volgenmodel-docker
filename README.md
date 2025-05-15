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
  - Create templates for combinations such as `00-01`, `01-02`, `00-02`, and `00-01-02`.
  - Note: The **order of the files does not matter** in these permutations.

### 4. **Integrated Jupyter Notebook**
The container is designed to start a **Jupyter Notebook server**, allowing an intuitive and interactive environment for managing the pipeline:
- Simply open your browser and navigate to `localhost:8888` to access the server.
- The main code for creating templates, performing file conversions, and generating permutations is located in the `create_template_from_mnc.ipynb` file.
- There's **nothing else to install**—everything you need is preinstalled in the Docker container.

### 5. **Workflow Automation**
The pipeline includes source code to:
1. **Convert NIfTI files to MINC format.**
2. Perform pre-processing like [N4 bias field correction](https://simpleitk.readthedocs.io/en/master/link_N4BiasFieldCorrection_docs.html), auto-crop and zero-padding (as a simple way to guarantee centring of the brains on the images with sufficiently large margins for registration; see also Figure 3 in http://dx.doi.org/10.1016/j.ymeth.2015.01.005)
3. Build all possible **permutations** of input base files.
4. Calculate templates using the **Volgenmodel-Nipype pipeline**.
5. Convert the output templates back to the NIfTI format for broader compatibility.

---

## How to Get Started

### Build the Docker Container Manually
To manually build the Docker container, use the following command in the root directory of the repository:
```bash
docker build -t volgenmodel-pipeline .
```

### TODO: Start the Prebuilt Container from Docker Hub (not yet registered on Docker Hub)
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

### Input File Requirements
- **File Format**: Source files must be in **NIfTI (.nii)** format.
- **File Location**: Place all source files in the directory `/data/masked_brains` before running the pipeline.

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
[Original README from Andrew Janke](https://github.com/andrewjanke/volgenmodel)
[OG Readme](./README_og.md)

