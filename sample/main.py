if __name__ == "__main__":
    try:
        from .compiler_gui import Compiler
    except ImportError:  # Supports `python sample/main.py` as well.
        from compiler_gui import Compiler

    Compiler().mainloop()
