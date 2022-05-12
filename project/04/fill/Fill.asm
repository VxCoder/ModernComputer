// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// Put your code here.
(LOOP)
@8191
D=A
@num
M=D

@KBD
D=M
@WHITE
D;JEQ

@i
M=0
(LOOP1)
@i
D=M
@num
D=D-M
@LOOP
D;JEQ 

@SCREEN
D=A
@i
A=D+M
M=0
M=!M
@i
M=M+1
@LOOP1
0;JMP

@LOOP
0;JMP

(WHITE)
@i
M=0
(LOOP2)
@i
D=M
@num
D=D-M
@LOOP
D;JEQ 

@SCREEN
D=A
@i
A=D+M
M=0
@i
M=M+1
@LOOP2
0;JMP

@LOOP
0;JMP