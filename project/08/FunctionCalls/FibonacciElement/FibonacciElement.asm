@256
D=A
@SP
M=D
@return_address_0
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@0
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(return_address_0)
// vm command:function Main.fibonacci 0
(Main.fibonacci)

// vm command:push argument 0
@ARG
D=M
@0
A=D+A
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:push constant 2
@2
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:lt
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R14
M=D
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R13
M=D
@R13
D=M
@R14
D=D-M
@LT0
D;JLT
// push the value into stack
@SP
A=M
M=0
@SP
M=M+1
@ENDLT0
0;JMP
(LT0)
// push the value into stack
@SP
A=M
M=-1
@SP
M=M+1
(ENDLT0)

// vm command:if-goto IF_TRUE
// get the top element of stack
@SP
M=M-1
A=M
D=M
@IF_TRUE
D;JNE

// vm command:goto IF_FALSE
@IF_FALSE
0;JMP

// vm command:label IF_TRUE
(IF_TRUE)

// vm command:push argument 0
@ARG
D=M
@0
A=D+A
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:return
@LCL
D=M
@FRAME
M=D
@5
A=D-A
D=M
@RET
M=D
// get the top element of stack
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@FRAME
A=M-1
D=M
@THAT
M=D
@FRAME
D=M
@2
A=D-A
D=M
@THIS
M=D
@FRAME
D=M
@3
A=D-A
D=M
@ARG
M=D
@FRAME
D=M
@4
A=D-A
D=M
@LCL
M=D
@RET
A=M
0;JMP

// vm command:label IF_FALSE
(IF_FALSE)

// vm command:push argument 0
@ARG
D=M
@0
A=D+A
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:push constant 2
@2
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:sub
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R14
M=D
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R13
M=D
@R13
D=M
@R14
D=D-M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:call Main.fibonacci 1
@return_address_1
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(return_address_1)

// vm command:push argument 0
@ARG
D=M
@0
A=D+A
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:push constant 1
@1
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:sub
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R14
M=D
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R13
M=D
@R13
D=M
@R14
D=D-M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:call Main.fibonacci 1
@return_address_2
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(return_address_2)

// vm command:add
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R14
M=D
// get the top element of stack
@SP
M=M-1
A=M
D=M
// store the result temporarily
@R13
M=D
@R13
D=M
@R14
D=D+M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:return
@LCL
D=M
@FRAME
M=D
@5
A=D-A
D=M
@RET
M=D
// get the top element of stack
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@FRAME
A=M-1
D=M
@THAT
M=D
@FRAME
D=M
@2
A=D-A
D=M
@THIS
M=D
@FRAME
D=M
@3
A=D-A
D=M
@ARG
M=D
@FRAME
D=M
@4
A=D-A
D=M
@LCL
M=D
@RET
A=M
0;JMP

// vm command:function Sys.init 0
(Sys.init)

// vm command:push constant 4
@4
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1

// vm command:call Main.fibonacci 1
@return_address_3
D=A
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
// push the value into stack
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(return_address_3)

// vm command:label WHILE
(WHILE)

// vm command:goto WHILE
@WHILE
0;JMP

