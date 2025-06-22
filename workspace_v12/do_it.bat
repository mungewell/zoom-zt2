echo off

REM script to dis-assemble the '.code' segement of a ZD2
REM call with name of file to process

if "%1"=="" goto end
echo processing %1

set dis6x="C:\ti\ccs1281\ccs\tools\compiler\ti-cgt-c6000_8.3.12\bin\dis6x.exe"
set python="C:\Program Files\Python312\python.exe"

REM don't know of a way to create reloc under windows...
if exist %1.reloc (
	echo Found '.reloc'
	%dis6x% --all --noaddr --realquiet %1 >> temp.asm
	%python% patch_asm.py -r %1.reloc temp.asm > %1.asm
) else (
	echo '.reloc' not found you may difficulty applying our '.diff' file
	%dis6x% --all --noaddr --realquiet --suppress %1 >> temp.asm
	%python% patch_asm.py temp.asm > %1.asm
)

:end
del temp.asm
