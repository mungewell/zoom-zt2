# convert 'icon.png' back to it's striped 'icon2.raw'

width=`identify "$1"| cut -d ' ' -f 3 | cut -d 'x' -f 1`

convert "$1" -transpose -crop 8x"$width"+0+0 stripe1.png
convert "$1" -transpose -crop 8x"$width"+8+0 stripe2.png
convert "$1" -transpose -crop 8x"$width"+16+0 stripe3.png
convert "$1" -transpose -crop 8x"$width"+24+0 stripe4.png

convert stripe1.png stripe2.png stripe3.png stripe4.png -append -monochrome -depth 1 MONO:icon2.raw

diff -s icon.raw icon2.raw
