2008000A  # ADDI $t0, $zero, 10      # $t0 = 10
20090014  # ADDI $t1, $zero, 20      # $t1 = 20
200A0005  # ADDI $t2, $zero, 5       # $t2 = 5
01095820  # ADD $t3, $t0, $t1        # $t3 = $t0 + $t1 = 10 + 20 = 30
016A6022  # SUB $t4, $t3, $t2        # $t4 = $t3 - $t2 = 30 - 5 = 25
11280003  # BEQ $t0, $t1, NO_JUMP    # Branch to NO_JUMP if $t0 == $t1 (does not branch)
200D0064  # ADDI $t5, $zero, 100     # $t5 = 100 (this should execute)
11080002  # BEQ $t0, $t0, DO_JUMP    # Branch to DO_JUMP if $t0 == $t0 (branches)
200E00C8  # ADDI $t6, $zero, 200     # $t6 = 200 (this should not execute)
200F012C  # NO_JUMP: ADDI $t7, $zero, 300 # $t7 = 300 (executed after first BEQ)
20180190  # DO_JUMP: ADDI $t8, $zero, 400 # $t8 = 400 (executed after second BEQ)
2008007B  # ADDI $t0, $zero, 123
0800000E  # J SOME_LABEL
200903E7  # ADDI $t1, $zero, 999  # This should be skipped
200901BC  # SOME_LABEL: ADDI $t1, $zero, 444  # Jumps here
