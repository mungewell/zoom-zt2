#!/usr/bin/python
#
# Script decode/encode 'ZPTC' patch files from Zoom F/W
# (c) Simon Wood, 13 May 2020
#

import zoomzt2
import hashlib
import crcmod
import os
from sys import exit

#--------------------------------------------------
def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="decode_effect")
    parser.add_argument('files', metavar='FILE', nargs=1,
        help='File to process')

    parser.add_argument("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")
    parser.add_argument("-s", "--summary",
        help="summarized configuration in human readable form",
        action="store_true", dest="summary")
    parser.add_argument("-n", "--id",
        help="output the effect's numerical ID (in hex)",
        action="store_true", dest="id")
    parser.add_argument("-v", "--version",
        help="output the effect's version",
        action="store_true", dest="version")
    parser.add_argument("-m", "--md5sum",
        help="include md5sum of file in summary report",
        action="store_true", dest="md5sum")

    parser.add_argument("-b", "--bitmap",
        help="extract Icon/Bitmap to FILE", dest="bitmap")
    parser.add_argument("-i", "--info",
        help="extract Info to FILE", dest="info")
    parser.add_argument("-c", "--code",
        help="extract Code to FILE", dest="code")

    language = parser.add_argument_group("Language",
        "Extract either English or Japanese segments")
    language.add_argument("-j", "--japan",
        help="select Japanese version for export",
        action="store_true", dest="japan")
    language.add_argument("-x", "--xml",
        help="extract XML to FILE", dest="xml")
    language.add_argument("-t", "--text",
        help="extract Text to FILE", dest="text")

    donor = parser.add_argument_group("Donor",
        "Take replacement sections from a donor ZD2")
    donor.add_argument("-D", "--donor",
        help="specify donor ZD2 FILE", dest="donor")
    donor.add_argument("-B", "--donor-bitmap",
        help="inject Icon/Bitmap from donor",
        action="store_true", dest="dbitmap")
    donor.add_argument("-T", "--donor-text",
        help="inject Text from donor",
        action="store_true", dest="dtext")
    donor.add_argument("-I", "--donor-info",
        help="inject Info from donor",
        action="store_true", dest="dinfo")
    donor.add_argument("-C", "--donor-code",
        help="inject Code from donor",
        action="store_true", dest="dcode")
    donor.add_argument("-X", "--donor-xml",
        help="inject XML from donor",
        action="store_true", dest="dxml")
    donor.add_argument("-F", "--donor-final",
        help="inject FinalBytes from donor",
        action="store_true", dest="dfinal")
    donor.add_argument("-E", "--donor-elf",
        help="replace Code with ELF file (ie whole file)",
        action="store_true", dest="delf")

    donor.add_argument("-V", "--crc",
        help="validate CRC32 checksum",
        action="store_true", dest="crc")
    donor.add_argument("--force-id",
        help="Force the ID to a particular value (in Hex)",
        dest="force_id")

    donor.add_argument("-o", "--output",
        help="output combined result to FILE", dest="output")

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

    if options.crc and data:
        config = zoomzt2.ZD2.parse(data)

        crc32 = crcmod.Crc(0x104c11db7, rev=True, initCrc=0x00000000, xorOut=0xFFFFFFFF)
        crc32.update(data[12:-16])

        print(config['hex1'])
        if (config['checksum'] == crc32.crcValue ^ 0xffffffff):
            print("Checksum Validated: 0x%8.8x" % config['checksum'])
        else:
            exit("Checksum Invalid: 0x%8.8x, should be 0x%8.8x" % \
                    (config['checksum'], crc32.crcValue ^ 0xffffffff))

    if options.dump and data:
        config = zoomzt2.ZD2.parse(data)
        print(config)

    if options.summary and data:
        config = zoomzt2.ZD2.parse(data)

        if options.md5sum:
            md5sum = hashlib.md5(data).hexdigest()
            print("0x%8.8x : %s, %s (v%s %2.2f%%), %s" % (config['id'], \
                    os.path.split(options.files[0])[-1], \
                    config['name'], config['version'], config['INFO']['dspload']/2.5, \
                    md5sum))
        else:
            print("0x%8.8x : %s, %s (v%s %2.2f%%)" % (config['id'], \
                    os.path.split(options.files[0])[-1], \
                    config['name'], config['version'], config['INFO']['dspload']/2.5))

    if options.id and data:
        config = zoomzt2.ZD2.parse(data)
        print("0x%8.8x" % (config['id']))

    if options.version and data:
        config = zoomzt2.ZD2.parse(data)
        print("%s" % (config['version']))

    if data and options.bitmap:
       outfile = open(options.bitmap, "wb")
       if not outfile:
           exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       outfile.write(config["ICON"]["data"])
       outfile.close()

    if data and options.xml:
       outfile = open(options.xml, "wb")
       if not outfile:
           exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       if options.japan:
           outfile.write(config["PRMJ"]["data"])
       else:
           outfile.write(bytes(config["PRME"]["xml"], encoding="ascii"))
       outfile.close()

    if data and options.text:
       outfile = open(options.text, "wb")
       if not outfile:
           exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       if options.japan:
           outfile.write(config["TXJ1"]["data"])
       else:
           outfile.write(bytes(config["TXE1"]["description"], encoding="ascii"))
       outfile.close()

    if data and options.info:
       outfile = open(options.info, "wb")
       if not outfile:
           exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       outfile.write(config["INFO"]["data"])
       outfile.close()

    if data and options.code:
       outfile = open(options.code, "wb")
       if not outfile:
           exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       outfile.write(config["DATA"]["data"])
       outfile.close()

    if data and options.output:
       outfile = open(options.output, "wb")
       if not outfile:
           exit("Unable to open output FILE for writing")
       config = zoomzt2.ZD2.parse(data)

       if options.donor:
           infile = open(options.donor, "rb")
           if not infile:
               exit("Unable to open donor FILE for reading")
           else:
               ddata = infile.read()
           infile.close()

           if options.delf:
               config["DATA"]["length"] = len(ddata)
               config["DATA"]["data"] = ddata
           else:
                dconfig = zoomzt2.ZD2.parse(ddata)
                if options.dbitmap:
                    config["ICON"] = dconfig["ICON"]
                if options.dtext:
                    config["TXJ1"] = dconfig["TXJ1"]
                    config["TXE1"] = dconfig["TXE1"]
                if options.dinfo:
                    config["INFO"] = dconfig["INFO"]
                if options.dcode:
                    config["DATA"] = dconfig["DATA"]
                if options.dxml:
                    config["PRMJ"] = dconfig["PRMJ"]
                    config["PRME"] = dconfig["PRME"]
                if options.dfinal:
                    config["unknown5"] = dconfig["unknown5"]

       if options.force_id:
           config['id'] = int(options.force_id, 16)

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

