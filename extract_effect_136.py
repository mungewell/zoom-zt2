#!/usr/bin/python
#
# Script to extract ZD2 effects from unzipped exe's 136 file
# (c) Simon Wood, 6 Nov 2021
#

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

#--------------------------------------------------
def main():
    from optparse import OptionParser
    location = 0xf000

    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)

    parser.add_option("-s", "--start",
        help="start location of ZDLF's",
        type=int, default=0xf000, dest="location")

    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("FILE not specified")

    infile = open(args[0], "rb")
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

            print(block["data"][0:4])
            if block["data"][0:4] == b"ZDLF":
                suffix = ".ZD2"
            elif block["data"][0:3] == b">>>":
                suffix = ".ZT2"
            else:
                suffix = ""
            print(suffix)

            print("Opening: %s" % (str(options.location + 6)+suffix))
            outfile = open(str(options.location + 6)+suffix, "wb")
            if not outfile:
                sys.exit("Unable to open FILE for writing")

        print("Writing: %d bytes" % block["length"])
        outfile.write(block["data"])

        # read next chunk
        inbytes = infile.read(4096)
        options.location = options.location + 4096

if __name__ == "__main__":
    main()

