
# ZD2 effects

The Zoom pedals are based around a TI TMS320C6000 (C6475 to be specific),
each of the effects contain a 'blob' of compiled code which can be loaded
into memory and this iteracts with pedals FW for UI control and processing
the audio from the Guitar/Bass (or previous effects in the 'chain').

The 'ZD2' file has several sections, once we have the file on disk we can 
extract each of these using the `decode_effect.py` script.

Note on copyright: The contents of the ZD2 file belongs to Zoom, we do NOT
provide these files. They can be download from a pedal that you own, or 
downloaded from Zoom's internet servers (which the GuitarLab software does).

```
$ python3 zoomzt2/decode_effect.py --help
usage: decode_effect [-h] [-d] [-s] [-n] [-v] [-m] [-7] [-b BITMAP] [-i INFO] [-c CODE] [-j]
                     [-x XML] [-t TEXT] [-D DONOR] [-B] [-T] [-I] [-C] [-X] [-F] [-E] [-V]
                     [--force-target FORCE_TARGET] [--force-id FORCE_ID]
                     [--force-name FORCE_NAME] [--force-gname FORCE_GNAME] [-o OUTPUT]
                     FILE

positional arguments:
  FILE                  File to process

options:
  -h, --help            show this help message and exit
  -d, --dump            dump configuration to text
  -s, --summary         summarized configuration in human readable form
  -n, --id              output the effect's numerical ID (in hex)
  -v, --version         output the effect's version
  -m, --md5sum          include md5sum of file in summary report
  -7, --7bit            include ID as 5x 7bit summary report
  -b BITMAP, --bitmap BITMAP
                        extract Icon/Bitmap to FILE
  -i INFO, --info INFO  extract Info to FILE
  -c CODE, --code CODE  extract Code to FILE

Language:
  Extract either English or Japanese segments

  -j, --japan           select Japanese version for export
  -x XML, --xml XML     extract XML to FILE
  -t TEXT, --text TEXT  extract Text to FILE

Donor:
  Take replacement sections from a donor ZD2

  -D DONOR, --donor DONOR
                        specify donor ZD2 FILE
  -B, --donor-bitmap    inject Icon/Bitmap from donor
  -T, --donor-text      inject Text from donor
  -I, --donor-info      inject Info from donor
  -C, --donor-code      inject Code from donor
  -X, --donor-xml       inject XML from donor
  -F, --donor-final     inject FinalBytes from donor
  -E, --donor-elf       replace Code with ELF file (ie whole file)

Modify:
  manipulate values specified in ZD2

  -V, --crc             validate CRC32 checksum
  --force-target FORCE_TARGET
                        Force target pedal (in Hex) - WARNING may be 'unsafe'
  --force-id FORCE_ID   Force the ID to a particular value (in Hex)
  --force-name FORCE_NAME
                        Force the Name to a particular string (max 11 chars)
  --force-gname FORCE_GNAME
                        Force the GroupName to a particular string (max 11 chars)
  -o OUTPUT, --output OUTPUT
                        output combined result to FILE

$ python3 zoomzt2/decode_effect.py -c LINESEL.ZD2.code LINESEL.ZD2 

$ ls -al LINE*
-rw-rw-r-- 1 simon simon 9049 Jun 13 13:06 LINESEL.ZD2
-rw-rw-r-- 1 simon simon 7743 Jun 13 13:07 LINESEL.ZD2.code
```

# TI Toolset

TI provides "Code Compiler Studio" which includes a compiler, linker and 
disassembler.... everything we need.

This is supported on Windows, Mac and Linux.

It can be downloaded from:
https://www.ti.com/tool/download/CCSTUDIO/12.8.1

# Reverse Engineering Process

In order to understand how an effect works, we will disassemble it so we can 
inspect the instructions. We can also recompile it, but we'll need to tweak the
'.asm' code in-order for it to build correctly.

In the simplest form the disassembler can be called with:
```
$ ~/ti/ccs1281/ccs/tools/compiler/ti-cgt-c6000_8.3.12/bin/dis6x --all --noaddr --realquiet --suppress LINESEL.ZD2.code
```

But for our purposes we have some scripts to help; The `do_it.sh` essentially
does the following, but with a few extra bits, for every `.code` file it can find...
```
$ readelf -r OUT_VP.ZD2.code > OUT_VP.reloc
$ ~/ti/ccs1281/ccs/tools/compiler/ti-cgt-c6000_8.3.12/bin/dis6x --all --noaddr --realquiet OUT_VP.ZD2.code | sed 's/\.fphead/;.fphead/' > temp.asm
$ python3 patch_asm.py -r OUT_VP.reloc temp.asm > OUT_VP.asm
```

The 'patch_asm.py' includes the information from the relocation table at the
appropriate place in the '.asm' code, allowing easier adjustment.

Once the '.asm' is copyied into the project, we need to:
1. Fix asm to reference relocs (comment is below affected line).
2. Fix any '$C$L1'/etc duplication (or maybe split into multiple files).
3. Comment out trailing NOPS at end of functions.
4. Correct any dwarf tags (sometimes glitches with multiple references to same bit of code).
5. Check project entry-point and exported symbols.
6. Build project.... :-)


As a short cut, I have provided a project and a 'diff' file of the changes
as required above, using this the proceedure is simplified to:
```
$ ./do_it.sh
processing all .code files
$ ls
diy_effect  do_it.sh  LINESEL.ZD2.code	LINESEL.ZD2.code.asm  LINESEL.ZD2.code.reloc  patch_asm.py  readme.md
$ cd diy_effect/
$ cp ../LINESEL.ZD2.code.asm LINESEL.asm
$ patch < LINESEL.diff
patching file LINESEL.asm
```
and the open the project in CCS and build. :-)

This can gives us a 100% duplicate compile, but it does depend on the effect.
'OUT_VP' is about as simple as one could be:
```
$ ~/ti/ccs1281/ccs/tools/compiler/ti-cgt-c6000_8.3.12/bin/dis6x --all OUT_VP.ZD2.code > temp.asm
$ ~/ti/ccs1281/ccs/tools/compiler/ti-cgt-c6000_8.3.12/bin/dis6x --all diy_effect/Debug/diy_effect.out > diy_effect.asm
$ meld temp.asm check2.asm
```

# Running DIY effects... Caution Will Robinson

Note: This project is NOT supported or authorized by Zoom, there is
a very large chance that DIY Effect will 'brick' your pedal.

I strongly advise the 'auto save' is disabled, so if a bad
effect is added to the current patch it will NOT be reloaded
if the pedal is rebooted.

If it's added perminately you may get the effect loaded everytime the
pedal is booted, and continuously crash the pedal...


Firstly the `.code` will need to be rewritten into a ZD2 contianer:
```
$ python3 zoomzt2/decode_effect.py --donor diy_effect/Debug/diy_effect.out --donor-elf -o LINESELm.ZD2 LINESEL.ZD2
Checksum Recalculated: 0x530e63a1
```

And then modified 'LINESELm.ZD2' can be uploaded to the pedal, and added to 
current patch via UI or midi.

Note: so far I have only uploaded the rebuilt 'LINESEL' effect, 
over time we should be able to rebuild others and/or modify them
to do new interesting stuff.
