
echo processing all '.code' files

export dis6x=~/ti/ccs1281/ccs/tools/compiler/ti-cgt-c6000_8.3.12/bin/dis6x

# Create relocation table, and merge with disassembly
# also:
# 	check whether any symbols are missed (ie not word aligned)
# 	add MD5Sum/Name of source effect's '.code'

find . -name '*.code' -exec bash -c "readelf -W -r {} > {}.reloc; \
	$dis6x --all --noaddr --realquiet {} > temp.asm; \
	\
	$dis6x --all --bytes --noaddr --realquiet --suppress {} | \
	grep -e \":$\" > 1.temp; \
	grep -e \":$\" {}.asm | grep -v -e \"^;.*:$\" > 2.temp; \
	diff -q 1.temp 2.temp >> {}.asm; \
	\
	echo    '                    zoomzt2:' >> temp.asm; \
	echo -n '                            .cstring \"' >> temp.asm; \
	md5sum {} | tr -d '\n' >> temp.asm; \
	echo '\"' >> temp.asm; \
	\
	python3 patch_asm.py -r {}.reloc temp.asm > {}.asm;" \;


rm -f temp.asm 1.temp 2.temp
