#!/usr/bin/python
#
# Script decode 'screen data' from Zoom G1Four
# (c) Simon Wood, 10 Dec 2020
#
# read with:
# $ amidi -p hw:1,0,0 -S 'F0 52 00 6e 64 02 00 09 00 F7' -r temp.bin -t 2
#                                                 ^^ Format: 00=Param/Value, 01=Value only
#                                              ^^ Stop Screen
#                                           ^^ Start Screen
#

from construct import *

#--------------------------------------------------
# Define format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

Info = Struct(
    "test2" / Peek(Int16ul),
    Check(this.test2 == this._.test1),

    "screen" / Byte,
    "param" / Byte,
    "type" / Enum(Byte,
        VALUE  = 0x00,
        NAME   = 0x01,
        INVERT = 0x07,
    ),
    "invert" / Byte,
    "value" / PaddedString(10, "ascii"),
)

Infos = Struct(
    "test1" / Peek(Int16ul),

    "info" / Info,
    "info2" / Optional(Info),
)

Screen = Struct(
    "infos" / Array(6, Infos),
)

Display = Struct(
    GreedyRange(Const(b"\x00")),        # get rid of leading zeros
    Const(b"\xf0\x52\x00\x6e\x64\x01"), 

    "screens" / GreedyRange(Screen),

    "end" / Optional(Const(b"\xf7")),   # not seen if we ask for too
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

    parser.add_argument("-a", "--all",
        help="display all parameters (include 'Dummy')",
        action="store_true", dest="all")

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
            for infos in screen['infos']:
                info = infos['info']
                if info['param'] == 0:
                    if info['value'] == "Dummy":
                        on_off = None
                    else:
                        if info['value'] == "1":
                            on_off = "On"
                        else:
                            on_off = "Off"
                        print("---")
                elif info['param'] == 1:
                    if on_off:
                        print("Effect: %s (%s)" % (info['value'], on_off))
                else:
                    if info['value'] != "Dummy" or options.all:
                        if infos['info2'] != None:
                            print("%s : " % infos['info2']['value'], end="")
                        print("%s" % info['value'])

        if config['end'] == None:
            print("\nWarning: data not complete!")


if __name__ == "__main__":
    main()

