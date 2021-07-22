python3 -m pingpong.speed_test pingpong/templates/large/ping.tar.gz pingpong/templates/large/pong.tar.gz  20000 ams
mv out/speedtest.txt out/speedtest.ams.large.txt

python3 -m pingpong.speed_test pingpong/templates/large/ping.tar.gz pingpong/templates/large/pong.tar.gz  20000 bma
mv out/speedtest.txt out/speedtest.bma.large.txt

python3 -m pingpong.speed_test pingpong/templates/large/ping.tar.gz pingpong/templates/large/pong.tar.gz  20000 sea
mv out/speedtest.txt out/speedtest.sea.large.txt


python3 -m pingpong.speed_test pingpong/templates/large/ping.tar.gz pingpong/templates/large/pong.tar.gz  20000 bog
mv out/speedtest.txt out/speedtest.bog.large.txt

# small

python3 -m pingpong.speed_test pingpong/templates/small/ping.tar.gz pingpong/templates/small/pong.tar.gz  20000 ams
mv out/speedtest.txt out/speedtest.ams.small.txt

python3 -m pingpong.speed_test pingpong/templates/small/ping.tar.gz pingpong/templates/small/pong.tar.gz  20000 bma
mv out/speedtest.txt out/speedtest.bma.small.txt

python3 -m pingpong.speed_test pingpong/templates/small/ping.tar.gz pingpong/templates/small/pong.tar.gz  20000 sea
mv out/speedtest.txt out/speedtest.sea.small.txt


python3 -m pingpong.speed_test pingpong/templates/small/ping.tar.gz pingpong/templates/small/pong.tar.gz  20000 bog
mv out/speedtest.txt out/speedtest.bog.small.txt



python3 -m pingpong.speed_test pingpong/templates/zero/package.tar.gz pingpong/templates/large/pong.tar.gz 8000 bma
mv out/speedtest.txt out/speedtest.bma.zero.txt