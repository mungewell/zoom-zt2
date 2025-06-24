# Script to automate disassembly of ZD2 code segements and combine it with
# relocation table to aid editting/re-compilation
#
# Extract 'code' section first, ie:
# $ python3 zoomzt2/decode_effect.py -c LINESEL.ZD2.code LINESEL.ZD2

if [ -z ${1+x} ]; then
	echo processing all '.code' files
	export target="*.code"
else
	echo processing $1
	export target=$1
fi

export dis6x=~/ti/ccs1281/ccs/tools/compiler/ti-cgt-c6000_8.3.12/bin/dis6x

# Create relocation table, and merge with disassembly
# also:
# 	check whether any symbols are missed (ie not word aligned)
# 	add MD5Sum/Name of source effect's '.code'

find . -name "$target" -exec bash -c " \
	readelf -W -r {} > {}.reloc; \
	$dis6x --all --noaddr --realquiet {} > temp.asm; \
	\
	echo -e '\n                    zoomzt2:' >> temp.asm; \
	echo -n '                              .cstring \"' >> temp.asm; \
	md5sum {} | tr -d '\n' >> temp.asm; \
	echo '\"' >> temp.asm; \
	\
	python3 patch_asm.py -r {}.reloc temp.asm > {}.asm; \
	\
	$dis6x --all --bytes --noaddr --realquiet --suppress {} | \
	grep -e \":$\" > 1.temp; \
	grep -e \":$\" {}.asm | grep -v -e \"^;.*:$\" | grep -v \"zoomzt2\" > 2.temp; \
	diff -q 1.temp 2.temp > 3.temp; if [ -s 3.temp ];then \
	echo -e '\n.emsg \"symbols are not word aligned!\"' >> {}.asm; \
	fi; \
	" \;


rm -f temp.asm 1.temp 2.temp 3.temp
