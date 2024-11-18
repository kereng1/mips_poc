# this is a simple python script that compiles the assembly code into machine code
#the script reads the assembly code from the file and writes the machine code to another file

def assemble_mips(file_path):
    # Mapping for instructions
    funct_codes = {
        "ADD": "100000",  # Funct code for ADD
        "SUB": "100010",  # Funct code for SUB
    }

    # Helper function to convert register to 5-bit binary
    def reg_to_bin(register):
        if not register.startswith("$"):
            raise ValueError(f"Invalid register format: {register}")
        reg_num = int(register[1:])
        return f"{reg_num:05b}"

    # Open input MIPS assembly file
    with open(file_path, "r") as asm_file:
        lines = asm_file.readlines()

    # Process each line and generate binary machine code
    binary_instructions = []
    for line in lines:
        # Strip comments and whitespace
        line = line.split("#")[0].strip()
        if not line:  # Skip empty lines
            continue

        # Split instruction into parts
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"Invalid instruction format: {line}")

        instr, rd, rs, rt = parts

        if instr not in funct_codes:
            raise ValueError(f"Unsupported instruction: {instr}")

        # Assemble binary instruction
        opcode = "000000"  # R-type opcode
        funct = funct_codes[instr]
        rs_bin = reg_to_bin(rs)
        rt_bin = reg_to_bin(rt)
        rd_bin = reg_to_bin(rd)
        shamt = "00000"  # Shift amount (not used)

        binary_instr = f"{opcode}{rs_bin}{rt_bin}{rd_bin}{shamt}{funct}"
        binary_instructions.append(binary_instr)

    # Save binary machine code to output file
    output_path = file_path.replace(".asm", ".bin")
    with open(output_path, "w") as bin_file:
        bin_file.write("\n".join(binary_instructions))

    print(f"Assembly compiled to machine code: {output_path}")


# Example usage
if __name__ == "__main__":
    input_file = "program.asm"  # Replace with your input file
    assemble_mips(input_file)
