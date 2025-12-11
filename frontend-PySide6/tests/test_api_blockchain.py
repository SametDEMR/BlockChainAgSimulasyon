"""Test API blockchain endpoint."""
from core.api_client import APIClient

api = APIClient("http://localhost:8000")

print("Testing API connection...")
print(f"Connected: {api.is_connected()}")

print("\nGetting blockchain data...")
blockchain = api.get_blockchain()
print(f"Blockchain data: {blockchain}")

if blockchain:
    print(f"\nChain length: {blockchain.get('chain_length')}")
    print(f"Blocks count: {len(blockchain.get('blocks', []))}")
    
    if blockchain.get('blocks'):
        print("\nFirst block:")
        print(blockchain['blocks'][0])
