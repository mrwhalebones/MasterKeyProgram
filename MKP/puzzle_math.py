import hashlib
import random
import ecdsa
import concurrent.futures  

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

    def randomized_nonce_jump(self, nonce_min, nonce_max):
        """ Generates nonces unpredictably using modular arithmetic to avoid sequential bias. """
        return (random.randint(nonce_min, nonce_max) * 0xDEADBEEF) % (nonce_max - nonce_min) + nonce_min

    def parallel_nonce_bounce(self, nonce_min, nonce_max, puzzle_address, thread_count=4):
        """ Runs nonce bouncing in parallel threads for faster key discovery. """
        print(f"⚡ Parallel nonce bouncing started with {thread_count} threads!")

        start_time = time.time()
        tested_count = 0
        found_winner = None  
        results_log = []  
        self.search_active = True  

        def search_nonce():
            while self.search_active:
                random_nonce = self.randomized_nonce_jump(nonce_min, nonce_max)  
                private_key_hex = hex(random_nonce)[2:].zfill(64)
                compressed_address = self.private_key_to_address(private_key_hex, compressed=True)
                uncompressed_address = self.private_key_to_address(private_key_hex, compressed=False)

                if compressed_address == puzzle_address or uncompressed_address == puzzle_address:
                    elapsed_time = time.time() - start_time
                    found_winner = f"✅ WINNER FOUND: {private_key_hex} (Checked: {tested_count}) (Time: {elapsed_time:.2f}s)"
                    results_log.append(("✔", found_winner))
                    print(found_winner)  
                    self.search_active = False  
                    return found_winner

                tested_count += 1
                results_log.append(("❌", f"Checked: {tested_count} | Private Key: {private_key_hex}"))

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(search_nonce) for _ in range(thread_count)]
            concurrent.futures.wait(futures)

        return results_log, found_winner  

    def baby_step_giant_step(self, puzzle_address):
        """ Implements Baby-step Giant-step (BSGS) method for faster key search when public key is exposed. """
        print("🔄 Running Baby-step Giant-step method...")

        steps = 2**12  
        precomputed = {}  

        for i in range(steps):
            private_key_hex = hex(i)[2:].zfill(64)
            address = self.private_key_to_address(private_key_hex, compressed=True)
            precomputed[address] = private_key_hex

        for j in range(steps, 2**16, steps):  
            private_key_hex = hex(j)[2:].zfill(64)
            address = self.private_key_to_address(private_key_hex, compressed=True)

            if address in precomputed:
                print(f"✅ BSGS Match Found: {precomputed[address]}")
                return precomputed[address]  

        print("❌ BSGS did not find a matching key.")
        return None

    def stop_search(self):
        """ Stops the nonce bouncing and puzzle-solving methods. """
        self.search_active = False

if __name__ == "__main__":
    solver = PuzzleSolver()
    print("🚀 Puzzle Solver Initialized!")
