/****************************************************************************/
/*  C6745.cmd                                                               */
/*  Copyright (c) 2012  Texas Instruments Incorporated                      */
/*  Author: Rafael de Souza                                                 */
/*                                                                          */
/*    Description: This file is a sample linker command file that can be    */
/*                 used for linking programs built with the C compiler and  */
/*                 running the resulting .out file on an C6745              */
/*                 device.  Use it as a guideline.  You will want to        */
/*                 change the memory layout to match your specific          */
/*                 target system.  You may want to change the allocation    */
/*                 scheme according to the size of your program.            */
/*                                                                          */
/****************************************************************************/

MEMORY
{
    SHDSPL2RAM   o = 0x00000000  l = 0x10000000
    DATA         o = 0x80000000  l = 0x10000000
}                                                                       

SECTIONS
{
    .text		> SHDSPL2RAM
    .audio		> SHDSPL2RAM
    .stack		> SHDSPL2RAM
    .args		> SHDSPL2RAM
    .neardata	> SHDSPL2RAM
    .rodata		> SHDSPL2RAM
    .bss		> SHDSPL2RAM

    .text		> SHDSPL2RAM
    .cinit		> SHDSPL2RAM
    .cio		> SHDSPL2RAM

    .const		> DATA

    .data		> SHDSPL2RAM
    .switch		> SHDSPL2RAM
    .sysmem		> SHDSPL2RAM
    .far		> SHDSPL2RAM
    .fardata	> SHDSPL2RAM
    .ppinfo		> SHDSPL2RAM
    .ppdata		> SHDSPL2RAM
}
