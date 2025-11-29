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
            ["DDoS", "Byzantine (Coming Soon)", "Sybil (Coming Soon)", 
             "51% Attack (Coming Soon)", "Network Partition (Coming Soon)", 
             "Selfish Mining (Coming Soon)"],
            key="attack_type_select"
        )
        
        node_options = [f"{node['id']} ({node['role']})" for node in nodes]
        target_selection = st.selectbox(
            "Target Node",
            node_options,
            key="target_node_select"
        )
        target_node_id = target_selection.split(" ")[0]
        
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
                else:
                    st.warning("This attack type is not implemented yet")
        
        with col2:
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        display_active_attacks()
        
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
