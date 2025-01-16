# this is a simple python script that "translates" MIPS assembly code into machine code
# it is used to compile the assembly code into machine code meaning:
#The script reads the assembly code from "verif/alive.asm" and writes the machine code to another file "output_app/alive.sv"
import sys
import re

########################################
# 1) Define opcode and function codes
########################################

R_TYPE_OPCODE = "000000"  # Opcode for R-type instructions
I_TYPE_OPCODES = {
    "ADDI": "001000",  # Opcode for ADDI
    "BEQ":  "000100",  # Opcode for BEQ
}
FUNCTION_CODES = {
    "ADD": "100000",
    "SUB": "100010",
    # Extend as needed (AND, OR, etc.)
}

J_OPCODE = "000010"       # 6-bit opcode for J

########################################
# 2) Define register map (name -> 5-bit)
########################################

REGISTER_MAP = {
    "$zero": "00000", "$at":   "00001",
    "$v0":   "00010", "$v1":   "00011",
    "$a0":   "00100", "$a1":   "00101", "$a2": "00110", "$a3": "00111",
    "$t0":   "01000", "$t1":   "01001", "$t2": "01010", "$t3": "01011",
    "$t4":   "01100", "$t5":   "01101", "$t6": "01110", "$t7": "01111",
    "$s0":   "10000", "$s1":   "10001", "$s2": "10010", "$s3": "10011",
    "$s4":   "10100", "$s5":   "10101", "$s6": "10110", "$s7": "10111",
    "$t8":   "11000", "$t9":   "11001",
    "$k0":   "11010", "$k1":   "11011",
    "$gp":   "11100", "$sp":   "11101", "$fp": "11110", "$ra": "11111",
}

# Also allow numeric registers like $8, $9, etc.
for i in range(32):
    REGISTER_MAP[f"${i}"] = format(i, "05b")

########################################
# 3) Parsing a single instruction into 32-bit binary string
########################################

def parse_instruction(instruction: str) -> str:
    """
    Parses a single MIPS instruction (with numeric offsets) into a 32-bit binary string.
    Example input: 'ADDI $t0, $zero, 10' -> '00100000000010000000000000001010'
    """
    parts = re.split(r"[,\s]+", instruction.strip())
    if len(parts) < 1:
        raise ValueError(f"Invalid instruction: {instruction}")

    op = parts[0].upper()

    #-----------------------------------------
    # R-type instructions (ADD, SUB, etc.)
    #-----------------------------------------
    if op in FUNCTION_CODES:
        # e.g. "ADD $t3, $t1, $t2"
        # parts = ["ADD", "$t3", "$t1", "$t2"]
        if len(parts) != 4:
            raise ValueError(f"Invalid R-type format: {instruction}")
        rd, rs, rt = parts[1], parts[2], parts[3]

        rs_bin = REGISTER_MAP.get(rs)
        rt_bin = REGISTER_MAP.get(rt)
        rd_bin = REGISTER_MAP.get(rd)
        if None in (rs_bin, rt_bin, rd_bin):
            raise ValueError(f"Invalid register in: {instruction}")

        shamt = "00000"
        func  = FUNCTION_CODES[op]
        return f"{R_TYPE_OPCODE}{rs_bin}{rt_bin}{rd_bin}{shamt}{func}"

    #-----------------------------------------
    # I-type instructions (ADDI, BEQ, etc.)
    #-----------------------------------------
    elif op in I_TYPE_OPCODES:
        # e.g. "ADDI $t1, $zero, 20"
        # or   "BEQ $t0, $t1, 5"
        if len(parts) != 4:
            raise ValueError(f"Invalid I-type format: {instruction}")
        rt, rs, imm_str = parts[1], parts[2], parts[3]

        rs_bin = REGISTER_MAP.get(rs)
        rt_bin = REGISTER_MAP.get(rt)
        if None in (rs_bin, rt_bin):
            raise ValueError(f"Invalid register in: {instruction}")

        try:
            imm = int(imm_str)
        except ValueError:
            raise ValueError(f"Invalid immediate value: {imm_str} in {instruction}")

        # 16-bit signed immediate
        imm_bin = format(imm & 0xFFFF, "016b")
        opcode = I_TYPE_OPCODES[op]
        return f"{opcode}{rs_bin}{rt_bin}{imm_bin}"

    #-----------------------------------------
    # J-type instruction (J <target>)
    #-----------------------------------------
    elif op == "J":
        # e.g. "J 10"
        if len(parts) != 2:
            raise ValueError(f"Invalid J format: {instruction}")
        try:
            jump_index = int(parts[1])
        except ValueError:
            raise ValueError(f"Invalid jump index: {parts[1]} in {instruction}")

        # Must fit in 26 bits
        if jump_index < 0 or jump_index > 0x03FFFFFF:
            raise ValueError(f"Jump index out of range: {jump_index}")

        imm_26 = format(jump_index, "026b")
        return f"{J_OPCODE}{imm_26}"

    else:
        raise ValueError(f"Unsupported operation: {op} in '{instruction}'")


########################################
# 4) The assembler function (two-pass)
########################################

def assemble(input_file: str, output_file: str):
    """
    Reads a MIPS ASM file and produces a machine code file.
    1) First pass: collect labels and addresses.
    2) Second pass: replace labels with numeric offsets/indices, then parse.
    """
    label_addresses = {}
    instructions = []

    #--------------------------------
    # First Pass: Identify labels
    #--------------------------------
    with open(input_file, "r") as infile:
        address = 0  # We'll treat 'address' as the instruction index
        for line in infile:
            original_line = line.strip()
            # Remove # and // comments
            line = re.sub(r"#.*", "", line)
            line = re.sub(r"//.*", "", line)
            line = line.strip()

            if not line:
                continue  # skip empty lines

            # Check if there's a label
            # e.g. "LOOP: ADDI $t0, $zero, 10"
            if ":" in line:
                # Could be "LOOP:" or "LOOP: ADD $t0, $t1, $t2"
                label, *rest = line.split(":")
                label = label.strip()
                label_addresses[label] = address

                # The rest is the instruction after the label
                line = ":".join(rest).strip()
                if not line:  # if it was just a label with no instruction on same line
                    continue

            # Save for second pass
            instructions.append((address, original_line, line))
            address += 1

    #--------------------------------
    # Second Pass: Label resolution
    #--------------------------------
    with open(output_file, "w") as outfile:
        for address, original_line, line in instructions:
            try:
                if not line.strip():
                    # Might happen if line had only a label
                    continue

                # Split to get the operation
                parts = re.split(r"[,\s]+", line.strip())
                op = parts[0].upper()

                #-------------------------
                # Handle BEQ <label>
                #-------------------------
                if op == "BEQ":
                    # e.g. "BEQ $t0, $t1, LABEL"
                    label = parts[-1]
                    if label in label_addresses:
                        offset = label_addresses[label] - (address + 1)
                        parts[-1] = str(offset)
                        line = " ".join(parts)

                #-------------------------
                # Handle J <label>
                #-------------------------
                elif op == "J":
                    # e.g. "J SOME_LABEL"
                    label = parts[-1]
                    if label in label_addresses:
                        jump_index = label_addresses[label]
                        # If your label_addresses are byte addresses, do:
                        # jump_index = label_addresses[label] >> 2
                        parts[-1] = str(jump_index)
                        line = " ".join(parts)

                # Now parse the updated instruction
                binary_instruction = parse_instruction(line)

                # Convert 32-bit bin -> hex
                hex_instruction = ''.join(
                    f"{int(binary_instruction[i:i+8], 2):02X}"
                    for i in range(0, 32, 8)
                )
                # Write machine code + original line as a comment
                outfile.write(f"{hex_instruction}  # {original_line}\n")

            except ValueError as e:
                print(f"Error processing line {address}: '{original_line}' - {e}")

    print(f"Assembly complete. Output written to {output_file}")


########################################
# 5) Main entry point
########################################

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 asm_compiler.py <input.asm> <output.sv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    assemble(input_file, output_file)