import hashlib
import requests
import time
import random
import ecdsa

BITCOIN_RPC_URL = "http://127.0.0.1:8332"
BITCOIN_RPC_USER = "your_rpc_user"
BITCOIN_RPC_PASS = "your_rpc_password"

def pollards_kangaroo(target):
    """ Searches for a private key collision using Pollard’s Kangaroo method. """
    print("🔄 Running Pollard’s Kangaroo method...")
    upper_bound = target + 1000000
    lower_bound = target - 1000000
    step_size = random.randint(1000, 5000)

    for i in range(lower_bound, upper_bound, step_size):
        key_guess = hashlib.sha256(str(i).encode()).hexdigest()
        if int(key_guess, 16) % (2**256) == target:
            return f"✅ Key found: {i}"

    return "❌ Key recovery failed."

def mine_block():
    """ Implements proof-of-work mining using nonce discovery. """
    block_template = get_block_template()
    target_hash = block_template["target"]
    nonce = 0

    while True:
        block_header = f"{block_template['previousblockhash']}{nonce}".encode()
        block_hash = hashlib.sha256(block_header).hexdigest()

        if int(block_hash, 16) < int(target_hash, 16):
            print(f"✅ Block mined successfully with nonce {nonce}: {block_hash}")
            return send_rpc_request("submitblock", [block_hash])
        
        nonce += 1
