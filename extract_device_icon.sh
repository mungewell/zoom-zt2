# Extract code section and locate icon pixels
python3 decode_effect.py -c test.code "$1"

objcopy -j .const -S -w -K *picTotalDisplay_* -I elf32-little test.code -O elf32-little test_mod.code
objcopy -I elf32-little test_mod.code -O binary test.bin
objdump -t test_mod.code

#
#test_mod.code:     file format elf32-little
#
#SYMBOL TABLE:
#80000000 l    d  .const	00000000 .const
#800006b0 g     O .const	0000005c .hidden picTotalDisplay_MATCH_30
#
#skip=1712 # hex 0x6b0
#count=92  # hex 0x5c

skiphex=`objdump -t test_mod.code | grep "picTotalDisplay" | cut -c 2-8 | tr '[:lower:]' '[:upper:]'`
counthex=`objdump -t test_mod.code | grep "picTotalDisplay" | cut -c 25-32 | tr '[:lower:]' '[:upper:]'`
skip=`echo "ibase=16; $skiphex" | bc`
count=`echo "ibase=16; $counthex" | bc`

#echo $skiphex $counthex $skip $count
dd if=test.bin of=icon.raw bs=1 skip=$skip count=$count


# Process the raw icon pixels to PNG
height=8
width=`echo "(8 * $count)/($height * 4)" | bc`
twice=`echo "$width * 2" | bc`
thrice=`echo "$width * 3" | bc`

echo icon width is $width
convert -monochrome -size "$height"x"$count" -depth 1 MONO:icon.raw -transpose -crop "$width"x"$height"+0+0 stripe1.png
convert -monochrome -size "$height"x"$count" -depth 1 MONO:icon.raw -transpose -crop "$width"x"$height"+"$width"+0 stripe2.png
convert -monochrome -size "$height"x"$count" -depth 1 MONO:icon.raw -transpose -crop "$width"x"$height"+"$twice"+0 stripe3.png
convert -monochrome -size "$height"x"$count" -depth 1 MONO:icon.raw -transpose -crop "$width"x"$height"+"$thrice"+0 stripe4.png
convert stripe1.png stripe2.png stripe3.png stripe4.png -append icon.png

#display icon.png 
