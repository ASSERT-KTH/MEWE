mkdir -p build
cd build
# set(LDFLAGS -L/usr/local/opt/libxml2/lib)
# set(CPPFLAGS -I/usr/local/opt/libxml2/include)
#export PATH="/usr/local/opt/libxml2/bin:$PATH"
#export LDFLAGS="-L/usr/local/opt/libxml2/lib"
#export CPPFLAGS="-I/usr/local/opt/libxml2/include"

cmake ../
make