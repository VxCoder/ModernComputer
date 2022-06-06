import argparse
import functools
from enum import IntEnum
from pathlib import Path
from typing import TextIO, List, Dict
from xml.etree.ElementTree import SubElement, ElementTree, Element, indent


class TokenType(IntEnum):
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5


class KeywordType(IntEnum):
    CLASS = 1
    METHOD = 2
    INT = 3
    FUNCTION = 4
    BOOLEAN = 5
    CONSTRUCTOR = 6
    CHAR = 7
    VOID = 8
    VAR = 9
    STATIC = 10
    FIELD = 11
    LET = 12
    DO = 13
    IF = 14
    ELSE = 15
    WHILE = 16
    RETURN = 17
    TRUE = 18
    FALSE = 19
    NULL = 20
    THIS = 21


Str2KeywordType: Dict[str, KeywordType] = {
    "class": KeywordType.CLASS,
    "constructor": KeywordType.CONSTRUCTOR,
    "function": KeywordType.FUNCTION,
    "method": KeywordType.METHOD,
    "field": KeywordType.FIELD,
    "static": KeywordType.STATIC,
    "var": KeywordType.VAR,
    "int": KeywordType.INT,
    "char": KeywordType.CHAR,
    "boolean": KeywordType.BOOLEAN,
    "void": KeywordType.VOID,
    "true": KeywordType.TRUE,
    "false": KeywordType.FALSE,
    "null": KeywordType.NULL,
    "this": KeywordType.THIS,
    "let": KeywordType.LET,
    "do": KeywordType.DO,
    "if": KeywordType.IF,
    "else": KeywordType.ELSE,
    "while": KeywordType.WHILE,
    "return": KeywordType.RETURN
}

KeywordType2Str: Dict[KeywordType, str] = {value: key for key, value in Str2KeywordType.items()}
KeyWords = set(Str2KeywordType.keys())

Symbols = set("{}()[].,;+-*/&|<>=~")
OpSymbols = set("+-*/&|<>=")
UnaryOpSymbols = set('-~')


class JackTokenizer:

    def __init__(self, parse_object: TextIO):
        self.parse_object = parse_object
        self.buffer = []
        self.preview_char = None

        self.token = ""
        self._token_type = None
        self._token_value = None

        self._next_token_value = None
        self._next_token_type = None

        # 先取一个符号
        self.has_more_commands()
        self.gen_token_info()

    def gen_token_info(self):
        self.token = "".join(self.buffer)
        self.buffer = []
        self.gen_token_type_and_value()

    def ignore_comments(self, char):
        if char == '/':   # // 类注释 到行尾
            while self.parse_object.read(1) != '\n':
                pass
        elif char == '*':  # /* 类注释 到 */
            preview = ''
            while char := self.parse_object.read(1):
                if preview == '*' and char == '/':
                    break
                else:
                    preview = char

    def has_more_commands(self) -> True:
        if self.preview_char in Symbols:
            self.buffer.append(self.preview_char)
            self.preview_char = None
            return True

        while char := self.preview_char or self.parse_object.read(1):  # 这样可支持流式输入
            self.preview_char = None
            if char == '/':
                next_char = self.parse_object.read(1)
                if next_char in "*/":
                    self.ignore_comments(next_char)
                else:
                    self.buffer.append(char)
                    if next_char != " ":
                        self.preview_char = next_char
                    break
            elif char in Symbols:
                # 比较丑陋的实现
                if not self.buffer:
                    self.buffer.append(char)
                else:
                    self.preview_char = char
                break
            elif char == '"':
                self.buffer.append(char)
                while (char := self.parse_object.read(1)) != '"':
                    self.buffer.append(char)
                self.buffer.append(char)
                break
            elif char not in ('\n', '\t', '', ' '):
                self.buffer.append(char)
            else:
                if self.buffer:
                    break
        return len(self.buffer) > 0

    def gen_token_type_and_value(self):
        if self.token in KeyWords:
            self._next_token_type = TokenType.KEYWORD
            self._next_token_value = Str2KeywordType[self.token]
        elif self.token in Symbols:
            self._next_token_type = TokenType.SYMBOL
            self._next_token_value = self.token
        elif self.token.isnumeric():
            self._next_token_type = TokenType.INT_CONST
            self._next_token_value = int(self.token)
        elif self.token.startswith('"'):
            self._next_token_type = TokenType.STRING_CONST
            self._next_token_value = self.token[1:-1]
        else:
            self._next_token_type = TokenType.IDENTIFIER
            self._next_token_value = self.token

    def advance(self):
        self._token_type = self._next_token_type
        self._token_value = self._next_token_value

        # 提前获取下一个token
        self.has_more_commands()
        self.gen_token_info()
        return self.token

    @property
    def next_token_type(self) -> TokenType:
        return self._next_token_type

    @property
    def next_token_value(self):
        return self._next_token_value

    @property
    def token_type(self) -> TokenType:
        return self._token_type

    @property
    def token_value(self):
        return self._token_value

    @property
    def keyword(self) -> KeywordType:
        return self._token_value

    @property
    def symbol(self) -> str:
        return self._token_value

    @property
    def identifier(self) -> str:
        return self._token_value

    @property
    def int_value(self) -> int:
        return self._token_value

    @property
    def string_value(self) -> str:
        return self._token_value


def sub_element(sub_name):
    def wrapper(func):
        @functools.wraps(func)
        def wraps(self: "CompilationEngine", *args, **kwargs):
            old_root = self.current_root
            self.current_root = SubElement(self.current_root, sub_name)
            self.indent += 1
            func(self, *args, **kwargs)
            self.indent -= 1
            self.current_root = old_root
        return wraps
    return wrapper


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer, file_name):
        self.tokenizer = tokenizer
        self.current_root = None
        self.root = None
        self.file_name = file_name
        self.class_name = None
        self.indent = 0

    def advance_and_check_token(self, token_type: TokenType, token_value=None, token_values=None):
        self.tokenizer.advance()
        if token_type != self.tokenizer.token_type:
            raise Exception(f"expect token_type[{token_type}] get token_type[{self.tokenizer.token_type}]")
        if token_value is not None and self.tokenizer.token_value != token_value:
            raise Exception(f"expect token_value[{token_value}] get token_value[{self.tokenizer.token_value}]")
        if token_values is not None and self.tokenizer.token_value not in token_values:
            raise Exception(f"expect token_values in [{token_values}] get token_value[{self.tokenizer.token_value}]")

    def check_token(self, token_type: TokenType, token_value=None, token_values=None) -> bool:
        if token_type != self.tokenizer.token_type:
            return False
        if token_value is not None and self.tokenizer.token_value != token_value:
            return False
        if token_values is not None and self.tokenizer.token_value not in token_values:
            return False
        return True

    def check_next_token(self, token_type: TokenType, token_value=None, token_values=None) -> bool:
        if token_type != self.tokenizer.next_token_type:
            return False
        if token_value is not None and self.tokenizer.next_token_value != token_value:
            return False
        if token_values is not None and self.tokenizer.next_token_value not in token_values:
            return False
        return True

    def gen_keyword_content(self):
        SubElement(self.current_root, "keyword").text = f" {KeywordType2Str[self.tokenizer.token_value]} "

    def gen_identifier_content(self):
        SubElement(self.current_root, "identifier").text = f" {self.tokenizer.token_value} "

    def gen_symbol_content(self):
        SubElement(self.current_root, "symbol").text = f" {self.tokenizer.token_value} "

    def gen_integer_constant_content(self):
        SubElement(self.current_root, "integerConstant").text = f" {self.tokenizer.token_value} "

    def gen_string_constant_content(self):
        SubElement(self.current_root, "stringConstant").text = f" {self.tokenizer.token_value} "

    def check_next_symbol(self, symbol_value=None, symbol_values=None) -> bool:
        return self.check_next_token(TokenType.SYMBOL, symbol_value, symbol_values)

    def check_symbol(self, symbol_value=None, symbol_values=None) -> bool:
        return self.check_token(TokenType.SYMBOL, symbol_value, symbol_values)

    def compile_symbol(self, symbol_value=None, symbol_values=None):
        self.advance_and_check_token(TokenType.SYMBOL, symbol_value, symbol_values)
        self.gen_symbol_content()

    def compile_identifier(self):
        self.advance_and_check_token(TokenType.IDENTIFIER)
        self.gen_identifier_content()

    def compile_var_name(self):
        self.compile_identifier()

    def compile_classname(self):
        self.compile_identifier()
        self.class_name = self.tokenizer.token_value

    def compile_keyword(self, keyword=None, keywords=None):
        self.advance_and_check_token(TokenType.KEYWORD, keyword, keywords)
        self.gen_keyword_content()

    def compile(self):
        try:
            self.compile_class()
        except Exception as error:
            print(f"************** {error}")
        xml_tree = ElementTree(self.root)
        indent(xml_tree)
        xml_tree.write(f'{self.file_name}.xml', encoding='utf-8', short_empty_elements=False)

    def compile_class(self):
        """
            'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.root = self.current_root = Element("class")

        self.compile_keyword(KeywordType.CLASS)
        self.compile_classname()
        self.compile_symbol('{')

        # classVarDec*
        while self.check_next_token(TokenType.KEYWORD, token_values={KeywordType.STATIC, KeywordType.FIELD}):
            self.compile_class_var_dec()

        # subroutineDec*
        while self.check_next_token(TokenType.KEYWORD, token_values={KeywordType.CONSTRUCTOR, KeywordType.FUNCTION, KeywordType.METHOD}):
            self.compile_subroutine()

        self.compile_symbol('}')

    @sub_element("classVarDec")
    def compile_class_var_dec(self):
        """
            ('static'|'filed') type varName (',' varName)* ';'
        """
        # ('static'|'filed')
        self.advance_and_check_token(TokenType.KEYWORD, token_values={KeywordType.STATIC, KeywordType.FIELD})
        self.gen_keyword_content()

        self.compile_type()
        self.compile_var_name()

        while self.check_next_symbol(","):
            self.compile_symbol(",")
            self.compile_var_name()

        self.compile_symbol(";")

    @sub_element("subroutineDec")
    def compile_subroutine(self):
        """
            ('constructor' | 'function' | 'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody
        """
        # ('constructor' | 'function' | 'method')
        self.advance_and_check_token(TokenType.KEYWORD, token_values={KeywordType.CONSTRUCTOR, KeywordType.FUNCTION, KeywordType.METHOD})
        self.gen_keyword_content()

        # ('void'|type)
        self.compile_type()

        # subroutineName
        self.compile_identifier()

        self.compile_symbol('(')
        self.compile_parameter_list()
        self.compile_symbol(')')

        self.compile_subroutine_body()

    def compile_type(self):
        self.tokenizer.advance()
        if self.check_token(TokenType.KEYWORD, token_values={KeywordType.VOID, KeywordType.INT, KeywordType.CHAR, KeywordType.BOOLEAN}):
            self.gen_keyword_content()
        elif self.check_token(TokenType.IDENTIFIER):
            self.gen_identifier_content()

    @sub_element("parameterList")
    def compile_parameter_list(self, finish_char=')'):
        """
            (type varName)(',' type varName)*
        """
        if self.check_next_symbol(finish_char):
            self.current_root.text = f"\n{self.indent*'  '}"
            return

        self.compile_type()
        self.compile_var_name()

        # ',' type varName)*
        while self.check_next_symbol(','):
            self.compile_symbol(',')
            self.compile_type()
            self.compile_var_name()

    @sub_element("subroutineBody")
    def compile_subroutine_body(self):
        """
            '{‘ varDec* statement '}'
        """
        self.compile_symbol('{')

        # varDec*
        while self.check_next_token(TokenType.KEYWORD, KeywordType.VAR):
            self.compile_var_dec()
        self.compile_statements()
        self.compile_symbol('}')

    @sub_element("varDec")
    def compile_var_dec(self):
        """
            ’var‘ type varName (',' varName)* ';'
        """
        # var
        self.advance_and_check_token(TokenType.KEYWORD, token_value=KeywordType.VAR)
        self.gen_keyword_content()

        self.compile_type()
        self.compile_var_name()

        while self.check_next_symbol(","):
            self.compile_symbol(",")
            self.compile_var_name()

        self.compile_symbol(";")

    @sub_element("statements")
    def compile_statements(self):

        while self.check_next_token(TokenType.KEYWORD, token_values={
            KeywordType.LET, KeywordType.IF, KeywordType.WHILE, KeywordType.DO, KeywordType.RETURN
        }):
            if self.check_next_token(TokenType.KEYWORD, token_value=KeywordType.LET):
                self.compile_let()
            elif self.check_next_token(TokenType.KEYWORD, token_value=KeywordType.DO):
                self.compile_do()
            elif self.check_next_token(TokenType.KEYWORD, token_value=KeywordType.RETURN):
                self.compile_return()
            elif self.check_next_token(TokenType.KEYWORD, token_value=KeywordType.IF):
                self.compile_if()
            elif self.check_next_token(TokenType.KEYWORD, token_value=KeywordType.WHILE):
                self.compile_while()

    def compile_subroutine_call(self):
        # subroutineName
        self.advance_and_check_token(TokenType.IDENTIFIER)
        self.gen_identifier_content()

        if self.check_next_token(TokenType.SYMBOL, "."):
            self.compile_symbol(".")

            self.advance_and_check_token(TokenType.IDENTIFIER)
            self.gen_identifier_content()

        self.compile_symbol('(')
        self.compile_expression_list()
        self.compile_symbol(')')

    @sub_element("doStatement")
    def compile_do(self):
        """
            'do' subroutineCall ';'

        """
        # do
        self.advance_and_check_token(TokenType.KEYWORD, KeywordType.DO)
        self.gen_keyword_content()

        # subroutineCall
        self.compile_subroutine_call()

        self.compile_symbol(";")

    @sub_element("letStatement")
    def compile_let(self):
        """
            'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.compile_keyword(KeywordType.LET)

        self.compile_var_name()

        # ('[' expression ']')?
        if self.check_next_symbol("["):
            self.compile_symbol("[")
            self.compile_expression()
            self.compile_symbol("]")

        self.compile_symbol("=")
        self.compile_expression()
        self.compile_symbol(";")

    @sub_element("whileStatement")
    def compile_while(self):
        self.advance_and_check_token(TokenType.KEYWORD, KeywordType.WHILE)
        self.gen_keyword_content()

        self.compile_symbol('(')
        self.compile_expression()
        self.compile_symbol(')')

        self.compile_symbol('{')
        self.compile_statements()
        self.compile_symbol('}')

    @sub_element("returnStatement")
    def compile_return(self):
        """
            'return' expression? ';'
        """
        self.advance_and_check_token(TokenType.KEYWORD, KeywordType.RETURN)
        self.gen_keyword_content()

        if not self.check_next_symbol(";"):
            self.compile_expression()

        self.compile_symbol(";")

    @sub_element("ifStatement")
    def compile_if(self):
        self.compile_keyword(KeywordType.IF)

        self.compile_symbol('(')
        self.compile_expression()
        self.compile_symbol(')')

        self.compile_symbol('{')
        self.compile_statements()
        self.compile_symbol('}')

        if self.check_next_token(TokenType.KEYWORD, KeywordType.ELSE):
            self.compile_keyword(KeywordType.ELSE)
            self.compile_symbol('{')
            self.compile_statements()
            self.compile_symbol('}')

    @sub_element("expression")
    def compile_expression(self):
        """
            term (op term)*
        """
        self.compile_term()

        # (op term)*
        while self.check_next_symbol(symbol_values=OpSymbols):
            self.compile_symbol(symbol_values=OpSymbols)
            self.compile_term()

    @sub_element("term")
    def compile_term(self):
        self.tokenizer.advance()
        if self.check_token(TokenType.IDENTIFIER):
            self.gen_identifier_content()
            if self.check_next_symbol("."):
                self.compile_symbol(".")
                self.compile_identifier()
                self.compile_symbol("(")
                self.compile_expression_list()
                self.compile_symbol(")")
            elif self.check_next_symbol("["):
                self.compile_symbol("[")
                self.compile_expression()
                self.compile_symbol("]")
        elif self.check_token(TokenType.KEYWORD):
            self.gen_keyword_content()
        elif self.check_token(TokenType.INT_CONST):
            self.gen_integer_constant_content()
        elif self.check_token(TokenType.STRING_CONST):
            self.gen_string_constant_content()
        elif self.check_token(TokenType.SYMBOL, '('):
            self.gen_symbol_content()
            self.compile_expression()
            self.compile_symbol(")")
        elif self.check_symbol(symbol_values=UnaryOpSymbols):
            self.gen_symbol_content()
            self.compile_term()

    @sub_element("expressionList")
    def compile_expression_list(self, finish_char=')'):
        """
            (expression (',' expression)*)?
        """
        if self.check_next_symbol(finish_char):
            self.current_root.text = f"\n{self.indent*'  '}"
            return

        self.compile_expression()

        # (',' expression)*
        while self.check_next_symbol(","):
            self.compile_symbol(",")
            self.compile_expression()


class JackAnalyzer:

    @staticmethod
    def handler_jack_file_or_dir(jack_file_or_dir: str) -> List[Path]:
        jack_path = Path(jack_file_or_dir)
        if jack_path.is_file():
            return [jack_path]
        elif jack_path.is_dir():
            jack_files = list(jack_path.glob("*.jack"))
            return jack_files

    def __init__(self, jack_file_or_dir: str):
        self.jack_files = self.handler_jack_file_or_dir(jack_file_or_dir)

    def analyzer(self):
        for jack_file in self.jack_files:
            jack_file_object = open(jack_file)
            tokenizer = JackTokenizer(open(jack_file))
            engine = CompilationEngine(tokenizer, jack_file.stem)
            engine.compile()
            jack_file_object.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="JackAnalyzer")
    parser.add_argument("jack_file_or_dir", type=str, help="jack file or dir path")
    input_args = parser.parse_args()
    JackAnalyzer(input_args.jack_file_or_dir).analyzer()
