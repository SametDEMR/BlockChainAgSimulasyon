"""
Metrics Dashboard Component
"""
import streamlit as st
import requests
import plotly.graph_objects as go
from typing import List, Dict

API_BASE = "http://localhost:8000"


def render_metrics_dashboard():
    """Metrik dashboard'unu render eder"""
    
    st.markdown("### 📊 Metrics Dashboard")
    
    try:
        # Tüm node metriklerini çek
        response = requests.get(f"{API_BASE}/metrics")
        data = response.json()
        metrics_list = data['metrics']
        
        if not metrics_list:
            st.info("No metrics available")
            return
        
        # Genel istatistikler
        display_overall_stats(metrics_list)
        
        st.markdown("---")
        
        # Grafik seçenekleri
        metric_type = st.selectbox(
            "Select Metric to Visualize",
            ["Response Time", "CPU Usage", "Memory Usage", "Network Latency", "Trust Score"],
            key="metric_type_select"
        )
        
        # Grafiği çiz
        if metric_type == "Response Time":
            plot_response_time(metrics_list)
        elif metric_type == "CPU Usage":
            plot_cpu_usage(metrics_list)
        elif metric_type == "Memory Usage":
            plot_memory_usage(metrics_list)
        elif metric_type == "Network Latency":
            plot_network_latency(metrics_list)
        elif metric_type == "Trust Score":
            plot_trust_score(metrics_list)
        
        st.markdown("---")
        
        # Node kartları
        display_node_cards(metrics_list)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load metrics: {e}")


def display_overall_stats(metrics_list: List[Dict]):
    """Genel istatistikleri gösterir"""
    
    # Hesaplamalar
    total_nodes = len(metrics_list)
    healthy_nodes = sum(1 for m in metrics_list if m['status'] == 'healthy')
    under_attack = sum(1 for m in metrics_list if m['status'] == 'under_attack')
    recovering = sum(1 for m in metrics_list if m['status'] == 'recovering')
    
    avg_response_time = sum(m['metrics']['response_time'] for m in metrics_list) / total_nodes
    avg_cpu = sum(m['metrics']['cpu_usage'] for m in metrics_list) / total_nodes
    
    # Görüntüleme
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Nodes", total_nodes)
    
    with col2:
        st.metric("🟢 Healthy", healthy_nodes)
    
    with col3:
        st.metric("🔴 Under Attack", under_attack)
    
    with col4:
        st.metric("🟡 Recovering", recovering)
    
    with col5:
        st.metric("Avg Response", f"{avg_response_time:.1f}ms")
    
    with col6:
        st.metric("Avg CPU", f"{avg_cpu:.1f}%")


def plot_response_time(metrics_list: List[Dict]):
    """Response time grafiği"""
    
    node_ids = [m['node_id'] for m in metrics_list]
    response_times = [m['metrics']['response_time'] for m in metrics_list]
    statuses = [m['status'] for m in metrics_list]
    
    # Renk kodlama
    colors = []
    for status in statuses:
        if status == 'healthy':
            colors.append('green')
        elif status == 'under_attack':
            colors.append('red')
        elif status == 'recovering':
            colors.append('orange')
        else:
            colors.append('gray')
    
    fig = go.Figure(data=[
        go.Bar(
            x=node_ids,
            y=response_times,
            marker_color=colors,
            text=[f"{rt:.1f}ms" for rt in response_times],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Response Time by Node",
        xaxis_title="Node ID",
        yaxis_title="Response Time (ms)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_cpu_usage(metrics_list: List[Dict]):
    """CPU usage grafiği"""
    
    node_ids = [m['node_id'] for m in metrics_list]
    cpu_usage = [m['metrics']['cpu_usage'] for m in metrics_list]
    statuses = [m['status'] for m in metrics_list]
    
    colors = []
    for status in statuses:
        if status == 'healthy':
            colors.append('green')
        elif status == 'under_attack':
            colors.append('red')
        elif status == 'recovering':
            colors.append('orange')
        else:
            colors.append('gray')
    
    fig = go.Figure(data=[
        go.Bar(
            x=node_ids,
            y=cpu_usage,
            marker_color=colors,
            text=[f"{cpu}%" for cpu in cpu_usage],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="CPU Usage by Node",
        xaxis_title="Node ID",
        yaxis_title="CPU Usage (%)",
        height=400,
        showlegend=False
    )
    
    # Kritik seviye çizgisi
    fig.add_hline(y=80, line_dash="dash", line_color="red", 
                  annotation_text="Critical Level (80%)")
    
    st.plotly_chart(fig, use_container_width=True)


def plot_memory_usage(metrics_list: List[Dict]):
    """Memory usage grafiği"""
    
    node_ids = [m['node_id'] for m in metrics_list]
    memory_usage = [m['metrics']['memory_usage'] for m in metrics_list]
    
    fig = go.Figure(data=[
        go.Bar(
            x=node_ids,
            y=memory_usage,
            marker_color='lightblue',
            text=[f"{mem}%" for mem in memory_usage],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Memory Usage by Node",
        xaxis_title="Node ID",
        yaxis_title="Memory Usage (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_network_latency(metrics_list: List[Dict]):
    """Network latency grafiği"""
    
    node_ids = [m['node_id'] for m in metrics_list]
    latency = [m['metrics']['network_latency'] for m in metrics_list]
    
    fig = go.Figure(data=[
        go.Scatter(
            x=node_ids,
            y=latency,
            mode='lines+markers',
            marker=dict(size=10, color='purple'),
            line=dict(width=2, color='purple')
        )
    ])
    
    fig.update_layout(
        title="Network Latency by Node",
        xaxis_title="Node ID",
        yaxis_title="Latency (ms)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_trust_score(metrics_list: List[Dict]):
    """Trust score grafiği"""
    
    node_ids = [m['node_id'] for m in metrics_list]
    trust_scores = [m['metrics']['trust_score'] for m in metrics_list]
    
    # Renk kodlama trust score'a göre
    colors = []
    for score in trust_scores:
        if score >= 80:
            colors.append('green')
        elif score >= 50:
            colors.append('orange')
        else:
            colors.append('red')
    
    fig = go.Figure(data=[
        go.Bar(
            x=node_ids,
            y=trust_scores,
            marker_color=colors,
            text=[f"{score}" for score in trust_scores],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Trust Score by Node",
        xaxis_title="Node ID",
        yaxis_title="Trust Score (0-100)",
        height=400,
        yaxis_range=[0, 105]
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_node_cards(metrics_list: List[Dict]):
    """Node metrik kartlarını gösterir"""
    
    st.markdown("#### 🎴 Node Metrics Cards")
    
    # Status'a göre filtrele
    filter_option = st.radio(
        "Filter by Status",
        ["All", "Healthy", "Under Attack", "Recovering"],
        horizontal=True,
        key="node_filter"
    )
    
    filtered_metrics = metrics_list
    if filter_option != "All":
        status_map = {
            "Healthy": "healthy",
            "Under Attack": "under_attack",
            "Recovering": "recovering"
        }
        filtered_metrics = [m for m in metrics_list if m['status'] == status_map[filter_option]]
    
    if not filtered_metrics:
        st.info(f"No {filter_option.lower()} nodes")
        return
    
    # Grid layout - 3 columns
    cols_per_row = 3
    for i in range(0, len(filtered_metrics), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j in range(cols_per_row):
            if i + j < len(filtered_metrics):
                metric = filtered_metrics[i + j]
                
                with cols[j]:
                    render_node_card(metric)


def render_node_card(metric: Dict):
    """Tek bir node kartı render eder"""
    
    # Status emoji
    status_emoji = {
        'healthy': '🟢',
        'under_attack': '🔴',
        'recovering': '🟡'
    }
    
    emoji = status_emoji.get(metric['status'], '⚪')
    
    with st.container():
        st.markdown(f"**{emoji} {metric['node_id']}** ({metric['role']})")
        
        m = metric['metrics']
        
        # Metrikler
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption(f"RT: {m['response_time']:.1f}ms")
            st.caption(f"CPU: {m['cpu_usage']}%")
            st.caption(f"Mem: {m['memory_usage']}%")
        
        with col2:
            st.caption(f"Latency: {m['network_latency']:.1f}ms")
            st.caption(f"Trust: {m['trust_score']}")
            st.caption(f"Errors: {m['errors_count']}")
        
        # Progress bar - CPU usage
        cpu_color = "normal"
        if m['cpu_usage'] > 80:
            cpu_color = "error"
        elif m['cpu_usage'] > 60:
            cpu_color = "warning"
        
        st.progress(m['cpu_usage'] / 100)
        
        st.markdown("---")
