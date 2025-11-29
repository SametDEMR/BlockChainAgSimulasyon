"""
Streamlit Frontend - Main UI with Attack Panel and Metrics Dashboard
"""
import streamlit as st
import requests
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_ui_config
from frontend.components.attack_panel import render_attack_panel
from frontend.components.metrics_dashboard import render_metrics_dashboard

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
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Attack Control", "📊 Metrics", "🔐 PBFT", "📡 Nodes"])
    
    with tab1:
        # Attack Panel
        render_attack_panel()
    
    with tab2:
        # Metrics Dashboard (NEW)
        render_metrics_dashboard()
    
    with tab3:
        # PBFT Status
        pbft_status = get_pbft_status()
        if pbft_status and pbft_status.get('enabled'):
            st.markdown("### 🔐 PBFT Consensus Status")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Primary", pbft_status.get('primary', 'N/A'))
            with col2:
                st.metric("View", pbft_status.get('current_view', 0))
            with col3:
                st.metric("Consensus", pbft_status.get('total_consensus_reached', 0))
            with col4:
                st.metric("Validators", pbft_status.get('total_validators', 0))
            
            st.markdown("#### Validator Details")
            for v in pbft_status.get('validators', []):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    badge = "👑" if v['is_primary'] else "  "
                    st.write(f"{badge} **{v['node_id']}**")
                with col2:
                    st.write(f"View: {v['view']}")
                with col3:
                    st.write(f"Consensus: {v['total_consensus_reached']}")
        else:
            st.info("PBFT not enabled")
    
    with tab4:
        # Nodes
        st.markdown("### 📡 Network Nodes")
        
        nodes_data = get_nodes()
        
        if nodes_data:
            subtab1, subtab2, subtab3 = st.tabs(["All Nodes", "Validators", "Regular"])
            
            with subtab1:
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
            
            with subtab2:
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
            
            with subtab3:
                regular = [n for n in nodes_data['nodes'] if n['role'] == 'regular']
                st.write(f"**Total: {len(regular)}**")
                for node in regular:
                    st.write(f"- **{node['id']}** | {node['balance']:.2f}")

else:
    st.error("❌ API not running. Start with: `python backend/main_old_2.py`")

if st.checkbox("Auto Refresh", value=True):
    time.sleep(ui_config['refresh_interval'])
    st.rerun()
