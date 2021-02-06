if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null
    brew install geos
    brew install proj
    brew install libxml2
    brew install --cask wireshark
    export CPLUS_INCLUDE_PATH="/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include"
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt install libgeos-dev wireshark proj docker.io -y
fi

sudo docker rm mongodb --force
sudo docker rm some-rabbit --force

sudo docker run -d --restart always  -it  -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=$MONGO_USER -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_PASS --name mongodb -d mongo
sudo docker run -d --hostname my-rabbit --name some-rabbit --restart always -p 5672:5672 -p 8080:15672 rabbitmq:3-management

VERSION="1.2.2rel"

if [[ ! -f basemap.zip ]]; then
    wget -O basemap.zip https://github.com/matplotlib/basemap/archive/v1.2.2rel.zip
fi

pip3 install --user --upgrade basemap.zip