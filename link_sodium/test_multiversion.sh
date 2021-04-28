range_folder=$1
NAME=$2
TIMEOUT=10

POPS=$(find $range_folder -name "range_*" | grep -Eo "range_.*\.json" | grep -Eo "_.{3}" | sed 's/_//')

PP=""
echo "" > paths.csv

for pop in $POPS
do
   # Read json file
   machine=$(jq '.valid[0].at' "$range_folder/range_$pop.json")

   if [[ $machine != "null" ]]
   then

      # max 1 second, allow insecure, redirect sterr to stdout
      RESPONSE=$(curl -m $TIMEOUT -k -H "Host: totally-devoted-krill.edgecompute.app" -i https://cache-$pop$machine.hosts.secretcdn.net 2>&1)
      POPHASH=$(echo "$RESPONSE" | grep "xpophash" | awk '{print $2}')
      XPATH=$(echo "$RESPONSE" | grep "xpath" | awk '{print $2}')
      PP=$(printf "$PP\n$POPHASH")
      a=$(python3 -c "print($POPHASH%7, end=\" \")" 2>/dev/null)
      #echo -n $a " "
      #echo "$RESPONSE"
      echo $pop, $XPATH >> paths.csv # to collect csv
   fi
done

mv paths.csv reports/$NAME.paths.csv
echo "Done!"


# 1 - sanity check, POP hash is unique
echo "$PP" | sort | uniq -c

# 2 - is the same for all rans
mkdir -p checks
echo "$PP" | sort  > "checks/$(date +'%d%m%H%s').check.txt"

