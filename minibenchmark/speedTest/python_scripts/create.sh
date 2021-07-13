
OUT_DIR=out/video_10fps
CROP_DIR=out/crop

#ffmpeg -r 1/5 -i img%03d.png -c:v libx264 -vf fps=25 -pix_fmt yuv420p out.mp4
rm wavefront4.mp4

for i in $OUT_DIR/*
do
    name=$(basename $i)
    #TODO the crop is hardcoded
    ffmpeg -i "$OUT_DIR/$name" -vf  'crop=1990:1000:320:490' "$CROP_DIR/$name"
done
ffmpeg -framerate 30 -pattern_type glob -i $CROP_DIR/'*.png' -ss 38 -c:v libx264 -r 30 -pix_fmt yuv420p wavefront4.mp4