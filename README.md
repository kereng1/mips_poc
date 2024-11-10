# my_first_mips
in this simple project we will create a  POC of a MIP CPU

## MIPS CPU - RTL \\the module design.
simple single cycle mips cpu - using a fetch-decode-execute-memory-writeback structure.

## MIPS CPU - verification \\the TB design.
will provide reset, clk, 
The TB will simply use XMR (xross module reference) to connect the CPU to the memory and the CPU to the instruction memory.
it will print the values of the registers and the memory so we can see and check the results of the program.

## MIPS CPU - test
using python we will create a sw "assembler" that will convert the assembly code to machine code. and will create a memory file that will be used by the TB.

