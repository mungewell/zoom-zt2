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
    #"dump" / Peek(HexDump(Bytes(24))),
    "autorev" / ByteSwapped(Bytes(24)),
    "reversed" / RestreamData(this.autorev, EDTB2), # this does not allow re-build of data :-(
)

EDTB = Struct(
    Const(b"EDTB"),
    "length" / Int32ul,
    "effects" / Array(this._.fx_count, EDTB1),
)

PPRM = Struct(
    Const(b"PPRM"),
    "length" / Int32ul,
    #"pprm_dump" / Peek(HexDump(Bytes(this.length))),
    Padding(this.length),
)

ZPTC = Padded(760, Struct(
    Const(b"PTCF"),
    Padding(8),
    "fx_count" / Int32ul,
    Padding(10),
    "name" / PaddedString(10, "ascii"),
    "ids" / Array(this.fx_count, Int32ul),

    "TXJ1" / TXJ1,
    "TXE1" / TXE1,
    "EDTB" / EDTB,
    "PPRM" / PPRM,
))


#--------------------------------------------------
def main():
    from optparse import OptionParser

    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")
    parser.add_option("-s", "--summary",
        help="summarize LINE in human readable form",
        action="store_true", dest="summary")

    parser.add_option("-o", "--output", dest="outfile",
        help="write data to OUTFILE")

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("FILE not specified")

    infile = open(args[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        data = infile.read()
    infile.close()

    if data:
        config = ZPTC.parse(data)

        if options.dump:
            print(config)

        if options.summary:
            print("Name: %s" % config['name'])
            for id in range(config['fx_count']):
                print("Effect %d: 0x%8.8X" % (id+1, config['ids'][id]))

                print("   Enabled:", config['EDTB']['effects'][id] \
                        ['reversed']['control']['enabled'])
                for param in range(1,9):
                    print("   Param %d: %d" % (param, config['EDTB']['effects'][id] \
                        ['reversed']['control']['param'+str(param)]))

        if options.outfile:
            outfile = open(options.outfile, "wb")

            # need to rebuild EDTB's reversed data
            for id in range(config['fx_count']):
                #config['EDTB']['effect'][id]['reversed']['control']['enabled'] = False
                blob = EDTB2.build(config['EDTB']['effects'][id]['reversed'])
                config['EDTB']['effects'][id]['autorev'] = blob

            data = ZPTC.build(config)
            if outfile:
                outfile.write(data)
                outfile.close

if __name__ == "__main__":
    main()

