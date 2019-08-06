# start from an ubuntu base
FROM ubuntu:18.10

# consume the build arg
# ARG TARGET_ENV

# persist the env variable in the built image
# ENV TARGET_ENV=$TARGET_ENV

# TARGET_ENV will appear as an env variable
# RUN echo $TARGET_ENV
# RUN env

# install packages
RUN apt-get update && \
    apt-get -y install \
        apt-utils \
        openjdk-11-jre \
        openjdk-11-jdk \
        openjdk-11-doc \
        curl \
        gradle \
        gradle-doc \
        libssl-dev \
        pkg-config \
        python3.6 \
        python3-pip \
    && apt-get clean

# install rustup
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# install rust
RUN ./root/.cargo/bin/rustup install stable
RUN ./root/.cargo/bin/rustup install beta
RUN ./root/.cargo/bin/rustup install nightly

# add cargo to path
ENV PATH=$PATH:./root/.cargo/bin

# copy the python dependencies and install
# we only copy the dependencies at this stage to allow the caching of python dependencies
# COPY ./requirements.txt ./requirements.txt
# RUN pip3 install -r requirements.txt

# copy the rest of the source tree
COPY . .

# run the worker
CMD ./run.sh
