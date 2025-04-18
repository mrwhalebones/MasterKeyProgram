import os
import hashlib
import base58
import sqlite3
import gzip
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
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

        save_btn = Button(text="Save to Database")
        save_btn.bind(on_press=self.save_to_db)
        layout.add_widget(save_btn)

        load_btn = Button(text="Load Last Key from Database")
        load_btn.bind(on_press=self.load_from_db)
        layout.add_widget(load_btn)

        self.compressed_wif = Label(text="Compressed WIF: ")
        layout.add_widget(self.compressed_wif)

        self.uncompressed_wif = Label(text="Uncompressed WIF: ")
        layout.add_widget(self.uncompressed_wif)

        # Button to switch to puzzle-solving screen
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

    def save_to_db(self, instance):
        """Save generated keys to the SQLite database."""
        pk = self.private_key.text.strip()
        if len(pk) != 64:
            return

        compressed_wif = self.to_wif(pk, compressed=True)
        uncompressed_wif = self.to_wif(pk, compressed=False)

        conn = sqlite3.connect("keys.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO keys (private_key, compressed_wif, uncompressed_wif) VALUES (?, ?, ?)", 
                       (pk, compressed_wif, uncompressed_wif))
        conn.commit()
        conn.close()

    def load_from_db(self, instance):
        """Retrieve the last saved private key from the database."""
        conn = sqlite3.connect("keys.db")
        cursor = conn.cursor()
        cursor.execute("SELECT private_key, compressed_wif, uncompressed_wif FROM keys ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            pk, compressed_wif, uncompressed_wif = result
            self.private_key.text = pk
            self.compressed_wif.text = f"Compressed WIF: {compressed_wif}"
            self.uncompressed_wif.text = f"Uncompressed WIF: {uncompressed_wif}"

    def go_to_puzzle_screen(self, instance):
        """Switch to the puzzle-solving screen."""
        self.manager.current = "puzzle_screen"


class PuzzleScreen(Screen):
    """Screen for solving puzzles and displaying progress."""
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
        """Check if the puzzle is already solved and mark progress."""
        puzzle_id = self.puzzle_number.text.strip()

        if not puzzle_id:
            popup = Popup(title="Error",
                          content=Label(text="Please enter a puzzle number before proceeding."),
                          size_hint=(0.5, 0.3))
            popup.open()
            return

        conn = sqlite3.connect("keys.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS puzzles (puzzle_id TEXT PRIMARY KEY, status TEXT)")
        conn.commit()

        cursor.execute("SELECT status FROM puzzles WHERE puzzle_id = ?", (puzzle_id,))
        result = cursor.fetchone()

        if result and result[0] == "SOLVED":
            popup = Popup(title="Puzzle Already Solved",
                          content=Label(text="Puzzle Already Solved, continue?"),
                          size_hint=(0.5, 0.3))
            popup.open()
        else:
            cursor.execute("INSERT OR REPLACE INTO puzzles (puzzle_id, status) VALUES (?, ?)", (puzzle_id, "SOLVED"))
            conn.commit()
            conn.close()

            self.status_label.text = f"Puzzle {puzzle_id} marked as SOLVED"
            Clock.schedule_interval(self.update_progress, 0.1)  # Start progress bar animation

            # Save puzzle info to compressed text file
            self.save_compressed_data(puzzle_id)

    def save_compressed_data(self, puzzle_id):
        """Save puzzle progress to a compressed text file."""
        with gzip.open(f"E:\\solved_puzzles.txt.gz", "ab") as file:
            file.write(f"Puzzle {puzzle_id} - SOLVED\n".encode())

    def update_progress(self, dt):
        """Animate progress bar."""
        if self.progress_bar.value < 100:
            self.progress_bar.value += 10
        else:
            Clock.unschedule(self.update_progress)

class WIFApp(App):
    def build(self):
        """Launch the app with screen navigation."""
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(PuzzleScreen(name="puzzle_screen"))
        return sm

if __name__ == "__main__":
    WIFApp().run()
