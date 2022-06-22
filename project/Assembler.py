import re
import sys
from collections import OrderedDict
from enum import IntEnum
from pathlib import Path
from typing import Tuple, Optional, TextIO

from BaseUtils import BaseParser

SYMBOL_PATTERN = re.compile(r'[a-zA-Z_.$:][0-9a-zA-Z_.$:]*')
COMP_PATTERN = re.compile(r'([AMD]*=)?(?P<comp>[ADM+\-&!01|]+)(;[A-Z]+)?')


class CommandType(IntEnum):
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3


class SymbolTable:

    def __init__(self):
        self.table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KDB": 24576,
        }

    def add_entry(self, symbol: str, address: int):
        self.table[symbol] = address

    def contains(self, symbol: str) -> bool:
        return symbol in self.table

    def get_address(self, symbol: str) -> int:
        return self.table[symbol]


class Parser(BaseParser):

    def __init__(self, asm_object: TextIO):
        super().__init__(asm_object)
        self.current_cmd = None

    def advance(self):
        self.current_cmd = self.current_line

    @property
    def command_type(self) -> CommandType:
        if self.current_cmd.find("@") >= 0:
            return CommandType.A_COMMAND
        elif self.current_cmd.find("(") >= 0:
            return CommandType.L_COMMAND
        else:
            return CommandType.C_COMMAND

    @property
    def symbol(self) -> str:
        if self.command_type == CommandType.A_COMMAND:
            return self.current_cmd.split("@")[1]
        elif self.command_type == CommandType.L_COMMAND:
            return self.current_cmd[1:-1]
        else:
            raise Exception("C_COMMAND cannot get symbol")

    @property
    def dest(self) -> Optional[str]:
        if self.current_cmd.find("=") >= 0:
            return self.current_cmd.split("=")[0]
        else:
            return None

    @property
    def comp(self) -> Optional[str]:
        if match := COMP_PATTERN.match(self.current_cmd):
            return match.groupdict()['comp']
        else:
            print("not find comp!!!")
            return None

    @property
    def jump(self) -> Optional[str]:
        if self.current_cmd.find(";") >= 0:
            return self.current_cmd.split(";")[1]
        else:
            return None


class Code:
    JUMP_TABLE = {
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111"
    }

    COMP_TABLE = {
        '0': '0101010',
        '1': '0111111',
        '-1': '0111010',
        'D': '0001100',
        'A': '0110000',
        'M': '1110000',
        '!D': '0001101',
        '!A': '0110001',
        '!M': '1110001',
        '-D': '0001111',
        '-A': '0110011',
        '-M': '1110011',
        'D+1': '0011111',
        '1+D': '0011111',
        'A+1': '0110111',
        '1+A': '0110111',
        'M+1': '1110111',
        '1+M': '1110111',
        'D-1': '0001110',
        'A-1': '0110010',
        'M-1': '1110010',
        'D+A': '0000010',
        'A+D': '0000010',
        'D+M': '1000010',
        'M+D': '1000010',
        'D-A': '0010011',
        'D-M': '1010011',
        'A-D': '0000111',
        'M-D': '1000111',
        'D&A': '0000000',
        'A&D': '0000000',
        'D&M': '1000000',
        'M&D': '1000000',
        'D|A': '0010101',
        'A|D': '0010101',
        'D|M': '1010101',
        'M|D': '1010101',
    }

    @classmethod
    def dest(cls, cmd: Optional[str]) -> str:
        if cmd is None:
            return '000'
        d1 = '1' if 'A' in cmd else '0'
        d2 = '1' if 'D' in cmd else '0'
        d3 = '1' if 'M' in cmd else '0'
        return f"{d1}{d2}{d3}"

    @classmethod
    def comp(cls, cmd: str) -> str:
        # 没发现规律,简单粗暴方案
        return cls.COMP_TABLE[cmd]

    @classmethod
    def jump(cls, cmd: Optional[str]) -> Tuple[str, str, str]:
        return cls.JUMP_TABLE.get(cmd, "000")


class Assembler:

    def __init__(self, asm_file):
        self.asm_file = asm_file
        self.hack_file = Path(asm_file).with_suffix(".hack")
        self.symbol_table = SymbolTable()
        self.parser = None

    def first_assemble(self):
        """ 遍历发现符号，并赋予地址"""
        asm_object = open(self.asm_file)
        self.parser = Parser(asm_object)
        pc_count = 0

        value_table = OrderedDict()

        while self.parser.has_more_commands():
            self.parser.advance()
            command_type = self.parser.command_type
            if command_type == CommandType.A_COMMAND:
                if symbol := SYMBOL_PATTERN.match(self.parser.symbol):
                    if symbol.string not in value_table and not self.symbol_table.contains(symbol.string):
                        value_table[symbol.string] = 1
            elif command_type == CommandType.L_COMMAND:
                self.symbol_table.add_entry(self.parser.symbol, pc_count)
                value_table.pop(self.parser.symbol, None)
                continue
            pc_count += 1

        address_count = 16
        for key in value_table:
            self.symbol_table.add_entry(key, address_count)
            address_count += 1

        asm_object.close()

    def second_assemble(self):
        asm_object = open(self.asm_file)
        self.parser = Parser(asm_object)
        hack_object = open(self.hack_file, "w")

        while self.parser.has_more_commands():
            self.parser.advance()
            command_type = self.parser.command_type
            if command_type == CommandType.A_COMMAND:
                if symbol := SYMBOL_PATTERN.match(self.parser.symbol):
                    address = self.symbol_table.get_address(symbol.string)
                else:
                    address = int(self.parser.symbol)
                print(f"0{address:0>15b}", file=hack_object)

            elif command_type == CommandType.C_COMMAND:
                dest = Code.dest(self.parser.dest)
                comp = Code.comp(self.parser.comp)
                jump = Code.jump(self.parser.jump)
                print(f"111{comp}{dest}{jump}", file=hack_object)

        asm_object.close()
        hack_object.close()

    def assemble(self):
        self.first_assemble()
        self.second_assemble()


if __name__ == '__main__':
    Assembler(sys.argv[1]).assemble()
