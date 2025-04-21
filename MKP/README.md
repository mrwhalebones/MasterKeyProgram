# 🚀 Bitcoin Mining Prototype  
## Overview  
This prototype enables **full-node mining execution**, featuring **SmartSelect optimizations, cryptographic integrity checks, and automatic mining efficiency enhancements.**  

## Features  
✅ Full-node integration with Bitcoin Core  
✅ SmartSelect dynamic mining configuration  
✅ Pollard’s Kangaroo algorithm for key recovery  
✅ Advanced nonce iteration optimization  
✅ Secure cryptographic validation  

## Installation  
### Prerequisites  
- **Bitcoin Core** installed and running  
- Python 3.x  
- Required libraries installed (`pip install -r requirements.txt`)  

### Setup Instructions  
1. Clone or download the repository  
2. Configure your **Bitcoin Core RPC credentials** in `prototype_main.py`  
3. Run `main.py` to start the execution  

## Mining Process  
1. Fetches mining template (`getblocktemplate`)  
2. Iterates nonce for hash discovery  
3. Validates block against target difficulty  
4. Submits mined block (`submitblock`)  
5. Logs mining results  

## Troubleshooting  
- **RPC connection issues?** Check Bitcoin Core’s config file (`bitcoin.conf`).  
- **Slow mining speed?** Adjust the `nonce iteration delay`.  
- **Hash mismatches?** Ensure cryptographic validation settings are correct.  

## Credits  
Developed in collaboration with **Melon Head** 🚀  
