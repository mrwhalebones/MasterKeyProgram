import os
import hashlib
import base58
import gzip
import threading
from concurrent.futures import ThreadPoolExecutor
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

# Resize window for better puzzle visualization
Window.size = (1000, 700)

class MainScreen(Screen):
    """Main UI for WIF Private Key Generation."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")

        self.private_key = TextInput(hint_text="Enter Private Key (or Generate)", multiline=False)
        layout.add_widget(self.private_key)

        generate_btn = Button(text="Generate Random Key")
        generate_btn.bind(on_press=self.generate_private_key)
        layout.add_widget(generate_btn)

        convert_btn = Button(text="Generate WIFs")
        convert_btn.bind(on_press=self.generate_wifs)
        layout.add_widget(convert_btn)

        solve_puzzles_btn = Button(text="Solve Puzzles")
        solve_puzzles_btn.bind(on_press=self.go_to_puzzle_screen)
        layout.add_widget(solve_puzzles_btn)

        self.compressed_wif = Label(text="Compressed WIF: ")
        layout.add_widget(self.compressed_wif)

        self.uncompressed_wif = Label(text="Uncompressed WIF: ")
        layout.add_widget(self.uncompressed_wif)

        self.add_widget(layout)

    def generate_private_key(self, instance):
        """Generate a random 64-character hexadecimal private key."""
        self.private_key.text = os.urandom(32).hex()

    def to_wif(self, private_key_hex, compressed=True):
        """Convert a private key to Wallet Import Format (WIF)."""
        prefix = "80"
        key_with_prefix = prefix + private_key_hex
        if compressed:
            key_with_prefix += "01"

        hashed = hashlib.sha256(bytes.fromhex(key_with_prefix)).digest()
        hashed = hashlib.sha256(hashed).digest()
        checksum = hashed[:4].hex()

        final_key = key_with_prefix + checksum
        return base58.b58encode(bytes.fromhex(final_key)).decode()

    def generate_wifs(self, instance):
        """Generate both compressed and uncompressed WIF formats for a given private key."""
        pk = self.private_key.text.strip()
        if len(pk) != 64:
            return

        self.compressed_wif.text = f"Compressed WIF: {self.to_wif(pk, compressed=True)}"
        self.uncompressed_wif.text = f"Uncompressed WIF: {self.to_wif(pk, compressed=False)}"

    def go_to_puzzle_screen(self, instance):
        """Switch to the puzzle-solving screen."""
        self.manager.current = "puzzle_screen"


class PuzzleScreen(Screen):
    """Advanced puzzle-solving with historical search data."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")

        self.puzzle_number = TextInput(hint_text="Enter Puzzle Number", multiline=False)
        layout.add_widget(self.puzzle_number)

        solve_btn = Button(text="Generate WIFs for Puzzle")
        solve_btn.bind(on_press=self.solve_puzzle)
        layout.add_widget(solve_btn)

        self.status_label = Label(text="Puzzle Status: Unknown")
        layout.add_widget(self.status_label)

        scroll_view = ScrollView(size_hint=(1, 0.5))
        puzzle_grid = GridLayout(cols=1, size_hint_y=None)
        puzzle_grid.bind(minimum_height=puzzle_grid.setter('height'))

        # Puzzle data retrieved from the webpage
        puzzles = [
            ("Puzzle 69", "6.9 BTC", "100000000000000000", "1fffffffffffffffff", 0),
            ("Puzzle 71", "7.1 BTC", "400000000000000000", "7fffffffffffffffff", 64.4),
            ("Puzzle 135", "13.5 BTC", "4000000000000000000000000000000000000", "7fffffffffffffffffffffffffffffff", 62.2),
        ]

        for puzzle_name, prize, start_range, end_range, solved_percent in puzzles:
            btn = Button(text=f"{puzzle_name} - {prize} | {solved_percent}% Found", size_hint_y=None, height=40)
            btn.bind(on_press=lambda instance, p_num=puzzle_name.split()[1], sr=start_range, er=end_range, sp=solved_percent: self.select_puzzle(p_num, sr, er, sp))
            puzzle_grid.add_widget(btn)

        scroll_view.add_widget(puzzle_grid)
        layout.add_widget(scroll_view)

        back_btn = Button(text="Back to Main Screen")
        back_btn.bind(on_press=self.go_to_main_screen)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def select_puzzle(self, puzzle_id, start_range, end_range, solved_percent):
        """Autofill puzzle number and set private key range for advanced search."""
        self.puzzle_number.text = puzzle_id
        self.start_range = int(start_range, 16)
        self.end_range = int(end_range, 16)
        self.search_range = int(self.start_range + (self.end_range - self.start_range) * (solved_percent / 100)) if solved_percent > 0 else self.end_range

    def solve_puzzle(self, instance):
        """Perform an advanced WIF search using historical solved percentages."""
        puzzle_id = self.puzzle_number.text.strip()

        if not puzzle_id:
            popup = Popup(title="Error",
                          content=Label(text="Please select a puzzle before proceeding."),
                          size_hint=(0.5, 0.3))
            popup.open()
            return

        self.multi_threaded_wif_generation(puzzle_id, self.start_range, self.search_range)

    def multi_threaded_wif_generation(self, puzzle_id, start_range, search_range):
        """Parallel WIF generation using multiple threads based on search probability."""
        output_dir = r"E:\puzzle_results"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"puzzle_{puzzle_id}_advanced_search.txt")

        def generate_key_wif(key):
            wif_compressed = self.to_wif(hex(key)[2:], compressed=True)
            wif_uncompressed = self.to_wif(hex(key)[2:], compressed=False)
            return f"Private Key: {hex(key)}\nCompressed WIF: {wif_compressed}\nUncompressed WIF: {wif_uncompressed}\n\n"

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(generate_key_wif, range(start_range, search_range)))

        with open(output_file, "w") as file:
            file.writelines(results)

        popup = Popup(title="Advanced Search Complete",
                      content=Label(text=f"Advanced WIFs saved in {output_file}"),
                      size_hint=(0.5, 0.3))
        popup.open()

    def go_to_main_screen(self, instance):
        """Switch back to the main screen."""
        self.manager.current = "main_screen"


class WIFApp(App):
    def build(self):
        """Launch the app with screen navigation."""
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(PuzzleScreen(name="puzzle_screen"))
        return sm

if __name__ == "__main__":
    WIFApp().run()
