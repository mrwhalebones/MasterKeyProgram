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
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

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

        save_btn = Button(text="Save to File")
        save_btn.bind(on_press=self.save_to_file)
        layout.add_widget(save_btn)

        load_btn = Button(text="Load Last Saved Key")
        load_btn.bind(on_press=self.load_from_file)
        layout.add_widget(load_btn)

        self.compressed_wif = Label(text="Compressed WIF: ")
        layout.add_widget(self.compressed_wif)

        self.uncompressed_wif = Label(text="Uncompressed WIF: ")
        layout.add_widget(self.uncompressed_wif)

        solve_puzzles_btn = Button(text="Solve Puzzles")
        solve_puzzles_btn.bind(on_press=self.go_to_puzzle_screen)
        layout.add_widget(solve_puzzles_btn)

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
            self.compressed_wif.text = "Error: Invalid Private Key!"
            self.uncompressed_wif.text = ""
            return

        self.compressed_wif.text = f"Compressed WIF: {self.to_wif(pk, compressed=True)}"
        self.uncompressed_wif.text = f"Uncompressed WIF: {self.to_wif(pk, compressed=False)}"

    def save_to_file(self, instance):
        """Save generated keys to a text file."""
        pk = self.private_key.text.strip()
        if len(pk) != 64:
            return

        compressed_wif = self.to_wif(pk, compressed=True)
        uncompressed_wif = self.to_wif(pk, compressed=False)

        with open(r"E:\saved_keys.txt", "a") as file:
            file.write(f"Private Key: {pk}\nCompressed WIF: {compressed_wif}\nUncompressed WIF: {uncompressed_wif}\n\n")

    def load_from_file(self, instance):
        """Retrieve the last saved private key from the text file."""
        try:
            with open(r"E:\saved_keys.txt", "r") as file:
                lines = file.readlines()
                if len(lines) < 3:
                    popup = Popup(title="Error",
                                  content=Label(text="No valid saved keys found."),
                                  size_hint=(0.5, 0.3))
                    popup.open()
                    return

                pk = lines[-3].split(": ")[1].strip()
                compressed_wif = lines[-2].split(": ")[1].strip()
                uncompressed_wif = lines[-1].split(": ")[1].strip()

                self.private_key.text = pk
                self.compressed_wif.text = f"Compressed WIF: {compressed_wif}"
                self.uncompressed_wif.text = f"Uncompressed WIF: {uncompressed_wif}"
        except FileNotFoundError:
            popup = Popup(title="Error",
                          content=Label(text="No saved keys file found."),
                          size_hint=(0.5, 0.3))
            popup.open()

    def go_to_puzzle_screen(self, instance):
        """Switch to the puzzle-solving screen."""
        self.manager.current = "puzzle_screen"


class PuzzleScreen(Screen):
    """Multi-threaded puzzle solving with range-based WIF generation."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")

        self.puzzle_number = TextInput(hint_text="Enter Puzzle Number", multiline=False)
        layout.add_widget(self.puzzle_number)

        solve_btn = Button(text="Solve Puzzle")
        solve_btn.bind(on_press=self.solve_puzzle)
        layout.add_widget(solve_btn)

        self.status_label = Label(text="Puzzle Status: Unknown")
        layout.add_widget(self.status_label)

        self.progress_bar = ProgressBar(max=100)
        layout.add_widget(self.progress_bar)

        back_btn = Button(text="Back to Main Screen")
        back_btn.bind(on_press=self.go_to_main_screen)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def go_to_main_screen(self, instance):
        """Switch back to the main screen."""
        self.manager.current = "main_screen"

    def solve_puzzle(self, instance):
        """Uses multi-threading to generate private keys within puzzle-defined ranges."""
        puzzle_id = self.puzzle_number.text.strip()
        puzzle_ranges = {
            "69": (0x100000000000000000, 0x1FFFFFFFFFFFFFFFFF),
            "71": (0x400000000000000000, 0x7FFFFFFFFFFFFFFFFF),
            "135": (0x4000000000000000000000000000000000000, 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF),
        }

        if puzzle_id not in puzzle_ranges:
            popup = Popup(title="Invalid Puzzle",
                          content=Label(text="Puzzle not found in the supported range."),
                          size_hint=(0.5, 0.3))
            popup.open()
            return

        start_range, end_range = puzzle_ranges[puzzle_id]
        self.multi_threaded_wif_generation(puzzle_id, start_range, end_range)

    def multi_threaded_wif_generation(self, puzzle_id, start_range, end_range):
        """Parallel WIF generation using multiple threads."""
        output_dir = r"E:\puzzle_results"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"puzzle_{puzzle_id}_results.txt")

        def generate_key_wif(key):
            wif_compressed = self.to_wif(hex(key)[2:], compressed=True)
            wif_uncompressed = self.to_wif(hex(key)[2:], compressed=False)
            return f"Private Key: {hex(key)}\nCompressed WIF: {wif_compressed}\nUncompressed WIF: {wif_uncompressed}\n\n"

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(generate_key_wif, range(start_range, end_range)))

        with open(output_file, "w") as file:
            file.writelines(results)

        popup = Popup(title="Generation Complete",
                      content=Label(text=f"WIFs saved in {output_file}"),
                      size_hint=(0.5, 0.3))
        popup.open()


class WIFApp(App):
    def build(self):
        """Launch the app with screen navigation."""
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(PuzzleScreen(name="puzzle_screen"))
        return sm

if __name__ == "__main__":
    WIFApp().run()
