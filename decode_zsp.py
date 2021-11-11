#!/usr/bin/python
#
# Script decode/encode 'ZSP' files, used by GCE-3
# (c) Simon Wood, 11 Nov 2021
#

from construct import *

#--------------------------------------------------
# Define ZSP file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

VAR = Struct(
    "name" / PaddedString(4, "Ascii"),

    "vlength" / Int32ul,
    "length" / Computed(this.vlength - 8),

    "data" / Bytes(this.length),
)

HDIF = Struct(
    Const(b"HDIF"),
    "length" / Bitwise(Struct(
        "length" / BitsInteger(4),      # Nyble swap?
        Padding(4),
        Padding(24),
    )),

    "unknown" / Bytes(0x20),
    "data" / Array(this.length.length, VAR),
)

APIF = Struct(
    Const(b"APIF"),
    "length" / Bitwise(Struct(
        "length" / BitsInteger(4),      # Nyble swap?
        Padding(4),
        Padding(24),
    )),

    "data" / Array(this.length.length, VAR),
)

ZTYP = Struct(
    Const(b"ZTYP"),

    "unknown" / Int32ul,
    "name" / PaddedString(12, "Ascii"),
    "unknown2" / Int32ul,
)

ZDLT = Struct(
    Const(b"ZDLT"),
    "blength" / Int32ul,            # in bytes
    "length" / Computed(this.blength // 24),

    "data" / Array(this.length, ZTYP),
)

ZSP = Struct(
    Const(b"ZSPF"),
    "length" / Int32ul,

    "HDIF" / HDIF,
    "APIF" / APIF,
    "ZDLT" / ZDLT,
)


#--------------------------------------------------
def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="decode_zsp")
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
        config = ZSP.parse(data)

        if options.dump:
            print(config)


if __name__ == "__main__":
    main()

