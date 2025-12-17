"""
Interactive Blockchain Attack Simulator - Configuration
Merkezi yapılandırma dosyası - tüm sistem parametreleri burada tanımlanır
"""

CONFIG = {
    # Network Configuration
    'network': {
        'total_nodes': 10,           # Toplam node sayısı
        'validator_nodes': 4,         # Validator node sayısı (PBFT için)
        'network_delay_ms': 100,      # Node'lar arası iletişim gecikmesi (ms)
    },
    
    # Blockchain Configuration
    'blockchain': {
        'block_time': 3,              # Blok üretim aralığı (saniye) - DÜZELTME: 5'ten 3'e düşürüldü
        'initial_difficulty': 4,      # Mining zorluğu (hash başındaki 0 sayısı)
        'max_transactions_per_block': 10,  # Bir blokta maksimum transaction sayısı
        'mining_reward': 50,          # Madencilik ödülü
    },
    
    # API Configuration
    'api': {
        'host': '0.0.0.0',           # API sunucu adresi
        'port': 8000,                 # API port
        'reload': True,               # Auto-reload (development için)
    },
    
    # UI Configuration
    'ui': {
        'refresh_interval': 2,        # Arayüz yenileme aralığı (saniye)
        'page_title': 'Blockchain Attack Simulator',
        'page_icon': '🔐',
        'layout': 'wide',
    },
    
    # Attack Configuration
    'attacks': {
        'ddos': {
            'request_multiplier': 100,  # DDoS istek çarpanı
            'duration': 20,               # Saldırı süresi (saniye)
        },
        'byzantine': {
            'fault_probability': 0.8,     # Hatalı davranış olasılığı
            'trust_penalty': 10,          # Trust score cezası
        },
        'sybil': {
            'fake_nodes_count': 25,       # Oluşturulacak sahte node sayısı
        },
        'majority': {
            'attacker_percentage': 0.51,  # Saldırgan node oranı
        },
        'partition': {
            'duration': 30,               # Partition süresi (saniye)
        },
        'selfish_mining': {
            'reveal_threshold': 2,        # Private chain public'ten kaç blok önde olmalı
        },
    },
    
    # Logging Configuration
    'logging': {
        'level': 'INFO',              # Log seviyesi (DEBUG, INFO, WARNING, ERROR)
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    },
}


def get_config():
    """Config dictionary'sini döndürür"""
    return CONFIG


def get_network_config():
    """Network yapılandırmasını döndürür"""
    return CONFIG['network']


def get_blockchain_config():
    """Blockchain yapılandırmasını döndürür"""
    return CONFIG['blockchain']


def get_api_config():
    """API yapılandırmasını döndürür"""
    return CONFIG['api']


def get_ui_config():
    """UI yapılandırmasını döndürür"""
    return CONFIG['ui']


def get_attack_config(attack_type=None):
    """
    Saldırı yapılandırmasını döndürür
    
    Args:
        attack_type (str, optional): Belirli bir saldırı tipi. None ise tüm saldırı config'i döner.
    
    Returns:
        dict: Saldırı yapılandırması
    """
    if attack_type:
        return CONFIG['attacks'].get(attack_type, {})
    return CONFIG['attacks']


def get_logging_config():
    """Logging yapılandırmasını döndürür"""
    return CONFIG['logging']


# Test için
if __name__ == "__main__":
    print("=" * 60)
    print("BLOCKCHAIN ATTACK SIMULATOR - CONFIGURATION")
    print("=" * 60)
    print("\n📡 Network Configuration:")
    for key, value in get_network_config().items():
        print(f"  {key}: {value}")
    
    print("\n⛓️  Blockchain Configuration:")
    for key, value in get_blockchain_config().items():
        print(f"  {key}: {value}")
    
    print("\n🔌 API Configuration:")
    for key, value in get_api_config().items():
        print(f"  {key}: {value}")
    
    print("\n🖥️  UI Configuration:")
    for key, value in get_ui_config().items():
        print(f"  {key}: {value}")
    
    print("\n⚔️  Attack Configurations:")
    for attack_name, attack_config in get_attack_config().items():
        print(f"  {attack_name}:")
        for key, value in attack_config.items():
            print(f"    {key}: {value}")
    
    print("\n" + "=" * 60)
