import random

class ColorPalettes:
    def __init__(self, initial_theme):
        self.palettes = {
            'ocean_depths': {
                'background': '#3b6064',  # Dark Slate Gray
                'primary': '#87bba2',     # Cambridge Blue
                'secondary': '#3b6064',   # Dark Slate Gray
                'accent1': '#87bba2',     # Cambridge Blue
                'accent2': '#55828b',     # Blue Munsell
                'dark_element': '#364958',# Charcoal
                'text': '#c9e4ca',        # Tea Green
                'highlight': '#c9e4ca'    # Tea Green
            },
            'desert_sunset': {
                'background': '#2d1b14',  # Dark Brown
                'primary': '#e85d04',     # Persimmon
                'secondary': '#dc2f02',   # Dark Orange
                'accent1': '#f48c06',     # Orange
                'accent2': '#faa307',     # Yellow Orange
                'dark_element': '#1b1009', # Very Dark Brown
                'text': '#ffba08',        # Yellow
                'highlight': '#ffd60a'     # Bright Yellow
            },
            'forest_night': {
                'background': '#1a2f1c',  # Dark Green
                'primary': '#4a7c59',     # Forest Green
                'secondary': '#3d6548',   # Hunter Green
                'accent1': '#729d78',     # Sage
                'accent2': '#95b8a1',     # Light Sage
                'dark_element': '#0f1b11', # Very Dark Green
                'text': '#d4e6d7',        # Mint
                'highlight': '#e8f1e9'     # Light Mint
            },
            'arctic_aurora': {
                'background': '#1f2937',  # Dark Blue Gray
                'primary': '#4c7399',     # Steel Blue
                'secondary': '#385d7c',   # Dark Steel Blue
                'accent1': '#60a5fa',     # Bright Blue
                'accent2': '#34d399',     # Emerald
                'dark_element': '#111827', # Very Dark Blue Gray
                'text': '#f3f4f6',        # Light Gray
                'highlight': '#38bdf8'     # Sky Blue
            },
            'cyber_neon': {
                'background': '#0f0e17',  # Almost Black
                'primary': '#ff8906',     # Orange
                'secondary': '#f25f4c',   # Red
                'accent1': '#e53170',     # Pink
                'accent2': '#7f5af0',     # Purple
                'dark_element': '#0a0a0f', # Pure Black
                'text': '#fffffe',        # White
                'highlight': '#2cb67d'     # Green
            },
            'volcanic': {
                'background': '#1a0f0f',
                'primary': '#ff4000',
                'secondary': '#cc0000',
                'accent1': '#ff8533',
                'accent2': '#ffcc00',
                'dark_element': '#0d0707',
                'text': '#fff3e6',
                'highlight': '#ff6600'
            },
            'deep_space': {
                'background': '#0a001a',
                'primary': '#6600cc',
                'secondary': '#9933ff',
                'accent1': '#cc99ff',
                'accent2': '#ff99ff',
                'dark_element': '#05000d',
                'text': '#e6ccff',
                'highlight': '#bf80ff'
            },
            'jungle_mist': {
                'background': '#1a331a',
                'primary': '#2d862d',
                'secondary': '#39ac39',
                'accent1': '#70db70',
                'accent2': '#a3e6a3',
                'dark_element': '#0d1a0d',
                'text': '#e6ffe6',
                'highlight': '#00ff00'
            },
            'midnight_ruby': {
                'background': '#1a0013',
                'primary': '#cc0099',
                'secondary': '#ff00bf',
                'accent1': '#ff66d9',
                'accent2': '#ffb3ec',
                'dark_element': '#0d0009',
                'text': '#ffe6f9',
                'highlight': '#ff33cc'
            },
            'golden_desert': {
                'background': '#332600',
                'primary': '#ffb300',
                'secondary': '#ffc933',
                'accent1': '#ffd966',
                'accent2': '#ffe699',
                'dark_element': '#1a1300',
                'text': '#fff5cc',
                'highlight': '#ffcc00'
            },
            'arctic_frost': {
                'background': '#1a1a1a',
                'primary': '#66ffff',
                'secondary': '#00ffff',
                'accent1': '#99ffff',
                'accent2': '#ccffff',
                'dark_element': '#0d0d0d',
                'text': '#ffffff',
                'highlight': '#33ffff'
            },
            'blood_moon': {
                'background': '#1a0000',
                'primary': '#ff0000',
                'secondary': '#cc0000',
                'accent1': '#ff3333',
                'accent2': '#ff6666',
                'dark_element': '#0d0000',
                'text': '#ffcccc',
                'highlight': '#ff1a1a'
            },
            'emerald_city': {
                'background': '#00261a',
                'primary': '#00cc99',
                'secondary': '#00b386',
                'accent1': '#00ff80',
                'accent2': '#33ff99',
                'dark_element': '#00130d',
                'text': '#ccfff2',
                'highlight': '#00ffbf'
            },
            'purple_rain': {
                'background': '#1a001a',
                'primary': '#9900cc',
                'secondary': '#7700b3',
                'accent1': '#cc33ff',
                'accent2': '#d966ff',
                'dark_element': '#0d000d',
                'text': '#f2ccff',
                'highlight': '#bf00ff'
            },
            'electric_blue': {
                'background': '#001a33',
                'primary': '#0080ff',
                'secondary': '#0066cc',
                'accent1': '#3399ff',
                'accent2': '#66b3ff',
                'dark_element': '#000d1a',
                'text': '#cce6ff',
                'highlight': '#1a8cff'
            },
            'autumn_leaves': {
                'background': '#331400',
                'primary': '#ff6600',
                'secondary': '#cc5200',
                'accent1': '#ff944d',
                'accent2': '#ffb380',
                'dark_element': '#1a0a00',
                'text': '#ffe6cc',
                'highlight': '#ff8533'
            },
            'toxic_waste': {
                'background': '#1a2600',
                'primary': '#80ff00',
                'secondary': '#66cc00',
                'accent1': '#99ff33',
                'accent2': '#b3ff66',
                'dark_element': '#0d1300',
                'text': '#f2ffcc',
                'highlight': '#8cff1a'
            },
            'cotton_candy': {
                'background': '#330033',
                'primary': '#ff99ff',
                'secondary': '#ff66ff',
                'accent1': '#ffccff',
                'accent2': '#ffe6ff',
                'dark_element': '#1a001a',
                'text': '#fff2ff',
                'highlight': '#ffb3ff'
            },
            'deep_ocean': {
                'background': '#000033',
                'primary': '#0000ff',
                'secondary': '#0000cc',
                'accent1': '#3333ff',
                'accent2': '#6666ff',
                'dark_element': '#00001a',
                'text': '#ccccff',
                'highlight': '#1a1aff'
            },
            'sunset_coral': {
                'background': '#331419',
                'primary': '#ff6b6b',
                'secondary': '#cc5555',
                'accent1': '#ff8e8e',
                'accent2': '#ffb1b1',
                'dark_element': '#1a0a0d',
                'text': '#ffe1e1',
                'highlight': '#ff7777'
            }
        }
        # Initialize with specified theme or random if None
        if initial_theme is None:
            initial_theme = random.choice(list(self.palettes.keys()))
        self.colors = self.palettes.get(initial_theme, self.palettes['ocean_depths'])
        self.current_theme = initial_theme

    def get_available_palettes(self):
        """Returns a list of all available palette names"""
        return list(self.palettes.keys())

    def set_palette(self, name=None):
        """Set the current color palette. If name is None, chooses randomly.
        Returns (True, theme_name) if successful, (False, None) if palette name not found."""
        if name is None:
            name = random.choice(list(self.palettes.keys()))
        
        if name in self.palettes:
            self.colors = self.palettes[name].copy()
            self.current_theme = name
            return True, name
        return False, None