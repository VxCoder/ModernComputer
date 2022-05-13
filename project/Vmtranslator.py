import sys
from enum import IntEnum
from typing import TextIO

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


class Parser(BaseParser):

    def __init__(self, asm_object: TextIO):
        super().__init__(asm_object)
        self.current_cmd = None

    def advance(self):
        self.current_cmd = self.current_line

    def command_type(self) -> CommandType:
        pass

    def arg1(self):
        pass

    def arg2(self):
        pass


class CodeWriter:

    def write_arithmetic(self):
        pass

    def write_push_pop(self):
        pass


class Vmtranslator:

    def __init__(self):
        pass

    def translator(self):
        pass


if __name__ == '__main__':
    Vmtranslator(sys.argv[1]).translator()
