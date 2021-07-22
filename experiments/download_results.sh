
if [ ! -f mewe.data.tar.gz ]
then
    wget -O mewe.data.tar.gz https://zenodo.org/record/5122817/files/mewe.tar.gz?download=1
fi

if [ ! -d data ]
then
    tar xvf mewe.data.tar.gz
fi

mkdir -p results
mv ./data/experiments_result/results/* ./results/