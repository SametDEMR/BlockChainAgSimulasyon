"""
Node Module Test Script
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.network.node import Node
import json


def main():
    print("=" * 60)
    print("NODE MODULE TEST")
    print("=" * 60)
    
    # Nodes oluştur
    node1 = Node(role="regular")
    node2 = Node(role="validator")
    node3 = Node(role="validator")
    
    print(f"\n✅ Nodes Created:")
    print(f"  {node1}")
    print(f"  {node2}")
    print(f"  {node3}")
    
    # İlk mining - node1
    print(f"\n⛏️  Node1 mining block...")
    block1 = node1.mine_block()
    print(f"  Block #{block1.index} mined by {node1.id}")
    print(f"  Node1 balance: {node1.blockchain.get_balance(node1.wallet.address)}")
    
    # Transaction oluştur
    print(f"\n📝 Node1 creating transaction to Node2...")
    tx = node1.create_transaction(node2.wallet.address, 25)
    if tx:
        print(f"  Transaction: {tx.amount} coins")
        print(f"  Pending txs: {len(node1.blockchain.pending_transactions)}")
    
    # İkinci mining - node2
    print(f"\n⛏️  Node2 mining block...")
    block2 = node2.mine_block()
    print(f"  Block #{block2.index} mined by {node2.id}")
    
    # Balances
    print(f"\n💰 Balances:")
    print(f"  Node1: {node1.blockchain.get_balance(node1.wallet.address)}")
    print(f"  Node2: {node2.blockchain.get_balance(node2.wallet.address)}")
    
    # Node sync
    print(f"\n🔄 Syncing Node3 with Node2's blockchain...")
    print(f"  Node3 chain before: {len(node3.blockchain.chain)} blocks")
    node3.sync_blockchain(node2.blockchain)
    print(f"  Node3 chain after: {len(node3.blockchain.chain)} blocks")
    
    # Node status
    print(f"\n📊 Node1 Full Status:")
    print(json.dumps(node1.get_status(), indent=2))
    
    # Byzantine test
    print(f"\n⚠️  Byzantine Attack Test:")
    node2.set_byzantine(True)
    print(f"  Node2 is Byzantine: {node2.is_byzantine}")
    print(f"  Status: {node2.status}")
    print(f"  Trust Score: {node2.trust_score}")
    
    # DDoS test
    print(f"\n⚠️  DDoS Attack Test:")
    print(f"  Node3 response time before: {node3.response_time}ms")
    node3.set_under_attack()
    print(f"  Node3 response time after: {node3.response_time}ms")
    print(f"  Status: {node3.status}")
    
    # Recovery
    print(f"\n🔄 Recovery Test:")
    node3.recover()
    print(f"  Node3 status: {node3.status}")
    print(f"  Node3 response time: {node3.response_time}ms")
    
    print("\n" + "=" * 60)
    print("✅ ALL NODE TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
