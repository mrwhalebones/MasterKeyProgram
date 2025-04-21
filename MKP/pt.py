# ✅ pt.py (Puzzle Tables) - Stores exact puzzle details from privatekeys.pw
PUZZLE_TABLES = {
    "Puzzle #69": {"nonce_min": int("100000000000000000", 16), "nonce_max": int("1fffffffffffffffff", 16), "btc_address": "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG", "prize": 6.90013661},
    "Puzzle #71": {"nonce_min": int("400000000000000000", 16), "nonce_max": int("7fffffffffffffffff", 16), "btc_address": "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU", "prize": 7.1000437},
    "Puzzle #72": {"nonce_min": int("800000000000000000", 16), "nonce_max": int("ffffffffffffffffff", 16), "btc_address": "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR", "prize": 7.20004379},
    "Puzzle #73": {"nonce_min": int("1000000000000000000", 16), "nonce_max": int("1ffffffffffffffffff", 16), "btc_address": "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4", "prize": 7.30004377},
    "Puzzle #74": {"nonce_min": int("2000000000000000000", 16), "nonce_max": int("3ffffffffffffffffff", 16), "btc_address": "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv", "prize": 7.40004977},
    "Puzzle #76": {"nonce_min": int("8000000000000000000", 16), "nonce_max": int("fffffffffffffffffff", 16), "btc_address": "1DJh2eHFYQfACPmrvpyWc8MSTYKh7w9eRF", "prize": 7.60000},
    "Puzzle #77": {"nonce_min": int("10000000000000000000", 16), "nonce_max": int("1fffffffffffffffffff", 16), "btc_address": "1Bxk4CQdqL9p22JEtDfdXMsng1XacifUtE", "prize": 7.70002426},
    "Puzzle #78": {"nonce_min": int("20000000000000000000", 16), "nonce_max": int("3fffffffffffffffffff", 16), "btc_address": "15qF6X51huDjqTmF9BJgxXdt1xcj46Jmhb", "prize": 7.80000},
    "Puzzle #79": {"nonce_min": int("40000000000000000000", 16), "nonce_max": int("7fffffffffffffffffff", 16), "btc_address": "1ARk8HWJMn8js8tQmGUJeQHjSE7KRkn2t8", "prize": 7.90000},
    "Puzzle #81": {"nonce_min": int("100000000000000000000", 16), "nonce_max": int("1ffffffffffffffffffff", 16), "btc_address": "15qsCm78whspNQFydGJQk5rexzxTQopnHZ", "prize": 8.10000},
    "Puzzle #82": {"nonce_min": int("200000000000000000000", 16), "nonce_max": int("3ffffffffffffffffffff", 16), "btc_address": "13zYrYhhJxp6Ui1VV7pqa5WDhNWM45ARAC", "prize": 8.20000},
    "Puzzle #83": {"nonce_min": int("400000000000000000000", 16), "nonce_max": int("7ffffffffffffffffffff", 16), "btc_address": "14MdEb4eFcT3MVG5sPFG4jGLuHJSnt1Dk2", "prize": 8.30000546},
    "Puzzle #84": {"nonce_min": int("800000000000000000000", 16), "nonce_max": int("fffffffffffffffffffff", 16), "btc_address": "1CMq3SvFcVEcpLMuuH8PUcNiqsK1oicG2D", "prize": 8.40000},
    "Puzzle #86": {"nonce_min": int("2000000000000000000000", 16), "nonce_max": int("3fffffffffffffffffffff", 16), "btc_address": "1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK", "prize": 8.60000},
    "Puzzle #135": {"nonce_min": int("4000000000000000000000000000000000", 16), "nonce_max": int("7fffffffffffffffffffffffffffffffff", 16), "btc_address": "16RGFo6hjq9ym6Pj7N5H7L1NR1rVPJyw2v", "prize": 13.50003408, "public_key": "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"},
    "Puzzle #160": {"nonce_min": int("8000000000000000000000000000000000000000", 16), "nonce_max": int("ffffffffffffffffffffffffffffffffffffffff", 16), "btc_address": "1NBC8uXJy1GiJ6drkiZa1WuKn51ps7EPTv", "prize": 16.00019082, "public_key": "02e0a8b039282faf6fe0fd769cfbc4b6b4cf8758ba68220eac420e32b91ddfa673"},
}

def get_puzzle_list():
    """ Returns available puzzles dynamically from pt.py. """
    return list(PUZZLE_TABLES.keys())

def get_puzzle_info(puzzle_name):
    """ Fetches puzzle details including nonce range, Bitcoin address, and prize amount. """
    return PUZZLE_TABLES.get(puzzle_name, None)
