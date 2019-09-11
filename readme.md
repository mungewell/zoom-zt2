
This repo contains a Python script and associated files for uploading effects to 
the ZOOM G Series pedals (G1Four and possibly others).

Inspired by another project, which allows for the re-packing of effects into the
ZOOM F/W Installer binary. Unfortunately that technique proved unsuccessful on the 
G1Four.
https://github.com/Barsik-Barbosik/Zoom-Firmware-Editor

The script has been tested with G1Four, it is expected/hoped that it will also 
work on the G1XFour, B1Four, B1XFour, G3n, G3Xn, B3n and G5n.

This project is not supported/authorized by ZOOM, use at your own risk.

## Operation.

The 'zoom-zt2.py' script uses MIDI SysEx to control the pedal, and functions
on Linux and Windows. A pre-built Windows binary is provided in releases for
convience for those who down have/want Python install.

In order to install a new effect, the binary for the effect must first be located - 
which can be extracted from the F/W Installer binary via 'Zoom-Firmware-Editor'.

Download current state of FLST_SEQ ("-R -w") from the pedal, then add new effect to 
it ("-A") and re-uploaded it & the new binary blob ("-S" & "-I").

```
$ python3 zoom-zt2.py -R -w try_glamcomp.zt2
$ python3 zoom-zt2.py -A 1 -n "GLAMCOMP.ZD2" -v "1.10" -i 112 -u 128 -w try_glamcomp.zt2
Group 1:
    GLAMCOMP.ZD2
Add:GLAMCOMP.ZD2
$ python3 zoom-zt2.py -I "GLAMCOMP.ZD2" -S try_glamcomp.zt2
```

And it's installed... :-)

## Effects

The effects used by the G1Four are '.ZD2' format, these are also used on the G3n and G5n 
pedals. They are not compatible with the '.ZDL' effects used on the 'MultiStomp' pedals.

Mostly effect binaries are common between the G1Four and the G3n/G5n, although it would appear 
that some effects are imcompatible due to hardware differences - these appear to be denoted with
'1U' (only one screen on G1Four) and '3S' suffixes on the filenames.

The is also a 'GUARDZDL.ZT2' file within the F/W which blacklists some effects from the
G3/G5.

The AC-2 and AC-3 use a similar '.ZD2' effects, but they do not have a LCD display
and all effects are in a special 'group 29'.

## Options

The script is controlled via command line options, primarily it used for editing the
contents of '.zt2' files. But it also allows for upload/download to the pedal.

```
$ python3 zoom-zt2.py -h
Usage: zoom-zt2.py [options] FILENAME

Options:
  -h, --help            show this help message and exit
  -d, --dump            dump configuration to text
  -s, --summary         summarized configuration in human readable form
  -b BUILD, --build=BUILD
                        output commands required to build this FLTS_SEQ
  -A ADD, --add=ADD     add an effect to group ADD
  -n NAME, --name=NAME  effect name (use with --add)
  -v VER, --ver=VER     effect version (use with --add)
  -i ID, --id=ID        effect id (use with --add)
  -u UNKNOWN, --unknown=UNKNOWN
                        effect unknown (use with --add)
  -t TOGGLE, --toggle=TOGGLE
                        toggle install/uninstall state of effect NAME in
                        FLST_SEQ
  -D DELETE, --delete=DELETE
                        delete last effect in group DEL
  -w, --write           write config back to same file
  -R, --receive         Receive FLST_SEQ from attached device
  -S, --send            Send FLST_SEQ to attached device
  -I INSTALL, --install=INSTALL
                        Install effect binary to attached device
  -U UNINSTALL, --uninstall=UNINSTALL
                        Remove effect binary from attached device
```
