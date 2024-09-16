# Convert ZIC files to (potentially) multiple PNG

from PIL import Image
from construct import *

#--------------------------------------------------
# Define ZIC file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

ZIC_Icon = Struct(
    "width" / Int16ul,
    "height" / Int16ul,
    "invert" / Peek(Int16ul),           # only last in array is valid

    Check(this.width != 0),
    Check(this.height != 0),

    "stripes" / Computed(((this.height - 1) >> 3) + 1),
    "bytes" / Computed(this.width * this.stripes),
)

ZIC_Data = Struct(
    "data" / Bytes(lambda this: this._.icons[this._index].bytes),
)

ZIC = Struct(
    Const(b"ZBMP"),
    "length" / Int32ul,
    "icons" / Padded(this.length, GreedyRange(ZIC_Icon)),

    "datas" / Array(lambda this: len(this.icons), ZIC_Data),
)


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
    from optparse import OptionParser
    import sys

    usage = "usage: %prog [options] FILENAME"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")

    parser.add_option("-p", "--prefix",
        help="Use 'prefix' for PNG output files",
        default="icon", dest="prefix")

    (options, args) = parser.parse_args()

    data = None
    zic = None

    if len(args) != 1:
        sys.exit("ZIC file not specified")
    else:
        print("Converting:", args[0])
        infile = open(args[0], "rb")
        if not infile:
            sys.exit("Unable to open FILE for reading")

        data = infile.read()
        infile.close()

    zic = ZIC.parse(data)
    if options.dump:
        print(zic)

    if zic:
        for i in range(len(zic.icons)):
            imgSize = (8, zic.icons[i].bytes)
            img = Image.frombytes('1', imgSize, zic.datas[i].data, 'raw', '1;I')

            img2 = destripe(img, zic.icons[i].stripes)
            img3 = img2.crop([0, 0, zic.icons[i].width, zic.icons[i].height])

            outfile = options.prefix + "_"+str(i)+".png"
            print("Writing:", outfile)
            img3.save(outfile)


if __name__ == "__main__":
    main()
