"""
Network Visualizer Component
streamlit-agraph ile ağ haritası görselleştirmesi
"""
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import requests


def display_network_visualizer(api_url: str):
    """
    Network topology visualizer
    
    Args:
        api_url: Backend API URL
    """
    st.subheader("🌐 Network Topology")
    
    try:
        # Network nodes bilgisini al
        response = requests.get(f"{api_url}/network/nodes", timeout=5)
        if response.status_code != 200:
            st.error("Failed to fetch network data")
            return
        
        data = response.json()
        nodes_data = data.get('nodes', [])
        
        if not nodes_data:
            st.warning("No nodes in network")
            return
        
        # Nodes ve edges oluştur
        graph_nodes = []
        graph_edges = []
        
        for node_data in nodes_data:
            node_id = node_data['id']
            role = node_data['role']
            status = node_data['status']
            is_sybil = node_data.get('is_sybil', False)
            is_byzantine = node_data.get('is_byzantine', False)
            
            # Node rengi belirle
            if is_sybil:
                color = "#FF4444"  # Kırmızı - Sybil
                size = 300
            elif is_byzantine:
                color = "#FF8800"  # Turuncu - Byzantine
                size = 400
            elif role == "validator":
                color = "#4444FF"  # Mavi - Validator
                size = 500
            else:
                color = "#44FF44"  # Yeşil - Regular
                size = 300
            
            # Status'e göre shape
            if status == "under_attack":
                shape = "triangleDown"
            elif status == "recovering":
                shape = "diamond"
            else:
                shape = "dot"
            
            # Label oluştur
            label = f"{node_id[:8]}"
            if role == "validator":
                label = f"🔷 {label}"
            if is_sybil:
                label = f"⚠️ {label}"
            
            graph_nodes.append(
                Node(
                    id=node_id,
                    label=label,
                    size=size,
                    color=color,
                    shape=shape
                )
            )
        
        # Bağlantıları oluştur (mesh topology simülasyonu)
        # Validator'lar birbirine bağlı
        validators = [n for n in nodes_data if n['role'] == 'validator']
        for i, v1 in enumerate(validators):
            for v2 in validators[i+1:]:
                graph_edges.append(
                    Edge(
                        source=v1['id'],
                        target=v2['id'],
                        color="#888888",
                        type="CURVE_SMOOTH"
                    )
                )
        
        # Her regular node en az 2 validator'a bağlı
        regulars = [n for n in nodes_data if n['role'] == 'regular']
        for regular in regulars:
            # İlk 2 validator'a bağlan
            for validator in validators[:2]:
                graph_edges.append(
                    Edge(
                        source=regular['id'],
                        target=validator['id'],
                        color="#CCCCCC",
                        type="CURVE_SMOOTH"
                    )
                )
        
        # Config
        config = Config(
            width=800,
            height=600,
            directed=False,
            physics=True,
            hierarchical=False,
            node={
                'labelProperty': 'label',
                'renderLabel': True
            },
            link={
                'renderLabel': False
            }
        )
        
        # Render graph
        agraph(nodes=graph_nodes, edges=graph_edges, config=config)
        
        # Legend
        st.markdown("**Legend:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("🔷 **Validator**")
            st.markdown("🟢 **Regular**")
        with col2:
            st.markdown("🔴 **Sybil Node**")
            st.markdown("🟠 **Byzantine**")
        with col3:
            st.markdown("🔻 **Under Attack**")
            st.markdown("🔹 **Recovering**")
        with col4:
            st.markdown(f"**Total:** {len(nodes_data)}")
            sybil_count = sum(1 for n in nodes_data if n.get('is_sybil', False))
            if sybil_count > 0:
                st.markdown(f"⚠️ **Sybil:** {sybil_count}")
        
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
