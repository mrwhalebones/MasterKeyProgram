import pt  # ✅ Import puzzle tables
import puzzle_math

def get_puzzle_list():
    """ Returns available puzzles dynamically from pt.py. """
    return pt.get_puzzle_list()

def get_puzzle_info(puzzle_name):
    """ Fetches puzzle details including nonce range, Bitcoin address, and prize amount. """
    return pt.get_puzzle_info(puzzle_name)
