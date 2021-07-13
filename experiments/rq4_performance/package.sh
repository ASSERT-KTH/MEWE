CURRENT=$PWD
FOLDER=$1

NAME=$(basename $FOLDER)
DIR=$(dirname $FOLDER)
cd $FOLDER
cd ..
echo $PWD
tar -cvzf $NAME.tar.gz $NAME
cd $CURRENT