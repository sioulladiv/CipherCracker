import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from cipher_manager import CipherManager
import config
from tkinter import PhotoImage
from ttkthemes import ThemedStyle
from monogram_graph import MonogramGraph
from multiprocessing import Process, Queue
import queue
import time  # Add this import


class CipherDecoderGUI:
    def __init__(self, root):
        self.root = root
        self.cipher_manager = CipherManager()
        self.root.title("Cipher Maxxer")
        self.root.geometry("800x700")
        
        # Apply modern theme
        self.style = ThemedStyle(self.root)
        self.style.set_theme("equilux")  # Modern dark theme
        
        # Configure colors
        self.bg_color = "#2E2E2E"
        self.accent_color = "#007ACC"
        self.text_color = "#FFFFFF"
        
        # Set window background
        self.root.configure(bg=self.bg_color)
        
        # Load and set icon
        icon = PhotoImage(file='icon.png')
        self.root.iconphoto(True, icon)
        
        # Custom style configurations
        self.style.configure("Custom.TNotebook",
                           background=self.bg_color,
                           padding=5)
        self.style.configure("Custom.TFrame",
                           background=self.bg_color)
        self.style.configure("Custom.TLabel",
                           background=self.bg_color,
                           foreground=self.text_color,
                           font=("Segoe UI", 10))
        self.style.configure("Custom.TButton",
                           background=self.accent_color,
                           foreground=self.text_color,
                           padding=(10, 5),
                           font=("Segoe UI", 10))
        
        # Create notebook with custom style
        self.notebook = ttk.Notebook(root, style="Custom.TNotebook")
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Main tab with custom styling
        self.main_tab = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(self.main_tab, text="Main")
        
        # Settings tab with custom styling
        self.settings_tab = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(self.settings_tab, text="Sigma Settings")
        
        # Add tab hover effect
        self.notebook.bind("<Enter>", self.on_tab_hover)
        self.notebook.bind("<Leave>", self.on_tab_leave)
        
        self.setup_main_tab()
        self.setup_settings_tab()
        self.setup_monogram_tab()

        # Create main container for layout
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side: Text input and buttons
        self.left_frame = ttk.Frame(self.main_container)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.update_info = {}
        self.update_info['time'] = ttk.Label(self.left_frame, text="time: 0")
        self.update_info['Best Fitness'] = ttk.Label(self.left_frame, text="Best Fitness: 0")
        self.update_info['Best text'] = ttk.Label(self.left_frame, text="Best text: 0")
        self.update_info['Best key'] = ttk.Label(self.left_frame, text="Best key: 0")
        for key in self.update_info:
            self.update_info[key].pack(side=tk.TOP, anchor='w')
            
        # Add this line to track if decoding is running
        self.is_decoding = False
        
        # Start the periodic update
        self.update_interval = 500  # 500ms = 0.5 seconds
        self.periodic_update()
 
        # self.monogram_button = ttk.Button(
        #     self.left_frame,
        #     text="Character Frequencies",
        #     command=self.show_monogram_window
        # )
        # self.monogram_button.pack(side=tk.LEFT, padx=2)

        self.update_queue = Queue()
        self.process = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.start_time = None

    def on_tab_hover(self, event):
        """Add hover effect to tabs"""
        self.style.configure("Custom.TNotebook.Tab",
                           background=self.accent_color)

    def on_tab_leave(self, event):
        """Remove hover effect from tabs"""
        self.style.configure("Custom.TNotebook.Tab",
                           background=self.bg_color)

    def create_gradient_frame(self, parent):
        """Create a frame with gradient effect"""
        gradient = tk.Canvas(parent, highlightthickness=0)
        gradient.pack(fill='both', expand=True)
        
        colors = [self.bg_color, self.accent_color]
        for i in range(len(colors)-1):
            gradient.create_gradient(colors[i], colors[i+1])
        
        return gradient

    def clear_all(self):
        """Clear all input and output text fields"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all fields?"):
            self.text_box.delete('1.0', tk.END)
            self.output_text.delete('1.0', tk.END)
            # Reset cipher selections
            self.var_substitution.set(False)
            self.var_transposition.set(False)
            self.var_vigenere.set(False)
            # Hide Vigenere settings if visible
            self.vigenere_frame.pack_forget()
        
    def setup_main_tab(self):
        # Input frame
        input_frame = ttk.LabelFrame(self.main_tab, text="Input", padding="5")
        input_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Cipher text input
        self.text_box = scrolledtext.ScrolledText(input_frame, height=10)
        self.text_box.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Cipher selection frame
        cipher_frame = ttk.LabelFrame(self.main_tab, text="Cipher Selection", padding="5")
        cipher_frame.pack(fill='x', padx=5, pady=5)
        
        # Cipher checkboxes
        self.var_substitution = tk.BooleanVar()
        self.var_transposition = tk.BooleanVar()  # Now used for shuffle
        self.var_vigenere = tk.BooleanVar()
        
        ttk.Checkbutton(cipher_frame, text="Substitution", variable=self.var_substitution).pack(side='left', padx=5)
        ttk.Checkbutton(cipher_frame, text="Shuffle", variable=self.var_transposition, command=self.toggle_cipher_settings).pack(side='left', padx=5)
        ttk.Checkbutton(cipher_frame, text="Vigenere", variable=self.var_vigenere, command=self.toggle_cipher_settings).pack(side='left', padx=5)
        
        # Add Polybius checkbox
        self.var_polybius = tk.BooleanVar()
        ttk.Checkbutton(cipher_frame, text="Polybius", 
                        variable=self.var_polybius,
                        command=self.toggle_cipher_settings).pack(side='left', padx=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(self.main_tab, text="Output", padding="5")
        output_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10)
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.main_tab)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Run Decoder", command=self.run_mcmc_algo).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_all).pack(side='left', padx=5)
        
        # Add binding to text box for automatic updates
        self.text_box.bind('<<Modified>>', self.update_monogram)
        #update = tk.Label(self, text="My clicker app").pack()
        
    def setup_settings_tab(self):
        self.vigenere_frame = ttk.LabelFrame(self.settings_tab, text="Vigenere Cipher Settings", padding="5")
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
        
        # Algorithm settings
        algo_frame = ttk.Frame(self.vigenere_frame)
        algo_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(algo_frame, text="Max Iterations:").pack(side='left', padx=5)
        self.max_iterations = tk.StringVar(value=str(config.MAX_ITERATIONS))
        ttk.Entry(algo_frame, textvariable=self.max_iterations, width=10).pack(side='left', padx=2)
        
        # Parallel processing
        parallel_frame = ttk.Frame(self.vigenere_frame)
        parallel_frame.pack(fill='x', padx=5, pady=5)
        
        self.use_parallel = tk.BooleanVar(value=config.USE_PARALLEL)
        ttk.Checkbutton(parallel_frame, text="Use Parallel Processing", variable=self.use_parallel).pack(side='left', padx=5)
        
        ttk.Label(parallel_frame, text="Max Workers:").pack(side='left', padx=5)
        self.max_workers = tk.StringVar(value=str(config.MAX_WORKERS))
        ttk.Entry(parallel_frame, textvariable=self.max_workers, width=5).pack(side='left', padx=2)
        
        # Save settings button
        ttk.Button(self.vigenere_frame, text="Save Settings", command=self.save_settings).pack(pady=10)
        
        # Initially hide Vigenere settings
        self.vigenere_frame.pack_forget()
        key_override_frame = ttk.Frame(self.vigenere_frame)
        key_override_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(key_override_frame, text="Force Key Length:").pack(side='left', padx=5)
        self.key_length_var = tk.StringVar()
        ttk.Entry(key_override_frame, textvariable=self.key_length_var, width=5).pack(side='left', padx=2)
        ttk.Label(key_override_frame, text="(leave empty for auto-detection)").pack(side='left', padx=5)

        # Add Shuffle Cipher Settings
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
        
        # Force specific group size
        shuffle_override_frame = ttk.Frame(self.shuffle_frame)
        shuffle_override_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(shuffle_override_frame, text="Force Group Size:").pack(side='left', padx=5)
        self.force_group_size = tk.StringVar()
        ttk.Entry(shuffle_override_frame, textvariable=self.force_group_size, width=5).pack(side='left', padx=2)
        ttk.Label(shuffle_override_frame, text="(leave empty for auto-detection)").pack(side='left', padx=5)
        
        # Initially hide Shuffle settings
        self.shuffle_frame.pack_forget()
        
        # Add Polybius Settings
        self.polybius_frame = ttk.LabelFrame(self.settings_tab, text="Polybius Cipher Settings", padding="5")
        self.polybius_frame.pack(fill='x', padx=5, pady=5)
        
        # Initial key input
        key_frame = ttk.Frame(self.polybius_frame)
        key_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(key_frame, text="Initial Key:").pack(side='left', padx=5)
        self.polybius_key = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.polybius_key, width=25).pack(side='left', padx=2)
        ttk.Label(key_frame, text="(optional)").pack(side='left', padx=5)
        
        # Initially hide Polybius settings
        self.polybius_frame.pack_forget()

    def toggle_vigenere_settings(self):
        if self.var_vigenere.get():
            self.vigenere_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.vigenere_frame.pack_forget()

    def toggle_cipher_settings(self):
        """Show/hide cipher specific settings based on selection"""
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
            'max_shuffle_group': self.max_shuffle_group.get()
        }
        
        if self.cipher_manager.update_config(settings):
            messagebox.showinfo("Success", "Settings saved successfully!")
        else:
            messagebox.showerror("Error", "Invalid input values. Please check your settings.")
            
    def run_mcmc_algo(self):
        cipher_text = self.text_box.get("1.0", tk.END).strip()
        if not cipher_text:
            messagebox.showwarning("Warning", "Please enter cipher text!")
            return
                
        self.selected_ciphers = []
        if self.var_substitution.get():
            self.selected_ciphers.append('substitution')
        if self.var_transposition.get():  # Now checks for shuffle cipher
            self.selected_ciphers.append('shuffle')
        if self.var_vigenere.get():
            self.selected_ciphers.append('vigenere')
        if self.var_polybius.get():
            self.selected_ciphers.append('polybius')
                
        if not self.selected_ciphers:
            messagebox.showwarning("Warning", "Please select at least one cipher type!")
            return
        
        try:
            self.is_decoding = True  # Set flag when starting decode
            self.start_time = time.time()  # Start timing when decoding begins
            if 'vigenere' in self.selected_ciphers:
                self.run_vigenere_decoder(cipher_text)
            elif 'shuffle' in self.selected_ciphers:  # Changed from transposition
                self.run_shuffle_decoder(cipher_text)
            elif 'polybius' in self.selected_ciphers:
                self.run_polybius_decoder(cipher_text)
            else:
                # Start decoding in separate process
                self.process = Process(
                    target=self.cipher_manager.run_substitution_decoder,
                    args=(cipher_text, None, None, self.update_queue)
                )
                self.process.start()
                self.check_process()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.is_decoding = False

    def check_process(self):
        """Check for updates from the decoding process"""
        if self.is_decoding:
            latest_update = None
            # Empty the queue and keep only the latest update
            try:
                while True:
                    update = self.update_queue.get_nowait()
                    if update.get('type') == 'progress':
                        latest_update = update
                    elif update.get('type') == 'finished':
                        self.is_decoding = False
                        self.display_result(update['result'])
                        return
            except queue.Empty:
                pass

            # Process only the most recent update
            if latest_update:
                current_time = time.time() - self.start_time
                self.update_info['time'].config(text=f"Time: {current_time:.1f}s")
                self.update_info['Best Fitness'].config(text=f"Best Fitness: {latest_update['score']:.4f}")
                self.update_info['Best text'].config(text=f"Best text: {latest_update['text'][:50]}...")
                self.update_info['Best key'].config(text=f"Best key: {latest_update['key']}")
            
            # Schedule next check
            self.root.after(self.update_interval, self.check_process)
            
    # Add this new method to CipherDecoderGUI class
    def run_vigenere_decoder(self, cipher_text):
        """Handle Vigenere cipher decoding"""
        # Update status
        self.output_text.delete('1.0', tk.END)
        
        def progress_callback(message):
            """Callback to update GUI with progress"""
            self.output_text.insert('end', f"{message}\n")
            self.output_text.see('end')
            self.root.update()
        
        forced_length = None
        if hasattr(self, 'key_length_var') and self.key_length_var.get():
            try:
                forced_length = int(self.key_length_var.get())
            except ValueError:
                pass

        result = self.cipher_manager.run_vigenere_decoder(
            cipher_text, 
            forced_length, 
            progress_callback
        )

        if result['success']:
            self.display_vigenere_result(result)
        else:
            messagebox.showerror("Error", f"Decryption failed: {result['error']}")

    def run_shuffle_decoder(self, cipher_text):
        """Handle Shuffle cipher decoding"""
        self.output_text.delete('1.0', tk.END)
        
        def progress_callback(message):
            self.output_text.insert('end', f"{message}\n")
            self.output_text.see('end')
            self.root.update()
        
        forced_size = None
        if self.force_group_size.get():
            try:
                forced_size = int(self.force_group_size.get())
            except ValueError:
                pass

        result = self.cipher_manager.run_shuffle_decoder(
            cipher_text,
            forced_size,
            progress_callback
        )

        if result['success']:
            self.display_shuffle_result(result)
        else:
            messagebox.showerror("Error", f"Decryption failed: {result['error']}")

    def display_shuffle_result(self, result):
        """Display Shuffle decoder results"""
        self.output_text.delete('1.0', tk.END)
        
        if result['success']:
            output_text = "=== Shuffle Decryption Results ===\n"
            output_text += f"Permutation: {result['key']}\n"
            output_text += f"Group size: {len(result['key'])}\n"
            output_text += f"Fitness score: {result['score']:.4f}\n"
            output_text += f"\nDecrypted text:\n{result['plaintext']}\n"
            
            self.output_text.insert('1.0', output_text)
            messagebox.showinfo("Success", f"Decryption completed! Group size: {len(result['key'])}")
        else:
            error_msg = f"Decryption failed: {result.get('error', 'Unknown error')}"
            self.output_text.insert('1.0', error_msg)
            messagebox.showerror("Error", error_msg)

    def run_polybius_decoder(self, cipher_text):
        """Handle Polybius cipher decoding"""
        self.output_text.delete('1.0', tk.END)
        
        def progress_callback(message):
            self.output_text.insert('end', f"{message}\n")
            self.output_text.see('end')
            self.root.update()

        initial_key = self.polybius_key.get() if self.polybius_key.get() else None
        
        result = self.cipher_manager.run_polybius_decoder(
            cipher_text,
            initial_key,
            progress_callback
        )

        if result['success']:
            self.display_polybius_result(result)
        else:
            messagebox.showerror("Error", f"Decryption failed: {result['error']}")

    def display_polybius_result(self, result):
        """Display Polybius decoder results"""
        self.output_text.delete('1.0', tk.END)
        
        if result['success']:
            output_text = "=== Polybius Decryption Results ===\n"
            output_text += f"Key: {result['key']}\n"
            output_text += f"Fitness score: {result['score']:.4f}\n"
            output_text += f"\nDecrypted text:\n{result['plaintext']}\n"
            
            self.output_text.insert('1.0', output_text)
            messagebox.showinfo("Success", "Decryption completed!")
        else:
            error_msg = f"Decryption failed: {result.get('error', 'Unknown error')}"
            self.output_text.insert('1.0', error_msg)
            messagebox.showerror("Error", error_msg)

    # Add this wherever you handle text changes
    def update_text(self, event=None):
        text = self.text_input.get("1.0", tk.END)  # Assuming you have a text input widget
        self.monogram_graph.update_graph(text.replace(" ",""))
        self.text_input.bind("<KeyRelease>", self.update_text)

    # Update show_monogram_window method
    def show_monogram_window(self):
        self.notebook.select(2)  # Switch to monogram tab

    # Add this method to CipherDecoderGUI class
    def setup_monogram_tab(self):
        monogram_frame = ttk.Frame(self.notebook)
        self.notebook.add(monogram_frame, text="Character Analysis")
        
        # Add instruction label
        ttk.Label(
            monogram_frame, 
            text="Enter text in the main input box to see character frequency analysis",
            style="Info.TLabel"
        ).pack(pady=10)
        
        # Add monogram graph
        self.monogram_graph = MonogramGraph(monogram_frame)
        self.monogram_graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update_monogram(self, event=None):
        text = self.text_box.get("1.0", tk.END).strip()
        if hasattr(self, 'monogram_graph'):
            self.monogram_graph.update_graph(text)
        # Reset modified flag
        self.text_box.edit_modified(False)

    def display_result(self, result):
        """Display MCMC decoder results"""
        self.output_text.delete('1.0', tk.END)
        
        if result['success']:
            output_text = "Decryption completed.\n"
            output_text += f"Key: {str(result.get('key', 'N/A'))}\n"
            output_text += f"Fitness Score: {result.get('score', 0.0):.4f}\n"
            output_text += f"Iterations: {result.get('iterations', 0)}\n"
            output_text += f"Decrypted Text: {str(result.get('text', 'N/A'))}"
        else:
            output_text = f"Decryption failed: {result.get('error', 'Unknown error')}\n"
            
        self.output_text.insert('1.0', output_text)

    def display_vigenere_result(self, result):
        """Display Vigenere decoder results"""
        self.output_text.delete('1.0', tk.END)
        
        if result['success']:
            output_text = "=== Decryption Results ===\n"
            output_text += f"Key found: {result['key']}\n"
            output_text += f"Fitness score: {result['score']:.4f}\n"
            output_text += f"\nDecrypted text:\n{result['plaintext']}\n"
            
            self.output_text.insert('1.0', output_text)
            messagebox.showinfo("Success", f"Decryption completed! Key found: {result['key']}")
        else:
            error_msg = f"Decryption failed: {result.get('error', 'Unknown error')}"
            self.output_text.insert('1.0', error_msg)
            messagebox.showerror("Error", error_msg)

    def periodic_update(self):
        """Remove this method since we're now handling updates in check_process"""
        pass

    def on_closing(self):
        if self.process and self.process.is_alive():
            self.process.terminate()
        self.root.destroy()

# Add this class after CipherDecoderGUI class
class MonogramWindow:
    def __init__(self, parent, text_widget):
        self.window = tk.Toplevel(parent)
        self.window.title("Character Frequency Analysis")
        self.window.geometry("600x400")
        
        # Create monogram graph
        self.graph = MonogramGraph(self.window)
        self.graph.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Update with current text
        self.text_widget = text_widget
        self.update_graph()
        
        # Bind text widget updates
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
if __name__ == "__main__":
    main()
