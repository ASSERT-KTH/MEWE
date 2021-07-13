
TIMES=100


for i in $(seq 1 $TIMES)
do
	curl -si https://totally-in-deer.edgecompute.app/
	echo
done