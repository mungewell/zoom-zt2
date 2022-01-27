#!/usr/bin/python
#
# Script decode/encode 'ZPTC' patch files from Zoom F/W
# (c) Simon Wood, 13 May 2020
#

import zoomzt2
import hashlib

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
        help="extract Icon/Bitmap from donor",
        action="store_true", dest="dbitmap")
    donor.add_argument("-T", "--donor-text",
        help="extract Text from donor",
        action="store_true", dest="dtext")
    donor.add_argument("-I", "--donor-info",
        help="extract Info from donor",
        action="store_true", dest="dinfo")
    donor.add_argument("-C", "--donor-code",
        help="extract Code from donor",
        action="store_true", dest="dcode")
    donor.add_argument("-X", "--donor-xml",
        help="extract XML from donor",
        action="store_true", dest="dxml")

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

    if options.dump and data:
        config = zoomzt2.ZD2.parse(data)
        print(config)

    if options.summary and data:
        config = zoomzt2.ZD2.parse(data)

        if options.md5sum:
            md5sum = hashlib.md5(data).hexdigest()
            print("0x%8.8x : %s (v%s), 0x%s, %s" % (config['id'], config['name'], config['version'], md5sum, options.files[0]))
        else:
            print("0x%8.8x : %s (v%s), %s" % (config['id'], config['name'], config['version'], options.files[0]))

    if data and options.bitmap:
       outfile = open(options.bitmap, "wb")
       if not outfile:
           sys.exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       outfile.write(config["ICON"]["data"])
       outfile.close()

    if data and options.xml:
       outfile = open(options.xml, "wb")
       if not outfile:
           sys.exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       if options.japan:
           outfile.write(config["PRMJ"]["data"])
       else:
           outfile.write(bytes(config["PRME"]["xml"], encoding="ascii"))
       outfile.close()

    if data and options.text:
       outfile = open(options.text, "wb")
       if not outfile:
           sys.exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       if options.japan:
           outfile.write(config["TXJ1"]["data"])
       else:
           outfile.write(bytes(config["TXE1"]["description"], encoding="ascii"))
       outfile.close()

    if data and options.info:
       outfile = open(options.info, "wb")
       if not outfile:
           sys.exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       outfile.write(config["INFO"]["data"])
       outfile.close()

    if data and options.code:
       outfile = open(options.code, "wb")
       if not outfile:
           sys.exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       outfile.write(config["DATA"]["data"])
       outfile.close()

    if data and options.output:
       outfile = open(options.output, "wb")
       if not outfile:
           sys.exit("Unable to open output FILE for writing")
       config = zoomzt2.ZD2.parse(data)

       if options.donor:
           infile = open(options.donor, "rb")
           if not infile:
               sys.exit("Unable to open donor FILE for reading")
           else:
               ddata = infile.read()
           infile.close()

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

       data = zoomzt2.ZD2.build(config)
       outfile.write(data)
       outfile.close()

if __name__ == "__main__":
    main()

