import time
from tkinter import font, ttk
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path

try:
    from .lexer import DICTIONARY as dictionary, Lexer, PROJECT_ROOT
    from .parser import Parser
except ImportError:  # Running sample/main.py directly.
    from lexer import DICTIONARY as dictionary, Lexer, PROJECT_ROOT
    from parser import Parser

DOCS_DIR = PROJECT_ROOT / "docs"
LOGS_DIR = DOCS_DIR / "Logs"
TRANSLATIONS_DIR = DOCS_DIR / "translates"

# Load config.json
def get_config():
    with (DOCS_DIR / "config.json").open(encoding="utf-8") as config_file:
        return json.load(config_file)

# Save config.json
def save_config(config):
    with (DOCS_DIR / "config.json").open("w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=4)

class Compiler(ctk.CTk):
    
    # GUI configuration
    def __init__(self):
        config = get_config()
        self.file_saved = False
        self.file_path = None
        self.tokens = []
        self.diagnostics = []
        self.error_count = 0
        
        super().__init__()
        self.title("Compiler - Text Editor")
        self.geometry("800x600")
        ctk.set_appearance_mode(config["theme"])
        self.iconphoto(False, tk.PhotoImage(file=str(DOCS_DIR / "assets" / "Logo.png")))
        
        # File menu   
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="    Ctrl+N", command=self.new_file)
        self.bind("<Control-n>", lambda event: self.new_file())
        self.bind("<Control-N>", lambda event: self.new_file())
        file_menu.add_command(label="Open...", accelerator="    Ctrl+O", command=self.open_file)
        self.bind("<Control-o>", lambda event: self.open_file())
        self.bind("<Control-O>", lambda event: self.open_file())
        file_menu.add_command(label="Save", accelerator="    Ctrl+S", command=self.save_file)
        self.bind("<Control-s>", lambda event: self.save_file())
        self.bind("<Control-S>", lambda event: self.save_file())
        file_menu.add_command(label="Save As...", accelerator="    Ctrl+Shift+S", command=self.saveAs_file)
        self.bind("<Control-Shift-KeyPress-s>", lambda event: self.saveAs_file())
        self.bind("<Control-Shift-KeyPress-S>", lambda event: self.saveAs_file())
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu, )
        self.config(menu=menubar)
        
        # Compiler menu
        compiler_menu = tk.Menu(menubar, tearoff=0)
        compiler_menu.add_command(label= "Analyze", accelerator= "    Ctrl+Shift+A", command= lambda:self.analyze())
        self.bind("<Control-Shift-a>", lambda event: self.analyze())
        self.bind("<Control-Shift-A>", lambda event: self.analyze())
        compiler_menu.add_command(label= "Translate", accelerator= "    Ctrl+Shift+T", command= lambda:self.translate())
        self.bind("<Control-Shift-t>", lambda event: self.translate())
        self.bind("<Control-Shift-T>", lambda event: self.translate())
        menubar.add_cascade(label="Compiler", menu=compiler_menu)
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_command(label = "Font...", command=self.configure_font)
        menubar.add_cascade(label = "Format", menu=format_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label = "Theme", menu=theme_menu)
        theme_menu.add_command(label = "Light", command = lambda: self.switch_theme("light"))
        theme_menu.add_command(label = "Dark", command = lambda: self.switch_theme("dark"))
        menubar.add_cascade(label = "View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "C Code Compiler & Analyzer\nVersion 1.0\nDeveloped by ZeusLeon"))
        menubar.add_cascade(label="Help", menu = help_menu)

        # Editor and line-number gutter
        self.editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_frame.pack(expand=True, fill="both", padx=15, pady=15)
        gutter_bg = "#242424" if config["theme"] == "dark" else "#f0f0f0"
        self.line_numbers = tk.Canvas(
            self.editor_frame, width=48, highlightthickness=0, bd=0, bg=gutter_bg
        )
        self.line_numbers.pack(side="left", fill="y")
        self.text = ctk.CTkTextbox(self.editor_frame, wrap=tk.NONE)
        self.text.pack(side="left", expand=True, fill="both")
        self.text.configure(font=(config["font"], config["size"]))
        self.text.bind("<KeyRelease>", self._mark_unsaved)
        self.text.bind("<<Paste>>", self._mark_unsaved)
        self.text.bind("<<Cut>>", self._mark_unsaved)
        self.text.bind("<Configure>", lambda event: self._redraw_line_numbers())
        self.text.bind("<MouseWheel>", lambda event: self._redraw_line_numbers())
        self.text.bind("<Button-4>", lambda event: self._redraw_line_numbers())
        self.text.bind("<Button-5>", lambda event: self._redraw_line_numbers())
        self.text._textbox.configure(yscrollcommand=self._on_editor_scroll)
        self.text._y_scrollbar.configure(command=self._scroll_editor)
        self.after_idle(self._redraw_line_numbers)

        # Terminal output
        self.terminal = ctk.CTkTextbox(self, wrap = tk.WORD, state='disabled', height= 200)
        self.terminal.pack(padx = 15, fill = 'x')
        self.terminal.configure(font = (config["font"], config["size"]))

        # Status bar
        status = ctk.StringVar()
        status.set("Ready")
        self.status_bar = ctk.CTkLabel(self, text = status.get(), anchor = 'w', font= (config["font"], 12))
        self.status_bar.pack(side = 'bottom', fill = 'x', padx = 20) 
    
    def get_text_content(self):
        content = self.text.get("1.0", tk.END)
        if content.endswith("\n"):
            return content[:-1]
        return content

    def _mark_unsaved(self, event):
        if not event.keysym or len(event.keysym) == 1 or event.keysym in {
            "BackSpace", "Delete", "Insert", "space", "Tab", "Return", "KP_Enter",
        }:
            self.file_saved = False
        self._redraw_line_numbers()

    def _on_editor_scroll(self, first, last):
        self.text._y_scrollbar.set(first, last)
        self._redraw_line_numbers()

    def _scroll_editor(self, *args):
        self.text._textbox.yview(*args)
        self._redraw_line_numbers()

    def _redraw_line_numbers(self):
        if not hasattr(self, "line_numbers") or not hasattr(self, "text"):
            return
        self.line_numbers.configure(bg=self.text._textbox.cget("bg"))
        self.line_numbers.delete("all")
        textbox = self.text._textbox
        y_offset = textbox.winfo_rooty() - self.line_numbers.winfo_rooty()
        line = int(textbox.index("@0,0").split(".")[0])
        max_line = int(textbox.index("end-1c").split(".")[0])
        while line <= max_line:
            line_info = textbox.dlineinfo(f"{line}.0")
            if line_info is None:
                break
            _, y, _, height, _ = line_info
            self.line_numbers.create_text(
                40, y + y_offset + height / 2, anchor="e", text=str(line),
                fill="#a0a0a0", font=(self.text.cget("font"), 12),
            )
            line += 1

    # New file functionality    
    def new_file(self):
        if not self.file_saved and self.text.get("1.0", tk.END).strip():
            result = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save the file?")
            if result is True:
                if not self.save_file():
                    return
            elif result is False:
                pass
            else:
                return

        self.text.delete("1.0", tk.END)
        self.status_bar.configure(text="New file open.")
        self.title("Compiler - Text Editor")
        self.file_saved = False
        self.file_path = None
        return True
            
    # Open file functionality
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("C files", "*.c"), ("Text files", "*.txt"), ("Backup files", "*.back")])
        if not path:
            return

        try:
            content = Path(path).read_text(encoding="utf-8").rstrip("\n")
        except OSError as error:
            self.status_bar.configure(text=f"The file could not be opened: {error}")
            return
        if not self.new_file():
            return
        self.text.insert(tk.END, content)
        self.title("Compiler - " + Path(path).stem)
        self.file_saved = True
        self.file_path = Path(path)
        self._redraw_line_numbers()
        
    # Save functionality        
    def save_file(self):
        if self.file_path is None:
            return self.saveAs_file()
        content = self.get_text_content()
        try:
            self.file_path.write_text(content, encoding="utf-8")
            self.file_saved = True
            self.status_bar.configure(text="File saved.")
            return True
        except OSError as error:
            self.status_bar.configure(text=f"Could not save file: {error}")
            return False
    
    # Save As functionality            
    def saveAs_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C files", "*.c"), ("Text files", "*.txt")])
        if path:
            selected_path = Path(path)
            try:
                selected_path.write_text(self.get_text_content(), encoding="utf-8")
                self.file_path = selected_path
                self.file_saved = True
                self.title("Compiler - " + selected_path.stem)
                self.status_bar.configure(text="File saved as: " + str(selected_path))
                return True
            except OSError as error:
                self.status_bar.configure(text=f"Could not save file: {error}")
                return False
        else:
            self.status_bar.configure(text="File save canceled.")
            return False
            
    # Analyze functionality
    def analyze(self):
        self.tokens = []
        self.diagnostics = []
        self.error_count = 0
        code = self.get_text_content()
        if not code.strip():
            self.status_bar.configure(text="Cannot analyze an empty file.")
            return False
        if not self.save_file():
            return False
        self.status_bar.configure(text="Analyzing...")
        self.tokens, lexical_diagnostics = Lexer(code).scan()
        syntax_diagnostics = Parser(self.tokens).parse()
        self.diagnostics = lexical_diagnostics + syntax_diagnostics
        self.error_count = len(self.diagnostics)

        source_name = self.file_path.stem if self.file_path else "untitled"
        log_path = LOGS_DIR / f"{source_name}_analysis_log_{time.strftime('%Y%m%d_%H%M%S')}_{time.time_ns() % 1_000_000_000:09d}.back"
        lines = [f"Lines analyzed: {code.count(chr(10)) + 1}", f"Errors found: {self.error_count}", ""]
        lines.extend(
            f"{token['line']}:{token['column']} {token['type']} | {token['category']} - {token['token']}"
            for token in self.tokens if token["type"] != "whitespace"
        )
        if self.diagnostics:
            lines.extend(["", "Diagnostics:"])
            lines.extend(
                f"{item['phase']} {item['line']}:{item['column']} - {item['message']}"
                for item in self.diagnostics
            )
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError as error:
            self.status_bar.configure(text=f"Analysis completed; log could not be saved: {error}")
            return False

        self.terminal.configure(state="normal")
        self.terminal.insert(
            tk.END,
            f"Analysis complete of {self.file_path.name}.\nLog saved to: {log_path}\n"
            f"Lines analyzed: {code.count(chr(10)) + 1}\nErrors found: {self.error_count}\n",
        )
        for item in self.diagnostics:
            self.terminal.insert(tk.END, f"{item['phase']} {item['line']}:{item['column']} - {item['message']}\n")
        self.terminal.insert(tk.END, "\n")
        self.terminal.configure(state="disabled")
        self.status_bar.configure(text="Analysis complete." if not self.error_count else f"Analysis complete with {self.error_count} error(s).")
        return True
            
    # Font configuration functionality
    def configure_font(self):
        config = get_config()
        font_window = tk.Toplevel(self)
        font_window.resizable(False, False)
        font_window.title("Font")
        font_window.geometry("400x200")
        font_window.iconphoto(False, tk.PhotoImage(file=str(DOCS_DIR / "assets" / "Logo.png")))
        font_window.focus_force()
        font_window.grid_columnconfigure([0, 1], weight=1)
        
        # Font selection
        font_label = tk.Label(font_window, text= "Font:")
        font_label.grid(row = 0, column = 0, pady = (15, 0), padx = (30, 0))
        font_label.grid_configure(sticky = 'w')
        font_combo = ttk.Combobox(font_window, values = font.families(), state = "readonly")
        font_combo.set(config["font"])
        font_combo.grid(row = 1, column = 0)
        
        # Font selection
        size_label = tk.Label(font_window, text = "Size:")
        size_label.grid(row = 0, column = 1, pady = (15, 0), padx = (30, 0))
        size_label.grid_configure(sticky = 'w')
        size_combo = ttk.Combobox(font_window, values = ["8", "10", "12", "14", "16", "18", "20", "22", "24", "26", "28", "30"], state = "readonly")
        size_combo.set(config["size"])
        size_combo.grid(row = 1, column = 1)

        # Save button
        save_button = ctk.CTkButton(font_window, text= "Save", command = lambda: save_font())
        save_button.grid(row = 2, column = 0, columnspan = 2, pady = (40, 0))
        
        def save_font():
            new_font = font_combo.get()
            new_size = int(size_combo.get())
            config["font"] = new_font
            config["size"] = new_size
            save_config(config)
            self.status_bar.configure(text= "Font changed.")  
            self.text.configure(font=(new_font, new_size))
            self.terminal.configure(font=(new_font, new_size))  
            font_window.destroy()
    
    # Theme switching functionality
    def switch_theme(self, theme):
        config = get_config()
        config["theme"] = theme
        save_config(config)
        ctk.set_appearance_mode(theme)
        self.after_idle(self._redraw_line_numbers)
        
    # Translate functionality   
    def translate(self):
        if not self.analyze():
            return
        if self.error_count == 0:
            translation_path = TRANSLATIONS_DIR / (
                f"{self.file_path.stem}_translate_code_{time.strftime('%Y%m%d_%H%M%S')}_{time.time_ns() % 1_000_000_000:09d}.txt"
            )
            translated_source = []
            for token in self.tokens:
                spelling = token["token"]
                if token["type"] in {"keyword", "preprocessor_directive"}:
                    spelling = dictionary["translations"].get(spelling, spelling)
                translated_source.append(spelling)
            try:
                TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)
                translation_path.write_text("".join(translated_source), encoding="utf-8")
            except OSError as error:
                self.status_bar.configure(text=f"Translation could not be saved: {error}")
                return

            self.status_bar.configure(text="Translate complete.")
            
            if messagebox.askyesno("Show translate", "Do you want to open the translation in the editor?"):
                
                try:
                    
                    with translation_path.open("r", encoding="utf-8") as translated_file:
                        content = translated_file.read().rstrip("\n")
                        self.text.delete("1.0", tk.END)
                        self.text.insert(tk.END, content)
                        self.title("Compiler - " + translation_path.stem)
                        self.file_saved = True
                        self.file_path = translation_path
                        self._redraw_line_numbers()
                        
                except OSError as error:
                    self.status_bar.configure(text="The file could not be opened.")
                    return   
                           
        else:
            messagebox.showwarning("Code errors", "Translation requires a successful lexical and syntax analysis.")
