module mips_tb;

    // Declare signals to connect to the DUT
    logic clk;
    logic rst;

    // Instantiate the DUT
    mips dut (
        .clk(clk),
        .rst(rst)
    );

    // Clock generation: 10ns period (5ns high, 5ns low)
    initial begin
        clk = 0;
        forever #10 clk = ~clk; // Toggle clk every 10ns
    end

    // Reset logic
    initial begin
        rst = 1;          // Assert reset
        #100 rst = 0;     // Deassert reset after 100ns
    end

    // Test sequence (if needed for further control)
    initial begin
        //load the i_mem with the instructions using the $readmemh system task
        //the location of the file is output_app/load_mem.sv
        $readmemh("output_app/load_mem.sv", dut.i_mem);
        $readmemh("output_app/load_mem.sv", dut.next_i_mem);

        // Initialize and observe behavior
        #1000;             // Run simulation for 1000ns
        $finish;          // End simulation
    end

    // Monitor signals from the DUT
    initial begin
        $monitor("Time: %0t | PC: %h | instruction: %h | ALUCtrl: %b | ALU in1: %h | ALU in2: %h | ALU result: %h | zero: %b |ALUop: %b ",
                 $time, dut.pc, dut.instruction, dut.ALUCtrl, dut.alu_in1, dut.alu_in2, dut.alu_result, dut.zero, dut.ALUOp,);
    end

    

endmodule
