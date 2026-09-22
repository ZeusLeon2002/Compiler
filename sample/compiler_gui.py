import time
from analyzers import *
from tkinter import font, ttk
import customtkinter as ctk
import tkinter as tk
import json
from pathlib import Path

file_saved = False
file_path = None
tokens = []
line_count = 1
error_count = 0

# Load config.json
def get_config():
    with open("docs/config.json", "r") as f:
        config = json.load(f)
    return config

# Save config.json
def save_config(config):
    with open("docs/config.json", "w") as f:
        json.dump(config, f, indent=4)    

class Compiler(ctk.CTk):
    
    # GUI configuration
    def __init__(self):
        config = get_config()
        
        super().__init__()
        self.title("Compiler - Text Editor")
        self.geometry("800x600")
        ctk.set_appearance_mode(config["theme"])
        self.iconphoto(False, tk.PhotoImage(file="docs/assets/Logo.png"))
        
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
        self.bind("<Control-Shift-t>", lambda event: self.analyze())
        self.bind("<Control-Shift-T>", lambda event: self.analyze())
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
        help_menu.add_command(label="About", command=  lambda: tk.messagebox.showinfo("About", "C Code Compiler & Analyzer\nVersion 1.0\nDeveloped by ZeusLeon"))
        menubar.add_cascade(label="Help", menu = help_menu)

        # Central text editor
        self.text = ctk.CTkTextbox(self, wrap = tk.NONE)
        self.text.pack(expand = True, fill = 'both', padx = 15, pady = 15)
        self.text.configure(font=(config["font"], config["size"]))

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

    # New file functionality    
    def new_file(self):
        global file_saved
        global file_path
        if not file_saved and self.text.get("1.0", tk.END).strip():
            result = tk.messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save the file?")
            if result is True:
                self.save_file()
            elif result is False:
                pass
            else:
                return

        self.text.delete("1.0", tk.END)
        self.status_bar.configure(text="New file open.")
        self.title("Compiler - Text Editor")
        file_saved = False
        file_path = None
            
    # Open file functionality
    def open_file(self):
        global file_saved
        global file_path
        path = tk.filedialog.askopenfilename(filetypes=[("C files", "*.c"), ("Text files", "*.txt"), ("Backup files", "*.back")])
        if not path:
            return

        selected_path = path
        self.new_file()

        try:
            with open(selected_path, 'r') as f:
                content = f.read().rstrip("\n")
                self.text.insert(tk.END, content)
                new_title = selected_path.split("/")[-1]
                new_title = new_title.replace(".c", "")
                new_title = new_title.replace(".txt", "")
                self.title("Compiler - " + new_title)
                file_saved = True
                file_path = selected_path
        except FileNotFoundError:
            self.status_bar.configure(text="The file could not be opened.")
            return
        
    # Save functionality        
    def save_file(self):
        global file_saved
        global file_path
        if file_path is None:
            self.saveAs_file()
        else:
            content = self.get_text_content()
            open(file_path, 'w').write(content)
            file_saved = True
            self.status_bar.configure(text="File saved.")
    
    # Save As functionality            
    def saveAs_file(self):
        global file_saved
        global file_path
        path = tk.filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C files", "*.c"), ("Text files", "*.txt")])
        if path:
            file_path = path
            open(file_path, 'w').write(self.get_text_content())
            file_saved = True
            new_title = path.split("/")[-1]
            new_title = new_title.replace(".c", "")
            new_title = new_title.replace(".txt", "")
            self.title("Compiler - " + new_title)
            self.status_bar.configure(text="File saved as: " + file_path)            
            
    # Analyze functionality
    def analyze(self):
        global tokens
        global position
        global line_count
        global error_count
        tokens.clear()
        position = 0
        line_count = 1
        error_count = 0
        self.save_file()
        self.status_bar.configure(text="Analyzing...")
        code = self.get_text_content()
        log_path = "docs/Logs/" + file_path.split("/")[-1].replace(".c", "").replace(".txt", "") + "_analysis_log_" + time.strftime("%Y%m%d_%H%M%S") + ".back"
        
        while position < len(code):
            
            if code[position] == ' ':
                token = ""
                
                while position < len(code) and code[position] == ' ':
                    token += code[position]
                    position += 1

                token_data = {
                    "token": token,
                    "type": "whitespace",
                    "category": None,
                    "subcategory": None,
                    "line": line_count
                }
                
            elif code[position] == '\t':
                token = ""
                
                while position < len(code) and code[position] == '\t':
                    token += code[position]
                    position += 1

                token_data = {
                    "token": token,
                    "type": "whitespace",
                    "category": None,
                    "subcategory": None,
                    "line": line_count
                }
                
            elif code[position] == '\n':
                token = ""
                i = 0
                 
                while position < len(code) and code[position] == '\n':
                    token += code[position]
                    position += 1
                    line_count += 1
                    i += 1

                token_data = {
                    "token": token,
                    "type": "whitespace",
                    "category": None,
                    "subcategory": None,
                    "line": line_count - i
                }
                
            elif code[position] == '/':
                find, position, line_count, token_data = block_comment(code, position, line_count)
                
                if not find:
                    position, line_count, error_count, token_data = found_operator(code, position, dictionary, line_count, error_count)
                
            elif code[position] == '#':
                position, line_count, error_count, token_data = preprocessor(code, position, line_count, error_count)
                
            elif code[position].isalpha() or code[position] == '_':
                position, line_count, token_data = keyword_or_identifier(code, position, line_count)
                
            elif code[position].isdigit():
                position, line_count, error_count, token_data = number(code, position, line_count, error_count)

            elif code[position] == "'":
                position, line_count, error_count, token_data = char(code, position, line_count, error_count)
                   
            elif code[position] == '"':
                position, line_count, error_count, token_data = strings(code, position, line_count, error_count)
                
            elif is_operator_or_symbol(code, position) == "operator":
                position, line_count, error_count, token_data = found_operator(code, position, line_count, error_count)    
            
            elif is_operator_or_symbol(code, position) == "symbol":
                position, line_count, error_count, token_data = found_symbol(code, position, line_count, error_count)
                                 
            else:
                token = code[position]
                error_count += 1
                token_data = {
                    "token": token,
                    "type": "invalid character",
                    "category": None,
                    "subcategory": None,
                    "line": line_count
                }
                position += 1
        
            tokens.append(token_data)
        
        with open(log_path, "w") as f:
            
            for token in tokens:
                
                if token["type"] != "whitespace":
                    f.write(
                        f'{token["type"]} | {token["category"]} - {token["token"]}\n'
                    )
                        
        with open(log_path, 'r+') as log_file:
            old_content = log_file.read()
            log_file.seek(0)
            log_file.write("Lines analyzed: " + str(line_count) + "\nErrors found: " + str(error_count) + "\n\n" + old_content)
            
        self.terminal.configure(state='normal')
        self.terminal.insert(tk.END, "Analysis complete of " + file_path.split("/")[-1] + ".\nLog saved to: " + log_path + "\nLines analyzed: " + str(line_count) + "\nErrors found: " + str(error_count) + "\n\n")
        self.terminal.configure(state='disabled')
        self.status_bar.configure(text="Analysis complete.")
            
    # Font configuration functionality
    def configure_font(self):
        config = get_config()
        font_window = tk.Toplevel(self)
        font_window.resizable(False, False)
        font_window.title("Font")
        font_window.geometry("400x200")
        font_window.iconphoto(False, tk.PhotoImage(file="docs/assets/Logo.png"))
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
        
    # Translate functionality   
    def translate(self):
        global file_saved
        global file_path
        self.analyze()
        if error_count == 0:
            path = "docs/translates/" + file_path.split("/")[-1].replace(".c", "").replace(".txt", "") + "_translate_code_" + time.strftime("%Y%m%d_%H%M%S") + ".txt"
           
            with open(path, "w") as f: 
                
                for token in tokens:
                    
                    if token["type"] == "keyword" or token["type"] == "preprocessor_directive":
                        
                        if token["token"] in dictionary["translations"]:
                            token["token"] = dictionary["translations"][token["token"]]
                
                    f.write(token["token"])
                    
            self.status_bar.configure(text="Translate complete.")
            
            if tk.messagebox.askyesno("Show translate", "Do you want to open the translation in the editor?"):
                
                try:
                    
                    with open(path, 'r') as f:
                        content = f.read().rstrip("\n")
                        self.text.delete("1.0", tk.END)
                        self.text.insert(tk.END, content)
                        new_title = path.split("/")[-1]
                        new_title = new_title.replace(".c", "")
                        new_title = new_title.replace(".txt", "")
                        self.title("Compiler - " + new_title)
                        file_saved = True
                        file_path = path
                        
                except FileNotFoundError:
                    self.status_bar.configure(text="The file could not be opened.")
                    return   
                           
        else:
            tk.messagebox.showwarning("Code errors", "It is not possible to start the translation if the code contains errors.")