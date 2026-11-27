from dataclasses import dataclass
from enum import Enum, auto
from typing import Any



class TokenType(Enum):
    """Token types"""

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()

    WHILE = auto()
    FOR = auto()

    TRY = auto()
    EXCEPT = auto()
    NOT = auto()  # !

    # Operators
    ASSIGN = auto()  # =
    PLUS = auto()  # +
    MINUS = auto()  # -
    PLUS_ASSIGN = auto()  # +=
    MINUS_ASSIGN = auto()  # -=
    STAR = auto()  # *
    SLASH = auto()  # /
    PERCENT = auto()  # %
    POWER = auto()  # **

    # Comparison
    EQ = auto()  # ==
    NE = auto()  # !=
    LT = auto()  # <
    LE = auto()  # <=
    GT = auto()  # >
    GE = auto()  # >=

    # Delimiters
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()  # ,
    DOT = auto()  # .
    COLON = auto()  # :
    SEMICOLON = auto()  # ;
    ARROW = auto()  # ->

    # Special
    EOF = auto()


KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "or": TokenType.OR,
    "||": TokenType.OR,
    "and": TokenType.AND,
    "&&": TokenType.AND,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "try": TokenType.TRY,
    "except": TokenType.EXCEPT,
    "not": TokenType.NOT,
}
COMPARISONS = (
    TokenType.EQ,
    TokenType.NE,
    TokenType.LE,
    TokenType.LT,
    TokenType.GE,
    TokenType.GT,
)
BINARY_OP = (
    TokenType.PLUS,
    TokenType.MINUS,
    TokenType.STAR,
    TokenType.SLASH,
    TokenType.PERCENT,
    TokenType.POWER,
)


@dataclass
class Token:
    """A single token representation"""

    type: TokenType
    value: Any
    line: int
    col: int

    def __post_init__(self):
        # changing indexing from 0-idx to 1-idx
        self.line += 1 
        self.col += 1

    def __repr__(self) -> str:
        return f"T_{self.type.name} <{self.value}> @ ({self.line}:{self.col})"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def pos(self) -> str:
        return f"{self.line}:{self.col}"


class LexicalError(Exception): ...
