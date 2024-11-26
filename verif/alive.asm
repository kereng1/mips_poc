
#simple ADD SUB test for my mips CPU 
#the input in assembly 

# Initialize registers with ADDI
ADDI $t0, $zero, 10      # $t0 = 10
ADDI $t1, $zero, 20      # $t1 = 20
ADDI $t2, $zero, 5       # $t2 = 5

# Perform arithmetic operations
ADD $t3, $t0, $t1        # $t3 = $t0 + $t1 = 10 + 20 = 30
SUB $t4, $t3, $t2        # $t4 = $t3 - $t2 = 30 - 5 = 25

# BEQ test: does not jump (because $t0 != $t1)
BEQ $t0, $t1, NO_JUMP    # Branch to NO_JUMP if $t0 == $t1 (does not branch)

# Additional instruction to verify no branch
ADDI $t5, $zero, 100     # $t5 = 100 (this should execute)

# BEQ test: jumps (because $t0 == $t0)
BEQ $t0, $t0, DO_JUMP    # Branch to DO_JUMP if $t0 == $t0 (branches)

# This instruction is skipped due to the branch
ADDI $t6, $zero, 200     # $t6 = 200 (this should not execute)

# NO_JUMP label
NO_JUMP: ADDI $t7, $zero, 300 # $t7 = 300 (executed after first BEQ)

# DO_JUMP label
DO_JUMP: ADDI $t8, $zero, 400 # $t8 = 400 (executed after second BEQ)
