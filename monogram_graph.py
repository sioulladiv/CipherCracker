import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

letterFrequency = {'E' : 12.0,
'T' : 9.10,
'A' : 8.12,
'O' : 7.68,
'I' : 7.31,
'N' : 6.95,
'S' : 6.28,
'R' : 6.02,
'H' : 5.92,
'D' : 4.32,
'L' : 3.98,
'U' : 2.88,
'C' : 2.71,
'M' : 2.61,
'F' : 2.30,
'Y' : 2.11,
'W' : 2.09,
'G' : 2.03,
'P' : 1.82,
'B' : 1.49,
'V' : 1.11,
'K' : 0.69,
'X' : 0.17,
'Q' : 0.11,
'J' : 0.10,
'Z' : 0.07 }

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
            
        char_freq = Counter(c.upper() for c in text if c.isalpha())
        total = sum(char_freq.values())
        if total == 0:
            return
            
        chars = sorted(char_freq.keys())
        actual_values = [char_freq[c] for c in chars]
        expected_values = [letterFrequency.get(c, 0) / 100 * total for c in chars]

        x = range(len(chars))
        width = 0.35
        
        self.ax.bar([i - width/2 for i in x], actual_values, width, 
            label='Actual', color='steelblue')
        self.ax.bar([i + width/2 for i in x], expected_values, width, 
            label='Expected', color='coral')

        self.ax.set_title('Character Frequencies')
        self.ax.set_xlabel('Characters')
        self.ax.set_ylabel('Frequency')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(chars)
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()

# Example usage (can be removed when integrating):
if __name__ == "__main__":
    root = tk.Tk()
    graph = MonogramGraph(root)
    graph.pack(fill=tk.BOTH, expand=True)
    graph.update_graph("Hello World! This is a test.")
    root.mainloop()