` //define the RST_DFF macro this is the PC reg.
define RST_DFF(q, d, clk, rst)                       //"define" creates a macro named RST_DFF       
    always_ff @(posedge clk or posedge rst) begin    // "always_ff" defines a flip-flop The block is executed whenever the clock ticks (a rising edge occurs) or when the reset signal is asserted (goes high).         
        q <= (rst) ? 0 : d;                                     
    end  `

**macro**
 is a reusable code snippet that can be expanded anywhere in the code. Think of it as a shortcut for commonly used code patterns.