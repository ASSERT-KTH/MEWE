if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null
    brew install geos
    brew install proj
    export CPLUS_INCLUDE_PATH="/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include"
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt install libgeos-dev proj-bin -y
fi

VERSION="1.2.2rel"

if [[ ! -f basemap.zip ]]; then
    wget -O basemap.zip https://github.com/matplotlib/basemap/archive/v1.2.2rel.zip
fi

pip3 install --user --upgrade basemap.zip