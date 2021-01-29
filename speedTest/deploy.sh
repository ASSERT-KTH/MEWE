INTERVAL=$1
POPS="bma sea"
TIMEOUT=10
service_name

	echo "bma"
for pop in $(seq 4400 4483)
do
	# TODO get ranges for all POPs

	status=$(timeout $TIMEOUT curl -l -HX-Pass:1 -ksSi -HX-Origin:https_teamc_origin -HHost:totally-in-deer.edgecompute.app "https://cache-sea$pop.hosts.secretcdn.net" -o /dev/null -w '%{http_code}\n' -s)
	if [ $status == "200" ]; then echo $pop; fi
	if [ $status == "500" ]; then echo "Internal error"; fi

	echo $status


	curl  
done