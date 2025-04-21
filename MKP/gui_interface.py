import tkinter as tk
from tkinter import messagebox
import threading
from puzzle_math import PuzzleSolver
from mining_engine import optimized_mine_block
import hashlib
import ecdsa
import base58
import json
import tkinter as tk

class PuzzleSelection:
    """Handles puzzle selection and custom search input."""
    
    def __init__(self, root, solver):
        self.root = root
        self.solver = solver
        self.setup_ui()

    def setup_ui(self):
        """Creates the selection and input fields."""
        tk.Label(self.root, text="Select Puzzle:", font=("Arial", 12)).pack()

        self.puzzle_entry = tk.Entry(self.root, font=("Arial", 12), width=30)
        self.puzzle_entry.pack(pady=5)

        tk.Label(self.root, text="Custom Address or Public Key:", font=("Arial", 12)).pack()
        self.address_entry = tk.Entry(self.root, font=("Arial", 12), width=40)
        self.address_entry.pack(pady=5)

        tk.Label(self.root, text="Nonce Min:", font=("Arial", 12)).pack()
        self.nonce_min_entry = tk.Entry(self.root, font=("Arial", 12), width=20)
        self.nonce_min_entry.pack(pady=5)

        tk.Label(self.root, text="Nonce Max:", font=("Arial", 12)).pack()
        self.nonce_max_entry = tk.Entry(self.root, font=("Arial", 12), width=20)
        self.nonce_max_entry.pack(pady=5)

        tk.Button(self.root, text="Start Search", command=self.start_nonce_bounce, font=("Arial", 12)).pack(pady=5)

    def start_nonce_bounce(self):
        """Executes nonce bouncing with the user-defined parameters."""
        puzzle_address = self.address_entry.get().strip()
        nonce_min = int(self.nonce_min_entry.get().strip(), 16) if self.nonce_min_entry.get() else 0x40000000000000000
        nonce_max = int(self.nonce_max_entry.get().strip(), 16) if self.nonce_max_entry.get() else 0x7ffffffffffffffff

        results, winner = self.solver.parallel_nonce_bounce(nonce_min, nonce_max, puzzle_address)

        if winner:
            tk.messagebox.showinfo("Puzzle Solved!", f"Winning Private Key: {winner}")

class ResultLogger:
    """Handles logging of puzzle-solving results."""
    
    def __init__(self, filename="results.json"):
        self.filename = filename

    def save_result(self, private_key, address, compressed):
        """Logs private key, WIF formats, and Bitcoin addresses."""
        wif_uncompressed = self.private_key_to_wif(private_key, compressed=False)
        wif_compressed = self.private_key_to_wif(private_key, compressed=True)

        data = {
            "private_key_hex": private_key,
            "wif_uncompressed": wif_uncompressed,
            "wif_compressed": wif_compressed,
            "address": address
        }

        with open(self.filename, "a") as file:
            json.dump(data, file)
            file.write("\n")

    def private_key_to_wif(self, private_key, compressed=True):
        """Converts private key to WIF format."""
        key_bytes = bytes.fromhex(private_key)
        extended_key = b"\x80" + key_bytes

        if compressed:
            extended_key += b"\x01"

        first_sha256 = hashlib.sha256(extended_key).digest()
        second_sha256 = hashlib.sha256(first_sha256).digest()
        checksum = second_sha256[:4]

        return base58.b58encode(extended_key + checksum).decode()


class PuzzleSolver:
    def __init__(self):
        self.running = False

    def stop_search(self):
        """Stops puzzle-solving execution."""
        self.running = False

    def parallel_nonce_bounce(self, nonce_min, nonce_max, puzzle_address):
        """Executes nonce bouncing search within a defined range."""
        self.running = True
        winning_key = None
        results = []

        for nonce in range(nonce_min, nonce_max):
            if not self.running:
                break

            private_key = hex(nonce)[2:].zfill(64)
            computed_address = self.private_key_to_address(private_key)

            if computed_address == puzzle_address:
                winning_key = private_key
                break

            results.append((private_key, computed_address))

        return results, winning_key

    def private_key_to_address(self, private_key, compressed=True):
        """Converts private key to Bitcoin address using compressed/uncompressed format."""
        key_bytes = bytes.fromhex(private_key)
        sk = ecdsa.SigningKey.from_string(key_bytes, curve=ecdsa.SECP256k1)

        if compressed:
            vk = sk.verifying_key.to_string()[:32]
            prefix = b'\x02' if vk[-1] % 2 == 0 else b'\x03'
            vk_bytes = prefix + vk
        else:
            vk_bytes = b'\x04' + sk.verifying_key.to_string()

        ripemd160 = hashlib.new('ripemd160', hashlib.sha256(vk_bytes).digest()).digest()
        extended_ripemd160 = b'\x00' + ripemd160
        first_sha256 = hashlib.sha256(extended_ripemd160).digest()
        second_sha256 = hashlib.sha256(first_sha256).digest()
        checksum = second_sha256[:4]

        return base58.b58encode(extended_ripemd160 + checksum).decode()

class BitcoinPuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Puzzle Solver & Miner")
        
        self.solver = PuzzleSolver()
        self.setup_ui()

    def setup_ui(self):
        """Creates the GUI layout."""
        tk.Label(self.root, text="Bitcoin Puzzle Solver", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self.root, text="Start Puzzle Solving", command=self.start_puzzle_solving, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Start Mining", command=self.start_mining, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Stop Process", command=self.stop_process, font=("Arial", 12)).pack(pady=5)

        self.status_label = tk.Label(self.root, text="Status: Idle", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def start_puzzle_solving(self):
        """Begins the puzzle-solving process using parallel execution."""
        self.status_label.config(text="Status: Puzzle Solving Running...")
        puzzle_thread = threading.Thread(target=self.run_puzzle_solver)
        puzzle_thread.start()

    def run_puzzle_solver(self):
        """Executes the puzzle solver with selected parameters."""
        puzzle_address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9"  # Example from Bitcoin Puzzle Challenge

        results, winner = self.solver.parallel_nonce_bounce(
            nonce_min=0x40000000000000000, nonce_max=0x7ffffffffffffffff, puzzle_address=puzzle_address
        )

        if winner:
            messagebox.showinfo("Puzzle Solved!", f"Winning Private Key: {winner}")
            self.status_label.config(text="Status: Puzzle Solved!")
        else:
            self.status_label.config(text="Status: No Solution Found.")

    def start_mining(self):
        """Starts the mining process."""
        self.status_label.config(text="Status: Mining Running...")
        mining_thread = threading.Thread(target=optimized_mine_block)
        mining_thread.start()

    def stop_process(self):
        """Stops the puzzle-solving or mining process."""
        self.solver.stop_search()
        self.status_label.config(text="Status: Stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BitcoinPuzzleGUI(root)
    root.mainloop()
