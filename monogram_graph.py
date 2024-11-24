import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

class MonogramGraph(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.figure = Figure(figsize=(6, 3))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def update_graph(self, text):
        self.ax.clear()
        if not text:
            return
            
        # Calculate frequencies
        char_freq = Counter(text.lower())
        chars = list(char_freq.keys())
        freqs = list(char_freq.values())
        
        # Create bar chart
        self.ax.bar(chars, freqs)
        self.ax.set_title('Character Frequencies')
        self.ax.set_xlabel('Characters')
        self.ax.set_ylabel('Frequency')
        self.ax.tick_params(axis='x', rotation=45)
        
        self.figure.tight_layout()
        self.canvas.draw()

# Example usage (can be removed when integrating):
if __name__ == "__main__":
    root = tk.Tk()
    graph = MonogramGraph(root)
    graph.pack(fill=tk.BOTH, expand=True)
    graph.update_graph("Hello World! This is a test.")
    root.mainloop()