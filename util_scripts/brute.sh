# enable/disable effect slot 0 for current patch
# amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 00 01 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin

# change effect slot 0 for current patch
# amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 01 03 00 00 00 00 f7' -r temp13.bin -t 2 ; hexdump -C temp13.bin
# amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 7 01 01 00 00 00 00 f7' -r temp13.bin -t 2 ; hexdump -C temp13.bin


# unknown, replies but no change seen on pedal
#amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 a 01 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
#amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 a 00 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin

# BPM - in rythm and setup
#amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 a 02 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin

# The cause pedal to send back identical Patch Files
#amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 a 07 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
#amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 a 08 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
#amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 a 09 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin

echo 0;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 00 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 1;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 01 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 2;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 02 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 3;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 03 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 4;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 04 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 5;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 05 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 6;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 06 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 7;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 07 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 8;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 08 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo 9;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 09 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo a;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 08 03 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo b;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 0b 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo c;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 0c 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo d;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 0d 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo e;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 0e 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
echo f;amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 8 0f 13 00 00 00 00 f7' -r temp.bin -t 2 ; hexdump -C temp.bin
