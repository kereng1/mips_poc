module mips(
    input logic clk,
    input logic rst
);

//cyncronic signals - ff outputs
logic [31:0] pc;
logic [31:0] next_pc; 
logic [31:0] pc_plus4; 
logic [31:0] branch_or_PcPlus4; //mux output for branch
logic [31:0] registers[31:0];
logic [31:0] next_registers[31:0]; 
logic [31:0] branch_target; //branch target address
logic [31:0] jump_target; //jump target address

logic [31:0] instruction;
logic [7:0] i_mem [127: 0]; //instruction memory matrix 128x32 each instruction (row) is 32 bits
logic [7:0] next_i_mem [127: 0]; //is this the Read data in ss mips?
logic [31:0] write_data_reg; //write data to the register file
logic [31:0] write_data_mem; //write data to the Data memory
logic [4:0] write_ptr; ///////////////do i neeed to add this?//////////
logic [31:0] read_data; 
logic [31:0] alu_result;

logic [7:0] d_mem [127: 0]; 
logic [7:0] next_d_mem [127: 0];

logic       RegDst;
logic       Jump;
logic       Branch;
logic       MemRead;
logic       MemtoReg;
logic       ALUOp;
logic       MemWrite;
logic       ALUSrc;
logic       RegWrite;

logic       zero;
logic       sel_branch;
logic       sel_jump;

logic [31:0] sign_extended_imm; //sign extended immidiate value
logic [31:0] alu_in1;
logic [31:0] alu_in2;

logic [31:0] rd_data1; //output
logic [31:0] rd_data2; //output
logic [4:0] rs; //input
logic [4:0] rt; //input
logic [4:0] rd; //input


//defining the instruction signal for ALU control
typedef enum logic [5:0] {
    ADD = 6'b100000,
    SUB = 6'b100010,
    AND = 6'b100100,
    OR = 6'b100101,
    NOR = 6'b100111,
    XOR = 6'b100110,
    SLT = 6'b101010
}t_alu_ctrl;

t_alu_ctrl ALUCtrl; //ALU control signals

//defining the opcode input for the main control unit
typedef enum logic [5:0] {
    R_TYPE = 6'b000000,
    ADDI   = 6'b001000,
    LW     = 6'b100011,
    SW     = 6'b101011,
    BEQ    = 6'b000100,
    J      = 6'b000010,
    BRANCH = 6'b000101,        // Define custom operation for branch
    LOAD_STORE = 6'b000110     // Define custom operation for load/store
} t_opcode;


//=====================
//FETCH
//=====================
// 1) get the instruction from memory
// 2) pc <= pc + 4  increment the pc by 4

assign pc_plus4 = pc + 4;
`RST_DFF(pc, next_pc, clk, rst); //PC dff macro

// the INSTRUCTION MEMORY dff "array"
`DFF (i_mem, next_i_mem, clk); 

//read the instruction from the i_memory
// Note: the instruction memory is byte (8 bit) accesable 
// so we need to read 4 bytes to get the 32 bit instruction 
assign instruction[7:0] = i_mem[pc[31:0]+0];
assign instruction[15:8] = i_mem[pc[31:0]+1];
assign instruction[23:16] = i_mem[pc[31:0]+2];
assign instruction[31:24] = i_mem[pc[31:0]+3];

//=====================
//DECODE
//=====================
// 1) decode the instruction: reading from refister_file, and control signals
// 2) sighn extension for immidiate values and speculated calculation of branch address
t_opcode opcode; //define opcode variable of type t_opcode (like list/stuct in C)
assign opcode[5:0] = instruction[31:26];

assign RegDst = (opcode == R_TYPE);
assign Jump = (opcode == J);
assign Branch = (opcode == BEQ);
assign MemRead = (opcode == LW);
assign MemtoReg = (opcode == LW);
assign ALUOp = (opcode == R_TYPE); //maby need to add more ,not only for Rtype but for all******
assign MemWrite = (opcode == SW);
assign ALUSrc = (opcode !== R_TYPE); //take the immidiate value if not Rtype (for lw and addi)
assign RegWrite = (opcode == R_TYPE || opcode == LW || opcode == ADDI);

assign rs = instruction[25:21];
assign rt = instruction[20:16];
assign rd = instruction[15:11];
assign sign_extended_imm = {{16{instruction[15]}}, instruction[15:0]}; //sign extension

//.....................
//Register File
//.....................
`DFF (registers, next_registers, clk); //dff for the register file

assign rd_data1 = (rs == 5'b0) ? 32'b0 : registers[rs];
assign rd_data2 = (rt == 5'b0) ? 32'b0 : registers[rt];

//write to the register file
assign write_ptr = RegDst ? rd : rt; //wich register to write to (mux for write register)
always_comb begin : rf_write         //rf_write is the name of the always_comb block
    next_registers = registers;      //default
    if (RegWrite) begin
        next_registers[write_ptr] = write_data_reg;
    end 
end 


//================
//EXECUTE
//================
// 1) ALU operation
// 2) branch evaluation and jump calculation

//ALU
assign alu_in1 = rd_data1;
assign alu_in2 = ALUSrc ? sign_extended_imm : rd_data2;

// ALU control logic based on ALUOp 
always_comb begin
    case (ALUOp)
        R_TYPE: ALUCtrl = t_alu_ctrl'(instruction[5:0]); // Explicitly cast to t_alu_ctrl
        BRANCH: ALUCtrl = SUB;                          // Set to SUB for branch comparison
        LOAD_STORE: ALUCtrl = ADD;                      // Set to ADD for load/store address calculation
        default: ALUCtrl = ADD;                         // Default to ADD
    endcase
end


//ALU operation
always_comb begin : alu
    case (ALUCtrl) //ALUCtrl is the output of ALU control
        ADD: alu_result = alu_in1 + alu_in2;
        SUB: alu_result = alu_in1 - alu_in2;
        AND: alu_result = alu_in1 & alu_in2;
        OR:  alu_result = alu_in1 | alu_in2;
        NOR: alu_result = ~(alu_in1 | alu_in2);
        XOR: alu_result = alu_in1 ^ alu_in2;
        SLT: alu_result = (alu_in1 < alu_in2) ? 1 : 0;
        default: alu_result = alu_in1 + alu_in2; //default is ADD
    endcase
    zero = (alu_result == 0); //set the zero flag
end 

//Branch 
assign branch_target = pc + 4 + (sign_extended_imm << 2); //compute branch target address
assign sel_branch = Branch && zero; //mux selector for branch
assign branch_or_PcPlus4 = sel_branch ? branch_target : pc_plus4; //mux for branch

//Jump
assign jump_target = {pc_plus4[31:28], instruction[25:0], 2'b00}; //compute jump target address using concatination 
assign next_pc = Jump ? jump_target : branch_or_PcPlus4; //mux for jump


//================
//MEMORY
//================
// 1) read/write to data memory

//read from data memory
`DFF (d_mem, next_d_mem, clk); //dff for the data memory
assign read_data[7:0] = d_mem[alu_result[31:0]+0];
assign read_data[15:8] = d_mem[alu_result[31:0]+1];
assign read_data[23:16] = d_mem[alu_result[31:0]+2];
assign read_data[31:24] = d_mem[alu_result[31:0]+3];

assign write_data_mem = rd_data2; //data to write to the data memory

//write to the data memory 
always_comb begin : mem_write
    next_d_mem = d_mem; //default
    if (MemWrite) begin  //approach writes write_data_mem (32 bits) to the byte-addressable next_d_mem
        next_d_mem[alu_result[31:0] +0] = write_data_mem[7:0];
        next_d_mem[alu_result[31:0] +1] = write_data_mem[15:8];
        next_d_mem[alu_result[31:0] +2] = write_data_mem[23:16];
        next_d_mem[alu_result[31:0] +3] = write_data_mem[31:24];
    end
end 


//write back to the register file
assign write_data_reg = MemtoReg ? read_data : alu_result;


endmodule
