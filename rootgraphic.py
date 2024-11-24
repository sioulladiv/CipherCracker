import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
from cipher_utils import bigram_fitness
from MCMC_ALGO import transp_subst_run
import config
from vigenere import VigenereCracker
from tkinter import PhotoImage
from ttkthemes import ThemedStyle
from monogram_graph import MonogramGraph


class CipherDecoderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher Maxxer")
        self.root.geometry("800x600")
        
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

        # Add monogram button
        self.monogram_button = ttk.Button(
            self.left_frame,
            text="Character Frequencies",
            command=self.show_monogram_window
        )
        self.monogram_button.pack(side=tk.LEFT, padx=2)

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
        self.var_transposition = tk.BooleanVar()
        self.var_vigenere = tk.BooleanVar()
        
        ttk.Checkbutton(cipher_frame, text="Substitution", variable=self.var_substitution).pack(side='left', padx=5)
        ttk.Checkbutton(cipher_frame, text="Transposition", variable=self.var_transposition).pack(side='left', padx=5)
        ttk.Checkbutton(cipher_frame, text="Vigenere", variable=self.var_vigenere, command=self.toggle_vigenere_settings).pack(side='left', padx=5)
        
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
        
    def toggle_vigenere_settings(self):
        if self.var_vigenere.get():
            self.vigenere_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.vigenere_frame.pack_forget()
            
    def save_settings(self):
        try:
            config.MIN_KEY_LENGTH = int(self.min_key.get())
            config.MAX_KEY_LENGTH = int(self.max_key.get())
            config.EXPECTED_IOC = float(self.expected_ioc.get())
            config.TARGET_FITNESS = float(self.target_fitness.get())
            config.MAX_ITERATIONS = int(self.max_iterations.get())
            config.USE_PARALLEL = self.use_parallel.get()
            config.MAX_WORKERS = int(self.max_workers.get())
            messagebox.showinfo("Success", "Settings saved successfully!")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid input values. Please check your settings.")
            
    def run_mcmc_algo(self):
        cipher_text = self.text_box.get("1.0", tk.END).strip()
        if not cipher_text:
            messagebox.showwarning("Warning", "Please enter cipher text!")
            return
                
        selected_ciphers = []
        if self.var_substitution.get():
            selected_ciphers.append('substitution')
        if self.var_transposition.get():
            selected_ciphers.append('transposition')
        if self.var_vigenere.get():
            selected_ciphers.append('vigenere')
                
        if not selected_ciphers:
            messagebox.showwarning("Warning", "Please select at least one cipher type!")
            return
        
        try:
            if 'vigenere' in selected_ciphers:
                self.run_vigenere_decoder(cipher_text)
            else:
                result = transp_subst_run(cipher_text, selected_ciphers[0])
                
                self.output_text.delete('1.0', tk.END)
                
                # Create default values if result is None
                if result is None:
                    result = {
                        'text': 'N/A',
                        'key': 'N/A',
                        'score': 0.0,
                        'iterations': 0
                    }
                    messagebox.showwarning("Warning", "Decryption was interrupted")
                    output_text = "Decryption was interrupted.\n"
                else:
                    output_text = "Decryption completed.\n"
                
                # Safely access dictionary values with defaults
                output_text += f"Key: {str(result.get('key', 'N/A'))}\n"
                output_text += f"Fitness Score: {result.get('score', 0.0):.4f}\n"
                output_text += f"Iterations: {result.get('iterations', 0)}\n"
                output_text += f"Decrypted Text: {str(result.get('text', 'N/A'))}"

                
                self.output_text.insert('1.0', output_text)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
              
        
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
        
        try:
            # Initialize cracker with progress callback
            cracker = VigenereCracker()
            cracker.progress_callback = progress_callback
            
            # Get key length from GUI if specified
            forced_length = None
            if hasattr(self, 'key_length_var') and self.key_length_var.get():
                try:
                    forced_length = int(self.key_length_var.get())
                except ValueError:
                    pass
            
            # Run decryption
            plaintext, key, score = cracker.decrypt(cipher_text, forced_length)
            
            # Format and display results
            result = f"\n=== Decryption Results ===\n"
            result += f"Key found: {key}\n"
            result += f"Fitness score: {score:.4f}\n"
            result += f"\nDecrypted text:\n{plaintext}\n"
            
            self.output_text.insert('end', result)
            self.output_text.see('end')
            
            # Show success message
            messagebox.showinfo("Success", f"Decryption completed!\nKey found: {key}")
            
        except Exception as e:
            self.output_text.insert('end', f"\nError: {str(e)}")
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")

    # Add this wherever you handle text changes
    def update_text(self, event=None):
        text = self.text_input.get("1.0", tk.END)  # Assuming you have a text input widget
        self.monogram_graph.update_graph(text)
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