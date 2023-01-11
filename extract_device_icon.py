# Extract images embedded in the ELF/Code section of ZD2 file

from PIL import Image
from argparse import ArgumentParser
from sys import exit
import zoomzt2
from pwn import *
import re

def destripe(src, stripes=4, width=None, height=None):
    x, y = src.size
    h = int(y / stripes)

    if not width:
        width = int(y / stripes)
    if not height:
        height = int(8 * stripes)

    dest = Image.new('1', (width, height),"white")

    for s in range(stripes):
        copy = src.crop((0, s * h, 8, (s + 1) * h)).transpose(Image.ROTATE_90)
        dest.paste(copy, (0, s * 8, h, (s + 1) * 8))

    return(dest)

#--------------------------------------------------
def main():
    parser = ArgumentParser(prog="extract_device_icon")

    parser.add_argument('files', metavar='FILE', nargs=1,
        help='File to process')
    parser.add_argument("-e", "--elf",
        help="read elf directly, rather than ZD2",
        action="store_true", dest="elf")

    parser.add_argument("-l", "--list",
        help="list available symbols",
        action="store_true", dest="list")
    parser.add_argument("-t", "--target",
        default = "_*picTotalDisplay_.*",
        help="regex to describe target icon", dest="target")
    parser.add_argument("-s", "--stripes",
        default = 4,
        help="number of 'stripes' in image", dest="stripes")

    parser.add_argument("-o", "--output",
        help="output image to FILE", dest="output")

    options = parser.parse_args()

    e = None
    if options.elf:
        # Read ELF file directly from disk
        e = ELF(options.files[0])
    else:
        # Read data from 'code' section of ZD2 file
        infile = open(options.files[0], "rb")
        if not infile:
            sys.exit("Unable to open FILE for reading")
        else:
            data = infile.read()
        infile.close()

        config = zoomzt2.ZD2.parse(data)
        e = ELF.__something__(config["DATA"]["data"])

    if not e:
        sys.exit("Error in reading ELF file")

    keys = e.symbols.keys()
    if options.list:
        print(keys)
    r = re.compile(options.target)
    found  = list(filter(r.match, keys))

    if not len(found):
        sys.exit("Target not found:" + options.target)

    print("Extracting symbol:", found[0])
    sort = sorted(e.symbols.items(), key=lambda x: x[1])

    # iterate through looking for start and end address
    start = e.symbols[found[0]]
    end = False
    found = False
    for (a,b) in sort:
        if found:
            if b != start:
                end = b
                break
        else:
            if b == start:
                found = True
                
    if end:
        print("From Address: 0x%8.8X to 0x%8.8X" % (start, end))
        rawData = e.read(start, end - start)

        imgSize = (8, len(rawData))
        img = Image.frombytes('1', imgSize, rawData, 'raw', '1;I')

        img2 = destripe(img, int(options.stripes))

        if options.output:
            img2.save(options.output)
        else:
            img2.save("icon.png")

if __name__ == "__main__":
    main()

