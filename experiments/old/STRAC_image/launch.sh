export JAVA=/STRAC/JDK/home/runner/work/STRAC/STRAC/panama/dev/build/linux-x86_64-server-release/jdk/bin/java

cp /STRAC/STRAC/STRACAlign/target/log4j.properties /WORKDIR
cd /WORKDIR
$JAVA -Xmx4g -jar /STRAC/STRAC/STRACAlign/target/STRAC-align-0.1.jar $@