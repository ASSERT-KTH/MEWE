FROM ubuntu:20.04


RUN apt-get update
RUN apt-get install -y wget unzip zip

# DOWNLOAD PANAMA
RUN mkdir /STRAC
WORKDIR /STRAC
RUN wget https://github.com/KTH/STRAC/releases/download/v0.6/JDK14-Ubuntu18-panama.zip
RUN unzip JDK14-Ubuntu18-panama.zip -d JDK
RUN wget https://github.com/KTH/STRAC/releases/download/v0.6/STRACAlign-jdk15-SIMD.zip
RUN unzip STRACAlign-jdk15-SIMD.zip -d STRAC

RUN ls

#  CHECK JAVA VERSION
RUN JDK/home/runner/work/STRAC/STRAC/panama/dev/build/linux-x86_64-server-release/jdk/bin/java --version

# COPY log4 to STRACAlign

RUN mkdir /WORKDIR
RUN cp STRAC/STRACAlign/target/log4j.properties /WORKDIR

COPY launch.sh launch.sh

ENTRYPOINT ["bash", "launch.sh"]