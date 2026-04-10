#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Governance Actions Dashboard - Streamlit Frontend
==================================================

A modern, intuitive interface for the Atlan Actions Engine
providing natural language governance automation.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# Configuration
API_BASE_URL = "http://localhost:5000"
DEFAULT_THEME = "light"

# Page Configuration
st.set_page_config(
    page_title="Governance Actions Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Atlan Actions Engine - Governance Automation"}
)

# Custom CSS for Better UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #fff;
    }
    
    /* Phase boxes */
    .phase-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-weight: bold;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .phase-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    .phase-box.completed {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .phase-box.current {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 0 20px rgba(245, 87, 108, 0.5);
    }
    
    /* Status indicator */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-left: 10px;
    }
    
    .status-badge.success {
        background: #28a745;
        color: white;
    }
    
    .status-badge.error {
        background: #dc3545;
        color: white;
    }
    
    .status-badge.pending {
        background: #ffc107;
        color: black;
    }
    
    /* Command input */
    .command-input {
        border: 2px solid #667eea;
        border-radius: 8px;
        padding: 12px;
        font-size: 1rem;
    }
    
    /* Result boxes */
    .result-success {
        background: rgba(17, 153, 142, 0.1);
        border-left: 4px solid #11998e;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .result-error {
        background: rgba(220, 53, 69, 0.1);
        border-left: 4px solid #dc3545;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .result-info {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE & INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = 0
    if 'phases_completed' not in st.session_state:
        st.session_state.phases_completed = []
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    if 'execution_history' not in st.session_state:
        st.session_state.execution_history = []
    if 'api_available' not in st.session_state:
        st.session_state.api_available = False

init_session_state()

# ============================================================================
# API FUNCTIONS
# ============================================================================

@st.cache_resource
def check_api_health():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

@st.cache_data(ttl=300)
def get_metadata():
    """Get metadata from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/metadata", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_audit_logs():
    """Get audit logs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/audit-logs", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def process_command(query: str, progress_placeholder=None):
    """Process natural language command"""
    try:
        payload = {"query": query}
        
        # Show status
        if progress_placeholder:
            with progress_placeholder.container():
                st.info("⏳ Processing your governance command...")
        
        # Call API
        response = requests.post(
            f"{API_BASE_URL}/api/process",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'status': 'error',
                'error': f"API error: {response.status_code}"
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

# ============================================================================
# UI COMPONENTS
# ============================================================================

def display_header():
    """Display dashboard header"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("⚡")
    
    with col2:
        st.markdown("""
        <h1 style='text-align: center; color: #667eea;'>
            Governance Actions Dashboard
        </h1>
        <p style='text-align: center; color: #666;'>
            Natural language governance automation powered by Atlan
        </p>
        """, unsafe_allow_html=True)
    
    with col3:
        # API Status
        api_status = check_api_health()
        if api_status:
            st.markdown("""
            <div style='text-align: right;'>
                <span style='color: #11998e; font-weight: bold;'>✓ API Online</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: right;'>
                <span style='color: #dc3545; font-weight: bold;'>✗ API Offline</span>
            </div>
            """, unsafe_allow_html=True)

def display_workflow_phases():
    """Display 6-phase governance workflow"""
    phases = [
        {"num": 1, "name": "OBSERVE", "desc": "Parse & analyze"},
        {"num": 2, "name": "ANALYZE", "desc": "PII detection"},
        {"num": 3, "name": "PLAN", "desc": "Generate rules"},
        {"num": 4, "name": "SIMULATE", "desc": "Preview impact"},
        {"num": 5, "name": "EXECUTE", "desc": "Apply policies"},
        {"num": 6, "name": "LEARN", "desc": "Verify & learn"}
    ]
    
    st.markdown("### 📊 6-Phase Governance Workflow")
    
    cols = st.columns(6)
    for idx, phase in enumerate(phases):
        with cols[idx]:
            if st.session_state.current_phase >= phase["num"]:
                status_class = "completed"
                icon = "✓"
            elif st.session_state.current_phase == phase["num"] - 1:
                status_class = "current"
                icon = "◆"
            else:
                status_class = "pending"
                icon = "○"
            
            st.markdown(f"""
            <div class='phase-box {status_class}'>
                <div style='font-size: 1.5rem; margin-bottom: 8px;'>{icon}</div>
                <div style='font-weight: bold;'>{phase['num']}. {phase['name']}</div>
                <div style='font-size: 0.85rem; margin-top: 5px;'>{phase['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

def display_command_input():
    """Display natural language command input"""
    st.markdown("### 🎯 Natural Language Commands")
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔒 Mask PII", use_container_width=True):
            return "mask pii in employee table"
    
    with col2:
        if st.button("🔍 Auto Discovery", use_container_width=True):
            return "automatically discover and mask all pii"
    
    with col3:
        if st.button("⚙️ Generate DAG", use_container_width=True):
            return "generate airflow dag for governance"
    
    with col4:
        if st.button("📋 Show Policies", use_container_width=True):
            return "show current governance policies"
    
    st.markdown("---")
    
    # Text input
    query = st.text_input(
        "Enter governance command:",
        placeholder="e.g., mask salary in employee table for analyst role",
        key="command_input"
    )
    
    return query

def display_result(result: Dict[str, Any]):
    """Display execution result"""
    if result is None:
        return
    
    status = result.get('status', 'unknown')
    
    if status == 'success':
        st.markdown("<div class='result-success'>", unsafe_allow_html=True)
        st.success(f"✅ **Execution Successful** - {result.get('message', 'Command executed')}")
        
        # Display phases
        if 'phases' in result:
            with st.expander("📊 Phase Details", expanded=True):
                for phase_name, phase_data in result['phases'].items():
                    st.markdown(f"**Phase: {phase_name.upper()}**")
                    st.json(phase_data)
        
        # Display SQL commands
        if 'sql_commands' in result:
            with st.expander("💾 SQL Commands Generated"):
                for i, sql in enumerate(result['sql_commands'], 1):
                    st.code(sql, language="sql")
        
        # Display metrics
        if 'total_time' in result:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Execution Time", f"{result.get('total_time', 0):.2f}s", "⚡")
            with col2:
                st.metric("Status", "✓ Success", "")
            with col3:
                st.metric("Mode", result.get('execution_mode', 'Unknown'), "")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif status == 'error':
        st.markdown("<div class='result-error'>", unsafe_allow_html=True)
        st.error(f"❌ **Execution Failed**: {result.get('error', 'Unknown error')}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        st.markdown("<div class='result-info'>", unsafe_allow_html=True)
        st.info(f"ℹ️ {result.get('message', 'Processing...')}")
        st.markdown("</div>", unsafe_allow_html=True)

def display_metadata():
    """Display metadata"""
    st.markdown("### 📚 Metadata")
    
    metadata = get_metadata()
    if metadata:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Classifications",
                metadata.get('total_classifications', 0),
                "📊"
            )
        
        with col2:
            st.metric(
                "Policies Applied",
                metadata.get('total_policies', 0),
                "🔒"
            )
        
        with col3:
            st.metric(
                "Tables Protected",
                metadata.get('total_tables', 0),
                "🛡️"
            )
        
        # Column classifications
        if 'classifications' in metadata:
            st.markdown("#### Column Classifications")
            df = pd.DataFrame(metadata['classifications'])
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No metadata available")

def display_audit_logs():
    """Display audit logs"""
    st.markdown("### 📋 Audit Logs")
    
    logs = get_audit_logs()
    if logs and isinstance(logs, list) and len(logs) > 0:
        # Create dataframe
        df = pd.DataFrame(logs[-20:])  # Last 20 entries
        
        # Format timestamp if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(df, use_container_width=True)
        
        # Download logs
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Audit Logs",
            data=csv,
            file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No audit logs available")

# ============================================================================
# SIDEBAR
# ============================================================================

def display_sidebar():
    """Display sidebar with configuration"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Configuration
        api_url = st.text_input(
            "API URL",
            value=API_BASE_URL,
            help="Backend API server URL"
        )
        
        # Quick stats
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("API Status", "🟢 Online" if check_api_health() else "🔴 Offline")
        with col2:
            st.metric("Mode", "Production")
        
        # Documentation
        st.markdown("---")
        st.markdown("### 📚 Documentation")
        
        st.markdown("""
        **Supported Commands:**
        - `mask pii in [table]`
        - `mask [column] for [role]`
        - `discover all pii`
        - `automatically [action]`
        
        **Quick Features:**
        - 📊 6-phase workflow
        - 🔍 Column detection
        - 👥 Role-based masking
        - 📈 Performance metrics
        - 🛡️ Audit logging
        """)
        
        # Help
        st.markdown("---")
        if st.button("❓ Help & Support"):
            st.markdown("""
            ### Help & Support
            
            **Getting Started:**
            1. Enter a governance command
            2. Review the 6-phase workflow
            3. Check execution results
            4. View audit logs
            
            **Example Queries:**
            - `mask salary in employee table for analyst role`
            - `discover and mask all pii in customers`
            - `apply masking policies automatically`
            
            **For Support:**
            - Check documentation files
            - Review audit logs for errors
            - Verify API connection
            """)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application logic"""
    
    # Sidebar
    display_sidebar()
    
    # Header
    display_header()
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🚀 Governance Engine", "📊 Metadata", "📋 Audit Logs", "📈 Analytics"]
    )
    
    # Tab 1: Governance Engine
    with tab1:
        # Workflow phases
        display_workflow_phases()
        
        st.markdown("---")
        
        # Command input
        query = display_command_input()
        
        # Execute button
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            execute_btn = st.button(
                "🎯 Execute Command",
                use_container_width=True,
                key="execute_btn",
                type="primary"
            )
        
        with col2:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)
        
        with col3:
            refresh_btn = st.button("🔄 Refresh", use_container_width=True)
        
        # Process command
        if execute_btn and query:
            progress_placeholder = st.empty()
            
            with st.spinner("⏳ Processing your command..."):
                result = process_command(query, progress_placeholder)
                st.session_state.last_result = result
                st.session_state.execution_history.append({
                    'query': query,
                    'result': result,
                    'timestamp': datetime.now()
                })
            
            # Display result
            display_result(result)
        
        elif clear_btn:
            st.session_state.last_result = None
            st.rerun()
        
        # Display previous result if available
        if st.session_state.last_result and not execute_btn:
            st.markdown("---")
            st.markdown("### 📊 Last Execution Result")
            display_result(st.session_state.last_result)
    
    # Tab 2: Metadata
    with tab2:
        display_metadata()
    
    # Tab 3: Audit Logs
    with tab3:
        display_audit_logs()
    
    # Tab 4: Analytics
    with tab4:
        st.markdown("### 📈 Execution Analytics")
        
        if st.session_state.execution_history:
            # Summary stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                successful = sum(
                    1 for h in st.session_state.execution_history 
                    if h['result'].get('status') == 'success'
                )
                st.metric("Successful Executions", successful)
            
            with col2:
                total = len(st.session_state.execution_history)
                st.metric("Total Executions", total)
            
            with col3:
                success_rate = (successful / total * 100) if total > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            st.markdown("---")
            
            # Execution history
            st.markdown("#### Execution History")
            history_data = []
            for h in st.session_state.execution_history[-10:]:
                history_data.append({
                    'Timestamp': h['timestamp'].strftime('%H:%M:%S'),
                    'Query': h['query'][:50] + "..." if len(h['query']) > 50 else h['query'],
                    'Status': h['result'].get('status', 'unknown').upper(),
                    'Time': f"{h['result'].get('total_time', 0):.2f}s"
                })
            
            df_history = pd.DataFrame(history_data)
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("No execution history yet. Try running a command!")

if __name__ == "__main__":
    main()
