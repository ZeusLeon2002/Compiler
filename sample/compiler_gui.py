try: 
    import customtkinter as ctk
    import tkinter as tk
    import json
    from pathlib import Path
    
except ImportError:
    import pip
    pip.main(['install', 'customtkinter', 'pathlib'])
    import customtkinter as ctk
    import tkinter as tk

file_saved = False
file_path = None

config_path = Path("docs/config.json")

def get_config():
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

class Compiler(ctk.CTk):
    
    # GUI configuration
    def __init__(self):
        config = get_config()
        
        super().__init__()
        self.title("Compiler - Text Editor")
        self.geometry("800x600")
        
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
        menubar.add_cascade(label="Compiler", menu=compiler_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Light", command=lambda: ctk.set_appearance_mode("light"))
        theme_menu.add_command(label="Dark", command=lambda: ctk.set_appearance_mode("dark"))
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Central text editor
        self.text = ctk.CTkTextbox(self, wrap=tk.NONE)
        self.text.pack(expand=True, fill= 'both')
        self.text.configure(font=(config["font"], config["size"]))
        
        # Status bar
        status = ctk.StringVar()
        status.set("Ready")
        self.status_bar = ctk.CTkLabel(self, text= status.get(), anchor= 'w')
        self.status_bar.pack(side= 'bottom', fill= 'x') 
    
    # New file functionality    
    def new_file(self):
        global file_saved
        if not file_saved:
            result = tk.messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save the file?")
            if result is True:            
                self.save_file()
                self.text.delete("1.0", tk.END)
                self.status_bar.configure(text="New file open.")
                self.title("Compiler - Text Editor")
                file_saved = False
            if result is False: 
                self.text.delete("1.0", tk.END)
                self.status_bar.configure(text="New file open.")
                self.title("Compiler - Text Editor")
                file_saved = False
            if result is None: 
                return                   
        if file_saved:
            self.text.delete("1.0", tk.END)
            self.status_bar.configure(text="New file open.")
            self.title("Compiler - Text Editor")
            file_saved = False
            
    # Open file functionality
    def open_file(self):
        global file_saved
        global file_path
        path = tk.filedialog.askopenfilename(filetypes=[("C files", "*.c"), ("Text files", "*.txt")])
        if path:
            file_path = path
            self.new_file()
            with open(file_path, 'r') as f:
                self.text.insert(tk.END, f.read())
                new_title = path.split("/")[-1]
                new_title = new_title.replace(".c", "")
                new_title = new_title.replace(".txt", "")
                self.title("Compiler - " + new_title)
                file_saved = True
    
    # Save functionality        
    def save_file(self):
        global file_saved
        global file_path
        if file_path is None:
            self.saveAs_file()
        else:
            open(file_path, 'w').write(self.text.get("1.0", tk.END))
            file_saved = True
            self.status_bar.configure(text="File saved.")
    
    # Save As functionality            
    def saveAs_file(self):
        global file_saved
        global file_path
        path = tk.filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C files", "*.c"), ("Text files", "*.txt")])
        if path:
            file_path = path
            open(file_path, 'w').write(self.text.get("1.0", tk.END))        
            file_saved = True
            new_title = path.split("/")[-1]
            new_title = new_title.replace(".c", "")
            new_title = new_title.replace(".txt", "")
            self.title("Compiler - " + new_title)
            self.status_bar.configure(text="File saved as: " + file_path)            
            
    # Analyze functionality
    def analyze(self):
        self.status_bar.configure(text="Analyzing...")
        self.after(5000, lambda: self.status_bar.configure(text="Analysis complete."))
