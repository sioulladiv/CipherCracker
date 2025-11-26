import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from cipher_manager import CipherManager
import config
from tkinter import PhotoImage
from ttkthemes import ThemedStyle
from monogram_graph import MonogramGraph
from multiprocessing import Process, Queue
import queue
import time
from colours import ColorPalettes
from cipher_manager import run_substitution_process_wrapper
from threading import Thread

def run_subprocess(cipher_text, queue):
    return run_substitution_process_wrapper(cipher_text, queue)

class CipherDecoderGUI:
    def __init__(self, root):
        self.root = root
        self.cipher_manager = CipherManager()
        self.root.title("Cipher Maxxer")
        self.root.geometry("800x700")

        self.theme = None

        color_palettes = ColorPalettes(self.theme)
        self.colors = color_palettes.colors
        self.root.configure(bg=self.colors['background'])
        self.root.option_add("*Font", "Consolas 10")
        self.root.option_add("*foreground", self.colors['text'])
        self.root.option_add("*background", self.colors['background'])
        self.root.option_add("*selectBackground", self.colors['primary'])
        self.root.option_add("*selectForeground", self.colors['background'])
        self.style = ThemedStyle(self.root)
        self.style.set_theme("equilux")
        self.style.configure("Cyber.TFrame",
            background=self.colors['background'],
            borderwidth=2,
            relief="solid"
        )
        self.style.configure("Cyber.TLabel",
            background=self.colors['background'],
            foreground=self.colors['primary'],
            font=("Consolas", 10)
        )
        self.style.configure("Cyber.TButton",
            background=self.colors['dark_element'],
            foreground=self.colors['primary'],
            borderwidth=2,
            relief="solid",
            font=("Consolas", 10, "bold"),
            padding=(15, 5)
        )
        self.style.map("Cyber.TButton",
            background=[('active', self.colors['primary'])],
            foreground=[('active', self.colors['background'])],
            relief=[('pressed', 'sunken')]
        )
        self.style.configure("Cyber.TNotebook",
            background=self.colors['background'],
            foreground=self.colors['text'],
            borderwidth=2,
            relief="solid"
        )
        self.style.configure("Cyber.TNotebook.Tab",
            background=self.colors['dark_element'],
            foreground=self.colors['text'],
            padding=(10, 2),
            font=("Consolas", 9)
        )
        self.style.map("Cyber.TNotebook.Tab",
            background=[('selected', self.colors['primary'])],
            foreground=[('selected', self.colors['background'])]
        )
        text_config = {
            'background': self.colors['dark_element'],
            'foreground': self.colors['text'],
            'insertbackground': self.colors['primary'],
            'selectbackground': self.colors['primary'],
            'selectforeground': self.colors['background'],
            'borderwidth': 2,
            'relief': 'solid',
            'font': ('Consolas', 10),
            'insertwidth': 3
        }
        self.root.option_add("*Text.background", self.colors['dark_element'])
        self.root.option_add("*Text.foreground", self.colors['text'])
        icon = PhotoImage(file='icon.png')
        self.root.iconphoto(True, icon)
        self.notebook = ttk.Notebook(root, style="Cyber.TNotebook")
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        self.main_tab = ttk.Frame(self.notebook, style="Cyber.TFrame")
        self.notebook.add(self.main_tab, text="Main")
        self.settings_tab = ttk.Frame(self.notebook, style="Cyber.TFrame")
        self.notebook.add(self.settings_tab, text="Sigma Settings")
        self.notebook.bind("<Enter>", self.on_tab_hover)
        self.notebook.bind("<Leave>", self.on_tab_leave)
        self.setup_main_tab()
        self.setup_settings_tab()
        self.setup_monogram_tab()
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.left_frame = ttk.Frame(self.main_container)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_frame = ttk.Frame(self.left_frame)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.update_info = {}
        self.update_info['time'] = ttk.Label(info_frame, text="Time: 0s")
        self.update_info['time'].pack(anchor='w')
        fitness_frame = ttk.Frame(info_frame)
        fitness_frame.pack(fill=tk.X, pady=5)
        ttk.Label(fitness_frame, text="Fitness Progress:", 
                 font=("Consolas", 12, "bold")).pack(side=tk.LEFT)
        self.progress_canvas = tk.Canvas(
            fitness_frame,
            width=300,
            height=20,
            bg=self.colors['dark_element'],
            highlightbackground=self.colors['background'],
            highlightthickness=1
        )
        self.progress_canvas.pack(side=tk.LEFT, padx=10, pady=5)
        self.progress_canvas.create_rectangle(
            2, 2, 298, 18,
            fill='black',
            outline=self.colors['accent1'],
            width=1
        )
        self.progress_rect = self.progress_canvas.create_rectangle(
            2, 2, 2, 18,
            fill=self.colors['accent1'],
            outline=self.colors['background'],
            width=1,
            stipple='gray50'
        )
        self.glow_rect = self.progress_canvas.create_rectangle(
            2, 2, 2, 18,
            fill='',
            outline=self.colors['accent1'],
            width=1,
            stipple='gray75'
        )
        self.update_info['Best Fitness'] = ttk.Label(fitness_frame, text="0.0000")
        self.update_info['Best Fitness'].pack(side=tk.LEFT)
        self.update_info['Best text'] = ttk.Label(info_frame, text="Best text: ")
        self.update_info['Best text'].pack(anchor='w')
        self.update_info['Best key'] = ttk.Label(info_frame, text="Best key: ")
        self.update_info['Best key'].pack(anchor='w')
        self.is_decoding = False
        self.update_interval = 50  # Change from 500 to 50 milliseconds
        self.periodic_update()
        self.update_queue = None  # Change this line - initialize as None
        self.process = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.start_time = None
        self.current_cipher = None  # Add this line
        self.selected_ciphers = []  # Add this line

    def setup_theme_selector(self):
        theme_frame = ttk.LabelFrame(self.settings_tab, text="Theme Settings", padding="5")
        theme_frame.pack(fill='x', padx=5, pady=5)
        themes = ['ocean_depths', 'desert_sunset', 'forest_night', 'arctic_aurora', 'cyber_neon']
        self.theme_var = tk.StringVar(value=self.theme)
        ttk.Label(theme_frame, text="Select Theme:").pack(side='left', padx=5)
        theme_menu = ttk.OptionMenu(
            theme_frame, 
            self.theme_var, 
            self.theme,
            *themes,
            command=self.change_theme
        )
        theme_menu.pack(side='left', padx=5)

    def change_theme(self, theme_name):
        color_palettes = ColorPalettes(theme_name)
        self.colors = color_palettes.colors
        self.theme = theme_name
        self.update_widget_colors()
        
    def update_widget_colors(self):
        self.root.configure(bg=self.colors['background'])
        self.root.option_add("*foreground", self.colors['text'])
        self.root.option_add("*background", self.colors['background'])
        self.root.option_add("*selectBackground", self.colors['primary'])
        self.root.option_add("*selectForeground", self.colors['background'])
        self.style.configure("Cyber.TFrame",
            background=self.colors['background'],
            borderwidth=2,
            relief="solid"
        )
        self.style.configure("Cyber.TLabel",
            background=self.colors['background'],
            foreground=self.colors['primary'],
            font=("Consolas", 10)
        )
        self.style.configure("Cyber.TButton",
            background=self.colors['dark_element'],
            foreground=self.colors['primary']
        )
        self.style.map("Cyber.TButton",
            background=[('active', self.colors['primary'])],
            foreground=[('active', self.colors['background'])]
        )
        self.style.configure("Cyber.TNotebook",
            background=self.colors['background'],
            foreground=self.colors['text']
        )
        self.style.configure("Cyber.TNotebook.Tab",
            background=self.colors['dark_element'],
            foreground=self.colors['text']
        )
        for widget in [self.text_box, self.output_text]:
            widget.configure(
                bg=self.colors['dark_element'],
                fg=self.colors['text'],
                insertbackground=self.colors['primary'],
                selectbackground=self.colors['primary'],
                selectforeground=self.colors['background']
            )
        self.progress_canvas.configure(
            bg=self.colors['dark_element'],
            highlightbackground=self.colors['background']
        )
        self.root.update_idletasks()

    def on_tab_hover(self, event):
        self.style.configure("Cyber.TNotebook.Tab",
                            background=self.colors['primary'])

    def on_tab_leave(self, event):
        self.style.configure("Cyber.TNotebook.Tab",
                            background=self.colors['dark_element'])

    def create_gradient_frame(self, parent):
        gradient = tk.Canvas(parent, highlightthickness=0)
        gradient.pack(fill='both', expand=True)
        gradient_colors = [
            self.colors['background'],
            self.colors['dark_element'],
            self.colors['background']
        ]
        height = 400
        for i in range(len(gradient_colors) - 1):
            start_color = gradient_colors[i]
            end_color = gradient_colors[i + 1]
            for j in range(height // len(gradient_colors)):
                y = i * (height // len(gradient_colors)) + j
                gradient.create_line(
                    0, y, 800, y,
                    fill=self.interpolate_color(start_color, end_color, j/(height/len(gradient_colors)))
                )
        return gradient
        
    def interpolate_color(self, color1, color2, factor):
        r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        return f'#{r:02x}{g:02x}{b:02x}'

    def clear_all(self):
        # Stop any running process first
        if self.is_decoding:
            self.cipher_manager.stop_decoder()
            self.cleanup_process()
            self.is_decoding = False
        
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all fields?"):
            self.text_box.delete('1.0', tk.END)
            self.output_text.delete('1.0', tk.END)
            self.var_substitution.set(False)
            self.var_transposition.set(False)
            self.var_vigenere.set(False)
            self.vigenere_frame.pack_forget()
            
            # Reset progress display
            self.update_info['time'].config(text="Time: 0s")
            self.update_info['Best Fitness'].config(text="0.0000")
            self.update_info['Best text'].config(text="Best text: ")
            self.update_info['Best key'].config(text="Best key: ")
            self.progress_canvas.coords(self.progress_rect, 2, 2, 2, 18)
            self.progress_canvas.coords(self.glow_rect, 2, 2, 2, 18)

        
    def setup_main_tab(self):
        input_frame = ttk.LabelFrame(self.main_tab, text="INPUT", style="Cyber.TFrame", padding="10")
        input_frame.pack(fill='both', expand=True, padx=5, pady=5)
        for child in input_frame.winfo_children():
            child.configure(highlightthickness=2, highlightcolor=self.colors['primary'])
        self.text_box = scrolledtext.ScrolledText(
            input_frame, 
            height=10,
            bg=self.colors['dark_element'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            relief="solid",
            borderwidth=2,
            font=("Consolas", 10)
        )
        self.text_box.pack(fill='both', expand=True, padx=5, pady=5)
        cipher_frame = ttk.LabelFrame(self.main_tab, text="Cipher Selection", padding="5")
        cipher_frame.pack(fill='x', padx=5, pady=5)
        self.var_substitution = tk.BooleanVar()
        self.var_transposition = tk.BooleanVar()
        self.var_vigenere = tk.BooleanVar()
        ttk.Checkbutton(cipher_frame, text="Substitution", variable=self.var_substitution).pack(side='left', padx=5)
        ttk.Checkbutton(cipher_frame, text="Shuffle", variable=self.var_transposition, command=self.toggle_cipher_settings).pack(side='left', padx=5)
        ttk.Checkbutton(cipher_frame, text="Vigenere", variable=self.var_vigenere, command=self.toggle_cipher_settings).pack(side='left', padx=5)
        self.var_polybius = tk.BooleanVar()
        ttk.Checkbutton(cipher_frame, text="Polybius", 
                        variable=self.var_polybius,
                        command=self.toggle_cipher_settings).pack(side='left', padx=5)
        self.var_playfair = tk.BooleanVar()
        ttk.Checkbutton(cipher_frame, text="Playfair", 
                       variable=self.var_playfair,
                       command=self.toggle_cipher_settings).pack(side='left', padx=5)
        output_frame = ttk.LabelFrame(self.main_tab, text="Output", padding="5")
        output_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10)
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
        button_frame = ttk.Frame(self.main_tab)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Run Decoder", command=self.run_mcmc_algo).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_all).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Terminate", command=self.stop).pack(side='left', padx=5)
        self.text_box.bind('<<Modified>>', self.update_monogram)
        
    def setup_settings_tab(self):
        # Add common fitness frame at top of settings tab
        common_frame = ttk.LabelFrame(self.settings_tab, text="Common Settings", padding="5")
        common_frame.pack(fill='x', padx=5, pady=5)
        
        fitness_frame = ttk.Frame(common_frame)
        fitness_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(fitness_frame, text="Target Fitness Score:").pack(side='left', padx=5)
        self.target_fitness = tk.StringVar(value="0.4")
        ttk.Entry(fitness_frame, textvariable=self.target_fitness, width=8).pack(side='left', padx=2)

        # Add target fitness settings to each cipher frame
        self.vigenere_frame = ttk.LabelFrame(self.settings_tab, text="Vigenere Cipher Settings", padding="5")
        # ...existing vigenere frame setup...
        vigenere_fitness_frame = ttk.Frame(self.vigenere_frame)
        vigenere_fitness_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(vigenere_fitness_frame, text="Vigenere Target Fitness:").pack(side='left', padx=5)
        self.vigenere_target_fitness = tk.StringVar(value="0.4")
        ttk.Entry(vigenere_fitness_frame, textvariable=self.vigenere_target_fitness, width=8).pack(side='left', padx=2)

        self.shuffle_frame = ttk.LabelFrame(self.settings_tab, text="Shuffle Cipher Settings", padding="5")
        # ...existing shuffle frame setup...
        shuffle_fitness_frame = ttk.Frame(self.shuffle_frame)
        shuffle_fitness_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(shuffle_fitness_frame, text="Shuffle Target Fitness:").pack(side='left', padx=5)
        self.shuffle_target_fitness = tk.StringVar(value="0.4")
        ttk.Entry(shuffle_fitness_frame, textvariable=self.shuffle_target_fitness, width=8).pack(side='left', padx=2)

        self.polybius_frame = ttk.LabelFrame(self.settings_tab, text="Polybius Cipher Settings", padding="5")
        # ...existing polybius frame setup...
        polybius_fitness_frame = ttk.Frame(self.polybius_frame)
        polybius_fitness_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(polybius_fitness_frame, text="Polybius Target Fitness:").pack(side='left', padx=5)
        self.polybius_target_fitness = tk.StringVar(value="0.4")
        ttk.Entry(polybius_fitness_frame, textvariable=self.polybius_target_fitness, width=8).pack(side='left', padx=2)

        self.playfair_frame = ttk.LabelFrame(self.settings_tab, text="Playfair Cipher Settings", padding="5")
        # ...existing playfair frame setup...
        playfair_fitness_frame = ttk.Frame(self.playfair_frame)
        playfair_fitness_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(playfair_fitness_frame, text="Playfair Target Fitness:").pack(side='left', padx=5)
        self.playfair_target_fitness = tk.StringVar(value="0.4")
        ttk.Entry(playfair_fitness_frame, textvariable=self.playfair_target_fitness, width=8).pack(side='left', padx=2)

        self.vigenere_frame.pack(fill='x', padx=5, pady=5)
        key_frame = ttk.Frame(self.vigenere_frame)
        key_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(key_frame, text="Key Length Range:").pack(side='left', padx=5)
        self.min_key = tk.StringVar(value=str(config.MIN_KEY_LENGTH))
        self.max_key = tk.StringVar(value=str(config.MAX_KEY_LENGTH))
        ttk.Entry(key_frame, textvariable=self.min_key, width=5).pack(side='left', padx=2)
        ttk.Label(key_frame, text="to").pack(side='left', padx=2)
        ttk.Entry(key_frame, textvariable=self.max_key, width=5).pack(side='left', padx=2)
        stat_frame = ttk.Frame(self.vigenere_frame)
        stat_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(stat_frame, text="Expected IoC:").pack(side='left', padx=5)
        self.expected_ioc = tk.StringVar(value=str(config.EXPECTED_IOC))
        ttk.Entry(stat_frame, textvariable=self.expected_ioc, width=8).pack(side='left', padx=2)
        ttk.Label(stat_frame, text="Target Fitness:").pack(side='left', padx=5)
        self.target_fitness = tk.StringVar(value=str(config.TARGET_FITNESS))
        ttk.Entry(stat_frame, textvariable=self.target_fitness, width=8).pack(side='left', padx=2)
        algo_frame = ttk.Frame(self.vigenere_frame)
        algo_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(algo_frame, text="Max Iterations:").pack(side='left', padx=5)
        self.max_iterations = tk.StringVar(value=str(config.MAX_ITERATIONS))
        ttk.Entry(algo_frame, textvariable=self.max_iterations, width=10).pack(side='left', padx=2)
        parallel_frame = ttk.Frame(self.vigenere_frame)
        parallel_frame.pack(fill='x', padx=5, pady=5)
        self.use_parallel = tk.BooleanVar(value=config.USE_PARALLEL)
        ttk.Checkbutton(parallel_frame, text="Use Parallel Processing", variable=self.use_parallel).pack(side='left', padx=5)
        ttk.Label(parallel_frame, text="Max Workers:").pack(side='left', padx=5)
        self.max_workers = tk.StringVar(value=str(config.MAX_WORKERS))
        ttk.Entry(parallel_frame, textvariable=self.max_workers, width=5).pack(side='left', padx=2)
        ttk.Button(self.vigenere_frame, text="Save Settings", command=self.save_settings).pack(pady=10)
        self.vigenere_frame.pack_forget()
        key_override_frame = ttk.Frame(self.vigenere_frame)
        key_override_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(key_override_frame, text="Force Key Length:").pack(side='left', padx=5)
        self.key_length_var = tk.StringVar()
        ttk.Entry(key_override_frame, textvariable=self.key_length_var, width=5).pack(side='left', padx=2)
        ttk.Label(key_override_frame, text="(leave empty for auto-detection)").pack(side='left', padx=5)
        self.shuffle_frame = ttk.LabelFrame(self.settings_tab, text="Shuffle Cipher Settings", padding="5")
        self.shuffle_frame.pack(fill='x', padx=5, pady=5)
        shuffle_group_frame = ttk.Frame(self.shuffle_frame)
        shuffle_group_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(shuffle_group_frame, text="Group Size Range:").pack(side='left', padx=5)
        self.min_shuffle_group = tk.StringVar(value="2")
        self.max_shuffle_group = tk.StringVar(value="8")
        ttk.Entry(shuffle_group_frame, textvariable=self.min_shuffle_group, width=5).pack(side='left', padx=2)
        ttk.Label(shuffle_group_frame, text="to").pack(side='left', padx=2)
        ttk.Entry(shuffle_group_frame, textvariable=self.max_shuffle_group, width=5).pack(side='left', padx=2)
        shuffle_override_frame = ttk.Frame(self.shuffle_frame)
        shuffle_override_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(shuffle_override_frame, text="Force Group Size:").pack(side='left', padx=5)
        self.force_group_size = tk.StringVar()
        ttk.Entry(shuffle_override_frame, textvariable=self.force_group_size, width=5).pack(side='left', padx=2)
        ttk.Label(shuffle_override_frame, text="(leave empty for auto-detection)").pack(side='left', padx=5)
        self.shuffle_frame.pack_forget()
        self.polybius_frame = ttk.LabelFrame(self.settings_tab, text="Polybius Cipher Settings", padding="5")
        self.polybius_frame.pack(fill='x', padx=5, pady=5)
        key_frame = ttk.Frame(self.polybius_frame)
        key_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(key_frame, text="Initial Key:").pack(side='left', padx=5)
        self.polybius_key = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.polybius_key, width=25).pack(side='left', padx=2)
        ttk.Label(key_frame, text="(optional)").pack(side='left', padx=5)
        self.polybius_frame.pack_forget()
        self.playfair_frame = ttk.LabelFrame(self.settings_tab, text="Playfair Cipher Settings", padding="5")
        self.playfair_frame.pack(fill='x', padx=5, pady=5)
        key_frame = ttk.Frame(self.playfair_frame)
        key_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(key_frame, text="Initial Key (optional):").pack(side='left', padx=5)
        self.playfair_key = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.playfair_key, width=25).pack(side='left', padx=2)
        self.playfair_frame.pack_forget()

    def toggle_vigenere_settings(self):
        if self.var_vigenere.get():
            self.vigenere_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.vigenere_frame.pack_forget()

    def toggle_cipher_settings(self):
        if self.var_vigenere.get():
            self.vigenere_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.vigenere_frame.pack_forget()
            
        if self.var_transposition.get():
            self.shuffle_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.shuffle_frame.pack_forget()
            
        if self.var_polybius.get():
            self.polybius_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.polybius_frame.pack_forget()
            
        if self.var_playfair.get():
            self.playfair_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.playfair_frame.pack_forget()
            
    def save_settings(self):
        settings = {
            'min_key_length': self.min_key.get(),
            'max_key_length': self.max_key.get(),
            'expected_ioc': self.expected_ioc.get(),
            'target_fitness': self.target_fitness.get(),
            'max_iterations': self.max_iterations.get(),
            'use_parallel': self.use_parallel.get(),
            'max_workers': self.max_workers.get(),
            'min_shuffle_group': self.min_shuffle_group.get(),
            'max_shuffle_group': self.max_shuffle_group.get(),
            'target_fitness': self.target_fitness.get(),
            'vigenere_target_fitness': self.vigenere_target_fitness.get(),
            'shuffle_target_fitness': self.shuffle_target_fitness.get(),
            'polybius_target_fitness': self.polybius_target_fitness.get(),
            'playfair_target_fitness': self.playfair_target_fitness.get(),
        }
        
        if self.cipher_manager.update_config(settings):
            messagebox.showinfo("Success", "Settings saved successfully!")
        else:
            messagebox.showerror("Error", "Invalid input values. Please check your settings.")
    
    def stop(self):
        if not self.is_decoding:
            return
        
        # Immediately stop the decoder - don't wait
        self.cipher_manager.stop_decoder()
        self.is_decoding = False
        
        # Get current best result before cleanup
        current_result = self.cipher_manager.get_current_result()
        
        # Clean up processes
        self.cleanup_process()
        
        # Only create default if no result exists at all
        if current_result is None:
            # Get latest info from GUI elements as fallback
            try:
                score_text = self.update_info['Best Fitness'].cget('text')
                score = float(score_text) if score_text != "0.0000" else 0.0
                current_result = {
                    'success': True,
                    'key': self.update_info['Best key'].cget('text').replace('Best key: ', ''),
                    'score': score,
                    'text': self.update_info['Best text'].cget('text').replace('Best text: ', ''),
                    'plaintext': self.update_info['Best text'].cget('text').replace('Best text: ', '')
                }
            except:
                current_result = {'success': False, 'error': 'Terminated by user'}
        
        # Display the current best result
        if current_result.get('success'):
            self.display_result(current_result)
        
        # Reset GUI elements
        self.update_info['time'].config(text="Time: 0s")
        self.progress_canvas.coords(self.progress_rect, 2, 2, 2, 18)
        self.progress_canvas.coords(self.glow_rect, 2, 2, 2, 18)

    def run_mcmc_algo(self):
        # If already running, stop current process first
        if self.is_decoding:
            self.stop()
            # Small delay to ensure cleanup
            self.root.after(100, lambda: self._start_new_process())
        else:
            self._start_new_process()

    def progress_callback(self, message):
        """Global progress callback method"""
        self.output_text.insert('end', f"{message}\n")
        self.output_text.see('end')
        self.root.update()

    def _start_new_process(self):
        # Ensure any existing process is fully cleaned up
        self.cleanup_process()
        
        # Initialize a fresh queue for each run
        self.update_queue = Queue()
        
        cipher_text = self.text_box.get("1.0", tk.END).strip()
        if not cipher_text:
            messagebox.showwarning("Warning", "Please enter cipher text!")
            return
        
        # Reset and populate selected ciphers
        self.selected_ciphers = []
        if self.var_substitution.get():
            self.selected_ciphers.append('substitution')
        if self.var_transposition.get():  
            self.selected_ciphers.append('shuffle')
        if self.var_vigenere.get():
            self.selected_ciphers.append('vigenere')
        if self.var_polybius.get():
            self.selected_ciphers.append('polybius')
        if self.var_playfair.get():
            self.selected_ciphers.append('playfair')
                
        if not self.selected_ciphers:
            messagebox.showwarning("Warning", "Please select at least one cipher type!")
            return
            
        # Rest of the existing process starting code...
        try:
            self.is_decoding = True
            self.start_time = time.time()
            self.current_cipher = self.selected_ciphers[0]
            
            self.output_text.delete('1.0', tk.END)
            
            # Build kwargs based on cipher type
            kwargs = {
                'queue': self.update_queue,
                'progress_callback': self.progress_callback
            }
            
            if self.current_cipher == 'vigenere':
                if self.key_length_var.get():
                    kwargs['forced_length'] = int(self.key_length_var.get())
            elif self.current_cipher in ['polybius', 'playfair']:
                if getattr(self, f'{self.current_cipher}_key').get():
                    kwargs['initial_key'] = getattr(self, f'{self.current_cipher}_key').get()
            
            # Start decoder in separate thread
            if self.current_cipher == 'substitution':
                self.process = Process(
                    target=run_subprocess,
                    args=(cipher_text, self.update_queue)
                )
                self.process.daemon = True
                self.process.start()
            else:
                decode_thread = Thread(
                    target=self._run_decoder_thread,
                    args=(cipher_text, kwargs),
                    daemon=True
                )
                decode_thread.start()
            
            self.check_process()
                
        except Exception as e:
            self.cleanup_process()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.is_decoding = False

    def _run_decoder_thread(self, cipher_text, kwargs):
        """Run decoder in separate thread and put results in queue"""
        try:
            result = self.cipher_manager.start_decoder(
                self.current_cipher,
                cipher_text,
                **kwargs
            )
            self.update_queue.put({'type': 'finished', 'result': result})
        except Exception as e:
            self.update_queue.put({
                'type': 'finished', 
                'result': {'success': False, 'error': str(e)}
            })

    def cleanup_process(self):
        """Clean up existing process and queue"""
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1) 
            self.process = None
        
        if self.update_queue:
            while True:
                try:
                    self.update_queue.get_nowait()
                except queue.Empty:
                    break
            self.update_queue = None

    def check_process(self):
        """Check for updates from decoder process/thread"""
        if self.is_decoding:
            try:
                while True:
                    try:
                        update = self.update_queue.get_nowait()
                        if update.get('type') == 'progress':
                            self.update_display(update, time.time() - self.start_time)
                        elif update.get('type') == 'finished':
                            self.is_decoding = False
                            self.display_result(update['result'])
                            return
                    except queue.Empty:
                        break
                        
                self.root.after(50, self.check_process)
            except Exception as e:
                self.is_decoding = False
                messagebox.showerror("Error", f"Update error: {str(e)}")

    def update_display(self, update, current_time):
        """Update GUI elements with latest progress"""
        self.update_info['time'].config(text=f"Time: {current_time:.1f}s")
        
        fitness_score = update['score']
        width = int((2.0 - fitness_score) * 187.5)
        self.progress_canvas.coords(
            self.progress_rect,
            2, 2, 2 + width, 18
        )
        self.progress_canvas.coords(
            self.glow_rect,
            2, 2, 2 + width, 18
        )
        
        self.update_info['Best Fitness'].config(text=f"{fitness_score:.4f}")
        self.update_info['Best text'].config(text=f"Best text: {update['text'][:50]}...")
        self.update_info['Best key'].config(text=f"Best key: {update['key']}")
        
        self.root.update_idletasks()

    def update_text(self, event=None):
        text = self.text_input.get("1.0", tk.END)
        self.monogram_graph.update_graph(text)
        self.text_input.bind("<KeyRelease>", self.update_text)

    def show_monogram_window(self):
        self.notebook.select(2)

    def setup_monogram_tab(self):
        monogram_frame = ttk.Frame(self.notebook)
        self.notebook.add(monogram_frame, text="Character Analysis")
        ttk.Label(
            monogram_frame, 
            text="Enter text in the main input box to see character frequency analysis",
            style="Info.TLabel"
        ).pack(pady=10)
        self.monogram_graph = MonogramGraph(monogram_frame)
        self.monogram_graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update_monogram(self, event=None):
        text = self.text_box.get("1.0", tk.END).strip()
        if hasattr(self, 'monogram_graph'):
            self.monogram_graph.update_graph(text.replace(" ",""))
        self.text_box.edit_modified(False)

    def display_result(self, result):
        self.output_text.delete('1.0', tk.END)
        if result and result.get('success', False):
            text_key = 'text' if 'text' in result else 'plaintext'
            output_text = "=== Decryption Completed ===\n"
            output_text += f"Key: {str(result.get('key', 'N/A'))}\n"
            output_text += f"Fitness Score: {result.get('score', 0.0):.4f}\n"
            output_text += f"Iterations: {result.get('iterations', 0)}\n"
            output_text += f"Time Taken: {getattr(self, 'start_time', None) and f'{time.time() - self.start_time:.2f}s' or 'N/A'}\n"
            output_text += f"\nDecrypted Text:\n{str(result.get(text_key, 'N/A'))}"
            
            self.output_text.insert('1.0', output_text)
            popup = tk.Toplevel(self.root)
            popup.title("Decryption Result")
            popup.geometry("500x400")
            popup.configure(bg=self.colors['background'])
            popup.transient(self.root)
            popup.grab_set()
            frame = ttk.Frame(popup, style="Cyber.TFrame", padding="10")
            frame.pack(expand=True, fill='both', padx=10, pady=10)
            ttk.Label(frame, text="Decryption Status", style="Cyber.TLabel", font=("Consolas", 12, "bold")).pack(pady=5)
            ttk.Label(frame, text=f"Key Found: {str(result.get('key', 'N/A'))}", style="Cyber.TLabel").pack(pady=5)
            ttk.Label(frame, text=f"Fitness Score: {result.get('score', 0.0):.4f}", style="Cyber.TLabel").pack(pady=5)
            ttk.Label(frame, text=f"Time Taken: {getattr(self, 'start_time', None) and f'{time.time() - self.start_time:.2f}s' or 'N/A'}", style="Cyber.TLabel").pack(pady=5)
            ttk.Label(frame, text=f"Text: {str(result.get(text_key, 'N/A'))[:100]}...", style="Cyber.TLabel", wraplength=350).pack(pady=5)
            if 'profile' in result:
                prof_text = result['profile'][:10000] + ("..." if len(result['profile']) > 10000 else "")
                ttk.Label(frame, text="Profiling Info (Top 10):", style="Cyber.TLabel", font=("Consolas", 10, "bold")).pack(pady=5)
                prof_box = scrolledtext.ScrolledText(frame, height=8, width=60)
                prof_box.insert('1.0', prof_text)
                prof_box.config(state='disabled')
                prof_box.pack(pady=5)
            ttk.Button(frame, text="OK", style="Cyber.TButton", command=popup.destroy).pack(pady=10)
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
        

    def display_vigenere_result(self, result):
        self.output_text.delete('1.0', tk.END)
        
        if result['success']:
            output_text = "=== Decryption Results ===\n"
            output_text += f"Key found: {result['key']}\n"
            output_text += f"Fitness score: {result['score']:.4f}\n"
            output_text += f"\nDecrypted text:\n{result['plaintext']}\n"
            
            self.output_text.insert('1.0', output_text)
            
            # Create success popup
            popup = tk.Toplevel(self.root)
            popup.title("Vigenère Decryption Success!")
            popup.geometry("400x200")
            popup.configure(bg=self.colors['background'])
            
            # Make popup modal
            popup.transient(self.root)
            popup.grab_set()
            
            # Style the popup
            frame = ttk.Frame(popup, style="Cyber.TFrame", padding="10")
            frame.pack(expand=True, fill='both', padx=10, pady=10)
            
            ttk.Label(frame, text="🔓 Vigenère Cipher Solved!", 
                     style="Cyber.TLabel",
                     font=("Consolas", 12, "bold")).pack(pady=5)
            
            ttk.Label(frame, text=f"Key Found: {result['key']}",
                     style="Cyber.TLabel").pack(pady=5)
            
            ttk.Label(frame, text=f"Fitness Score: {result['score']:.4f}",
                     style="Cyber.TLabel").pack(pady=5)
            
            ttk.Button(frame, text="OK",
                      style="Cyber.TButton",
                      command=popup.destroy).pack(pady=10)
            
            # Center popup on main window
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
        else:
            error_msg = f"Decryption failed: {result.get('error', 'Unknown error')}"
            self.output_text.insert('1.0', error_msg)
            messagebox.showerror("Error", error_msg)

    def periodic_update(self):
        pass

    def on_closing(self):
        self.cleanup_process()
        self.root.destroy()

class MonogramWindow:
    def __init__(self, parent, text_widget):
        self.window = tk.Toplevel(parent)
        self.window.title("Character Frequency Analysis")
        self.window.geometry("600x400")
        self.graph = MonogramGraph(self.window)
        self.graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_widget = text_widget
        self.update_graph()
        self.text_widget.bind("<<Modified>>", self.update_graph)
        
    def update_graph(self, event=None):
        if self.text_widget:
            text = self.text_widget.get("1.0", tk.END)
            self.graph.update_graph(text)
        if event:
            self.text_widget.edit_modified(False)

def main():

    root = tk.Tk()
    app = CipherDecoderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
