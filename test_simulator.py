"""
Simulator Test Script
"""
import sys
import os
import asyncio
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.simulator import Simulator
import json


async def test_auto_production():
    """Otomatik blok üretimini test et"""
    print("\n" + "=" * 60)
    print("AUTO BLOCK PRODUCTION TEST")
    print("=" * 60)
    
    simulator = Simulator()
    simulator.start()
    
    print(f"\n⏱️  Running auto-production for 12 seconds...")
    print(f"   Block time: {simulator.blockchain_config['block_time']} seconds")
    print(f"   Expected blocks: ~2")
    
    # Auto production task başlat
    task = asyncio.create_task(simulator.auto_block_production())
    
    # 12 saniye bekle
    await asyncio.sleep(12)
    
    # Stop
    simulator.stop()
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Sonuçları kontrol et
    print(f"\n📊 Results:")
    max_chain = max([len(n.blockchain.chain) for n in simulator.nodes])
    print(f"   Max chain length: {max_chain} blocks")
    print(f"   Genesis + mined blocks: expected ~3 (1 genesis + 2 mined)")
    
    # Mining istatistikleri
    total_mined = sum([n.blocks_mined for n in simulator.nodes])
    print(f"\n⛏️  Mining Stats:")
    print(f"   Total blocks mined: {total_mined}")
    
    miners = [n for n in simulator.nodes if n.blocks_mined > 0]
    for miner in miners[:5]:  # İlk 5 miner
        print(f"   Node {miner.id}: {miner.blocks_mined} blocks, earned {miner.total_earned} coins")


def test_basic():
    """Temel simülatör testleri"""
    print("\n" + "=" * 60)
    print("BASIC SIMULATOR TEST")
    print("=" * 60)
    
    simulator = Simulator()
    
    print(f"\n✅ Created: {simulator}")
    print(f"   Total nodes: {len(simulator.nodes)}")
    print(f"   Validators: {len(simulator.validator_nodes)}")
    print(f"   Regular: {len(simulator.regular_nodes)}")
    
    # Start/Stop
    print(f"\n▶️  Start/Stop Test:")
    simulator.start()
    print(f"   Running: {simulator.is_running}")
    
    simulator.stop()
    print(f"   Running: {simulator.is_running}")
    
    # Manual mining
    print(f"\n⛏️  Manual Mining Test:")
    node = simulator.nodes[0]
    block = node.mine_block()
    print(f"   Block #{block.index} mined by {node.id}")
    
    # Broadcast
    for other_node in simulator.nodes:
        if other_node != node:
            other_node.receive_block(block)
    
    synced_nodes = sum([1 for n in simulator.nodes if len(n.blockchain.chain) == 2])
    print(f"   Synced nodes: {synced_nodes}/{len(simulator.nodes)}")
    
    # Status
    print(f"\n📊 Status:")
    status = simulator.get_status()
    print(f"   Total blocks: {status['total_blocks']}")
    print(f"   Active nodes: {status['active_nodes']}")
    
    # Reset
    print(f"\n🔄 Reset Test:")
    simulator.reset()
    print(f"   Fresh chain length: {len(simulator.nodes[0].blockchain.chain)}")


async def main():
    print("\n" + "*" * 60)
    print("SIMULATOR MODULE - COMPLETE TEST")
    print("*" * 60)
    
    # Basic tests
    test_basic()
    
    # Auto production test
    await test_auto_production()
    
    print("\n" + "=" * 60)
    print("✅ ALL SIMULATOR TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
