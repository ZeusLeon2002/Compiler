"""Small, location-aware lexer for the C subset used by this project."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DICTIONARY_PATH = PROJECT_ROOT / "docs" / "dictionary.json"


def load_dictionary():
    with DICTIONARY_PATH.open(encoding="utf-8") as dictionary_file:
        return json.load(dictionary_file)


DICTIONARY = load_dictionary()


def _token(lexeme, kind, category, line, column, start, end):
    return {
        "token": lexeme,
        "type": kind,
        "category": category,
        "subcategory": None,
        "line": line,
        "column": column,
        "start": start,
        "end": end,
    }


class Lexer:
    """Tokenize source while retaining whitespace for lossless translation."""

    def __init__(self, source, dictionary=None):
        self.source = source
        self.dictionary = dictionary or DICTIONARY
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.diagnostics = []
        self._keywords = {
            word: category
            for category, words in self.dictionary["keywords"].items()
            for word in words
        }
        self._libraries = {
            word: category + " library"
            for category, words in self.dictionary["standard_library"].items()
            for word in words
        }
        self._operators = {
            item: category
            for category, items in self.dictionary["operators"].items()
            for item in items
        }
        self._symbols = {
            item: category
            for category, items in self.dictionary["symbols"].items()
            for item in items
        }
        self._spellings = sorted(
            set(self._operators) | set(self._symbols), key=len, reverse=True
        )

    def _advance(self):
        character = self.source[self.position]
        self.position += 1
        if character == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return character

    def _emit(self, start, line, column, kind, category):
        lexeme = self.source[start:self.position]
        self.tokens.append(
            _token(lexeme, kind, category, line, column, start, self.position)
        )

    def _diagnose(self, message, line=None, column=None):
        self.diagnostics.append({
            "phase": "lexical",
            "message": message,
            "line": self.line if line is None else line,
            "column": self.column if column is None else column,
        })

    def _scan_quoted(self, quote, kind):
        start, line, column = self.position, self.line, self.column
        self._advance()
        closed = False
        while self.position < len(self.source):
            char = self.source[self.position]
            if char == quote:
                self._advance()
                closed = True
                break
            if char == "\n":
                break
            if char == "\\":
                self._advance()
                if self.position < len(self.source) and self.source[self.position] != "\n":
                    self._advance()
            else:
                self._advance()
        if not closed:
            self._diagnose(
                "Cadena sin cerrar" if quote == '"' else "Literal de carácter sin cerrar",
                line, column,
            )
        elif quote == "'":
            content = self.source[start + 1:self.position - 1]
            valid_simple_escapes = set("'\"?\\abfnrtv0")
            if content.startswith("\\"):
                escape = content[1:]
                if escape.startswith("x"):
                    valid_escape = len(escape) > 1 and all(c in "0123456789abcdefABCDEF" for c in escape[1:])
                elif escape.startswith("u"):
                    valid_escape = len(escape) == 5 and all(c in "0123456789abcdefABCDEF" for c in escape[1:])
                elif escape.startswith("U"):
                    valid_escape = len(escape) == 9 and all(c in "0123456789abcdefABCDEF" for c in escape[1:])
                elif escape and escape[0] in "01234567":
                    valid_escape = len(escape) <= 3 and all(c in "01234567" for c in escape)
                else:
                    valid_escape = escape in valid_simple_escapes
                valid_content = valid_escape
            else:
                valid_content = len(content) == 1
            if not valid_content:
                self._diagnose("Literal de carácter inválido o con escape no reconocido", line, column)
        self._emit(start, line, column, kind if closed else "invalid_" + kind, kind)

    def _scan_number(self):
        import re

        start, line, column = self.position, self.line, self.column
        pattern = re.compile(
            r"(?:"
            r"0[xX](?:[0-9a-fA-F]+(?:\.[0-9a-fA-F]*)?|\.[0-9a-fA-F]+)[pP][+-]?\d+[fFlL]?|"
            r"0[xX][0-9a-fA-F]+(?:[uU](?:ll|LL|[lL])?|(?:ll|LL|[lL])[uU]?)?|"
            r"(?:(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)[fFlL]?|"
            r"\d+(?:[uU](?:ll|LL|[lL])?|(?:ll|LL|[lL])[uU]?)?"
            r")"
        )
        match = pattern.match(self.source, self.position)
        lexeme = match.group(0)
        for _ in lexeme:
            self._advance()
        malformed = False
        # Consume an incomplete exponent as part of the malformed literal.
        if self.position < len(self.source) and self.source[self.position] in "eEpP":
            malformed = True
            self._advance()
            if self.position < len(self.source) and self.source[self.position] in "+-":
                self._advance()
            while self.position < len(self.source) and self.source[self.position].isdigit():
                self._advance()
        if self.position < len(self.source) and self.source[self.position] == ".":
            malformed = True
            while self.position < len(self.source) and self.source[self.position] == ".":
                self._advance()
        if self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == "_"):
            malformed = True
            while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == "_"):
                self._advance()
        lexeme = self.source[start:self.position]
        if malformed:
            self._diagnose("Literal numérico inválido", line, column)
            self._emit(start, line, column, "invalid_number", "number")
        else:
            category = "real_number" if any(c in lexeme for c in ".eE") else "integer"
            self._emit(start, line, column, "number", category)

    def scan(self):
        source = self.source
        while self.position < len(source):
            start, line, column = self.position, self.line, self.column
            char = source[self.position]

            if char.isspace():
                while self.position < len(source) and source[self.position].isspace():
                    self._advance()
                self._emit(start, line, column, "whitespace", None)
            elif source.startswith("//", self.position):
                while self.position < len(source) and source[self.position] != "\n":
                    self._advance()
                self._emit(start, line, column, "comments", "single_line")
            elif source.startswith("/*", self.position):
                self._advance(); self._advance()
                closed = False
                while self.position < len(source):
                    if source.startswith("*/", self.position):
                        self._advance(); self._advance()
                        closed = True
                        break
                    self._advance()
                self._emit(start, line, column, "comments" if closed else "invalid_comment", "multi_line")
                if not closed:
                    self._diagnose("Comentario multilínea sin cerrar", line, column)
            elif char == "#":
                self._advance()
                while self.position < len(source) and source[self.position].isspace() and source[self.position] != "\n":
                    self._advance()
                while self.position < len(source) and (source[self.position].isalpha() or source[self.position] == "_"):
                    self._advance()
                directive = "".join(source[start:self.position].split())
                valid = directive in self.dictionary["preprocessor_directive"]
                self._emit(start, line, column, "preprocessor_directive" if valid else "invalid_preprocessor", "directive" if valid else "invalid")
                if not valid:
                    self._diagnose("Directiva del preprocesador no reconocida", line, column)
            elif char.isalpha() or char == "_":
                self._advance()
                while self.position < len(source) and (source[self.position].isalnum() or source[self.position] == "_"):
                    self._advance()
                word = source[start:self.position]
                if word in self._keywords:
                    self._emit(start, line, column, "keyword", self._keywords[word])
                elif word in self._libraries:
                    self._emit(start, line, column, "library function", self._libraries[word])
                else:
                    self._emit(start, line, column, "identifier", None)
            elif char.isdigit() or (char == "." and self.position + 1 < len(source) and source[self.position + 1].isdigit()):
                self._scan_number()
            elif char == '"':
                self._scan_quoted('"', "string")
            elif char == "'":
                self._scan_quoted("'", "char")
            else:
                spelling = next((item for item in self._spellings if source.startswith(item, self.position)), None)
                if spelling is None:
                    self._advance()
                    self._emit(start, line, column, "invalid_character", None)
                    self._diagnose("Carácter no válido", line, column)
                else:
                    for _ in spelling:
                        self._advance()
                    if spelling in self._operators:
                        self._emit(start, line, column, "operator", self._operators[spelling])
                    else:
                        self._emit(start, line, column, "symbol", self._symbols[spelling])
        return self.tokens, self.diagnostics
