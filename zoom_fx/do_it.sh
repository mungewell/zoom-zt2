
# process multiple directories of 'zips' of Zoom ZD2 effects, aquired with
# https://github.com/fuzboxz/zdownload

# make a list of unzipping and do it
echo > do_it2.sh
find . -name '*.zip' -exec bash -c 'export p="{}"; p="${p// /\\ }"; echo unzip -o $p -d ${p%/*}/unzipped' \; >> do_it2.sh
bash do_it2.sh

# find and summarize each effect, directory by directory
find . -name 'unzipped' -type d -exec bash -c 'echo Processing {}; find "{}" -name "*.ZD2" -exec python3 ../decode_effect.py --summary --md5sum \{\} \; >> "{}"/list ' \;
find . -name 'list' -exec bash -c 'cat "{}" | sort | uniq > "{}_sorted.txt"' \;

# make a master list
echo > list.txt
find . -name "list_sorted.txt" -exec bash -c 'cat "{}" | cut -d "," -f 1-2 >> list.txt' \;
cat list.txt | sort | uniq > master.txt

echo Done
