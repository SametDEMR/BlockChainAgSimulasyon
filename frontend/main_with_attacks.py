"""
Streamlit Frontend - Main UI with Attack Panel
"""
import streamlit as st
import requests
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_ui_config
from frontend.components.attack_panel import render_attack_panel

ui_config = get_ui_config()
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title=ui_config['page_title'],
    page_icon=ui_config['page_icon'],
    layout=ui_config['layout']
)

st.title("🔐 Blockchain Attack Simulator")
st.markdown("---")


def get_api_status():
    try:
        return requests.get(f"{API_URL}/status").json()
    except:
        return None

def get_nodes():
    try:
        return requests.get(f"{API_URL}/nodes").json()
    except:
        return None

def get_pbft_status():
    try:
        return requests.get(f"{API_URL}/pbft/status").json()
    except:
        return None

def get_network_messages():
    try:
        return requests.get(f"{API_URL}/network/messages").json()
    except:
        return None

# Control buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start", use_container_width=True):
        result = requests.post(f"{API_URL}/start").json()
        st.success("Started!" if result else "Failed")

with col2:
    if st.button("⏸️ Stop", use_container_width=True):
        result = requests.post(f"{API_URL}/stop").json()
        st.warning("Stopped!" if result else "Failed")

with col3:
    if st.button("🔄 Reset", use_container_width=True):
        result = requests.post(f"{API_URL}/reset").json()
        st.info("Reset!" if result else "Failed")

st.markdown("---")

# Status
status = get_api_status()

if status:
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
    
    # Attack Panel (NEW)
    render_attack_panel()
    
    st.markdown("---")
    
    # PBFT Status
    pbft_status = get_pbft_status()
    if pbft_status and pbft_status.get('enabled'):
        st.subheader("🔐 PBFT Consensus")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Primary", pbft_status.get('primary', 'N/A'))
        with col2:
            st.metric("View", pbft_status.get('current_view', 0))
        with col3:
            st.metric("Consensus", pbft_status.get('total_consensus_reached', 0))
        with col4:
            st.metric("Validators", pbft_status.get('total_validators', 0))
        
        with st.expander("Validator Details"):
            for v in pbft_status.get('validators', []):
                badge = "👑" if v['is_primary'] else "  "
                st.write(f"{badge} {v['node_id']} | View: {v['view']} | Consensus: {v['total_consensus_reached']}")
        
        st.markdown("---")
    
    # Nodes
    st.subheader("📡 Network Nodes")
    
    nodes_data = get_nodes()
    
    if nodes_data:
        tab1, tab2, tab3 = st.tabs(["All Nodes", "Validators", "Regular"])
        
        with tab1:
            st.write(f"**Total: {nodes_data['total_nodes']}**")
            for node in nodes_data['nodes']:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{node['id']}** ({node['role']})")
                with col2:
                    emoji = "🟢" if node['status'] == "healthy" else "🟡" if node['status'] == "recovering" else "🔴"
                    st.write(f"{emoji} {node['status']}")
                with col3:
                    st.write(f"⛓️ {node['chain_length']}")
                with col4:
                    st.write(f"💰 {node['balance']:.2f}")
        
        with tab2:
            validators = [n for n in nodes_data['nodes'] if n['role'] == 'validator']
            st.write(f"**Total: {len(validators)}**")
            for node in validators:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    badge = "👑" if node.get('pbft', {}).get('is_primary') else ""
                    st.write(f"{badge} **{node['id']}**")
                with col2:
                    st.write(f"Trust: {node['trust_score']}")
                with col3:
                    st.write(f"Blocks: {node['blocks_mined']}")
        
        with tab3:
            regular = [n for n in nodes_data['nodes'] if n['role'] == 'regular']
            st.write(f"**Total: {len(regular)}**")
            for node in regular:
                st.write(f"- **{node['id']}** | {node['balance']:.2f}")

else:
    st.error("❌ API not running. Start with: `python backend/main.py`")

if st.checkbox("Auto Refresh", value=True):
    time.sleep(ui_config['refresh_interval'])
    st.rerun()
