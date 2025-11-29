"""
Streamlit Frontend - Main UI
"""
import streamlit as st
import requests
import time
import sys
import os

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_ui_config

# Config
ui_config = get_ui_config()
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title=ui_config['page_title'],
    page_icon=ui_config['page_icon'],
    layout=ui_config['layout']
)

# Title
st.title("🔐 Blockchain Attack Simulator")
st.markdown("---")


def get_api_status():
    """API'den status al"""
    try:
        response = requests.get(f"{API_URL}/status")
        return response.json()
    except:
        return None


def get_nodes():
    """API'den node'ları al"""
    try:
        response = requests.get(f"{API_URL}/nodes")
        return response.json()
    except:
        return None


def get_pbft_status():
    """API'den PBFT status al"""
    try:
        response = requests.get(f"{API_URL}/pbft/status")
        return response.json()
    except:
        return None


def get_network_messages():
    """API'den network mesajları al"""
    try:
        response = requests.get(f"{API_URL}/network/messages")
        return response.json()
    except:
        return None


def start_simulator():
    """Simülasyonu başlat"""
    try:
        response = requests.post(f"{API_URL}/start")
        return response.json()
    except:
        return None


def stop_simulator():
    """Simülasyonu durdur"""
    try:
        response = requests.post(f"{API_URL}/stop")
        return response.json()
    except:
        return None


def reset_simulator():
    """Simülasyonu sıfırla"""
    try:
        response = requests.post(f"{API_URL}/reset")
        return response.json()
    except:
        return None


# Main UI
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start", use_container_width=True):
        result = start_simulator()
        if result:
            st.success("Simulator started!")
        else:
            st.error("Failed to start")

with col2:
    if st.button("⏸️ Stop", use_container_width=True):
        result = stop_simulator()
        if result:
            st.warning("Simulator stopped!")
        else:
            st.error("Failed to stop")

with col3:
    if st.button("🔄 Reset", use_container_width=True):
        result = reset_simulator()
        if result:
            st.info("Simulator reset!")
        else:
            st.error("Failed to reset")

st.markdown("---")

# Status section
status = get_api_status()

if status:
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", "🟢 Running" if status['is_running'] else "🔴 Stopped")
    
    with col2:
        st.metric("Total Nodes", status['total_nodes'])
    
    with col3:
        st.metric("Active Nodes", status['active_nodes'])
    
    with col4:
        st.metric("Chain Length", status['total_blocks'])
    
    st.markdown("---")
    
    # PBFT Status (YENİ)
    pbft_status = get_pbft_status()
    if pbft_status and pbft_status.get('enabled'):
        st.subheader("🔐 PBFT Consensus Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Primary Validator", pbft_status.get('primary', 'N/A'))
        
        with col2:
            st.metric("Current View", pbft_status.get('current_view', 0))
        
        with col3:
            st.metric("Consensus Reached", pbft_status.get('total_consensus_reached', 0))
        
        with col4:
            st.metric("Total Validators", pbft_status.get('total_validators', 0))
        
        # Validator details
        with st.expander("📊 Validator Details", expanded=False):
            validators = pbft_status.get('validators', [])
            for v in validators:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    primary_badge = "👑" if v['is_primary'] else "  "
                    st.write(f"{primary_badge} **{v['node_id']}**")
                with col2:
                    st.write(f"View: {v['view']}")
                with col3:
                    st.write(f"Consensus: {v['total_consensus_reached']}")
        
        st.markdown("---")
    
    # Network Messages (YENİ)
    network_msgs = get_network_messages()
    if network_msgs:
        st.subheader("📨 PBFT Message Traffic")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Messages", network_msgs.get('total_messages', 0))
        
        with col2:
            st.metric("PBFT Messages", network_msgs.get('pbft_messages', 0))
        
        with col3:
            msg_types = network_msgs.get('message_types', {})
            st.metric("Message Types", len(msg_types))
        
        # Message type breakdown
        if msg_types:
            with st.expander("📋 Message Type Breakdown", expanded=False):
                for msg_type, count in msg_types.items():
                    st.write(f"- **{msg_type}**: {count}")
        
        st.markdown("---")
    
    # Config info
    with st.expander("⚙️ Configuration", expanded=False):
        st.json(status['config'])
    
    # Nodes section
    st.subheader("📡 Network Nodes")
    
    nodes_data = get_nodes()
    
    if nodes_data:
        # Filter tabs
        tab1, tab2, tab3 = st.tabs(["All Nodes", "Validators", "Regular"])
        
        with tab1:
            st.write(f"**Total: {nodes_data['total_nodes']} nodes**")
            for node in nodes_data['nodes']:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**Node {node['id']}**")
                        st.caption(f"{node['role']}")
                    
                    with col2:
                        status_emoji = "🟢" if node['status'] == "healthy" else "🟡" if node['status'] == "recovering" else "🔴"
                        st.write(f"{status_emoji} {node['status']}")
                    
                    with col3:
                        st.write(f"⛓️ {node['chain_length']} blocks")
                    
                    with col4:
                        st.write(f"💰 {node['balance']:.2f}")
        
        with tab2:
            validators = [n for n in nodes_data['nodes'] if n['role'] == 'validator']
            st.write(f"**Total: {len(validators)} validators**")
            
            for node in validators:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        # Primary badge
                        is_primary = False
                        if 'pbft' in node and node['pbft']['is_primary']:
                            is_primary = True
                            st.write(f"👑 **{node['id']}** (PRIMARY)")
                        else:
                            st.write(f"**{node['id']}**")
                    
                    with col2:
                        st.write(f"Trust: {node['trust_score']}")
                    
                    with col3:
                        st.write(f"Blocks: {node['blocks_mined']}")
                    
                    with col4:
                        if 'pbft' in node:
                            st.write(f"View: {node['pbft']['view']}")
        
        with tab3:
            regular = [n for n in nodes_data['nodes'] if n['role'] == 'regular']
            st.write(f"**Total: {len(regular)} regular nodes**")
            for node in regular:
                st.write(f"- **{node['id']}** | Balance: {node['balance']:.2f}")

else:
    st.error("❌ Cannot connect to API server. Make sure it's running:")
    st.code("python backend/main_old_1.py", language="bash")

# Auto refresh
if st.checkbox("Auto Refresh", value=True):
    time.sleep(ui_config['refresh_interval'])
    st.rerun()
