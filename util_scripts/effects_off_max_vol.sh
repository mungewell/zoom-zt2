# turn off each effect in patch
amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 00  00 00 00 00 00 00 f7'
amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 01  00 00 00 00 00 00 f7'
amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 02  00 00 00 00 00 00 f7'
amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 03  00 00 00 00 00 00 f7'

# max volume
amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 0a  00 7f 00 00 00 00 f7'

# read screen(s) and display
amidi -p hw:2,0,0 -S 'F0 52 00 6e 64 02 00 05 00 F7' -r temp.bin -t 2
python3 decode_screens.py -a temp.bin
