#!/usr/bin/env python3
import sys
import re

# Define opcode and function code mapping for R-type and I-type instructions
R_TYPE_OPCODE = "000000"  # Opcode for R-type instructions
I_TYPE_OPCODES = {
    "ADDI": "001000",  # Opcode for ADDI
}
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
    if len(parts) < 2:
        raise ValueError(f"Invalid instruction format: {instruction}")
    
    op = parts[0].upper()

    if op in FUNCTION_CODES:  # R-type instruction
        if len(parts) != 4:
            raise ValueError(f"Invalid R-type instruction format: {instruction}")
        rd, rs, rt = parts[1], parts[2], parts[3]
        rs_bin = REGISTER_MAP.get(rs)
        rt_bin = REGISTER_MAP.get(rt)
        rd_bin = REGISTER_MAP.get(rd)
        if None in (rs_bin, rt_bin, rd_bin):
            raise ValueError(f"Invalid register in instruction: {instruction}")
        shamt = "00000"  # Shift amount is always 0 for ADD and SUB
        func = FUNCTION_CODES[op]
        return f"{R_TYPE_OPCODE}{rs_bin}{rt_bin}{rd_bin}{shamt}{func}"

    elif op in I_TYPE_OPCODES:  # I-type instruction (e.g., ADDI)
        if len(parts) != 4:
            raise ValueError(f"Invalid I-type instruction format: {instruction}")
        rt, rs, imm = parts[1], parts[2], parts[3]
        rs_bin = REGISTER_MAP.get(rs)
        rt_bin = REGISTER_MAP.get(rt)
        if None in (rs_bin, rt_bin):
            raise ValueError(f"Invalid register in instruction: {instruction}")
        try:
            imm_bin = format(int(imm), "016b")
        except ValueError:
            raise ValueError(f"Invalid immediate value in instruction: {instruction}")
        opcode = I_TYPE_OPCODES[op]
        return f"{opcode}{rs_bin}{rt_bin}{imm_bin}"

    else:
        raise ValueError(f"Unsupported operation: {op}. Skipping...")

def assemble(input_file, output_file):
    """Assembles a MIPS ASM file into machine code."""
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line_num, line in enumerate(infile, start=1):
            original_line = line.strip()  # Save the original line for the comment
            # Remove comments and trim whitespace
            line = re.sub(r"#.*", "", line).strip()  # Remove inline comments starting with #
            line = re.sub(r"//.*", "", line).strip()  # Remove inline comments starting with //
            if not line:  # Skip empty lines after removing comments
                continue
            try:
                # Parse the instruction and get binary string
                binary_instruction = parse_instruction(line)
                # Convert the 32-bit binary instruction into 8-bit hexadecimal chunks
                hex_instruction = ''.join(f"{int(binary_instruction[i:i+8], 2):02X}" for i in range(0, 32, 8))
                # Write the full instruction in hex followed by the original line as a comment
                outfile.write(f"{hex_instruction}  # {original_line}\n")
            except ValueError as e:
                print(f"Error processing line {line_num}: '{original_line}' - {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python assembler.py <input.asm> <output.bin>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    assemble(input_file, output_file)
    print(f"Assembly complete. Output written to {output_file}")
