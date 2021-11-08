#!/usr/bin/python
#
# Script to extract ZD2 effects from unzipped exe's 136 file
# (c) Simon Wood, 6 Nov 2021
#

import zoomzt2

from construct import *

#--------------------------------------------------
# Define 136 file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

Extract = Struct(
    "a" / Int16ul,
    "b" / Int16ul,
    "length" / Int16ul,

    "data" / Bytes(this.length),
    If(this.length != 0x0ffa,
        Padding(0x0ffa - this.length),
    ),
)

# short extract, just to lookup ID within the 1st 4096 bytes
short_ZD2 = Struct(
    Const(b"ZDLF"),
    "length" / Int32ul,
    "unknown" / Bytes(81),
    "version" / PaddedString(4, "ascii"),
    Const(b"\x00\x00"),
    "group" / Byte,
    "id" / Int32ul,
)

#--------------------------------------------------
def main():
    from argparse import ArgumentParser
    location = 0xf000

    parser = ArgumentParser(prog="extract_effect_136")
    parser.add_argument('files', metavar='FILE', nargs=1,
        help='File to process')

    parser.add_argument("-s", "--start",
        help="start location of ZDLF's",
        type=int, default=0xf000, dest="location")

    parser.add_argument("-z", "--zt2",
        help="get Id's from local ZT2 file and lookup ZD2 filenames",
        dest="zt2")

    options = parser.parse_args()
    
    ids = []
    if options.zt2:
        infile = open(options.zt2, "rb")
        if not infile:
            options.zt2 = None
        else:
            data = infile.read()
            zt2 = zoomzt2.ZT2.parse(data)

            # scan through effects remembering Ids and Effect names
            for group in zt2[1]:
                for effect in dict(group)["effects"]:
                    ids.append([effect["id"], effect["effect"]])

            infile.close()

    if not len(options.files):
        parser.error("FILE not specified")

    infile = open(options.files[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    outfile = None

    # skip to the start of 'ZDLF's
    inbytes = infile.read(options.location)

    inbytes = infile.read(4096)
    while inbytes:
        block = Extract.parse(inbytes)

        # change to new output file
        if block["a"] == 0xffff:
            if outfile:
                outfile.close()

            zd2 = None
            if block["data"][0:4] == b"ZDLF":
                suffix = ".ZD2"
                zd2 = short_ZD2.parse(block["data"])
            elif block["data"][0:3] == b">>>":
                suffix = ".ZT2"
            else:
                suffix = ""

            outname = (str(options.location + 6)+suffix)
            if options.zt2 and zd2:
                for check in ids:
                    if check[0] == zd2['id']:
                        outname = check[1]

            print("Writing: %s" % outname)
            outfile = open(outname, "wb")
            if not outfile:
                sys.exit("Unable to open FILE for writing")

        outfile.write(block["data"])

        # read next chunk
        inbytes = infile.read(4096)
        options.location = options.location + 4096

if __name__ == "__main__":
    main()

