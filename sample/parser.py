"""Recursive-descent parser for a practical introductory C subset."""


TYPE_WORDS = {
    "void", "char", "short", "int", "long", "float", "double", "_Bool",
    "signed", "unsigned", "const", "volatile", "static", "extern", "register",
    "auto", "inline", "struct", "union", "enum", "typedef",
}

PRECEDENCE = {
    ",": 1,
    "=": 2, "+=": 2, "-=": 2, "*=": 2, "/=": 2, "%=": 2,
    "&=": 2, "|=": 2, "^=": 2, "<<=": 2, ">>=": 2,
    "?": 3,
    "||": 4,
    "&&": 5,
    "|": 6,
    "^": 7,
    "&": 8,
    "==": 9, "!=": 9,
    "<": 10, "<=": 10, ">": 10, ">=": 10,
    "<<": 11, ">>": 11,
    "+": 12, "-": 12,
    "*": 13, "/": 13, "%": 13,
}


class Parser:
    """Parse declarations, functions, common statements and expressions."""

    def __init__(self, tokens):
        self.tokens = [
            token for token in tokens
            if token["type"] not in {"whitespace", "comments", "invalid_comment"}
        ]
        self.index = 0
        self.diagnostics = []

    def _current(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def _lexeme(self):
        token = self._current()
        return token["token"] if token else "<eof>"

    def _is(self, value):
        return self._lexeme() == value

    def _advance(self):
        token = self._current()
        if token is not None:
            self.index += 1
        return token

    def _error(self, message):
        token = self._current() or (self.tokens[-1] if self.tokens else {})
        self.diagnostics.append({
            "phase": "syntax",
            "message": message,
            "line": token.get("line", 1),
            "column": token.get("column", 1),
        })

    def _expect(self, value):
        if self._is(value):
            return self._advance()
        self._error(f"Se esperaba '{value}' y se encontró '{self._lexeme()}'")
        return None

    def _identifier(self):
        token = self._current()
        if token and token["type"] in {"identifier", "library function"}:
            return self._advance()
        # `main` is categorized as a type in the project's original dictionary.
        if token and token["token"] == "main":
            return self._advance()
        self._error(f"Se esperaba un identificador y se encontró '{self._lexeme()}'")
        return None

    def _is_type_start(self):
        token = self._current()
        return bool(token and (token["token"] in TYPE_WORDS or token["type"] == "keyword" and token["category"] == "user_defined_type"))

    def _skip_directive(self):
        line = self._current()["line"]
        while self._current() and self._current()["line"] == line:
            self._advance()

    def parse(self):
        while self._current():
            before = self.index
            if self._current()["type"] in {"preprocessor_directive", "invalid_preprocessor"}:
                self._skip_directive()
            elif self._is_type_start():
                self._declaration(top_level=True)
            else:
                self._error("Se esperaba una declaración o definición de función")
                self._recover({";", "}"})
            if self.index == before:
                self._advance()
        return self.diagnostics

    def _type_specifier(self):
        if not self._is_type_start():
            self._error("Se esperaba un especificador de tipo")
            return
        if self._lexeme() in {"struct", "union", "enum"}:
            self._advance()
            if self._current() and self._current()["type"] == "identifier":
                self._advance()
            if self._is("{"):
                self._advance()
                while self._current() and not self._is("}"):
                    if self._is_type_start():
                        self._type_specifier()
                        self._declarator()
                        while self._is(","):
                            self._advance(); self._declarator()
                        self._expect(";")
                    else:
                        self._error("Se esperaba un campo de estructura")
                        self._recover({";", "}"})
                        if self._is(";"): self._advance()
                self._expect("}")
            return
        self._advance()
        while self._current() and self._lexeme() in TYPE_WORDS:
            self._advance()

    def _declaration(self, top_level=False):
        self._type_specifier()
        self._declarator()
        if self._is("("):
            self._parameters()
            if top_level and self._is("{"):
                self._block()
            else:
                self._expect(";")
            return
        self._declaration_tail()

    def _declaration_tail(self):
        if self._is("["):
            self._advance()
            if not self._is("]"):
                self._expression()
            self._expect("]")
            while self._is("["):
                self._advance()
                if not self._is("]"): self._expression()
                self._expect("]")
        if self._is("="):
            self._advance()
            self._initializer()
        while self._is(","):
            self._advance()
            self._declarator()
            if self._is("["):
                self._advance()
                if not self._is("]"): self._expression()
                self._expect("]")
            if self._is("="):
                self._advance(); self._initializer()
        self._expect(";")

    def _initializer(self):
        if not self._is("{"):
            self._expression(2)
            return
        self._advance()
        while self._current() and not self._is("}"):
            self._initializer()
            if not self._is(","):
                break
            self._advance()
        self._expect("}")

    def _declarator(self):
        while self._is("*"):
            self._advance()
            while self._lexeme() in {"const", "volatile", "restrict"}:
                self._advance()
        self._identifier()

    def _parameters(self):
        self._expect("(")
        if self._is("void"):
            self._advance()
        elif not self._is(")"):
            while self._current() and not self._is(")"):
                if not self._is_type_start():
                    self._error("Se esperaba el tipo del parámetro")
                    self._recover({",", ")"})
                else:
                    self._type_specifier()
                    if not self._is(",") and not self._is(")"):
                        self._declarator()
                        if self._is("["):
                            self._advance()
                            if not self._is("]"): self._expression()
                            self._expect("]")
                if not self._is(","):
                    break
                self._advance()
        self._expect(")")

    def _block(self):
        self._expect("{")
        while self._current() and not self._is("}"):
            before = self.index
            self._statement()
            if self.index == before:
                self._advance()
        self._expect("}")

    def _statement(self):
        if self._current() and self._current()["type"] in {"preprocessor_directive", "invalid_preprocessor"}:
            self._skip_directive()
        elif self._is("{"):
            self._block()
        elif self._is_type_start():
            self._type_specifier(); self._declarator(); self._declaration_tail()
        elif self._is("if"):
            self._advance(); self._expect("("); self._expression(); self._expect(")"); self._statement()
            if self._is("else"):
                self._advance(); self._statement()
        elif self._is("while"):
            self._advance(); self._expect("("); self._expression(); self._expect(")"); self._statement()
        elif self._is("switch"):
            self._advance(); self._expect("("); self._expression(); self._expect(")"); self._statement()
        elif self._is("case"):
            self._advance(); self._expression(2); self._expect(":"); self._statement()
        elif self._is("default"):
            self._advance(); self._expect(":"); self._statement()
        elif self._is("do"):
            self._advance(); self._statement(); self._expect("while"); self._expect("("); self._expression(); self._expect(")"); self._expect(";")
        elif self._is("for"):
            self._advance(); self._expect("(")
            if self._is_type_start(): self._type_specifier(); self._declarator(); self._declaration_tail()
            elif not self._is(";"): self._expression(); self._expect(";")
            if not self._is(";"): self._expression()
            self._expect(";")
            if not self._is(")"): self._expression()
            self._expect(")"); self._statement()
        elif self._is("return"):
            self._advance()
            if not self._is(";"): self._expression()
            self._expect(";")
        elif self._is("break") or self._is("continue"):
            self._advance(); self._expect(";")
        elif self._is("goto"):
            self._advance(); self._identifier(); self._expect(";")
        elif self._is(";"):
            self._advance()
        else:
            self._expression(); self._expect(";")

    def _expression(self, minimum=1):
        self._prefix()
        while self._current():
            operator = self._lexeme()
            if operator in {"(", "[", ".", "->", "++", "--"}:
                if 15 < minimum: break
                self._advance()
                if operator == "(":
                    if not self._is(")"):
                        self._expression(2)
                        while self._is(","):
                            self._advance(); self._expression(2)
                    self._expect(")")
                elif operator == "[":
                    self._expression(); self._expect("]")
                elif operator in {".", "->"}:
                    self._identifier()
                continue
            precedence = PRECEDENCE.get(operator, 0)
            if precedence < minimum:
                break
            self._advance()
            if operator == "?":
                self._expression(1); self._expect(":"); self._expression(precedence)
            else:
                self._expression(precedence if precedence == 2 else precedence + 1)

    def _prefix(self):
        if self._lexeme() in {"+", "-", "!", "~", "*", "&", "++", "--", "sizeof"}:
            operator = self._advance()["token"]
            if operator == "sizeof" and self._is("(") and self.index + 1 < len(self.tokens) and self.tokens[self.index + 1]["token"] in TYPE_WORDS:
                self._advance(); self._type_specifier()
                while self._is("*"): self._advance()
                self._expect(")")
            else:
                self._prefix()
        elif self._is("("):
            if self.index + 1 < len(self.tokens) and self.tokens[self.index + 1]["token"] in TYPE_WORDS:
                self._advance(); self._type_specifier()
                while self._is("*"): self._advance()
                self._expect(")"); self._prefix()
            else:
                self._advance(); self._expression(); self._expect(")")
        elif self._current() and self._current()["type"] in {
            "identifier", "library function", "number", "string", "char",
        }:
            self._advance()
        elif self._lexeme() in {"NULL", "true", "false"}:
            self._advance()
        else:
            self._error(f"Se esperaba una expresión y se encontró '{self._lexeme()}'")
            if self._current(): self._advance()

    def _recover(self, stops):
        while self._current() and self._lexeme() not in stops:
            self._advance()
