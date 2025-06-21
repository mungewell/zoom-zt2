import re
from argparse import ArgumentParser

parser = ArgumentParser(prog="patch_asm")

parser.add_argument('files', metavar='FILE', nargs=1,
    help='File to process')
parser.add_argument("-s", "--sect",
    default = 1, type=int,
    help="add dwarf tags after section SECT", dest="sect")

parser.add_argument("-r", "--reloc",
    help="merge in reloc statements from file RELOC", dest="reloc")

options = parser.parse_args()

c = 0
d = 0
e = 0
f = open(options.files[0], "r")

if options.reloc:
    g = open(options.reloc, "r")
    r = g.readline()
    r = g.readline()
    r = g.readline()
    r = g.readline()

print("	.compiler_opts --abi=eabi --array_alignment=8 --c64p_l1d_workaround=off --diag_wrap=off --endian=little --hll_source=on --long_precision_bits=32 --mem_model:code=near --mem_model:const=data --mem_model:data=far_aggregates --object_format=elf --silicon_version=6740")
print()

l = f.readline()
while l:
    if options.reloc:
        if re.match(re.compile(r"^\s+\.sect*"), l):
            # special case as '.sect' does not align with addresses
            a = "        "
        else:
            a = l[0:8]
            l = l[20:]

        # print reloc as comment (not after header if it exist)
        if not re.match(re.compile(r".+:$"), l):
            if a == r[0:8]:
                l = l + "\t; " + r
                r = g.readline()

    # count sections
    if re.match(re.compile(r"^\s+\.sect*"), l):
        d += 1

    if re.match(re.compile(r".+:$"), l):
        if re.match(re.compile(r"^[$]{1,}"), l):
            #if re.match(re.compile(r"^[$]+.*L[0123456789]{1,}:$"), l):
            print(";%s_%d:" % (l[:-2], e))
        else:
            e += 1
            if c:
                print("	.dwendtag $C$DW$%d" % c)

            print()
            print("	.def %s" % l[0:-2])

            if d == 1:
                print("	.align 32")

            if d > options.sect:
                c = c + 1

                print("$C$DW$%d	.dwtag  DW_TAG_subprogram" % c)
                print("	.dwattr $C$DW$%d, DW_AT_name(\"%s\")" % (c, l[0:-2]))
                print("	.dwattr $C$DW$%d, DW_AT_low_pc(%s)" % (c, l[0:-2]))
                print("	.dwattr $C$DW$%d, DW_AT_high_pc(0x00)" % c)

    print(l.replace(".fphead", ";.fphead"), end="")
    l = f.readline()

if c:
    print("	.dwendtag $C$DW$%d" % c)

