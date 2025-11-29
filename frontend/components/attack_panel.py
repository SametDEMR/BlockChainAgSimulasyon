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
            ["DDoS", "Byzantine", "Sybil", 
             "51% Attack (Coming Soon)", "Network Partition (Coming Soon)", 
             "Selfish Mining (Coming Soon)"],
            key="attack_type_select"
        )
        
        node_options = [f"{node['id']} ({node['role']})" for node in nodes]
        
        # Target selection (sadece DDoS ve Byzantine için)
        target_node_id = None
        if attack_type in ["DDoS", "Byzantine"]:
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
