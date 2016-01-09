# Docker test container

Install the Docker Engine: https://docs.docker.com/engine/installation/

## Run the test workflow

Clone repositories including the sample mouse brain data:

    git clone https://github.com/carlohamalainen/volgenmodel-nipype.git
    cd volgenmodel-nipype/docker
    https://github.com/carlohamalainen/volgenmodel-fast-example.git # about 96Mb

Build and run:

    ./build.sh && docker run -i -t user/volgenmodel-nipype /bin/bash /opt/go.sh

End of output should look like:


