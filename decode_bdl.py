#!/usr/bin/python
#
# Script decode/re-encode 'BDL' files from Zoom F/W
# (c) Simon Wood, 16 Dec 2023
#

import zoomzt2
import hashlib
import crcmod
from argparse import ArgumentParser
from sys import exit
from re import match

# requires https://github.com/sashs/filebytes
from filebytes.elf import ELF

# requires https://github.com/construct/construct
from construct import *

TBL = Struct(
        "Values" / GreedyRange(Float32l),
)

tables = ["LoFreqTBL", "LoGainTBL", "LoQTBL",
          "MidFreqTBL", "MidGainTBL", "MidQTBL",
          "HiFreqTBL", "HiGainTBL", "HiQTBL"]

# Values from 'B_OUT_EQ.BDL', uncomment/change the ones you want to update

#LoFreqTBL =  [20, 20, 20, 20, 20, 100, 100, 100, 100, 100, 100]
#LoGainTBL =  [-25, -20, -15, -10, -5, 0, 1.60000002384186, 3.20000004768372, 4.80000019073486, 6.40000009536743, 8]
#LoQTBL =     [1.5, 1.25, 0.800000011920929, 0.699999988079071, 0.699999988079071, 0.699999988079071, 1, 1.25, 1.5, 1.75, 2]
#MidFreqTBL = [1000, 1000, 1000, 1000, 1000, 300, 300, 300, 300, 300, 300]
#MidGainTBL = [-20, -17.5, -15, -10, -5, 0, 2, 4, 6, 8, 10]
#MidQTBL =    [4, 4, 4, 4, 2, 1, 1.5, 2, 2.5, 2.75, 3]
#HiFreqTBL =  [4000, 4000, 4000, 4000, 4000, 3000, 3000, 3000, 3000, 3000, 3000]
#HiGainTBL =  [-20, -15, -10, -5, -2.5, 0, 3.5, 7, 10.5, 14, 17.5]
#HiQTBL =     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

#--------------------------------------------------
def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="decode_bdl")
    parser.add_argument('files', metavar='FILE', nargs=1,
        help='File to process')

    parser.add_argument("-o", "--output",
        help="output adjusted BDL to FILE", dest="output")

    parser.add_argument("-l", "--list",
        help="list available symbols",
        action="store_true", dest="list")

    options = parser.parse_args()

    if not len(options.files):
        parser.error("FILE not specified")

    # Read data from BDL file
    infile = open(options.files[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        data = infile.read()
    infile.close()

    if data:
        config = zoomzt2.ZD2.parse(data)
        e = ELF("fake-elf", config["DATA"]["data"])

        if not e:
            exit("Error in extracting CODE/ELF blob")

        for table in tables:
            a = None
            l = None
            rawData = None

            for s in e.sections:
                if s.name == '.symtab':
                    if options.list:
                        for z in s.symbols:
                            print(z.name)
                        quit()

                    for z in s.symbols:
                        if match(table, z.name):
                            if z.header.st_size:
                                a = z.header.st_value
                                l = z.header.st_size
                                break

            if not l:
                print("Table not found: " + table)
            else:
                for s in e.segments:
                    if a >= s.vaddr and a < (s.vaddr + len(s.bytes)): 
                        print("Table located:", table, hex(a))
                        rawData = bytes(s.bytes[a - s.vaddr : a - s.vaddr + l])
                        values = TBL.parse(rawData)
                        print(values['Values'])

                        # Update values as previously specified 
                        if table in globals() and options.output:
                            print("Updating:", eval(table))
                            values['Values'] = eval(table)
                            newData = TBL.build(values)

                            if len(newData) <= len(rawData):
                                c = 0
                                for byte in newData:
                                    s.raw[a - s.vaddr + c] = byte
                                    c += 1

                        break


        if options.output:
            outfile = open(options.output, "wb")
            if not outfile:
                exit("Unable to open output FILE for writing")

            # rewrite the processed ELF into the CODE section
            config["DATA"]["data"] = bytes(e._bytes)
            data = zoomzt2.ZD2.build(config)
          
            # recalc the CRC32
            crc32 = crcmod.Crc(0x104c11db7, rev=True, initCrc=0x00000000, xorOut=0xFFFFFFFF)
            crc32.update(data[12:-16])
          
            config['checksum'] = crc32.crcValue ^ 0xffffffff
            print("Checksum Recalculated: 0x%8.8x" % config['checksum'])
            data = zoomzt2.ZD2.build(config)
          
            outfile.write(data)
            outfile.close()

if __name__ == "__main__":
    main()
