import hashlib
import time
import requests

BITCOIN_RPC_URL = "http://127.0.0.1:8332"
BITCOIN_RPC_USER = "your_rpc_user"
BITCOIN_RPC_PASS = "your_rpc_password"

def get_payout_address():
    """Fetches a new payout address from Bitcoin Core."""
    rpc_call = {
        "jsonrpc": "1.0",
        "id": "getnewaddress",
        "method": "getnewaddress",
        "params": []
    }
    response = requests.post(BITCOIN_RPC_URL, json=rpc_call, auth=(BITCOIN_RPC_USER, BITCOIN_RPC_PASS))
    if response.status_code == 200:
        return response.json().get("result")
    return None

def get_block_template():
    """Fetches the latest block template for mining."""
    rpc_call = {
        "jsonrpc": "1.0",
        "id": "getblocktemplate",
        "method": "getblocktemplate",
        "params": [{}]
    }
    response = requests.post(BITCOIN_RPC_URL, json=rpc_call, auth=(BITCOIN_RPC_USER, BITCOIN_RPC_PASS))
    if response.status_code == 200:
        return response.json().get("result")
    return None

def submit_mined_block(block_hash):
    """Submits a mined block to Bitcoin Core."""
    rpc_call = {
        "jsonrpc": "1.0",
        "id": "submitblock",
        "method": "submitblock",
        "params": [block_hash]
    }
    response = requests.post(BITCOIN_RPC_URL, json=rpc_call, auth=(BITCOIN_RPC_USER, BITCOIN_RPC_PASS))
    return response.status_code == 200

def optimized_mine_block():
    """Executes optimized mining using dynamic nonce iteration."""
    print("🚀 Mining Engine Activated")
    
    # Get mining template
    block_template = get_block_template()
    if not block_template:
        print("❌ Failed to fetch block template.")
        return

    target_hash = block_template["target"]
    nonce = 0
    max_nonce = 2**32
    payout_address = get_payout_address()
    
    if not payout_address:
        print("❌ Failed to retrieve payout address.")
        return

    print(f"⚡ Mining with payout to {payout_address}")

    while nonce < max_nonce:
        block_header = f"{block_template['previousblockhash']}{nonce}".encode()
        block_hash = hashlib.sha256(block_header).hexdigest()

        if int(block_hash, 16) < int(target_hash, 16):
            print(f"✅ Block mined successfully at nonce {nonce}: {block_hash}")
            submit_mined_block(block_hash)
            return

        nonce += 1
        time.sleep(0.005)

    print("❌ Maximum nonce limit reached without finding a valid block.")

if __name__ == "__main__":
    optimized_mine_block()
