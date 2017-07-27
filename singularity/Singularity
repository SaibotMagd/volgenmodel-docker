BootStrap:docker
From:ubuntu:latest

%files

%labels
MAINTAINER Steffen.Bollmann@cai.uq.edu.au

%environment

%runscript
echo "This gets run when you run the image!"

%post
echo "This section happens once after bootstrap to build the image."

apt-get update

apt-get install -y \
 build-essential g++ bc \
 cmake \
 bison flex \
 libx11-dev x11proto-core-dev \
 libxi6 libxi-dev \
 libxmu6 libxmu-dev libxmu-headers \
 libgl1-mesa-dev libglu1-mesa-dev \
 libjpeg-dev  \
 git


cd /

  git clone --recursive https://github.com/BIC-MNI/minc-toolkit-v2.git minc-toolkit-v2
  cd minc-toolkit-v2
  mkdir build && cd build

 cmake .. \
-DCMAKE_BUILD_TYPE:STRING=Release   \
-DCMAKE_INSTALL_PREFIX:PATH=/opt/minc/1.9.15 \
-DMT_BUILD_ABC:BOOL=ON   \
-DMT_BUILD_ANTS:BOOL=ON   \
-DMT_BUILD_C3D:BOOL=ON   \
-DMT_BUILD_ELASTIX:BOOL=ON   \
-DMT_BUILD_IM:BOOL=OFF   \
-DMT_BUILD_ITK_TOOLS:BOOL=ON   \
-DMT_BUILD_LITE:BOOL=OFF   \
-DMT_BUILD_SHARED_LIBS:BOOL=ON   \
-DMT_BUILD_VISUAL_TOOLS:BOOL=ON   \
-DMT_USE_OPENMP:BOOL=ON   \
-DUSE_SYSTEM_FFTW3D:BOOL=OFF   \
-DUSE_SYSTEM_FFTW3F:BOOL=OFF   \
-DUSE_SYSTEM_GLUT:BOOL=OFF   \
-DUSE_SYSTEM_GSL:BOOL=OFF   \
-DUSE_SYSTEM_HDF5:BOOL=OFF   \
-DUSE_SYSTEM_ITK:BOOL=OFF   \
-DUSE_SYSTEM_NETCDF:BOOL=OFF   \
-DUSE_SYSTEM_NIFTI:BOOL=OFF   \
-DUSE_SYSTEM_PCRE:BOOL=OFF   \
-DUSE_SYSTEM_ZLIB:BOOL=OFF

make && make install
