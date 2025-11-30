"""
Data Engineering AI Agent - Streamlit Frontend
With Real-Time Agent Activity Visualization, User Authentication, and Data Analysis
"""
import streamlit as st
import requests
import json
import time
import pandas as pd
import io

# ===========================================
# CONFIGURATION
# ===========================================
# NOTE: Ensure this endpoint points to your NEW deployment URL
API_ENDPOINT = st.secrets.get("API_ENDPOINT", "") 
API_KEY = st.secrets.get("API_KEY", "")
USER_ACCESS_KEY = st.secrets.get("USER_ACCESS_KEY", "")

# ===========================================
# PAGE CONFIGURATION
# ===========================================
st.set_page_config(
    page_title="Data Engineering AI Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================================
# CUSTOM STYLING
# ===========================================
st.markdown("""
<style>
    /* Main header gradient */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
    }
    
    /* Agent workflow visualization */
    .agent-flow {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 8px;
        margin: 1rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 10px;
    }
    
    .agent-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Agent activity panel */
    .agent-panel {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.85rem;
    }
    
    .agent-panel-header {
        color: #00ff88;
        font-weight: bold;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .agent-step {
        padding: 8px 0;
        border-bottom: 1px solid #333;
    }
    
    .agent-step-completed { color: #00ff88; }
    .agent-step-running { color: #ffcc00; }
    .agent-step-error { color: #ff4444; }
    
    .agent-name { font-weight: bold; font-size: 0.9rem; }
    .agent-action { color: #aaa; margin-left: 25px; font-size: 0.8rem; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;} 
</style>
""", unsafe_allow_html=True)

# ===========================================
# SESSION STATE
# ===========================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(int(time.time()))
if 'context' not in st.session_state:
    st.session_state.context = "medallion_architecture"
if 'custom_instructions' not in st.session_state:
    st.session_state.custom_instructions = ""
if 'show_agent_activity' not in st.session_state:
    st.session_state.show_agent_activity = True

# ===========================================
# AUTHENTICATION
# ===========================================
def verify_access_key(entered_key: str) -> bool:
    if not USER_ACCESS_KEY: return True
    return entered_key == USER_ACCESS_KEY

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-header">Data Engineering AI</h1>', unsafe_allow_html=True)
        with st.form("login_form"):
            access_key = st.text_input("Access Key", type="password")
            submit = st.form_submit_button("🔓 Unlock", use_container_width=True, type="primary")
            if submit and verify_access_key(access_key):
                st.session_state.authenticated = True
                st.rerun()

# ===========================================
# CONTEXT CONFIGURATIONS
# ===========================================
CONTEXTS = {
    "pipeline_design": {"name": "🔄 Pipeline Design", "desc": "Design ETL/ELT pipelines"},
    "schema_design": {"name": "📐 Schema Design", "desc": "Design database schemas"},
    "medallion_architecture": {"name": "🏗️ Medallion Architecture", "desc": "Design Bronze/Silver/Gold layers"},
    "dlt_development": {"name": "⚡ DLT Development", "desc": "Delta Live Tables pipelines"},
    "performance_optimization": {"name": "🚀 Performance", "desc": "Optimize queries/storage"},
    "custom": {"name": "✨ Custom", "desc": "Any data engineering question"}
}

# ===========================================
# API FUNCTIONS
# ===========================================
def call_api(operation: str, data: dict):
    if not API_ENDPOINT:
        st.error("⚠️ API not configured. Please check secrets.")
        return None
    
    try:
        # Force routing to new deployment if using shared endpoint
        # headers = {"Authorization": f"Bearer {API_KEY}", "azureml-model-deployment": "blue"} 
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
        
        response = requests.post(
            API_ENDPOINT,
            json={"operation": operation, **data},
            headers=headers,
            timeout=180
        )
        result = response.json()
        return json.loads(result) if isinstance(result, str) else result
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def send_chat(message: str, file_data: dict = None, metadata: str = None):
    payload = {
        "message": message,
        "session_id": st.session_state.session_id,
        "context": st.session_state.context,
        "custom_instructions": st.session_state.custom_instructions
    }
    if file_data:
        payload["file_data"] = file_data
    if metadata:
        payload["metadata"] = metadata
        
    return call_api("chat", payload)

def upload_doc(content: str, name: str, context: str):
    return call_api("add_document", {"content": content, "document_name": name, "context": context})

# ===========================================
# AGENT ACTIVITY VISUALIZATION
# ===========================================
def render_agent_activity(agent_steps: list, is_complete: bool = True):
    if not agent_steps: return
    
    status_emoji = "✅" if is_complete else "🔄"
    with st.expander(f"🤖 Agent Activity {status_emoji}", expanded=True):
        # Progress
        total = len(agent_steps)
        completed = sum(1 for s in agent_steps if s.get("status") == "completed")
        progress = completed / total if total > 0 else 0
        st.progress(progress)
        
        for step in agent_steps:
            icon = step.get("agent_icon", "🔹")
            agent = step.get("agent", "Agent")
            action = step.get("action", "Processing")
            
            st.markdown(f"**{icon} {agent}**")
            st.markdown(f"<small style='color: gray;'>└─ {action}</small>", unsafe_allow_html=True)
            
            for detail in step.get("details", [])[:3]:
                st.markdown(f"<small style='color: #888; margin-left: 20px;'>└─ {detail}</small>", unsafe_allow_html=True)
            st.markdown("---")

# ===========================================
# MAIN APPLICATION
# ===========================================
def show_main_app():
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("# 🏗️ DE Agent")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        # 1. Context Selector
        st.markdown("### 🎯 Context")
        selected = st.selectbox("Focus", list(CONTEXTS.keys()), format_func=lambda x: CONTEXTS[x]["name"], index=list(CONTEXTS.keys()).index(st.session_state.context))
        st.session_state.context = selected
        st.info(CONTEXTS[selected]["desc"])
        
        st.markdown("---")
        
        # 2. DATA ANALYSIS UPLOAD (NEW)
        st.markdown("### 📊 Data Analysis")
        uploaded_file = st.file_uploader("Upload CSV/JSON", type=['csv', 'json'])
        
        file_payload = None
        metadata_input = ""
        
        if uploaded_file:
            st.success(f"Loaded: {uploaded_file.name}")
            metadata_input = st.text_area("Data Dictionary (Optional)", height=100, placeholder="e.g., 'amt' column is in cents...")
            
            # Process File for Backend
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_preview = pd.read_csv(uploaded_file)
                    file_payload = {"content": df_preview.to_csv(index=False), "format": "csv"}
                elif uploaded_file.name.endswith('.json'):
                    df_preview = pd.read_json(uploaded_file)
                    file_payload = {"content": df_preview.to_json(), "format": "json"}
                
                with st.expander("👀 Preview Data"):
                    st.dataframe(df_preview.head(3))
            except Exception as e:
                st.error(f"Error reading file: {e}")

        st.markdown("---")
        
        # 3. Knowledge Base (Existing)
        with st.expander("📚 Knowledge Base"):
            doc_name = st.text_input("Doc Name")
            doc_content = st.text_area("Content")
            if st.button("Upload Doc"):
                upload_doc(doc_content, doc_name, st.session_state.context)
                st.success("Uploaded!")

    # --- MAIN AREA ---
    st.markdown('<h1 class="main-header">🏗️ Data Engineering AI Assistant</h1>', unsafe_allow_html=True)
    
    # Visualization of Swarm
    st.markdown("""
    <div class="agent-flow">
        <span class="agent-badge">🎯 Intent</span>
        <span>→</span>
        <span class="agent-badge">📚 RAG</span>
        <span>→</span>
        <span class="agent-badge">📊 Analyst</span>
        <span>→</span>
        <span class="agent-badge">📐 Architect</span>
        <span>→</span>
        <span class="agent-badge">💻 Engineer</span>
    </div>
    """, unsafe_allow_html=True)

    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                if st.session_state.show_agent_activity and msg.get("agent_steps"):
                    render_agent_activity(msg["agent_steps"], is_complete=True)
                st.markdown(msg["content"])
            else:
                st.markdown(msg["content"])

    # Input
    prompt = st.chat_input("Ask about pipelines, schemas, or analyze the uploaded file...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            if file_payload:
                st.caption(f"📎 Attached: {uploaded_file.name}")

        with st.chat_message("assistant"):
            placeholder = st.empty()
            if st.session_state.show_agent_activity:
                placeholder.markdown("... 🤖 Agents are thinking ...")
            
            # Send to Backend
            with st.spinner(""):
                result = send_chat(prompt, file_data=file_payload, metadata=metadata_input)
            
            if result and result.get("success"):
                response = result.get("response", "")
                steps = result.get("agent_steps", [])
                
                # Render steps
                if st.session_state.show_agent_activity:
                    with placeholder:
                        render_agent_activity(steps, is_complete=True)
                else:
                    placeholder.empty()
                
                st.markdown(response)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "agent_steps": steps
                })
            else:
                placeholder.empty()
                st.error("Connection failed or backend error.")

# ===========================================
# ENTRY POINT
# ===========================================
if __name__ == "__main__":
    if st.session_state.authenticated:
        show_main_app()
    else:
        show_login_page()
