# app.py
"""
Data Engineering AI Agent - Streamlit Frontend
With Real-Time Agent Activity Visualization & User Authentication
"""
import streamlit as st
import requests
import json
import time
import hashlib

# ===========================================
# CONFIGURATION
# ===========================================
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
    
    /* Lock icon for login */
    .lock-icon {
        font-size: 4rem;
        text-align: center;
        margin-bottom: 1rem;
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
    
    /* Context card */
    .context-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 10px 0;
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
    
    .agent-step:last-child {
        border-bottom: none;
    }
    
    .agent-step-completed {
        color: #00ff88;
    }
    
    .agent-step-running {
        color: #ffcc00;
    }
    
    .agent-step-waiting {
        color: #666;
    }
    
    .agent-step-error {
        color: #ff4444;
    }
    
    .agent-name {
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .agent-action {
        color: #aaa;
        margin-left: 25px;
        font-size: 0.8rem;
    }
    
    .agent-detail {
        color: #888;
        margin-left: 35px;
        font-size: 0.75rem;
    }
    
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #00ff88;
        border-radius: 50%;
        margin-right: 5px;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
    
    /* Progress bar */
    .progress-container {
        background: #333;
        border-radius: 5px;
        overflow: hidden;
        height: 6px;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    
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
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'show_agent_activity' not in st.session_state:
    st.session_state.show_agent_activity = True

# ===========================================
# AUTHENTICATION
# ===========================================
def verify_access_key(entered_key: str) -> bool:
    """Verify the access key."""
    if not USER_ACCESS_KEY:
        return True
    return entered_key == USER_ACCESS_KEY

def show_login_page():
    """Display login page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown('<p class="lock-icon">🔐</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="main-header">Data Engineering AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Enter your access key to continue</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            access_key = st.text_input(
                "Access Key",
                type="password",
                placeholder="Enter your access key..."
            )
            
            submit = st.form_submit_button("🔓 Unlock", use_container_width=True, type="primary")
            
            if submit:
                if access_key and verify_access_key(access_key):
                    st.session_state.authenticated = True
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    remaining = 5 - st.session_state.login_attempts
                    if remaining > 0:
                        st.error(f"❌ Invalid key. {remaining} attempts remaining.")
                    else:
                        st.error("🚫 Too many failed attempts.")
        
        st.markdown("---")
        st.caption("Powered by Deep Agents • Azure AI • LangGraph")

# ===========================================
# CONTEXT CONFIGURATIONS
# ===========================================
CONTEXTS = {
    "pipeline_design": {
        "name": "🔄 Pipeline Design",
        "desc": "Design ETL/ELT data pipelines",
        "examples": ["Create a daily ETL pipeline", "Design a streaming pipeline"]
    },
    "schema_design": {
        "name": "📐 Schema Design",
        "desc": "Design database schemas",
        "examples": ["Design a customer table", "Create an orders schema"]
    },
    "medallion_architecture": {
        "name": "🏗️ Medallion Architecture",
        "desc": "Design Bronze/Silver/Gold layers",
        "examples": ["Design medallion for e-commerce", "Create Bronze layer for IoT"]
    },
    "dlt_development": {
        "name": "⚡ DLT Development",
        "desc": "Delta Live Tables pipelines",
        "examples": ["Create DLT with expectations", "Build streaming DLT"]
    },
    "performance_optimization": {
        "name": "🚀 Performance",
        "desc": "Optimize queries and structures",
        "examples": ["Optimize slow Spark query", "Recommend partitioning"]
    },
    "custom": {
        "name": "✨ Custom",
        "desc": "Any data engineering question",
        "examples": ["Ask anything"]
    }
}

# ===========================================
# API FUNCTIONS
# ===========================================
def call_api(operation: str, data: dict):
    """Call the backend API."""
    if not API_ENDPOINT:
        st.error("⚠️ API not configured.")
        return None
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"operation": operation, **data},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            timeout=180
        )
        result = response.json()
        return json.loads(result) if isinstance(result, str) else result
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def send_chat(message: str):
    """Send chat message."""
    return call_api("chat", {
        "message": message,
        "session_id": st.session_state.session_id,
        "context": st.session_state.context,
        "custom_instructions": st.session_state.custom_instructions
    })

def upload_doc(content: str, name: str, context: str):
    """Upload document."""
    return call_api("add_document", {
        "content": content,
        "document_name": name,
        "context": context
    })

def get_docs():
    return call_api("get_documents", {})

def get_stats():
    return call_api("get_stats", {})

# ===========================================
# AGENT ACTIVITY VISUALIZATION
# ===========================================
def render_agent_activity(agent_steps: list, is_complete: bool = True):
    """Render the real-time agent activity panel using Streamlit components."""
    
    if not agent_steps:
        return
    
    # Use an expander for the agent activity
    status_emoji = "✅" if is_complete else "🔄"
    status_text = "Complete" if is_complete else "Processing..."
    
    with st.expander(f"🤖 Agent Activity {status_emoji} {status_text}", expanded=True):
        
        # Progress bar at top
        total_steps = len(agent_steps)
        completed = sum(1 for s in agent_steps if s.get("status") == "completed")
        progress = completed / total_steps if total_steps > 0 else 0
        
        st.progress(progress, text=f"{completed}/{total_steps} steps completed")
        
        st.markdown("---")
        
        # Render each step
        for step in agent_steps:
            status = step.get("status", "completed")
            icon = step.get("agent_icon", "🔹")
            agent = step.get("agent", "Agent")
            action = step.get("action", "Processing")
            details = step.get("details", [])
            
            # Status icon
            if status == "completed":
                status_icon = "✅"
                color = "green"
            elif status == "running":
                status_icon = "🔄"
                color = "orange"
            elif status == "error":
                status_icon = "❌"
                color = "red"
            else:
                status_icon = "⏳"
                color = "gray"
            
            # Agent header
            st.markdown(f"**{status_icon} {icon} {agent}**")
            st.markdown(f"<small style='color: gray; margin-left: 20px;'>└─ {action}</small>", unsafe_allow_html=True)
            
            # Details
            for detail in details[:4]:
                st.markdown(f"<small style='color: #888; margin-left: 40px;'>└─ {detail}</small>", unsafe_allow_html=True)
            
            st.markdown("")  # Spacing

# ===========================================
# MAIN APPLICATION
# ===========================================
def show_main_app():
    """Display the main application."""
    
    # SIDEBAR
    with st.sidebar:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("# 🏗️ DE Agent")
        with col2:
            if st.button("🚪", help="Logout"):
                st.session_state.authenticated = False
                st.session_state.messages = []
                st.rerun()
        
        st.markdown("---")
        
        # Context selection
        st.markdown("## 🎯 Context")
        
        selected = st.selectbox(
            "Focus",
            list(CONTEXTS.keys()),
            format_func=lambda x: CONTEXTS[x]["name"],
            index=list(CONTEXTS.keys()).index(st.session_state.context),
            label_visibility="collapsed"
        )
        st.session_state.context = selected
        
        ctx = CONTEXTS[selected]
        st.info(ctx["desc"])
        
        # Examples
        for i, ex in enumerate(ctx["examples"][:2]):
            if st.button(f"💡 {ex[:25]}...", key=f"ex_{i}"):
                st.session_state.pending_prompt = ex
        
        # Custom instructions
        with st.expander("⚙️ Custom Instructions"):
            st.session_state.custom_instructions = st.text_area(
                "Instructions",
                st.session_state.custom_instructions,
                height=80,
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        # Agent activity toggle
        st.markdown("## 🤖 Display Options")
        st.session_state.show_agent_activity = st.checkbox(
            "Show Agent Activity",
            value=st.session_state.show_agent_activity,
            help="Display real-time agent workflow"
        )
        
        st.markdown("---")
        
        # Knowledge Base
        st.markdown("## 📚 Knowledge Base")
        
        with st.expander("📤 Add Document"):
            doc_name = st.text_input("Name", placeholder="my_doc")
            doc_ctx = st.selectbox(
                "Category",
                [k for k in CONTEXTS if k != "custom"],
                format_func=lambda x: CONTEXTS[x]["name"]
            )
            doc_content = st.text_area("Content", height=100)
            
            if st.button("Upload", use_container_width=True, type="primary"):
                if doc_name and doc_content:
                    with st.spinner("Uploading..."):
                        r = upload_doc(doc_content, doc_name, doc_ctx)
                        if r and r.get("success"):
                            st.success(f"✅ Added!")
                        else:
                            st.error("Failed")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Stats"):
                s = get_stats()
                if s:
                    st.metric("Docs", s.get("total_documents", 0))
        with col2:
            if st.button("🗑️ Clear"):
                st.session_state.messages = []
                st.rerun()
    
    # MAIN CONTENT
    st.markdown('<h1 class="main-header">🏗️ Data Engineering AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Powered by Deep Agents • GPT-4o • LangGraph • Azure AI</p>', unsafe_allow_html=True)
    
    # Agent flow visualization
    st.markdown("""
    <div class="agent-flow">
        <span class="agent-badge">🎯 Intent</span>
        <span style="color: #764ba2; font-weight: bold;"> → </span>
        <span class="agent-badge">📚 RAG</span>
        <span style="color: #764ba2; font-weight: bold;"> → </span>
        <span class="agent-badge">📋 Planner</span>
        <span style="color: #764ba2; font-weight: bold;"> → </span>
        <span class="agent-badge">📐 Architect</span>
        <span style="color: #764ba2; font-weight: bold;"> → </span>
        <span class="agent-badge">💻 Coder</span>
        <span style="color: #764ba2; font-weight: bold;"> → </span>
        <span class="agent-badge">🔍 Critic</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Context display
    ctx = CONTEXTS[st.session_state.context]
    st.markdown(f'<div class="context-card"><strong>Context:</strong> {ctx["name"]} — {ctx["desc"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # Show agent activity for assistant messages
            if msg["role"] == "assistant":
                # Show agent activity panel if enabled and steps exist
                if st.session_state.show_agent_activity and msg.get("agent_steps"):
                    render_agent_activity(msg["agent_steps"], is_complete=True)
                
                # Show the response
                st.markdown(msg["content"])
                
                # Show metadata
                if msg.get("metadata"):
                    meta = msg["metadata"]
                    with st.expander("📊 Summary"):
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.caption(f"**Intent:** {meta.get('intent', 'N/A')}")
                        with c2:
                            conf = meta.get('intent_confidence', 0)
                            st.caption(f"**Confidence:** {conf:.0%}")
                        with c3:
                            docs = meta.get('rag_documents', [])
                            st.caption(f"**Docs Used:** {len(docs)}")
                        with c4:
                            val = meta.get('validation', {})
                            st.caption(f"**Validated:** {'✅' if val.get('passed', True) else '⚠️'}")
            else:
                st.markdown(msg["content"])
    
    # Handle pending prompt from sidebar
    if hasattr(st.session_state, 'pending_prompt') and st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
    else:
        prompt = st.chat_input(f"Ask about {ctx['desc'].lower()}...")
    
    # Process new message
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            # Show placeholder for agent activity
            activity_placeholder = st.empty()
            
            if st.session_state.show_agent_activity:
                # Show "processing" state
                activity_placeholder.markdown("""
                <div class="agent-panel">
                    <div class="agent-panel-header">
                        <span>🤖 AGENT ACTIVITY</span>
                        <span style="color: #ffcc00;"><span class="live-indicator"></span> Processing...</span>
                    </div>
                    <div class="agent-step agent-step-running">
                        <div class="agent-name">🔄 🎯 Intent Classifier</div>
                        <div class="agent-action">└─ Analyzing your request...</div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: 10%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.spinner(""):
                result = send_chat(prompt)
            
            if result and result.get("success"):
                response = result.get("response", "")
                agent_steps = result.get("agent_steps", [])
                
                # Update activity panel with completed steps
                if st.session_state.show_agent_activity and agent_steps:
                    with activity_placeholder:
                        render_agent_activity(agent_steps, is_complete=True)
                else:
                    activity_placeholder.empty()
                
                # Show response
                st.markdown(response)
                
                # Show summary
                with st.expander("📊 Summary"):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.caption(f"**Intent:** {result.get('intent', 'N/A')}")
                    with c2:
                        conf = result.get('intent_confidence', 0)
                        st.caption(f"**Confidence:** {conf:.0%}")
                    with c3:
                        docs = result.get('rag_documents', [])
                        st.caption(f"**Docs Used:** {len(docs)}")
                    with c4:
                        val = result.get('validation', {})
                        st.caption(f"**Validated:** {'✅' if val.get('passed', True) else '⚠️'}")
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "agent_steps": agent_steps,
                    "metadata": {
                        "intent": result.get("intent"),
                        "intent_confidence": result.get("intent_confidence"),
                        "validation": result.get("validation"),
                        "rag_documents": result.get("rag_documents", [])
                    }
                })
            else:
                activity_placeholder.empty()
                error = result.get("error", "Unknown error") if result else "Connection failed"
                st.error(f"❌ {error}")
    
    # Footer
    st.markdown("---")
    st.caption("Built with ❤️ using Deep Agents, LangGraph, and Azure AI")

# ===========================================
# MAIN ENTRY
# ===========================================
def main():
    if st.session_state.authenticated:
        show_main_app()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
