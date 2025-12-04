"""
Kesinlikle Çözülen Hataların Test Runner'ı
9 düzeltilen test'i tek seferde çalıştırır
"""
import subprocess
import sys

# Düzeltilen testlerin listesi
FIXED_TESTS = [
    # Constructor Hataları (#1, #2)
    "tests/test_attacks.py::TestMajorityAttack::test_majority_execute",
    "tests/test_attacks.py::TestNetworkPartition::test_partition_execute",
    
    # Byzantine Trust Score (#6)
    "tests/test_attacks.py::TestByzantineAttack::test_byzantine_trigger",
    
    # Manual Mining (#5)
    "tests/test_simulator.py::TestSimulatorNodes::test_manual_mining",
    
    # PBFT Testleri (#7, #8)
    "tests/test_integration.py::TestNodePBFTIntegration::test_node_pbft_setup",
    "tests/test_integration.py::TestNodePBFTIntegration::test_pbft_propose_block",
    
    # Fork Detection (#12)
    "tests/test_integration.py::TestBlockchainFork::test_fork_detection",
    
    # Byzantine Commit (#10)
    "tests/test_pbft_handler.py::TestPBFTByzantine::test_byzantine_node_fake_hash",
    
    # Partition Status (#11)
    "tests/test_message_broker.py::TestMessageBrokerPartition::test_set_partition",
]

def main():
    """Testleri çalıştır"""
    print("=" * 70)
    print("KEŞİNLİKLE ÇÖZÜLMEŞİ GEREKEN 9 TEST ÇALIŞTIRILIYOR")
    print("=" * 70)
    print(f"\nToplam test sayısı: {len(FIXED_TESTS)}\n")
    
    for i, test in enumerate(FIXED_TESTS, 1):
        print(f"{i}. {test}")
    
    print("\n" + "=" * 70)
    print("Testler başlatılıyor...\n")
    
    # Pytest komutunu hazırla
    cmd = ["pytest", "-v", "--tb=short"] + FIXED_TESTS
    
    # Testleri çalıştır
    result = subprocess.run(cmd, capture_output=False)
    
    print("\n" + "=" * 70)
    if result.returncode == 0:
        print("✅ TÜM TESTLER BAŞARILI!")
    else:
        print("❌ BAZI TESTLER BAŞARISIZ!")
        print("Detaylı çıktı için yukarıya bakın.")
    print("=" * 70)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
