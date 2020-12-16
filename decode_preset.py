#!/usr/bin/python
#
# Script decode/encode 'ZPTC' patch files from Zoom F/W
# (c) Simon Wood, 13 May 2020
#

from construct import *

#--------------------------------------------------
# Define ZPTC file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

PTCF = Struct(
    Const(b"PTCF"),
    Padding(8),
    "effects" / Int32ul,
    Padding(10),
    "name" / PaddedString(10, "ascii"),
    "id1" / Int32ul,
    "id2" / Int32ul,
    "id3" / Int32ul,
    "id4" / Int32ul,
    "id5" / Int32ul,
)

TXJ1 = Struct(
    Const(b"TXJ1"),
    "length" / Int32ul,
    Padding(this.length),
)

TXE1 = Struct(
    Const(b"TXE1"),
    "length" / Int32ul,
    "name" / PaddedString(this.length, "ascii"),
)

EDTB2 = Struct( # Working with a Byte-reversed copy of data
    Padding(9),
    "control" / Bitwise(Struct(
        Padding(6),
        "param8" / BitsInteger(8),
        "param7" / BitsInteger(8),
        "param6" / BitsInteger(8),
        "param5" / BitsInteger(12),
        "param4" / BitsInteger(12),
        "param3" / BitsInteger(12),
        "param2" / BitsInteger(12),
        "param1" / BitsInteger(12),
        "unknown" / Bit, # always '0', so far
        "id" / BitsInteger(28),
        "enabled" / Flag,
    )),
)

EDTB1 = Struct(
    # "dump" / Peek(HexDump(Bytes(24))),
    "autorev" / ByteSwapped(Bytes(24)),
    "reversed" / RestreamData(this.autorev, EDTB2), # this does not allow re-build of data :-(
)

EDTB = Struct(
    Const(b"EDTB"),
    "length" / Int32ul,
    "effect1" / EDTB1,
    "effect2" / EDTB1,
    "effect3" / EDTB1,
    "effect4" / EDTB1,
    "effect5" / EDTB1,
)

PPRM = Struct(
    Const(b"PPRM"),
    "length" / Int32ul,
    #"pprm_dump" / Peek(HexDump(Bytes(this.length))),
    Padding(this.length),
)

ZPTC = Struct(
    "PTCF" / PTCF,
    "TXJ1" / TXJ1,
    "TXE1" / TXE1,
    "EDTB" / EDTB,
    "PPRM" / PPRM,
)


#--------------------------------------------------
def main():
    from optparse import OptionParser

    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("FILE not specified")

    infile = open(args[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        data = infile.read()
    infile.close()

    if options.dump and data:
        config = ZPTC.parse(data)
        print(config)


if __name__ == "__main__":
    main()

