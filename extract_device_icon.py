# Extract images embedded in the ELF/Code section of ZD2 file

from PIL import Image

def destripe(src, stripes=4, width=None, height=None):
    x, y = src.size
    h = int(y / stripes)

    if not width:
        width = int(y / stripes)
    if not height:
        height = int(8 * stripes)

    dest = Image.new('1', (width, height),"white")

    for s in range(stripes):
        try:
            copy = src.crop((0, s * h, 8, (s + 1) * h)).transpose(Image.ROTATE_90)
        except:
            copy = src.crop((0, s * h, 8, (s + 1) * h)).transpose(Image.Transpose.ROTATE_90)
        dest.paste(copy, (0, s * 8, h, (s + 1) * 8))

    return(dest)

#--------------------------------------------------
def main():
    from argparse import ArgumentParser
    from sys import exit
    from re import match
    import zoomzt2

    # from https://github.com/sashs/filebytes
    from filebytes.elf import ELF

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
        default = "_*picTotalDisplay_.*", dest="target",
        help="regex to describe target icon (_*picTotalDisplay_.*)")
    parser.add_argument("-S", "--skip",
        default = 0, type=int,
        help="skip a number of targets when found", dest="skip")
    parser.add_argument("-s", "--stripes",
        default = 4, type=int,
        help="number of 'stripes' in image", dest="stripes")

    parser.add_argument("-r", "--raw",
        help="saw as raw bytes",
        action="store_true", dest="raw")
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
            exit("Unable to open FILE for reading")
        else:
            data = infile.read()
        infile.close()

        config = zoomzt2.ZD2.parse(data)
        e = ELF("fake-elf", config["DATA"]["data"])

    if not e:
        exit("Error in reading ELF file")

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
                if match(options.target, z.name):
                    print("Target matched:", z.name)
                    if options.skip:
                        options.skip -= 1
                    elif z.header.st_size:
                        a = z.header.st_value
                        l = z.header.st_size
                        break

    if not l:
        exit("Target not found: " + options.target)

    for s in e.segments:
        if a >= s.vaddr and a < (s.vaddr + len(s.bytes)): 
            print("Symbol located:", hex(a))
            rawData = bytes(s.bytes[a - s.vaddr : a - s.vaddr + l])
            break

    if rawData:
        if options.raw:
            if options.output:
                output = open(options.output, "wb")
            else:
                output = open("raw.bin", "wb")
            output.write(rawData)
            output.close()
        else:
            imgSize = (8, len(rawData))
            img = Image.frombytes('1', imgSize, rawData, 'raw', '1;I')

            img2 = destripe(img, options.stripes)

            if options.output:
                img2.save(options.output)
            else:
                img2.save("icon.png")

if __name__ == "__main__":
    main()

