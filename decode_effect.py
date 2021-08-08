#!/usr/bin/python
#
# Script decode/encode 'ZPTC' patch files from Zoom F/W
# (c) Simon Wood, 13 May 2020
#

import zoomzt2

#--------------------------------------------------
def main():
    from optparse import OptionParser

    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")
    parser.add_option("-s", "--summary",
        help="summarized configuration in human readable form",
    action="store_true", dest="summary")

    parser.add_option("-b", "--bitmap",
    help="extract icon bitmap to FILE", dest="bitmap")

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
        config = zoomzt2.ZD2.parse(data)
        print(config)

    if options.summary and data:
        config = zoomzt2.ZD2.parse(data)

        print("0x%8.8x : %s (v%s), %s" % (config['id'], config['name'], config['version'], args[0]))

    if data and options.bitmap:
       outfile = open(options.bitmap, "wb")
       if not outfile:
           sys.exit("Unable to open FILE for writing")

       config = zoomzt2.ZD2.parse(data)
       outfile.write(config["ICON"]["data"])
       outfile.close()

if __name__ == "__main__":
    main()

