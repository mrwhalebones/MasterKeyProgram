import hashlib
import random
import time
import base58
import ecdsa
import requests
import pt  

BLOCKCHAIN_API_URL = "https://blockchain.info/rawaddr/"

class PuzzleSolver:
    def __init__(self):
        self.search_active = False  

    def private_key_to_wif(self, private_key, compressed=True):
        """ Converts a private key to Wallet Import Format (WIF). """
        prefix = b'\x80'
        key_bytes = bytes.fromhex(private_key)

        if compressed:
            key_bytes += b'\x01'  

        extended_key = prefix + key_bytes
        first_sha256 = hashlib.sha256(extended_key).digest()
        second_sha256 = hashlib.sha256(first_sha256).digest()
        checksum = second_sha256[:4]

        return base58.b58encode(extended_key + checksum).decode()

    def private_key_to_address(self, private_key, compressed=True):
        """ Converts private key to Bitcoin address using compressed/uncompressed format. """
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

    def pollards_kangaroo(self, nonce_min, nonce_max, puzzle_address):
        """ ✅ Pollard's Kangaroo optimized for Bitcoin puzzles with proper terminal outputs. """
        print(f"🔄 Running Pollard’s Kangaroo method... Searching between {nonce_min} and {nonce_max}")

        start_time = time.time()
        tested_count = 0
        results_log = []  
        found_winner = None  
        self.search_active = True  

        while self.search_active:
            random_nonce = random.randint(nonce_min, nonce_max)  
            private_key_hex = hex(random_nonce)[2:].zfill(64)
            compressed_wif = self.private_key_to_wif(private_key_hex, compressed=True)
            uncompressed_wif = self.private_key_to_wif(private_key_hex, compressed=False)
            compressed_address = self.private_key_to_address(private_key_hex, compressed=True)
            uncompressed_address = self.private_key_to_address(private_key_hex, compressed=False)
            tested_count += 1

            if compressed_address == puzzle_address or uncompressed_address == puzzle_address:
                elapsed_time = time.time() - start_time
                found_winner = f"✅ WINNER FOUND: {private_key_hex} (Compressed WIF: {compressed_wif}, Uncompressed WIF: {uncompressed_wif}, Checked: {tested_count}) (Time: {elapsed_time:.2f}s)"
                self.save_winner(found_winner, puzzle_address)
                results_log.append(("✔", found_winner))
                print(found_winner)  
                return results_log, found_winner  

            log_entry = f"❌ {private_key_hex} (Compressed Addr: {compressed_address}, Uncompressed Addr: {uncompressed_address}, Checked: {tested_count})"
            results_log.append(("❌", log_entry))
            print(log_entry)  

        return results_log, found_winner  

    def stop_search(self):
        """ ✅ Allows user to pause search progress while keeping results intact. """
        self.search_active = False
