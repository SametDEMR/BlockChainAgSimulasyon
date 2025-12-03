"""
Blockchain Visualizer Component
Blokları görselleştir - normal, fork, saldırı durumları
"""
import streamlit as st
import requests
from datetime import datetime


def display_blockchain_visualizer(api_url: str):
    """
    Blockchain'i görselleştir - Public ve Private chain'leri göster
    
    Args:
        api_url: Backend API URL'i
    """
    st.subheader("📦 Blockchain Explorer")
    
    try:
        # Blockchain verisini al
        response = requests.get(f"{api_url}/blockchain", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        blockchain = data.get("chain", {})
        chain = blockchain.get("chain", [])
        fork_status = blockchain.get("fork_status", {})
        
        # Node'ları al (malicious ve selfish miner kontrolü için)
        nodes_response = requests.get(f"{api_url}/nodes", timeout=5)
        nodes_data = nodes_response.json()
        nodes = {n['id']: n for n in nodes_data.get('nodes', [])}
        
        # Selfish mining status al
        selfish_status = None
        try:
            selfish_response = requests.get(f"{api_url}/attack/selfish/status", timeout=5)
            if selfish_response.status_code == 200:
                selfish_status = selfish_response.json()
        except:
            pass
        
        # Fork durumu
        if fork_status.get("fork_detected", False):
            st.error(f"⚠️ FORK DETECTED! {fork_status.get('fork_events_count', 0)} fork events")
        
        # Selfish mining aktif ise uyarı
        if selfish_status and selfish_status.get('active', False):
            st.warning(f"🟠 SELFISH MINING ACTIVE | Advantage: +{selfish_status.get('advantage', 0)} blocks")
        
        # Blockchain istatistikleri
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Blocks", len(chain))
        with col2:
            st.metric("Difficulty", blockchain.get("difficulty", 4))
        with col3:
            st.metric("Pending TXs", blockchain.get("pending_transactions_count", 0))
        with col4:
            st.metric("Fork Events", fork_status.get("fork_events_count", 0))
        
        st.divider()
        
        # Selfish mining aktif ise private chain göster
        if selfish_status and selfish_status.get('active', False):
            target_node_id = selfish_status.get('target_node')
            if target_node_id and target_node_id in nodes:
                target_node = nodes[target_node_id]
                
                # Private chain'i göster
                st.subheader("🟠 Private Chain (Selfish Miner)")
                st.info(f"Selfish Miner: {target_node_id} | Private: {selfish_status.get('private_chain_length', 0)} blocks | Public: {selfish_status.get('public_chain_length', 0)} blocks")
                
                # Private chain bloklarini fetch et (node detail'den)
                try:
                    node_response = requests.get(f"{api_url}/nodes/{target_node_id}", timeout=5)
                    if node_response.status_code == 200:
                        node_detail = node_response.json()
                        # Private chain varsa göster (simdi sadece indicator)
                        st.success(f"🔒 Private Chain: {selfish_status.get('private_chain_length', 0)} blocks (hidden from network)")
                except:
                    pass
        
        # Public chain'i göster
        st.subheader("🟢 Public Chain")
        
        # Blokları göster
        if not chain:
            st.info("No blocks in chain")
            return
        
        # Ters sırada göster (en yeni önce)
        for block in reversed(chain):
            display_block_card(block, nodes)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch blockchain: {e}")


def display_block_card(block: dict, nodes: dict = None):
    """
    Tek bir bloğu kart olarak göster
    
    Args:
        block: Block dictionary
        nodes: Node'lar dictionary (miner malicious kontrolü için)
    """
    index = block.get("index", 0)
    block_hash = block.get("hash", "")[:16]
    prev_hash = block.get("previous_hash", "")[:16]
    timestamp = block.get("timestamp", 0)
    miner = block.get("miner", "Unknown")[:12]
    transactions = block.get("transactions", [])
    nonce = block.get("nonce", 0)
    
    # Miner'in malicious olup olmadığını kontrol et
    is_malicious = False
    if nodes and miner in nodes:
        is_malicious = nodes[miner].get('is_malicious', False)
    
    # Blok rengini belirle
    is_genesis = index == 0
    
    # Renk şeması
    if is_genesis:
        border_color = "#00BFFF"  # Mavi - Genesis
        bg_color = "#E6F7FF"
        status_label = "GENESIS"
    elif is_malicious:
        border_color = "#FF4444"  # Kırmızı - Malicious
        bg_color = "#FFE6E6"
        status_label = "MALICIOUS"
    else:
        border_color = "#00CC66"  # Yeşil - Normal
        bg_color = "#E6FFE6"
        status_label = "NORMAL"
    
    # Timestamp formatla
    time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    
    # HTML kart
    card_html = f"""
    <div style="
        border: 3px solid {border_color};
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: {bg_color};
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h3 style="margin: 0; color: #333;">
                {'🔷 Genesis Block' if is_genesis else f'Block #{index}'}
            </h3>
            <span style="
                background-color: {border_color};
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 12px;
            ">
                {status_label}
            </span>
        </div>
        
        <div style="font-size: 13px; color: #555; line-height: 1.8;">
            <div><strong>Hash:</strong> <code>{block_hash}...</code></div>
            <div><strong>Prev Hash:</strong> <code>{prev_hash}...</code></div>
            <div><strong>Miner:</strong> {miner}</div>
            <div><strong>Transactions:</strong> {len(transactions)}</div>
            <div><strong>Nonce:</strong> {nonce}</div>
            <div><strong>Time:</strong> {time_str}</div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Transaction detayları (expandable)
    if transactions and len(transactions) > 0:
        with st.expander(f"📄 View {len(transactions)} Transactions"):
            for i, tx in enumerate(transactions):
                sender = tx.get("sender", "")[:12]
                receiver = tx.get("receiver", "")[:12]
                amount = tx.get("amount", 0)
                
                if sender == "COINBASE":
                    st.write(f"**{i+1}.** 🎁 Coinbase → {receiver}: **{amount}** coins")
                else:
                    st.write(f"**{i+1}.** {sender} → {receiver}: **{amount}** coins")


def display_fork_status(api_url: str):
    """
    Fork durumunu ayrı bir panel olarak göster
    
    Args:
        api_url: Backend API URL'i
    """
    st.subheader("🔀 Fork Status")
    
    try:
        response = requests.get(f"{api_url}/blockchain/fork-status", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        fork_statuses = data.get("fork_statuses", [])
        
        # Genel durum
        any_fork = any(fs.get("fork_status", {}).get("fork_detected", False) for fs in fork_statuses)
        
        if any_fork:
            st.error("⚠️ FORK DETECTED IN NETWORK!")
        else:
            st.success("✅ No forks detected - network in sync")
        
        # Node bazlı fork durumu
        st.write("**Node Fork Status:**")
        
        for fs in fork_statuses:
            node_id = fs.get("node_id", "unknown")
            role = fs.get("role", "unknown")
            chain_length = fs.get("chain_length", 0)
            fork_status = fs.get("fork_status", {})
            
            fork_detected = fork_status.get("fork_detected", False)
            fork_events = fork_status.get("fork_events_count", 0)
            
            status_icon = "⚠️" if fork_detected else "✅"
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{status_icon} **{node_id}** ({role})")
            with col2:
                st.write(f"Chain: {chain_length}")
            with col3:
                st.write(f"Forks: {fork_events}")
            with col4:
                if fork_detected:
                    st.write("🔴 FORK")
                else:
                    st.write("🟢 OK")
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch fork status: {e}")
