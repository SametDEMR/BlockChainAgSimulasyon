"""
Blockchain Module - Ana blockchain yapısı ve zincir yönetimi
"""
import time
import sys
import os

# Parent directory'yi path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .block import Block
from .transaction import Transaction

# Config import için parent directory'yi ekle
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import get_blockchain_config


class Blockchain:
    """
    Ana blockchain sınıfı - zincir yönetimi ve doğrulama
    
    Attributes:
        chain (List[Block]): Blok zinciri
        pending_transactions (List[Transaction]): Bekleyen transaction'lar
        difficulty (int): Mining zorluğu
        mining_reward (float): Madencilik ödülü
        max_transactions_per_block (int): Blok başına max transaction
    """
    
    def __init__(self):
        """Blockchain'i başlat ve genesis block oluştur"""
        config = get_blockchain_config()
        
        self.chain = []
        self.pending_transactions = []
        self.difficulty = config['initial_difficulty']
        self.mining_reward = config['mining_reward']
        self.max_transactions_per_block = config['max_transactions_per_block']
        
        # Fork handling
        self.fork_detected = False
        self.alternative_chains = []  # Fork durumunda alternatif zincirler
        self.fork_history = []  # Fork geçmişi
        self.orphaned_blocks = []  # Orphan bloklar
        
        # Genesis block oluştur
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """İlk blok (Genesis Block) oluştur"""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0",
            miner="GENESIS"
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
    
    def get_latest_block(self):
        """
        Zincirdeki son bloğu döndür
        
        Returns:
            Block: Son blok
        """
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        """
        Bekleyen transaction listesine ekle
        
        Args:
            transaction (Transaction): Eklenecek transaction
            
        Returns:
            bool: Ekleme başarılı mı?
        """
        # Coinbase transaction değilse imza kontrolü
        if transaction.sender != "COINBASE":
            if not transaction.signature:
                print(f"Transaction rejected: No signature")
                return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, miner_address):
        """
        Bekleyen transaction'ları mine et ve yeni blok oluştur
        
        Args:
            miner_address (str): Madenci adresi (ödül alacak)
            
        Returns:
            Block: Oluşturulan blok veya None
        """
        # Madencilik ödülü için coinbase transaction
        coinbase_tx = Transaction(
            sender="COINBASE",
            receiver=miner_address,
            amount=self.mining_reward
        )
        coinbase_tx.sign(None)
        
        # Bekleyen transaction'lardan max sayı kadar al
        transactions_to_mine = self.pending_transactions[:self.max_transactions_per_block]
        transactions_to_mine.insert(0, coinbase_tx)  # Coinbase her zaman ilk sırada
        
        # Yeni blok oluştur
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=transactions_to_mine,
            previous_hash=self.get_latest_block().hash,
            miner=miner_address
        )
        
        # Bloku mine et
        new_block.mine_block(self.difficulty)
        
        # Zincire ekle
        self.chain.append(new_block)
        
        # Mine edilen transaction'ları pending'den çıkar
        self.pending_transactions = self.pending_transactions[self.max_transactions_per_block:]
        
        return new_block
    
    def add_block(self, block):
        """
        Hazır bir bloğu zincire ekle (konsensüs için)
        
        Args:
            block (Block): Eklenecek blok
            
        Returns:
            bool: Ekleme başarılı mı?
        """
        # Fork tespiti - aynı parent'a sahip farklı bloklar var mı?
        fork_detected = self._check_fork_on_add(block)
        
        if fork_detected:
            # Fork durumunda alternatif zincir oluştur
            return self._handle_fork_block(block)
        
        # Normal durum - blok doğrulama
        if not self._is_valid_new_block(block):
            return False
        
        self.chain.append(block)
        return True
    
    def _is_valid_new_block(self, new_block):
        """
        Yeni bloğun geçerli olup olmadığını kontrol et
        
        Args:
            new_block (Block): Kontrol edilecek blok
            
        Returns:
            bool: Blok geçerli mi?
        """
        latest_block = self.get_latest_block()
        
        # Index kontrolü
        if new_block.index != latest_block.index + 1:
            print(f"Invalid index: {new_block.index} != {latest_block.index + 1}")
            return False
        
        # Previous hash kontrolü
        if new_block.previous_hash != latest_block.hash:
            print(f"Invalid previous_hash")
            return False
        
        # Hash kontrolü
        if new_block.hash != new_block.calculate_hash():
            print(f"Invalid hash")
            return False
        
        # Difficulty kontrolü
        if not new_block.hash.startswith('0' * self.difficulty):
            print(f"Invalid difficulty")
            return False
        
        return True
    
    def is_valid(self):
        """
        Tüm zincirin geçerliliğini kontrol et
        
        Returns:
            bool: Zincir geçerli mi?
        """
        # Genesis block'u atla
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Hash kontrolü
            if current_block.hash != current_block.calculate_hash():
                print(f"Block #{i} has invalid hash")
                return False
            
            # Previous hash bağlantısı
            if current_block.previous_hash != previous_block.hash:
                print(f"Block #{i} has invalid previous_hash")
                return False
        
        return True
    
    def get_balance(self, address):
        """
        Bir adresin bakiyesini hesapla
        
        Args:
            address (str): Adres
            
        Returns:
            float: Bakiye
        """
        balance = 0.0
        
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        
        return balance
    
    def get_chain_length(self):
        """Zincir uzunluğunu döndür"""
        return len(self.chain)
    
    def detect_fork(self, incoming_chain):
        """
        Fork tespit et - yeni bir zincir geldiğinde karşılaştır
        
        Args:
            incoming_chain (list): Gelen alternatif zincir
            
        Returns:
            bool: Fork tespit edildi mi?
        """
        # Zincirlerin uzunluklarını karşılaştır
        if len(incoming_chain) <= len(self.chain):
            return False
        
        # Genesis block aynı olmalı
        if incoming_chain[0].hash != self.chain[0].hash:
            print("Fork rejected: Different genesis block")
            return False
        
        # Farklılaşma noktasını bul
        fork_point = 0
        for i in range(min(len(self.chain), len(incoming_chain))):
            if self.chain[i].hash != incoming_chain[i].hash:
                fork_point = i
                break
        
        if fork_point > 0:
            self.fork_detected = True
            self._record_fork_event(fork_point, incoming_chain)
            return True
        
        return False

    def resolve_fork(self, incoming_chain):
        """Fork çözümle - en uzun zincir kuralı"""
        # En uzun zincir kazanır
        if len(incoming_chain) > len(self.chain):
            # Mevcut zinciri yedeğe al
            orphaned = self.chain.copy()
            self.orphaned_blocks.extend(orphaned)

            # Yeni zinciri kabul et
            self.chain = incoming_chain
            self.fork_detected = False

            # ✅ EKLE - Fork history'deki son event'i resolved yap
            if self.fork_history:
                self.fork_history[-1]['resolved'] = True

            print(f"✅ Fork resolved: Longer chain accepted ({len(incoming_chain)} blocks)")
            return True

        print(f"⚠️  Fork resolved: Current chain kept ({len(self.chain)} blocks)")

        # ✅ EKLE - Mevcut zincir kazandıysa da resolved işaretle
        if self.fork_history:
            self.fork_history[-1]['resolved'] = True

        return False
    
    def add_alternative_chain(self, chain):
        """
        Alternatif zincir ekle (fork tracking için)
        
        Args:
            chain (list): Alternatif zincir
        """
        self.alternative_chains.append({
            'chain': chain,
            'length': len(chain),
            'added_at': time.time()
        })
    
    def add_block_to_alternative_chain(self, block, chain_index=0):
        """
        Alternatif zincire blok ekle (fork büyümesi için)
        
        Args:
            block (Block): Eklenecek blok
            chain_index (int): Hangi alternatif zincir (varsayılan: 0 = en son eklenen)
            
        Returns:
            bool: Ekleme başarılı mı?
        """
        if not self.alternative_chains:
            return False
        
        # Chain index kontrolü
        if chain_index >= len(self.alternative_chains):
            chain_index = len(self.alternative_chains) - 1
        
        alt_chain_data = self.alternative_chains[chain_index]
        alt_chain = alt_chain_data['chain']
        
        # Bloğun parent'inin alternatif zincirdeki son blok olup olmadığını kontrol et
        if alt_chain and block.previous_hash == alt_chain[-1].hash:
            alt_chain.append(block)
            alt_chain_data['length'] = len(alt_chain)
            return True
        
        return False
    
    def _record_fork_event(self, fork_point, incoming_chain):
        """
        Fork olayını kaydet
        
        Args:
            fork_point (int): Forkun başladığı blok index
            incoming_chain (list): Gelen zincir
        """
        fork_event = {
            'timestamp': time.time(),
            'fork_point': fork_point,
            'current_chain_length': len(self.chain),
            'incoming_chain_length': len(incoming_chain),
            'resolved': False
        }
        self.fork_history.append(fork_event)
        print(f"⚠️  Fork detected at block #{fork_point}")
    
    def _check_fork_on_add(self, new_block):
        """
        Yeni blok eklenirken fork kontrolü yap
        Aynı parent'a sahip farklı bir blok zaten var mı?
        
        Args:
            new_block (Block): Kontrol edilecek blok
            
        Returns:
            bool: Fork tespit edildi mi?
        """
        # Eğer zincirin son bloğu ile aynı parent'a sahipse ve hash farklıysa -> FORK!
        latest_block = self.get_latest_block()
        
        # Yeni blok bir sonraki index'te değilse
        if new_block.index != len(self.chain):
            # Önceki bir noktadan fork olmuş olabilir
            return True
        
        # Aynı index'te başka blok var mı kontrol et
        if new_block.index == latest_block.index and new_block.hash != latest_block.hash:
            # Aynı parent'tan iki farklı blok -> FORK!
            print(f"🔴 FORK DETECTED: Two blocks at index {new_block.index}")
            print(f"   Current: {latest_block.hash[:16]}...")
            print(f"   Incoming: {new_block.hash[:16]}...")
            return True
        
        return False
    
    def _handle_fork_block(self, fork_block):
        """
        Fork durumunda gelen bloğu alternatif zincir olarak ekle
        
        Args:
            fork_block (Block): Fork oluşturan blok
            
        Returns:
            bool: İşlem başarılı mı?
        """
        # Fork point'i bul (ortak parent)
        fork_point = fork_block.index - 1
        
        # Alternatif zincir oluştur (fork_point'e kadar ana zincir + yeni blok)
        alternative_chain = self.chain[:fork_point + 1].copy()
        alternative_chain.append(fork_block)
        
        # Alternatif zinciri kaydet
        self.add_alternative_chain(alternative_chain)
        self.fork_detected = True
        
        # Fork event kaydet
        self._record_fork_event(fork_point, alternative_chain)
        
        print(f"✅ Fork block added to alternative chain (fork_point: #{fork_point})")
        return True
    
    def _get_fork_branches_for_ui(self):
        """
        UI için fork branch'lerini hazırla
        Ana zincir + alternatif zincirler
        
        Returns:
            list: Fork branch'leri
        """
        branches = []
        
        # Ana zincir (winner veya active)
        main_status = 'winner' if not self.fork_detected else 'active'
        branches.append({
            'chain': [block.to_dict() for block in self.chain],
            'length': len(self.chain),
            'status': main_status,
            'fork_point': 0,
            'is_main': True
        })
        
        # Alternatif zincirler
        for idx, alt_chain_data in enumerate(self.alternative_chains):
            alt_chain = alt_chain_data['chain']
            
            # Fork point bul (ana zincir ile ayrıldığı nokta)
            fork_point = 0
            for i in range(min(len(self.chain), len(alt_chain))):
                if i >= len(alt_chain) or self.chain[i].hash != alt_chain[i].hash:
                    fork_point = i
                    break
            
            # Status belirle (uzunluk karşılaştırması)
            if len(alt_chain) < len(self.chain):
                status = 'orphaned'
            elif len(alt_chain) == len(self.chain):
                status = 'active'
            else:
                status = 'active'  # Daha uzunsa da active (henüz resolve olmamış)
            
            branches.append({
                'chain': [block.to_dict() for block in alt_chain],
                'length': len(alt_chain),
                'status': status,
                'fork_point': fork_point,
                'is_main': False
            })
        
        return branches
    
    def get_fork_status(self):
        """
        Fork durumunu döndür
        
        Returns:
            dict: Fork bilgileri
        """
        return {
            'fork_detected': self.fork_detected,
            'alternative_chains_count': len(self.alternative_chains),
            'fork_events_count': len(self.fork_history),
            'orphaned_blocks_count': len(self.orphaned_blocks),
            'fork_history': self.fork_history[-5:] if self.fork_history else [],  # Son 5 olay
            'fork_branches': self._get_fork_branches_for_ui()  # UI için fork branch'leri
        }
    
    def to_dict(self):
        """
        Blockchain'i dictionary'ye çevir
        
        Returns:
            dict: Blockchain bilgileri
        """
        # TÜM blokları topla (ana zincir + alternatif zincirler)
        all_blocks = []
        block_hashes = set()  # Duplicate blokları önlemek için
        
        # Ana zincir bloklarini ekle
        for block in self.chain:
            if block.hash not in block_hashes:
                all_blocks.append(block.to_dict())
                block_hashes.add(block.hash)
        
        # Alternatif zincirlerdeki blokları ekle
        for alt_chain_data in self.alternative_chains:
            alt_chain = alt_chain_data['chain']
            for block in alt_chain:
                if block.hash not in block_hashes:
                    all_blocks.append(block.to_dict())
                    block_hashes.add(block.hash)
        
        return {
            'chain_length': len(self.chain),
            'difficulty': self.difficulty,
            'pending_transactions_count': len(self.pending_transactions),
            'pending_transactions': len(self.pending_transactions),  # Alias
            'chain': [block.to_dict() for block in self.chain],  # Ana zincir
            'blocks': all_blocks,  # TÜM bloklar (UI için)
            'fork_status': self.get_fork_status()
        }
    
    def __repr__(self):
        """String representation"""
        return f"Blockchain(Blocks: {len(self.chain)} | Pending TXs: {len(self.pending_transactions)})"


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("BLOCKCHAIN MODULE TEST")
    print("=" * 60)
    
    # Blockchain oluştur
    blockchain = Blockchain()
    
    print(f"\n✅ Blockchain Created:")
    print(f"  {blockchain}")
    print(f"  Difficulty: {blockchain.difficulty}")
    print(f"  Mining Reward: {blockchain.mining_reward}")
    
    print(f"\n✅ Genesis Block:")
    genesis = blockchain.get_latest_block()
    print(f"  Index: {genesis.index}")
    print(f"  Hash: {genesis.hash}")
    
    # Transaction'lar ekle
    tx1 = Transaction("Alice", "Bob", 50)
    tx1.signature = b"mock_signature"
    
    tx2 = Transaction("Bob", "Charlie", 25)
    tx2.signature = b"mock_signature"
    
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    
    print(f"\n✅ Transactions Added:")
    print(f"  Pending: {len(blockchain.pending_transactions)}")
    
    # Blok mine et
    print(f"\n⛏️  Mining block...")
    new_block = blockchain.mine_pending_transactions("Miner123")
    
    print(f"\n✅ Block Mined:")
    print(f"  Block #{new_block.index}")
    print(f"  Hash: {new_block.hash}")
    print(f"  Transactions: {len(new_block.transactions)}")
    print(f"  Miner: {new_block.miner}")
    
    # Bakiye kontrolü
    print(f"\n✅ Balances:")
    print(f"  Miner123: {blockchain.get_balance('Miner123')}")
    print(f"  Alice: {blockchain.get_balance('Alice')}")
    print(f"  Bob: {blockchain.get_balance('Bob')}")
    print(f"  Charlie: {blockchain.get_balance('Charlie')}")
    
    # Zincir doğrulama
    print(f"\n✅ Chain Valid: {blockchain.is_valid()}")
    
    print(f"\n✅ Blockchain Status:")
    print(f"  {blockchain}")
    
    print("\n" + "=" * 60)
