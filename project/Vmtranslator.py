import argparse
from enum import IntEnum
from pathlib import Path
from typing import TextIO, Dict, List, Tuple

from BaseUtils import BaseParser


class CommandType(IntEnum):
    C_ARITHMETIC = 1
    C_PUSH = 2
    C_POP = 3
    C_LABEL = 4
    C_GOTO = 5
    C_IF = 6
    C_FUNCTION = 7
    C_RETURN = 8
    C_CALL = 9


class SegmentType(IntEnum):
    S_ARGUMENT = 1      # 函数参数
    S_LOCAL = 2         # 函数局部变量
    S_STATIC = 3       # 同一vm文件所有函数共享的静态变量
    S_CONSTANT = 4      # 所有常数的伪段(0~32767)
    S_THIS = 5          # 通用段
    S_THAT = 6          # 通用段
    S_POINTER = 7       # 保存this/that的段基地址
    S_TEMP = 8          # 保存临时变量(R5 ~ R12)


Str2SegmentTypeMap: Dict[str, SegmentType] = {
    "argument": SegmentType.S_ARGUMENT,
    "local": SegmentType.S_LOCAL,
    "static": SegmentType.S_STATIC,
    "constant": SegmentType.S_CONSTANT,
    "this": SegmentType.S_THIS,
    "that": SegmentType.S_THAT,
    "pointer": SegmentType.S_POINTER,
    "temp": SegmentType.S_TEMP
}


SegmentType2LocalStrMap: Dict[SegmentType, str] = {
    SegmentType.S_LOCAL: "LCL",
    SegmentType.S_ARGUMENT: "ARG",
    SegmentType.S_THIS: "THIS",
    SegmentType.S_THAT: "THAT",
}


class ArithmeticType(IntEnum):
    A_ADD = 1
    A_SUB = 2
    A_NEG = 3
    A_EQ = 4
    A_GT = 5
    A_LT = 6
    A_AND = 7
    A_OR = 8
    A_NOT = 9


Str2ArithmeticMap: Dict[str, ArithmeticType] = {
    "add": ArithmeticType.A_ADD,
    "sub": ArithmeticType.A_SUB,
    "neg": ArithmeticType.A_NEG,
    "eq": ArithmeticType.A_EQ,
    "gt": ArithmeticType.A_GT,
    "lt": ArithmeticType.A_LT,
    "and": ArithmeticType.A_AND,
    "or": ArithmeticType.A_OR,
    "not": ArithmeticType.A_NOT
}

ArithmeticType2OptStr: Dict[ArithmeticType, str] = {
    ArithmeticType.A_ADD: '+',
    ArithmeticType.A_SUB: '-',
    ArithmeticType.A_AND: '&',
    ArithmeticType.A_OR: '|',
    ArithmeticType.A_EQ: 'EQ',
    ArithmeticType.A_GT: 'GT',
    ArithmeticType.A_LT: 'LT',
}


class Parser(BaseParser):

    def __init__(self, asm_object: TextIO):
        super().__init__(asm_object)
        self.current_cmd = None

    def advance(self):
        self.current_cmd = self.current_line

    def command_type(self) -> CommandType:
        if self.current_cmd.find("push") == 0:
            return CommandType.C_PUSH
        elif self.current_cmd.find("pop") == 0:
            return CommandType.C_POP
        elif self.current_cmd.find("label") == 0:
            return CommandType.C_LABEL
        elif self.current_cmd.find("goto") == 0:
            return CommandType.C_GOTO
        elif self.current_cmd.find("if-goto") == 0:
            return CommandType.C_IF
        elif self.current_cmd.find("function") == 0:
            return CommandType.C_FUNCTION
        elif self.current_cmd.find("call") == 0:
            return CommandType.C_CALL
        elif self.current_cmd.find("return") == 0:
            return CommandType.C_RETURN
        else:
            return CommandType.C_ARITHMETIC

    def arg1(self) -> str:
        result = self.current_cmd.split()[1]
        return result

    def arg2(self) -> str:
        result = self.current_cmd.split()[2]
        return result


class CodeWriter:

    def __init__(self, asm_file: str):
        self.asm_file = asm_file
        self.asm_obj = open(self.asm_file, "w")
        self.label_count = 0
        self.return_address_count = 0
        self.asm_filename = None

    def set_filename(self, filename: str):
        self.asm_filename = filename

    @staticmethod
    def push_value_snippets(value="D") -> str:
        commands = [
            "// push the value into stack",
            "@SP",
            "A=M",
            f"M={value}",
            "@SP",
            "M=M+1",
        ]
        return "\n".join(commands)

    @staticmethod
    def get_top_value_snippets() -> str:
        commands = [
            "// get the top element of stack",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
        ]
        return "\n".join(commands)

    @staticmethod
    def store_result_by_r14():
        commands = [
            "// store the result temporarily",
            "@R14",
            "M=D"
        ]
        return "\n".join(commands)

    @staticmethod
    def store_result_by_r13():
        commands = [
            "// store the result temporarily",
            "@R13",
            "M=D"
        ]
        return "\n".join(commands)

    @staticmethod
    def store_top_value_by_r13():
        commands = [
            "// store the top value",
            "@R13",
            "A=M",
            "M=D",
        ]
        return "\n".join(commands)

    def get_func_call_snippets(self, function_name: str, num_args: int):
        return_address = f"return_address_{self.return_address_count}"
        commands = [
            # push return-address
            f"@{return_address}",
            "D=A",
            self.push_value_snippets(),
            # push LCL"
            "@LCL",
            "D=M",
            self.push_value_snippets(),
            # push ARG
            "@ARG",
            "D=M",
            self.push_value_snippets(),
            # push THIS
            "@THIS",
            "D=M",
            self.push_value_snippets(),
            # push THAT
            "@THAT",
            "D=M",
            self.push_value_snippets(),
            # ARG = SP-n-5
            "@SP",
            "D=M",
            f"@{num_args}",
            "D=D-A",
            f"@5",
            "D=D-A",
            "@ARG",
            "M=D",
            # LCL = SP
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            # goto f
            f"@{function_name}",
            "0;JMP",
            f"({return_address})",
        ]
        self.return_address_count += 1
        return "\n".join(commands)

    def write_commands(self, asm_commands: List[str]):
        write_commands = "\n".join(asm_commands) + "\n"
        self.asm_obj.write(write_commands)

    def write_init(self):
        asm_commands = [
            "@256",
            "D=A",
            "@SP",
            "M=D",
            self.get_func_call_snippets("Sys.init", 0),
        ]
        self.write_commands(asm_commands)

    def write_label(self, label: str):
        asm_commands = [
            f"({label})",
        ]
        self.write_commands(asm_commands)

    def write_goto(self, label: str):
        asm_commands = [
            f"@{label}",
            "0;JMP",
        ]
        self.write_commands(asm_commands)

    def write_if(self, label: str):
        asm_commands = [
            self.get_top_value_snippets(),
            f"@{label}",
            "D;JNE",
        ]
        self.write_commands(asm_commands)

    def write_call(self, function_name: str, num_args: int):
        self.asm_obj.write(self.get_func_call_snippets(function_name, num_args) + "\n")

    def write_return(self):
        asm_commands = [
            # Frame = LCL
            "@LCL",
            "D=M",
            "@FRAME",
            "M=D",
            # RET = *(FRAME - 5)
            "@5",
            "A=D-A",
            "D=M",
            "@RET",
            "M=D",
            # *ARG = pop()
            self.get_top_value_snippets(),
            "@ARG",
            "A=M",
            "M=D",
            # SP = ARG+1
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",
            # THAT = *(FRAME-1)
            "@FRAME",
            "A=M-1",
            "D=M",
            "@THAT",
            "M=D",
            # THIS = *(FRAME-2)
            "@FRAME",
            "D=M",
            "@2",
            "A=D-A",
            "D=M",
            "@THIS",
            "M=D",
            # ARG = *(FRAME-3)
            "@FRAME",
            "D=M",
            "@3",
            "A=D-A",
            "D=M",
            "@ARG",
            "M=D",
            # LCL = *(FRAME=4)
            "@FRAME",
            "D=M",
            "@4",
            "A=D-A",
            "D=M",
            "@LCL",
            "M=D",
            # goto RET
            "@RET",
            "A=M",
            "0;JMP",

        ]
        self.write_commands(asm_commands)

    def write_function(self, function_name: str, num_locals: int):
        asm_commands = [
            f"({function_name})",
        ] + [self.push_value_snippets("0") for _ in range(num_locals)]
        self.write_commands(asm_commands)

    def write_arithmetic(self, command: ArithmeticType):
        asm_commands = []

        if command in (ArithmeticType.A_ADD, ArithmeticType.A_SUB, ArithmeticType.A_AND, ArithmeticType.A_OR):
            cmd_opt = ArithmeticType2OptStr[command]
            asm_commands = [
                self.get_top_value_snippets(),
                self.store_result_by_r14(),
                self.get_top_value_snippets(),
                self.store_result_by_r13(),
                "@R13",
                "D=M",
                "@R14",
                f"D=D{cmd_opt}M",
                self.push_value_snippets(),
            ]
        elif command in (ArithmeticType.A_EQ, ArithmeticType.A_GT, ArithmeticType.A_LT):
            cmd_opt = ArithmeticType2OptStr[command]
            asm_commands = [
                self.get_top_value_snippets(),
                self.store_result_by_r14(),
                self.get_top_value_snippets(),
                self.store_result_by_r13(),
                "@R13",
                "D=M",
                "@R14",
                "D=D-M",
                f"@{cmd_opt}{self.label_count}",
                f"D;J{cmd_opt}",
                self.push_value_snippets(value="0"),
                f"@END{cmd_opt}{self.label_count}",
                "0;JMP",
                f"({cmd_opt}{self.label_count})",
                self.push_value_snippets(value="-1"),
                f"(END{cmd_opt}{self.label_count})",
            ]
            self.label_count += 1
        elif command == ArithmeticType.A_NEG:
            asm_commands = [
                self.get_top_value_snippets(),
                "@0",
                "D=A-D",
                self.push_value_snippets(),
            ]
        elif command == ArithmeticType.A_NOT:
            asm_commands = [
                self.get_top_value_snippets(),
                "D=!D",
                self.push_value_snippets(),
            ]

        self.write_commands(asm_commands)

    def write_push_pop(self, command_type: CommandType, segment: SegmentType, index: int):
        asm_commands = []
        if command_type == CommandType.C_PUSH:
            if segment == SegmentType.S_CONSTANT:
                asm_commands = [
                    f"@{index}",
                    "D=A",
                    self.push_value_snippets(),
                ]
            elif segment in (SegmentType.S_TEMP, SegmentType.S_LOCAL, SegmentType.S_ARGUMENT, SegmentType.S_THIS, SegmentType.S_THAT):
                if segment == SegmentType.S_TEMP:
                    local = "R5"
                    local_data = 'A'
                else:
                    local = SegmentType2LocalStrMap[segment]
                    local_data = 'M'
                asm_commands = [
                    f"@{local}",
                    f"D={local_data}",
                    f"@{index}",
                    "A=D+A",
                    "D=M",
                    self.push_value_snippets(),
                ]
            elif segment == SegmentType.S_POINTER:
                asm_commands = [
                    "@THIS",
                    "D=A",
                    f"@{index}",
                    "A=D+A",
                    "D=M",
                    self.push_value_snippets(),
                ]
            elif segment == SegmentType.S_STATIC:
                asm_commands = [
                    f"@{self.asm_filename}.{index}",
                    "D=M",
                    self.push_value_snippets(),
                ]
        elif command_type == CommandType.C_POP:
            if segment in (SegmentType.S_TEMP, SegmentType.S_LOCAL, SegmentType.S_ARGUMENT, SegmentType.S_THIS, SegmentType.S_THAT):
                if segment == SegmentType.S_TEMP:
                    local = "5"
                    local_data = 'A'
                else:
                    local = SegmentType2LocalStrMap[segment]
                    local_data = 'M'
                asm_commands = [
                    f"@{local}",
                    f"D={local_data}",
                    f"@{index}",
                    "D=D+A",
                    self.store_result_by_r13(),
                    self.get_top_value_snippets(),
                    self.store_top_value_by_r13(),
                ]
            elif segment == SegmentType.S_POINTER:
                asm_commands = [
                    "@THIS",
                    "D=A",
                    f"@{index}",
                    "D=D+A",
                    self.store_result_by_r13(),
                    self.get_top_value_snippets(),
                    self.store_top_value_by_r13(),
                ]
            elif segment == SegmentType.S_STATIC:
                asm_commands = [
                    self.get_top_value_snippets(),
                    f"@{self.asm_filename}.{index}",
                    "M=D",
                ]

        self.write_commands(asm_commands)

    def close(self):
        self.asm_obj.close()


class Vmtranslator:

    @staticmethod
    def handler_vm_file_or_dir(vm_file_or_dir: str) -> Tuple[str, List[Path]]:
        vm_path = Path(vm_file_or_dir)
        if vm_path.is_file():
            return str(Path(vm_file_or_dir).with_suffix('.asm')), [Path(vm_file_or_dir)]
        elif vm_path.is_dir():
            vm_files = list(vm_path.glob("*.vm"))
            asm_file_name = str(vm_path.with_suffix('.asm'))
            return asm_file_name, vm_files

    def __init__(self, vm_file_or_dir: str, bootstrap=True):
        self.bootstrap = bootstrap
        self.asm_file, self.vm_files = self.handler_vm_file_or_dir(vm_file_or_dir)
        self.code_writer = CodeWriter(self.asm_file)
        self.parser = None

    def translator(self):
        if self.bootstrap:
            self.code_writer.write_init()

        for vm_file in self.vm_files:
            vm_file_object = open(vm_file)
            self.parser = Parser(vm_file_object)
            self.code_writer.set_filename(vm_file.stem)

            while self.parser.has_more_commands():
                self.parser.advance()
                self.code_writer.asm_obj.write(f"// vm command:{self.parser.current_cmd}\n")
                command_type = self.parser.command_type()
                if command_type in (CommandType.C_PUSH, CommandType.C_POP):
                    segment = Str2SegmentTypeMap[self.parser.arg1()]
                    index = int(self.parser.arg2())
                    self.code_writer.write_push_pop(command_type, segment, index)
                elif command_type == CommandType.C_ARITHMETIC:
                    command = Str2ArithmeticMap[self.parser.current_cmd]
                    self.code_writer.write_arithmetic(command)
                elif command_type == CommandType.C_LABEL:
                    self.code_writer.write_label(self.parser.arg1())
                elif command_type == CommandType.C_GOTO:
                    self.code_writer.write_goto(self.parser.arg1())
                elif command_type == CommandType.C_IF:
                    self.code_writer.write_if(self.parser.arg1())
                elif command_type == CommandType.C_RETURN:
                    self.code_writer.write_return()
                elif command_type == CommandType.C_FUNCTION:
                    self.code_writer.write_function(self.parser.arg1(), int(self.parser.arg2()))
                elif command_type == CommandType.C_CALL:
                    self.code_writer.write_call(self.parser.arg1(), int(self.parser.arg2()))
                self.code_writer.asm_obj.write("\n")
            vm_file_object.close()
        self.code_writer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Vmtranslator")
    parser.add_argument("vm_file_or_dir", type=str, help="vm file or dir path")
    parser.add_argument('--no-bootstrap', '-n', help="don't add bootstrap code", action="store_true")
    args = parser.parse_args()
    Vmtranslator(args.vm_file_or_dir, not args.no_bootstrap).translator()
