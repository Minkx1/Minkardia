""" 
**Lexical analyzer**(a.k.a. lexer) for Mikandria programming language
"""

from typing import Optional

from src.lex_structs import Token, TokenType, KEYWORDS, LexicalError


class Lexer:
    """Lexical analyzer realization"""
    WHITESPACE = " \t\n"
    ESCAPE_MAP = {
        "n": "\n",
        "t": "\t",
        "r": "\r",
        "\\": "\\",
        "'": "\'",
        "\"": "\"",
        "0": "\0"
    }

    def __init__(self, src_code: str | list[str]):
        self.code: list[str] = src_code.splitlines() if isinstance(src_code, str) else src_code
        self.line = 0 # for counting position of tokens
        self.char = 0
        self.tokens: list[Token] = [] # list of tokens, the result of tokenization
        self.eof = False # have reached the EOF  

    ## general methods

    def error(self, message: str) -> None:
        """Raises _LexicalError_ """
        raise LexicalError(message)

    def push_token(self, token: Optional[Token]) -> None:
        """Pushes token to the tokens list"""
        if isinstance(token, Token):
            self.tokens.append(token)

    ## characters methods

    def cur_char(self) -> str:
        """Returns: current charecter or '\\0' """
        if self.eof or not self.code:
            return "\0"
        return self.code[self.line][self.char]

    def peek_char(self):
        """Shows next character"""
        if self.eof or not self.code:
            return "\0"

        if self.char + 1 < len(self.code[self.line]):
            return self.code[self.line][self.char + 1]

        next_line = self.line + 1
        while next_line < len(self.code) and self.code[next_line] == "":
            next_line += 1

        if next_line < len(self.code):
            return self.code[next_line][0]
        return "\0"

    def advance(self):
        """Advancing to the next char"""
        if self.eof:
            return

        if self.char < len(self.code[self.line]) - 1:
            self.char += 1
        else:
            if self.line + 1 < len(self.code):
                self.char = 0
                self.line += 1
            else:
                self.eof = True

    def skip_trivia(self):
        while True:
            if self.cur_char() in Lexer.WHITESPACE: # if char is a space, tabulation or a new line
                self.advance()
                continue # advancing until we get a informative char

            if self.cur_char() == "/":
                if self.peek_char() == "/": # single-line comments
                    while not self.eof and self.cur_char() != "\n":
                        if self.char == len(self.code[self.line]) - 1: # if the end of line is reached: skipping to next line 
                            self.advance()
                            break
                        self.advance()
                    if self.cur_char() == "\n":
                        self.advance()  # skip "\n" after comment
                    continue

            break

    ## complex parsing

    def parse_number(self) -> Token:
        """Parses number literal"""
        start_line = self.line
        start_char = self.char

        num_string = ""

        while self.cur_char().isdigit():
            num_string += self.cur_char()
            self.advance()
        if self.cur_char() == ".":
            num_string += "."
            self.advance()
            if not self.cur_char().isdigit():
                self.error("Invalid number format")
            while self.cur_char().isdigit():
                num_string += self.cur_char()
                self.advance()

        if self.cur_char() == ".":
            self.error("Invalid number format")

        num = float(num_string) if "." in num_string else int(num_string)
        return Token(TokenType.NUMBER, num, start_line, start_char)

    def parse_string(self) -> Token:
        start_line = self.line
        start_col = self.char

        quote_char = self.cur_char()
        self.advance()  # Skip opening quote

        value = ""
        while self.cur_char() != quote_char and self.cur_char() != "\0":
            if self.cur_char() == "\\":
                self.advance()
                # Handle escape sequences
                escape_char = self.cur_char()
                esc_val: str|None = Lexer.ESCAPE_MAP.get(escape_char, None)

                if esc_val is None:
                    value += ("\\" + escape_char)
                else:
                    value += esc_val
                
                self.advance()
            else:
                value += self.cur_char()
                self.advance()

        if self.cur_char() != quote_char:
            self.error(f"Unterminated string.")

        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, value, start_line, start_col)

    def parse_identifier(self) -> Token:
        identifier = ""
        start_line = self.line
        start_char = self.char

        while self.cur_char().isalnum() or self.cur_char() == "_":
            identifier += self.cur_char()
            self.advance()

        t_type = KEYWORDS.get(identifier, TokenType.IDENTIFIER)
        if t_type == TokenType.TRUE:
            return Token(t_type, True, start_line, start_char)
        elif t_type == TokenType.FALSE:
            return Token(t_type, False, start_line, start_char)

        return Token(t_type, identifier, start_line, start_char)

    def parse_operators(self) -> Token:
        char = self.cur_char()
        start_line, start_char = self.line, self.char

        if char == "+":
            if self.peek_char() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.PLUS_ASSIGN, "+=", start_line, start_char)
            self.advance()
            return Token(TokenType.PLUS, "+", start_line, start_char)

        elif char == "-":
            if self.peek_char() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.MINUS_ASSIGN, "-=", start_line, start_char)
            elif self.peek_char() == ">":
                self.advance()
                self.advance()
                return Token(TokenType.ARROW, "->", start_line, start_char)
            self.advance()
            return Token(TokenType.MINUS, "-", start_line, start_char)

        elif char == "*":
            if self.peek_char() == "*":
                self.advance()
                self.advance()
                return Token(TokenType.POWER, "**", start_line, start_char)
            self.advance()
            return Token(TokenType.STAR, "*", start_line, start_char)

        elif char == "/":
            self.advance()
            return Token(TokenType.SLASH, "/", start_line, start_char)

        elif char == "%":
            self.advance()
            return Token(TokenType.PERCENT, "%", start_line, start_char)

        elif char == "=":
            if self.peek_char() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.EQ, "==", start_line, start_char)
            self.advance()
            return Token(TokenType.ASSIGN, "=", start_line, start_char)

        elif char == "!":
            if self.peek_char() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.NE, "!=", start_line, start_char)
            self.advance()
            return Token(TokenType.NOT, "!", start_line, start_char)

        elif char == "<":
            if self.peek_char() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.LE, "<=", start_line, start_char)
            self.advance()
            return Token(TokenType.LT, "<", start_line, start_char)

        elif char == ">":
            if self.peek_char() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.GE, ">=", start_line, start_char)
            self.advance()
            return Token(TokenType.GT, ">", start_line, start_char)

        elif char == "(":
            self.advance()
            return Token(TokenType.LPAREN, "(", start_line, start_char)
        elif char == ")":
            self.advance()
            return Token(TokenType.RPAREN, ")", start_line, start_char)
        elif char == "{":
            self.advance()
            return Token(TokenType.LBRACE, "{", start_line, start_char)
        elif char == "}":
            self.advance()
            return Token(TokenType.RBRACE, "}", start_line, start_char)
        elif char == "[":
            self.advance()
            return Token(TokenType.LBRACKET, "[", start_line, start_char)
        elif char == "]":
            self.advance()
            return Token(TokenType.RBRACKET, "]", start_line, start_char)
        elif char == ",":
            self.advance()
            return Token(TokenType.COMMA, ",", start_line, start_char)
        elif char == ".":
            self.advance()
            return Token(TokenType.DOT, ".", start_line, start_char)
        elif char == ":":
            self.advance()
            return Token(TokenType.COLON, ":", start_line, start_char)
        elif char == ";":
            self.advance()
            return Token(TokenType.SEMICOLON, ";", start_line, start_char)
        else:
            self.error(f"Unexpected character: {char}")

        return Token(TokenType.EOF, '\0', self.line, self.char)

    def tokenize(self) -> list[Token]:
        while not self.eof:
            self.skip_trivia()

            char = self.cur_char()

            if self.eof:
                break

            if char.isdigit():
                self.push_token(self.parse_number())
            elif char == '"' or char == "'":
                self.push_token(self.parse_string())
            elif char.isalpha() or char == "_":
                self.push_token(self.parse_identifier())
            else:
                self.push_token(self.parse_operators())

        if not self.tokens or self.tokens[-1].type != TokenType.EOF: # adding EOF token in the end of tokens list
            self.push_token(Token(TokenType.EOF, "\0", self.line, self.char))

        return self.tokens

def tokenize(source: str | list[str]) -> list[Token]:
    lexer = Lexer(source)
    return lexer.tokenize()