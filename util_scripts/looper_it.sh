# Plug GCE-3 in and....
export am="amidi -p hw:1,0,0 -r temp.bin -t 2"
echo "Go!"

echo Switch to editor mode
$am -S 'F0 52 00 6e 50 F7'; hexdump -C temp.bin

echo Select preset 200
$am -S 'b0 20 31 c0 03'; hexdump -C temp.bin 

echo Grab screen and decode
$am -S 'F0 52 00 6e 64 02 00 05 00 F7'
python3 decode_screens.py -a temp.bin | head -n 15

# ---------

echo Prime Looper
$am -S "f0 52 00 6e 64 03 00 0a 01 00 00 00 00 00 f7"; hexdump -C temp.bin 

echo Looper Rec
$am -S "f0 52 00 6e 64 03 00 0a 03 01 00 00 00 00 f7"; hexdump -C temp.bin 

echo Grab screen and decode
$am -S 'F0 52 00 6e 64 02 00 05 00 F7'
python3 decode_screens.py -a temp.bin | head -n 15

sleep 15
echo Looper Play
$am -S "f0 52 00 6e 64 03 00 0a 03 01 00 00 00 00 f7"; hexdump -C temp.bin 

echo Grab screen and decode
$am -S 'F0 52 00 6e 64 02 00 05 00 F7'
python3 decode_screens.py -a temp.bin | head -n 15

# ---------

sleep 15
echo Looper Overdub
$am -S "f0 52 00 6e 64 03 00 0a 03 01 00 00 00 00 f7"; hexdump -C temp.bin 

echo Grab screen and decode
$am -S 'F0 52 00 6e 64 02 00 05 00 F7'
python3 decode_screens.py -a temp.bin | head -n 15

sleep 15
echo Looper Play
$am -S "f0 52 00 6e 64 03 00 0a 03 01 00 00 00 00 f7"; hexdump -C temp.bin 

echo Grab screen and decode
$am -S 'F0 52 00 6e 64 02 00 05 00 F7'
python3 decode_screens.py -a temp.bin | head -n 15

# ---------
sleep 15
echo Looper Stop and Clear - FootSwitch 2
$am -S "f0 52 00 6e 64 03 00 0a 04 01 00 00 00 00 f7"; hexdump -C temp.bin
echo "Done."

echo Grab screen and decode
$am -S 'F0 52 00 6e 64 02 00 05 00 F7'
python3 decode_screens.py -a temp.bin | head -n 15

