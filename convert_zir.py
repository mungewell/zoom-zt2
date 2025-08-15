# Convert ZIR files between known formats

from PIL import Image, ImageOps
from construct import *

#--------------------------------------------------
# For wav file output (optional)
# https://github.com/WarrenWeckesser/wavio

try:
   import wavio
   _hasWavIO = True
except ImportError:
   _hasWavIO = False
'''
_hasWavIO = False
'''

#--------------------------------------------------
# Define ZIR file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

ZIR_1U = Struct(
    "type" / Computed("1U"),

    "low" / Array(512, Float32l),
    "mid" / Array(512, Float32l),
    "high" / Array(512, Float32l),
)

ZIR_ST = Struct(
    "type" / Computed("ST"),

    "left" / Array(768, Float32l),
    "right" / Array(768, Float32l),
)

ZIR_LT = Padded(12288, 
    Struct(
    "type" / Computed("LT"),

    "low" / Array(256, Float32l),
    "mid" / Array(256, Float32l),
    "high" / Array(256, Float32l),
))

ZIR_IR = Struct(
    "type" / Computed("IR"),

    "low" / Array(1024, Float32l),
    "mid" / Array(1024, Float32l),
    "high" / Array(1024, Float32l),
)

#--------------------------------------------------

def downscale_1x5(a):               # 768 -> 512
    o = []
    for i in range(0, len(a), 3):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        try:
            m = a[i+2]
        except:
            m = 0
        o.append((c+c+n)/3)
        o.append((n+m+m)/3)
    return o

def downscale_2x(a):                # 512 -> 256, or 1024 -> 512
    o = []
    for i in range(0, len(a), 2):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        o.append((c+n)/2)
    return o

def downscale_3x(a):                # 768 -> 256
    o = []
    for i in range(0, len(a), 3):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        try:
            m = a[i+2]
        except:
            m = 0
        o.append((c+n+m)/3)
    return o

def downscale_4x(a):                # 1024 -> 256
    o = []
    for i in range(0, len(a), 4):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        try:
            m = a[i+2]
        except:
            m = 0
        try:
            l = a[i+3]
        except:
            l = 0
        o.append((c+n+m+l)/4)
    return o

def upscale_1x5(a):                 # 512 -> 768
    o = []
    for i in range(0, len(a), 2):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        try:
            m = a[i+2]
        except:
            m = 0
        o.append(c)
        o.append((c+n+n)/3)
        o.append((n+n+m)/3)
    return o

def upscale_2x(a):                  # 256 -> 512, or 512 -> 1024
    o = []
    for i in range(len(a)):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        o.append(c)
        o.append((c+n)/2)
    return o

def upscale_3x(a):                  # 256 -> 768
    o = []
    for i in range(len(a)):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        o.append(c)
        o.append((c+c+n)/3)
        o.append((c+n+n)/3)
    return o

def upscale_4x(a):                  # 256 -> 1024
    o = []
    for i in range(len(a)):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        o.append(c)
        o.append((c+c+c+n)/4)
        o.append((c+c+n+n)/4)
        o.append((c+n+n+n)/4)
    return o

#--------------------------------------------------

def main():
    import os
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="convert-zir")
    parser.add_argument('files', metavar='FILE', nargs='+',
        help='File(s) to process')

    parser.add_argument("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")

    tpx = parser.add_mutually_exclusive_group()
    tpx.add_argument("-1", "--1U",
        help="ZIR Type 1 '_1U' = 6144 bytes, low/mid/high",
        action="store_true", dest="type_1u")
    tpx.add_argument("-2", "--ST",
        help="ZIR Type 2 '_ST' = 6144 bytes, left/right",
        action="store_true", dest="type_st")
    tpx.add_argument("-3", "--LT",
        help="ZIR Type 3 '_LT' = 12288 bytes, low/mid/high",
        action="store_true", dest="type_lt")
    tpx.add_argument("-4", "--IR",
        help="ZIR Type 4 '_IR' = 12288 bytes, low/mid/high",
        action="store_true", dest="type_ir")

    opx = parser.add_mutually_exclusive_group()
    opx.add_argument("-O", "--writeback",
        help="write output back to same file",
        action="store_true", dest="writeback")
    opx.add_argument("-o", "--output",
        help="write output to FILE",
        dest="output")

    if _hasWavIO:
        parser.add_argument("-w", "--wav",
            help="write spectrum to a wav file, for easy inspection",
            dest="wav")
        parser.add_argument("-s", "--scale",
            help="wav file scale, set '0.0' for auto-scale",
            type=float, default=1.0, dest="scale")
        parser.add_argument("-S", "--source",
            help="wav file source, 'low/mid/high' or 'left/right' for '_ST.ZIR'",
            dest="source")

    options = parser.parse_args()

    zir = None
    data = None
    guess = False

    if not len(options.files):
        parser.error("FILE not specified")
    else:
        print("Inspecting:", options.files[0])
        infile = open(options.files[0], "rb")
        if not infile:
            sys.exit("Unable to open FILE for reading")

        data = infile.read()
        infile.close()

        #print("length:", len(data))

    if options.output or options.writeback:
        # type specifies wanted output, so we guess at input type
        guess = True

    if not guess:
        if options.type_1u:
            zir = ZIR_1U.parse(data)
        elif options.type_st:
            zir = ZIR_ST.parse(data)
        elif options.type_lt:
            zir = ZIR_LT.parse(data)
        elif options.type_ir:
            zir = ZIR_IR.parse(data)
        else:
            guess = True

    if guess:
        filename, extension = os.path.splitext(options.files[0])
        if filename[-2:] == "ST":
            print("Guessing 'ST'")
            zir = ZIR_ST.parse(data)
        elif filename[-2:] == "1U":
            print("Guessing '1U'")
            zir = ZIR_1U.parse(data)
        elif filename[-2:] == "LT":
            print("Guessing 'LT'")
            zir = ZIR_LT.parse(data)
        elif filename[-2:] == "IR":
            print("Guessing 'IR'")
            zir = ZIR_IR.parse(data)
        elif filename[-2:] == "88":     # B2 Four
            print("Guessing '88/IR'")
            zir = ZIR_IR.parse(data)

        if not zir:
            sys.exit("unable to guess....")


    if options.dump:
        print(zir)


    if options.output or options.writeback:
        # up/down-sample data to change type
        if zir['type'] == "1U":         # 512
            if options.type_st:         #       -> 768
                zir['left'] = upscale_1x5(zir['mid'])
                zir['right'] = upscale_1x5(zir['mid'])
                zir['type'] = "ST"
            elif options.type_lt:         #       -> 256
                zir['low'] = downscale_2x(zir['low'])
                zir['mid'] = downscale_2x(zir['mid'])
                zir['high'] = downscale_2x(zir['high'])
                zir['type'] = "LT"
            elif options.type_ir:         #       -> 1024
                zir['low'] = upscale_2x(zir['low'])
                zir['mid'] = upscale_2x(zir['mid'])
                zir['high'] = upscale_2x(zir['high'])
                zir['type'] = "IR"
            else:
                sys.exit("Conversion not supported yet")

        if zir['type'] == "ST":         # 768
            if options.type_1u:         #       -> 512
                zir['low'] = downscale_1x5(zir['left'])
                zir['mid'] = downscale_1x5(zir['left'])
                zir['high'] = downscale_1x5(zir['left'])
                zir['type'] = "1U"
            elif options.type_lt:         #       -> 256
                zir['low'] = downscale_3x(zir['left'])
                zir['mid'] = downscale_3x(zir['left'])
                zir['high'] = downscale_3x(zir['left'])
                zir['type'] = "LT"
            else:
                sys.exit("Conversion not supported yet")

        if zir['type'] == "LT":         # 256
            if options.type_1u:         #       -> 512
                zir['low'] = upscale_2x(zir['low'])
                zir['mid'] = upscale_2x(zir['mid'])
                zir['high'] = upscale_2x(zir['high'])
                zir['type'] = "1U"
            elif options.type_st:         #       -> 768
                zir['left'] = upscale_3x(zir['mid'])
                zir['right'] = upscale_3x(zir['mid'])
                zir['type'] = "ST"
            elif options.type_ir:         #       -> 1024
                zir['low'] = upscale_4x(zir['low'])
                zir['mid'] = upscale_4x(zir['mid'])
                zir['high'] = upscale_4x(zir['high'])
                zir['type'] = "IR"
            else:
                sys.exit("Conversion not supported yet")

        if zir['type'] == "IR":         # 1024
            if options.type_1u:         #       -> 512
                zir['low'] = downscale_2x(zir['low'])
                zir['mid'] = downscale_2x(zir['mid'])
                zir['high'] = downscale_2x(zir['high'])
                zir['type'] = "1U"
            elif options.type_lt:         #       -> 256
                zir['low'] = downscale_4x(zir['low'])
                zir['mid'] = downscale_4x(zir['mid'])
                zir['high'] = downscale_4x(zir['high'])
                zir['type'] = "LT"
            else:
                sys.exit("Conversion not supported yet")

        if options.writeback:
            outfile = open(options.files[0], "wb")
            if not outfile:
               sys.exit("Unable to open FILE for writing")
        if options.output:
            outfile = open(options.output, "wb")
            if not outfile:
               sys.exit("Unable to open FILE for writing")

        if zir['type'] == "1U":
            data = ZIR_1U.build(zir)
        elif zir['type'] == "ST":
            data = ZIR_ST.build(zir)
        elif zir['type'] == "LT":
            data = ZIR_LT.build(zir)
        elif zir['type'] == "IR":
            data = ZIR_IR.build(zir)

        outfile.write(data)
        outfile.close()


    if _hasWavIO:
        if options.wav:
            if options.scale == 0:
                options.scale = "auto"

            if options.source:
                source = options.source
            elif zir['type'] == "ST":
                source = 'left'
            else:
                source = 'mid'

            wavio.write(options.wav, zir[source], 44100, sampwidth=3, scale=options.scale)

if __name__ == "__main__":
    main()
