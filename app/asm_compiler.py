# this is a simple python script that compiles the assembly code into machine code
#the script reads the assembly code from the file and writes the machine code to another file

import sys
import re

# Define opcode and function code mapping for R-type instructions
R_TYPE_OPCODE = "000000"  # Opcode for R-type instructions
FUNCTION_CODES = {
    "ADD": "100000",
    "SUB": "100010",
}

# Register name to number mapping
REGISTER_MAP = {
    "$zero": "00000",
    "$at": "00001",
    "$v0": "00010", "$v1": "00011",
    "$a0": "00100", "$a1": "00101", "$a2": "00110", "$a3": "00111",
    "$t0": "01000", "$t1": "01001", "$t2": "01010", "$t3": "01011",
    "$t4": "01100", "$t5": "01101", "$t6": "01110", "$t7": "01111",
    "$s0": "10000", "$s1": "10001", "$s2": "10010", "$s3": "10011",
    "$s4": "10100", "$s5": "10101", "$s6": "10110", "$s7": "10111",
    "$t8": "11000", "$t9": "11001",
    "$k0": "11010", "$k1": "11011",
    "$gp": "11100", "$sp": "11101", "$fp": "11110", "$ra": "11111",
}

# Extend register map to include numeric register names
for i in range(32):
    REGISTER_MAP[f"${i}"] = format(i, "05b")

def parse_instruction(instruction):
    """Parses a single MIPS instruction into binary."""
    parts = re.split(r"[,\s]+", instruction.strip())
    if len(parts) < 4:
        raise ValueError(f"Invalid instruction format: {instruction}")
    
    op = parts[0].upper()
    rd, rs, rt = parts[1], parts[2], parts[3]
    
    if op not in FUNCTION_CODES:
        raise ValueError(f"Unsupported operation: {op}")
    
    # Get binary representations for registers
    rs_bin = REGISTER_MAP.get(rs)
    rt_bin = REGISTER_MAP.get(rt)
    rd_bin = REGISTER_MAP.get(rd)
    
    if None in (rs_bin, rt_bin, rd_bin):
        raise ValueError(f"Invalid register in instruction: {instruction}")
    
    # Construct the binary representation of the instruction
    shamt = "00000"  # Shift amount is always 0 for ADD and SUB
    func = FUNCTION_CODES[op]
    return f"{R_TYPE_OPCODE}{rs_bin}{rt_bin}{rd_bin}{shamt}{func}"

def assemble(input_file, output_file):
    """Assembles a MIPS ASM file into machine code."""
    with open(input_file, "r") as infile, open(output_file, "wb") as outfile:
        for line in infile:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip empty lines or comments
                continue
            try:
                binary_instruction = parse_instruction(line)
                # Convert binary string to bytes and write to output file
                outfile.write(int(binary_instruction, 2).to_bytes(4, byteorder="big"))
            except ValueError as e:
                print(f"Error processing line '{line}': {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python assembler.py <input.asm> <output.bin>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    assemble(input_file, output_file)
    print(f"Assembly complete. Output written to {output_file}")
