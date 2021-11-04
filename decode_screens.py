#!/usr/bin/python
#
# Script decode 'screen data' from Zoom G1Four
# (c) Simon Wood, 10 Dec 2020
#
# read with:
# $ amidi -p hw:1,0,0 -S 'F0 52 00 6e 64 02 00 09 00 F7' -r temp.bin -t 2
#

from construct import *

#--------------------------------------------------
# Define ZPTC file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

Info = Struct(
    "screen1" / Byte,
    "param1" / Byte,
    "type1" / Enum(Byte,
        VALUE  = 0x00,
        NAME   = 0x01,
        INVERT = 0x07,
    ),
    "invert1" / Byte,
    "value" / PaddedString(10, "ascii"),

    "screen2" / Byte,
    "param2" / Byte,
    "type2" / Enum(Byte,
        VALUE  = 0x00,
        NAME   = 0x01,
        INVERT = 0x07,
    ),
    "invert2" / Byte,
    "name" / PaddedString(10, "ascii"),
)

Screen = Struct(
    "info" / Array(6, Info),
)

Display = Struct(
    GreedyRange(Const(b"\x00")),        # get rid of leading zeros
    Const(b"\xf0\x52\x00\x6e\x64\x01"), 
    "screens" / GreedyRange(Screen),
    #Const(b"\xf7"),                    # not seen if we ask for too
                                        # many screens worth of data
)

#--------------------------------------------------
def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="decode_effect")
    parser.add_argument('files', metavar='FILE', nargs=1,
        help='File to process')

    parser.add_argument("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")

    options = parser.parse_args()

    if not len(options.files):
        parser.error("FILE not specified")

    # Read data from file
    infile = open(options.files[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        data = infile.read()
    infile.close()

    if data:
        config = Display.parse(data)
        if options.dump:
            print(config)

        for screen in config['screens']:
            for info in screen['info']:
                if info['param1'] == 0:
                    if info['name'] == "Dummy":
                        on_off = None
                    else:
                        if info['value'] == "1":
                            on_off = "On"
                        else:
                            on_off = "Off"
                        print("---")
                elif info['param1'] == 1:
                    if on_off:
                        print("Effect: %s (%s)" % (info['name'], on_off))
                else:
                    if info['name'] != "Dummy":
                        print("%s : %s" % (info['name'], info['value']))


if __name__ == "__main__":
    main()

