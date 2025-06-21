
amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 3 01 01 00 00 00 00 f7' -r temp13.bin -t 2 ; hexdump -C temp13.bin
amidi -p hw:2,0,0 -S 'f0 52 00 6e 64 03 00 3 01 04 00 00 00 00 f7' -r temp14.bin -t 2 ; hexdump -C temp14.bin
