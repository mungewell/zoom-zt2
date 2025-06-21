#!/usr/bin/python
#
# Script encode effect IDs to the 7-bit values needed for SysEx
# (c) Simon Wood, 20 June 2025
#

from argparse import ArgumentParser

parser = ArgumentParser(prog="convert_id_to_7bit")
parser.add_argument('id', metavar='FILE', nargs=1,
    help='effect ID to process (in hex)')
parser.add_argument("-d", "--decimal",
    help="ID is specified as decimal value",
    action="store_true", dest="decimal")

parser.add_argument("-s", "--slot", type=int, default=-1,
    help="output midi command to store is slot SLOT", dest="slot")
parser.add_argument("-p", "--plus",
    help="modify midi for the MS-plus pedals",
    action="store_true", dest="plus")

options = parser.parse_args()

if not len(options.id):
    parser.error("ID not specified")

if options.decimal:
    ID = int(options.id[0], 10)
else:
    ID = int(options.id[0], 16)

if options.slot == -1:
    print ("0x%8.8x" % ID)
    print ("--")
    print ("0x%2.2x" % (ID       & 0x7f))
    print ("0x%2.2x" % (ID >> 7  & 0x7f))
    print ("0x%2.2x" % (ID >> 14 & 0x7f))
    print ("0x%2.2x" % (ID >> 21 & 0x7f))
    print ("0x%2.2x" % (ID >> 28 & 0x7f))
else:
    if options.plus:
        print("for MS-plus:")
        print("amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 20 00 %2.2x 01 %2.2x %2.2x %2.2x %2.2x %2.2x f7'" % \
                (options.slot, (ID & 0x7f), (ID >> 7  & 0x7f), \
                (ID >> 14 & 0x7f), (ID >> 21 & 0x7f), (ID >> 28 & 0x7f)))
    else:
        print("amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 %2.2x 01 %2.2x %2.2x %2.2x %2.2x %2.2x f7'" % \
                (options.slot, (ID & 0x7f), (ID >> 7  & 0x7f), \
                (ID >> 14 & 0x7f), (ID >> 21 & 0x7f), (ID >> 28 & 0x7f)))
