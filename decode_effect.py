#!/usr/bin/python
#
# Script decode/encode 'ZPTC' patch files from Zoom F/W
# (c) Simon Wood, 13 May 2020
#

import zoomzt2

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

    parser.add_argument("-b", "--bitmap",
    help="extract icon bitmap to FILE", dest="bitmap")
    parser.add_argument("-j", "--japan",
        help="select Japanese version for export",
        action="store_true", dest="japan")
    parser.add_argument("-x", "--xml",
    help="extract XML to FILE", dest="xml")
    parser.add_argument("-t", "--text",
    help="extract Text to FILE", dest="text")
    parser.add_argument("-i", "--info",
    help="extract Info to FILE", dest="info")
    parser.add_argument("-c", "--code",
    help="extract Code to FILE", dest="code")

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

if __name__ == "__main__":
    main()

