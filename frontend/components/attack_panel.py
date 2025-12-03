"""
Attack Control Panel Component
"""
import streamlit as st
import requests
from typing import Optional

API_BASE = "http://localhost:8000"

def render_attack_panel():
    """Saldırı kontrol panelini render eder"""
    
    st.markdown("### 🎯 Attack Control Panel")
    
    try:
        response = requests.get(f"{API_BASE}/nodes")
        nodes = response.json()['nodes']
        
        attack_type = st.selectbox(
            "Attack Type",
            ["DDoS", "Byzantine", "Sybil", "Majority Attack (51%)",
             "Network Partition", 
             "Selfish Mining"],
            key="attack_type_select"
        )
        
        node_options = [f"{node['id']} ({node['role']})" for node in nodes]
        
        # Target selection (sadece DDoS, Byzantine ve Selfish Mining için)
        target_node_id = None
        if attack_type in ["DDoS", "Byzantine", "Selfish Mining"]:
            # Selfish Mining için sadece regular node'lar
            if attack_type == "Selfish Mining":
                regular_nodes = [n for n in nodes if n['role'] == 'regular']
                if not regular_nodes:
                    st.warning("No regular nodes available for Selfish Mining")
                    return
                node_options = [f"{node['id']} ({node['role']})" for node in regular_nodes]
            
            target_selection = st.selectbox(
                "Target Node",
                node_options,
                key="target_node_select"
            )
            target_node_id = target_selection.split(" ")[0]
        
        # Sybil için num_nodes
        num_fake_nodes = None
        if attack_type == "Sybil":
            num_fake_nodes = st.slider(
                "Number of Fake Nodes",
                min_value=5,
                max_value=50,
                value=20,
                step=5,
                key="sybil_num_nodes"
            )
        
        intensity = None
        if attack_type == "DDoS":
            intensity = st.select_slider(
                "Attack Intensity",
                options=["low", "medium", "high"],
                value="high",
                key="intensity_select"
            )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🚀 Trigger Attack", type="primary", use_container_width=True):
                if attack_type == "DDoS":
                    trigger_ddos_attack(target_node_id, intensity)
                elif attack_type == "Byzantine":
                    trigger_byzantine_attack(target_node_id)
                elif attack_type == "Sybil":
                    trigger_sybil_attack(num_fake_nodes)
                elif attack_type == "Majority Attack (51%)":
                    trigger_majority_attack()
                elif attack_type == "Network Partition":
                    trigger_partition_attack()
                elif attack_type == "Selfish Mining":
                    trigger_selfish_mining_attack(target_node_id)
                else:
                    st.warning("This attack type is not implemented yet")
        
        with col2:
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        display_active_attacks()
        
        st.markdown("---")
        display_byzantine_status()
        
        st.markdown("---")
        display_sybil_status()
        
        st.markdown("---")
        display_majority_status()
        
        st.markdown("---")
        display_partition_status()
        
        st.markdown("---")
        display_selfish_mining_status()
        
        st.markdown("---")
        display_attack_history()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API: {e}")


def trigger_ddos_attack(target_node_id: str, intensity: str):
    """DDoS saldırısı tetikler"""
    try:
        attack_data = {
            "attack_type": "ddos",
            "target_node_id": target_node_id,
            "parameters": {"intensity": intensity}
        }
        
        response = requests.post(f"{API_BASE}/attack/trigger", json=attack_data)
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.info(f"Attack ID: {result['attack_id']}")
        else:
            st.error(f"Failed to trigger attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def trigger_byzantine_attack(target_node_id: str):
    """Byzantine saldırısı tetikler"""
    try:
        attack_data = {
            "attack_type": "byzantine",
            "target_node_id": target_node_id,
            "parameters": {}
        }
        
        response = requests.post(f"{API_BASE}/attack/trigger", json=attack_data)
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.info(f"Target: {result['target']} | Duration: {result['duration']}s")
        else:
            st.error(f"Failed to trigger attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def display_byzantine_status():
    """Byzantine saldırı durumunu gösterir"""
    st.markdown("#### 🚫 Byzantine Attack Status")
    
    try:
        response = requests.get(f"{API_BASE}/attack/byzantine/status")
        status = response.json()
        
        if not status['active']:
            st.info("✅ No active Byzantine attack")
            return
        
        # Aktif Byzantine saldırısı var
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Target Node", status['target_node'])
        
        with col2:
            st.metric("Elapsed Time", f"{status['elapsed_time']:.1f}s")
        
        with col3:
            st.metric("Remaining Time", f"{status['remaining_time']:.1f}s")
        
        # Progress bar
        progress = status['elapsed_time'] / status['attack_duration']
        st.progress(min(1.0, progress))
        
        # Stop butonu
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⏹️ Stop Byzantine Attack", type="secondary", use_container_width=True):
                stop_byzantine_attack()
        
        # Hedef node'un durumunu göster
        with st.expander("🔍 View Target Node Details"):
            try:
                node_response = requests.get(f"{API_BASE}/nodes/{status['target_node']}")
                node_data = node_response.json()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Status", node_data['status'])
                    st.metric("Is Byzantine", "Yes" if node_data['is_byzantine'] else "No")
                
                with col2:
                    st.metric("Trust Score", node_data['trust_score'])
                    st.metric("Response Time", f"{node_data['response_time']:.1f}ms")
                
                with col3:
                    if node_data.get('pbft'):
                        st.metric("PBFT View", node_data['pbft']['view'])
                        st.metric("Consensus Reached", node_data['pbft']['total_consensus_reached'])
                
            except Exception as e:
                st.error(f"Failed to load node details: {e}")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Byzantine attack status: {e}")


def stop_byzantine_attack():
    """Byzantine saldırısını durdurur"""
    try:
        response = requests.post(f"{API_BASE}/attack/byzantine/stop")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.rerun()
        else:
            st.error(f"Failed to stop Byzantine attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def display_active_attacks():
    """Aktif saldırıları gösterir"""
    st.markdown("#### ⚡ Active Attacks")
    
    try:
        response = requests.get(f"{API_BASE}/attack/status")
        data = response.json()
        
        active_attacks = data['active_attacks']
        
        if not active_attacks:
            st.info("No active attacks")
            return
        
        for attack in active_attacks:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{attack['attack_id']}**")
                    st.caption(f"Type: {attack['attack_type']}")
                
                with col2:
                    st.markdown(f"Target: `{attack['target']}`")
                    st.caption(f"Status: {attack['status']}")
                
                with col3:
                    params = attack.get('parameters', {})
                    if params:
                        st.caption(f"Params: {params}")
                
                with col4:
                    if st.button("⏹️ Stop", key=f"stop_{attack['attack_id']}"):
                        stop_attack(attack['attack_id'])
                
                effects = attack.get('effects', [])
                if effects:
                    with st.expander("View Effects"):
                        for effect in effects[-5:]:
                            st.caption(f"• {effect}")
                
                st.markdown("---")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load active attacks: {e}")


def display_attack_history():
    """Saldırı geçmişini gösterir"""
    st.markdown("#### 📜 Attack History")
    
    try:
        response = requests.get(f"{API_BASE}/attack/status")
        data = response.json()
        
        history = data['recent_history']
        
        if not history:
            st.info("No attack history")
            return
        
        for attack in history[:5]:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 2])
                
                with col1:
                    st.markdown(f"**{attack['attack_id']}**")
                    st.caption(f"Type: {attack['attack_type']}")
                
                with col2:
                    st.caption(f"Target: `{attack['target']}`")
                    st.caption(f"Status: {attack['status']}")
                
                with col3:
                    duration = attack.get('duration')
                    if duration:
                        st.caption(f"Duration: {duration:.1f}s")
                
                st.markdown("---")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load attack history: {e}")


def stop_attack(attack_id: str):
    """Saldırıyı durdurur"""
    try:
        response = requests.post(f"{API_BASE}/attack/stop/{attack_id}")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.rerun()
        else:
            st.error(f"Failed to stop attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def trigger_sybil_attack(num_nodes: int):
    """Sybil saldırısı tetikler"""
    try:
        response = requests.post(f"{API_BASE}/attack/sybil/trigger?num_nodes={num_nodes}")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.info(f"Attack ID: {result['attack_id']}")
            st.rerun()
        else:
            st.error(f"Failed to trigger Sybil attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def display_sybil_status():
    """Sybil saldırı durumunu gösterir"""
    st.markdown("#### 🔴 Sybil Attack Status")
    
    try:
        response = requests.get(f"{API_BASE}/attack/sybil/status")
        status = response.json()
        
        if status['status'] not in ['active', 'recovering']:
            st.info("⚪ No active Sybil attack")
            return
        
        # Status indicator
        if status['status'] == 'active':
            st.error("🔴 **Sybil Attack ACTIVE**")
        else:
            st.warning("🟡 **Recovering from Sybil Attack**")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Fake Nodes Created",
                status['parameters']['num_fake_nodes']
            )
        
        with col2:
            st.metric(
                "Currently Active",
                status['parameters']['active_fake_nodes']
            )
        
        with col3:
            # Progress bar based on remaining fake nodes
            total = status['parameters']['num_fake_nodes']
            active = status['parameters']['active_fake_nodes']
            if total > 0:
                progress = active / total
                st.progress(progress)
                st.caption(f"Cleanup: {100-int(progress*100)}%")
        
        # Effects
        if status.get('effects'):
            with st.expander("📊 View Attack Effects"):
                for effect in status['effects'][-5:]:
                    st.caption(f"• {effect}")
        
        # Stop button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⏹️ Stop Sybil Attack", type="secondary", use_container_width=True):
                stop_sybil_attack()
        
        # Fake nodes list (sample)
        if status.get('fake_node_ids'):
            with st.expander("🔍 View Fake Node IDs (Sample)"):
                sample_nodes = status['fake_node_ids'][:10]
                for node_id in sample_nodes:
                    st.code(node_id, language=None)
                if len(status['fake_node_ids']) > 10:
                    st.caption(f"... and {len(status['fake_node_ids']) - 10} more")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Sybil attack status: {e}")


def stop_sybil_attack():
    """Sybil saldırısını durdurur"""
    try:
        response = requests.post(f"{API_BASE}/attack/sybil/stop")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.rerun()
        else:
            st.error(f"Failed to stop Sybil attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def trigger_majority_attack():
    """Majority (%51) saldırısı tetikler"""
    try:
        response = requests.post(f"{API_BASE}/attack/majority/trigger")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.info(f"Attack ID: {result['attack_id']}")
            st.rerun()
        else:
            st.error(f"Failed to trigger Majority attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def display_majority_status():
    """Majority saldırı durumunu gösterir"""
    st.markdown("#### 🔴 Majority Attack (%51) Status")
    
    try:
        response = requests.get(f"{API_BASE}/attack/majority/status")
        status = response.json()
        
        if not status.get('active', False):
            st.info("⚪ No active Majority attack")
            return
        
        # Status indicator
        st.error("🔴 **Majority Attack ACTIVE - Network Compromised!**")
        
        # Attack metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Malicious Validators",
                status.get('malicious_validators', 0)
            )
        
        with col2:
            st.metric(
                "Honest Validators",
                status.get('honest_validators', 0)
            )
        
        with col3:
            if status.get('fork_created', False):
                st.error("⚠️ Fork Created")
            else:
                st.success("✅ No Fork")
        
        # Malicious validator list
        if status.get('malicious_validator_ids'):
            with st.expander("🔍 View Compromised Validators"):
                for validator_id in status['malicious_validator_ids']:
                    st.markdown(f"🔴 `{validator_id}` - COMPROMISED")
        
        # Stop button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⏹️ Stop Majority Attack", type="secondary", use_container_width=True):
                stop_majority_attack()
        
        # Warning message
        st.warning("🚨 **Warning**: Malicious validators control the network. They can approve fraudulent transactions and create alternative chains.")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Majority attack status: {e}")


def stop_majority_attack():
    """Majority saldırısını durdurur"""
    try:
        response = requests.post(f"{API_BASE}/attack/majority/stop")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.rerun()
        else:
            st.error(f"Failed to stop Majority attack: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def trigger_partition_attack():
    """Network Partition saldırısı tetikler"""
    try:
        response = requests.post(f"{API_BASE}/attack/partition/trigger")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.info(f"Attack ID: {result['attack_id']}")
            st.rerun()
        else:
            st.error(f"Failed to trigger Network Partition: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def display_partition_status():
    """Network Partition saldırı durumunu gösterir"""
    st.markdown("#### 🔶 Network Partition Status")
    
    try:
        response = requests.get(f"{API_BASE}/attack/partition/status")
        status = response.json()
        
        if not status.get('active', False):
            st.info("⚪ No active Network Partition")
            return
        
        # Status indicator
        st.error("🔴 **Network Partition ACTIVE - Network Split!**")
        
        # Partition metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Group A Nodes",
                status.get('group_a_size', 0)
            )
        
        with col2:
            st.metric(
                "Group B Nodes",
                status.get('group_b_size', 0)
            )
        
        with col3:
            if status.get('message_broker_partition', {}).get('active', False):
                blocked = status['message_broker_partition'].get('blocked_messages', 0)
                st.metric("Blocked Messages", blocked)
        
        # Group lists
        col1, col2 = st.columns(2)
        
        with col1:
            if status.get('group_a_ids'):
                with st.expander("🔵 View Group A Nodes"):
                    for node_id in status['group_a_ids']:
                        st.markdown(f"🔵 `{node_id}`")
        
        with col2:
            if status.get('group_b_ids'):
                with st.expander("🟢 View Group B Nodes"):
                    for node_id in status['group_b_ids']:
                        st.markdown(f"🟢 `{node_id}`")
        
        # Stop button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⏹️ Stop Partition", type="secondary", use_container_width=True):
                stop_partition_attack()
        
        # Warning message
        st.warning("🚨 **Warning**: Network is split into two isolated partitions. Nodes cannot communicate across partitions. Parallel chains may form.")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Partition status: {e}")


def stop_partition_attack():
    """Network Partition saldırısını durdurur"""
    try:
        response = requests.post(f"{API_BASE}/attack/partition/stop")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.rerun()
        else:
            st.error(f"Failed to stop Partition: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def trigger_selfish_mining_attack(target_node_id: str):
    """Selfish Mining saldırısı tetikler"""
    try:
        response = requests.post(f"{API_BASE}/attack/selfish/trigger", params={"target_node_id": target_node_id})
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.info(f"Target: {result['target_node']} | Duration: {result['duration']}s | Reveal Threshold: {result['reveal_threshold']} blocks")
            st.rerun()
        else:
            st.error(f"Failed to trigger Selfish Mining: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")


def display_selfish_mining_status():
    """Selfish Mining saldırı durumunu gösterir"""
    st.markdown("#### 🟠 Selfish Mining Status")
    
    try:
        response = requests.get(f"{API_BASE}/attack/selfish/status")
        status = response.json()
        
        if not status.get('active', False):
            st.info("⚪ No active Selfish Mining")
            return
        
        # Status indicator
        st.error("🔴 **Selfish Mining ACTIVE - Private Chain Hidden!**")
        
        # Attack metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Target Node",
                status.get('target_node', 'N/A')
            )
        
        with col2:
            st.metric(
                "Private Chain",
                f"{status.get('private_chain_length', 0)} blocks"
            )
        
        with col3:
            st.metric(
                "Public Chain",
                f"{status.get('public_chain_length', 0)} blocks"
            )
        
        with col4:
            advantage = status.get('advantage', 0)
            if advantage >= status.get('reveal_threshold', 2):
                st.error(f"+{advantage} ⚠️")
            else:
                st.metric("Advantage", f"+{advantage}")
        
        # Progress metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Blocks Mined (Private)", status.get('blocks_mined_private', 0))
        
        with col2:
            st.metric("Blocks Revealed", status.get('blocks_revealed', 0))
        
        with col3:
            elapsed = status.get('elapsed_time', 0)
            remaining = status.get('remaining_time', 0)
            st.metric("Remaining Time", f"{remaining:.1f}s")
        
        # Progress bar
        if status.get('attack_duration', 0) > 0:
            progress = elapsed / status['attack_duration']
            st.progress(min(1.0, progress))
        
        # Stop button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⏹️ Stop Selfish Mining", type="secondary", use_container_width=True):
                stop_selfish_mining_attack()
        
        # Warning message
        if advantage >= status.get('reveal_threshold', 2):
            st.warning("🚨 **Warning**: Selfish miner is about to reveal private chain! Public chain will be orphaned.")
        else:
            st.info(f"🔒 Private chain is {advantage} blocks ahead. Will reveal at +{status.get('reveal_threshold', 2)} blocks.")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Selfish Mining status: {e}")


def stop_selfish_mining_attack():
    """Selfish Mining saldırısını durdurur"""
    try:
        response = requests.post(f"{API_BASE}/attack/selfish/stop")
        result = response.json()
        
        if response.status_code == 200:
            st.success(f"✅ {result['message']}")
            st.info(f"Total Mined: {result.get('blocks_mined_private', 0)} | Total Revealed: {result.get('blocks_revealed', 0)}")
            st.rerun()
        else:
            st.error(f"Failed to stop Selfish Mining: {result}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
