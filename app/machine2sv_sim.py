#!/usr/bin/env python3

def machine_to_sv(input_file, output_file):
    """
    Converts machine code in hex format to a SystemVerilog-readable memory initialization file.
    Each 32-bit instruction is split into 4 bytes (8-bit chunks) in little-endian order,
    and every 16 bytes (4 instructions) are written on a single line in `readmemh` format.
    """
    try:
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            # Write the header for SystemVerilog memory initialization
            outfile.write("// Memory initialization for simulation\n")
            outfile.write("// Generated from machine code\n\n")

            byte_accumulator = []  # Temporary storage for 16 bytes
            for line_num, line in enumerate(infile, start=1):
                line = line.strip()
                if "#" in line:
                    machine_code, comment = line.split("#", 1)
                else:
                    machine_code = line
                    comment = ""
                
                machine_code = machine_code.strip()
                if not machine_code:
                    continue  # Skip empty lines

                # Ensure the instruction is 32 bits long
                if len(machine_code) != 8:
                    print(f"Error: Invalid instruction length in line {line_num}: '{machine_code}'")
                    continue

                # Split the 32-bit instruction into four 8-bit parts (one byte each)
                byte0 = machine_code[0:2]
                byte1 = machine_code[2:4]
                byte2 = machine_code[4:6]
                byte3 = machine_code[6:8]

                # Append the bytes in little-endian order (least significant byte first)
                byte_accumulator.extend([byte3, byte2, byte1, byte0])

                # If we have accumulated 16 bytes, write them as a single line
                if len(byte_accumulator) == 16:
                    outfile.write(" ".join(byte_accumulator) + "\n")
                    byte_accumulator = []  # Clear the accumulator

            # Write any remaining bytes in the accumulator
            if byte_accumulator:
                outfile.write(" ".join(byte_accumulator) + "\n")

        print(f"SystemVerilog memory file created: {output_file}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 machine2sv_sim.py <input_machine_code> <output_memh_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    machine_to_sv(input_file, output_file)
