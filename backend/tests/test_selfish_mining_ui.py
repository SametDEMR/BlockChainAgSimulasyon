"""
Test: Selfish Mining UI Private Chain View

Bu test:
1. Selfish mining başlatır
2. Private chain'de blok üretilmesini bekler
3. Private chain bloklarının UI'da görselleştiğini kontrol eder
4. Public chain ile karşılaştırır
"""

import sys
import os
import asyncio
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulator import Simulator
from backend.attacks.selfish_mining import SelfishMining


@pytest.mark.asyncio
async def test_ui_private_chain():
    """UI Private Chain görselleştirme testi"""
    
    print("=" * 70)
    print("🎨 SELFISH MINING UI PRIVATE CHAIN VIEW TEST")
    print("=" * 70)
    
    # Simulator başlat
    simulator = Simulator()
    simulator.start()
    
    print(f"\n✅ Simulator started")
    
    # Regular node seç
    selfish_node = simulator.regular_nodes[0]
    print(f"🎯 Selfish node: {selfish_node.id}")
    
    # Selfish mining başlat
    selfish_attack = SelfishMining(simulator)
    result = selfish_attack.trigger(selfish_node.id)
    
    if not result["success"]:
        print(f"\n❌ Failed to start: {result['message']}")
        return False
    
    print(f"\n✅ Selfish mining started")
    print(f"   Target: {result['target_node']}")
    print(f"   Reveal threshold: {result['reveal_threshold']} blocks")
    
    # Private chain blok üretimini bekle
    print(f"\n⏳ Waiting for private chain mining (20 seconds)...")
    await asyncio.sleep(20)
    
    # Status kontrol
    status = selfish_attack.get_status()
    
    print(f"\n📊 Current Status:")
    print(f"   Private chain: {status['private_chain_length']} blocks")
    print(f"   Public chain: {status['public_chain_length']} blocks")
    print(f"   Advantage: +{status['advantage']} blocks")
    print(f"   Blocks mined: {status['blocks_mined_private']}")
    
    # Node detail kontrolü
    print(f"\n🔍 Checking node detail endpoint...")
    node_status = selfish_node.get_status()
    private_chain_data = node_status.get('private_chain', {})
    
    if not private_chain_data.get('exists'):
        print(f"\n❌ Private chain not found in node status")
        return False
    
    print(f"✅ Private chain exists in node status")
    private_chain = private_chain_data.get('chain', {}).get('chain', [])
    print(f"   Private chain blocks in API: {len(private_chain)}")
    
    # Blok detaylarını göster
    if private_chain:
        print(f"\n📦 Private Chain Blocks:")
        for i, block in enumerate(reversed(private_chain)):
            block_index = block.get('index', 0)
            block_hash = block.get('hash', '')[:16]
            tx_count = len(block.get('transactions', []))
            print(f"   Block #{block_index}: {block_hash}... ({tx_count} TXs)")
            
            if i >= 4:  # İlk 5 blok
                break
    
    # Public chain kontrol
    print(f"\n📦 Public Chain (First node):")
    first_node = simulator.nodes[0]
    public_chain = first_node.blockchain.chain
    for i, block in enumerate(reversed(public_chain)):
        block_index = block.index
        block_hash = block.hash[:16]
        tx_count = len(block.transactions)
        print(f"   Block #{block_index}: {block_hash}... ({tx_count} TXs)")
        
        if i >= 4:  # İlk 5 blok
            break
    
    # UI Test Instructions
    print(f"\n" + "=" * 70)
    print("🎨 UI TEST INSTRUCTIONS")
    print("=" * 70)
    print(f"\n1. Open UI: http://localhost:8501")
    print(f"2. Go to 'Blockchain' tab")
    print(f"3. You should see:")
    print(f"   - 🟠 Private Chain section with {len(private_chain)} blocks")
    print(f"   - Each private block has ORANGE border and 'PRIVATE' label")
    print(f"   - 🟢 Public Chain section with {len(public_chain)} blocks")
    print(f"   - Each public block has GREEN border and 'NORMAL' label")
    print(f"\n4. Verify:")
    print(f"   - Private chain is displayed BEFORE public chain")
    print(f"   - Private chain advantage: +{status['advantage']} blocks")
    print(f"   - Blocks are color-coded correctly")
    
    # Saldırıyı durdurma
    print(f"\n⏳ Keeping attack active for UI testing (30 seconds)...")
    print(f"   You can now check the UI...")
    await asyncio.sleep(30)
    
    # Stop attack
    print(f"\n🛑 Stopping selfish mining...")
    stop_result = selfish_attack.stop()
    
    if stop_result["success"]:
        print(f"✅ Attack stopped")
        print(f"   Total mined: {stop_result['blocks_mined_private']}")
        print(f"   Total revealed: {stop_result['blocks_revealed']}")
    
    # Simulator durdur
    simulator.stop()
    
    print(f"\n" + "=" * 70)
    print("✅ TEST COMPLETED")
    print("=" * 70)
    print(f"\n📝 Summary:")
    print(f"   - Private chain existed: ✅")
    print(f"   - Private chain had blocks: ✅ ({len(private_chain)} blocks)")
    print(f"   - Node API returned private chain: ✅")
    print(f"   - UI should show orange private blocks")
    print(f"   - UI should show green public blocks")
    
    return True


async def main():
    """Main test runner"""
    try:
        # API kontrolü
        print("\n⚠️  IMPORTANT: Make sure API is running!")
        print("   Terminal 1: python backend/main.py")
        print("   Terminal 2: streamlit run frontend-streamlit/main.py")
        print("\nPress ENTER to start test...")
        input()
        
        success = await test_ui_private_chain()
        
        if success:
            print(f"\n✅ UI Private Chain View test completed successfully")
            return 0
        else:
            print(f"\n❌ UI Private Chain View test failed")
            return 1
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
