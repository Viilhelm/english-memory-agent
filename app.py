import os
import json
import asyncio
import uuid
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up page config
st.set_page_config(
    page_title="English Memory Agent Dashboard",
    page_icon="🧠",
    layout="wide"
)

# Imports from our modules
from english_memory_agent.tools import (
    init_db,
    privacy_scan,
    save_card,
    search_cards,
    list_recent_cards,
    delete_card,
    generate_review_quiz_from_cards
)

# Initialize database at app startup
init_db()

# Try to import ADK agent. If key is missing or libraries fail, we fail gracefully.
agent_ready = False
agent_error = None
try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.events import RequestInput
    from google.genai import types
    from english_memory_agent.agent import root_agent
    agent_ready = True
except Exception as e:
    agent_error = str(e)

# Initialize Session State
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "original_text" not in st.session_state:
    st.session_state.original_text = ""
if "privacy_results" not in st.session_state:
    st.session_state.privacy_results = None
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "invocation_id" not in st.session_state:
    st.session_state.invocation_id = None
if "approval_requested" not in st.session_state:
    st.session_state.approval_requested = False
if "workflow_message" not in st.session_state:
    st.session_state.workflow_message = None

# Initialize runner session service globally in session state
if agent_ready and "runner" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()
    st.session_state.runner = Runner(
        agent=root_agent,
        app_name="english_memory_agent",
        session_service=st.session_state.session_service
    )

# Inject custom CSS styles for bento card and SaaS look
css_styles = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background-color: #F8FAFC !important;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

div[data-testid="stTabBar"] {
    border-bottom: 2px solid #E2E8F0;
    margin-bottom: 20px;
}
button[data-baseweb="tab"] {
    font-weight: 500;
    color: #475569;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #4F46E5 !important;
    border-bottom-color: #4F46E5 !important;
}

.bento-card {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.025);
    margin-bottom: 1.5rem;
}

.bento-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 1rem;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.bento-content {
    color: #334155;
    line-height: 1.6;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 6px;
    background-color: #EEF2FF;
    color: #4F46E5;
    margin-right: 0.5rem;
    border: 1px solid #E0E7FF;
}

.badge-sec {
    background-color: #F0FDFA;
    color: #0D9488;
    border: 1px solid #CCFBF1;
}

.badge-orange {
    background-color: #FFFBEB;
    color: #D97706;
    border: 1px solid #FEF3C7;
}

.badge-gray {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

.status-bar-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 1.5rem 0;
    padding: 1rem;
    background-color: #FFFFFF;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
}
.status-step {
    display: flex;
    align-items: center;
    font-size: 0.85rem;
    font-weight: 500;
    color: #94A3B8;
}
.status-step.active {
    color: #4F46E5;
}
.status-step.completed {
    color: #10B981;
}
.status-arrow {
    color: #CBD5E1;
    margin: 0 0.5rem;
}

.hero-container {
    background: linear-gradient(135deg, #EEF2FF 0%, #F8FAFC 100%);
    border-radius: 12px;
    padding: 2rem;
    border: 1px solid #E2E8F0;
    margin-bottom: 2rem;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.5rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #475569;
    margin-bottom: 1.5rem;
}

.hitl-banner {
    background-color: #EEF2FF;
    border: 1.5px solid #C7D2FE;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.hitl-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #3730A3;
    margin-bottom: 0.5rem;
}
.hitl-body {
    font-size: 0.95rem;
    color: #4F46E5;
    margin-bottom: 1rem;
}

.corrected-box {
    background-color: #ECFDF5;
    border-left: 4px solid #10B981;
    padding: 1rem;
    border-radius: 4px;
    font-size: 1.1rem;
    font-weight: 600;
    color: #065F46;
    margin-bottom: 1rem;
}

.original-box {
    background-color: #F8FAFC;
    border-left: 4px solid #94A3B8;
    padding: 1rem;
    border-radius: 4px;
    font-size: 1rem;
    color: #334155;
    margin-bottom: 1rem;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

# Sidebar Check
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 1.5rem;">
    <span style="font-size: 3rem;">🧠</span>
    <h2 style="margin-top: 0.5rem; margin-bottom: 0; color: #0F172A;">Memory Agent</h2>
    <span style="font-size: 0.85rem; color: #64748B;">English Learning Concierge</span>
</div>
""", unsafe_allow_html=True)

use_enterprise = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").lower() == "true"
if use_enterprise:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip('"\'')
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    if not project_id or not location:
        st.sidebar.warning("⚠️ Configuration Incomplete\nGOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION is missing in enterprise mode.")
    elif not agent_ready:
        st.sidebar.error(f"⚠️ Initialization Error\nError initializing Google ADK: {agent_error}")
    else:
        st.sidebar.success("💼 Mode: Vertex AI Enterprise")
else:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        st.sidebar.warning("⚠️ Configuration Incomplete\nGOOGLE_API_KEY is not set. Please check `.env`.")
    elif not agent_ready:
        st.sidebar.error(f"⚠️ Initialization Error\nError initializing Google ADK: {agent_error}")
    else:
        st.sidebar.success("🤖 Mode: Gemini Developer API")


# Privacy Reminder
st.sidebar.markdown("""
---
**🔒 Privacy Safeguard:**
All inputs are scanned for sensitive info (PII) like phone numbers, emails, passwords, and ID numbers before saving to database.
""")

# Demo Input Examples
st.sidebar.markdown("### 💡 Try These Examples:")
examples = [
    "I very like table tennis.",
    "I am interesting in learning Swedish.",
    "I enjoy the sense of accomplishment after exercising.",
    "I was wondering if you could help me with this."
]
for ex in examples:
    st.sidebar.code(ex, language="text")

# Header/Hero Section
hero_html = """
<div class="hero-container">
    <div class="hero-title">🧠 English Memory Agent</div>
    <div class="hero-subtitle">Correct, rewrite, save, and review your personal English expressions.</div>
    <div>
        <span class="badge">ADK 2.0</span>
        <span class="badge badge-sec">Human-in-the-Loop</span>
        <span class="badge badge-orange">SQLite Database</span>
        <span class="badge badge-gray">MCP Server</span>
        <span class="badge">Privacy Scan</span>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# Streamlit Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "✍️ Analyze English", 
    "🔍 Search Memory", 
    "🎯 Review Quiz", 
    "📋 Recent Cards"
])


# ------------------ Helper functions for ADK running ------------------
def safe_str(value):
    return "" if value is None else str(value)

def render_workflow_status():
    if st.session_state.approval_requested:
        stage = "approval"
    elif st.session_state.workflow_message:
        if "saved" in st.session_state.workflow_message.lower() or "success" in st.session_state.workflow_message.lower():
            stage = "completed"
        else:
            stage = "skipped"
    else:
        stage = "idle"

    stages = [
        ("Input", "📝"),
        ("Analysis", "🧠"),
        ("Privacy Scan", "🔒"),
        ("Human Approval", "👉"),
        ("Memory Save", "💾")
    ]
    
    html = '<div class="status-bar-container">'
    for i, (name, icon) in enumerate(stages):
        step_class = "status-step"
        if stage == "idle":
            if i == 0:
                step_class += " active"
        elif stage == "approval":
            if i < 3:
                step_class += " completed"
            elif i == 3:
                step_class += " active"
        elif stage == "completed":
            step_class += " completed"
        elif stage == "skipped":
            if i < 4:
                step_class += " completed"
            else:
                step_class += " active"
                
        status_icon = "⚪"
        if "completed" in step_class:
            status_icon = "🟢"
        elif "active" in step_class:
            status_icon = "🔵"
            
        if i == 4 and stage == "skipped":
            status_icon = "⚪"
            
        html += f'<div class="{step_class}">{icon} {name} {status_icon}</div>'
        if i < len(stages) - 1:
            html += '<div class="status-arrow">──►</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


async def _iter_workflow_events(events_iter, allow_hitl: bool):
    import logging
    try:
        timeout_s = float(os.environ.get("EMA_WORKFLOW_TIMEOUT", "120"))
        async with asyncio.timeout(timeout_s):
            async for event in events_iter:
                # Debug logging for each event
                author = getattr(event, "author", None)
                evt_content = getattr(event, "content", None)
                parts = None
                if evt_content and hasattr(evt_content, "parts"):
                    parts = evt_content.parts
                actions = getattr(event, "actions", None)
                evt_state_delta = getattr(event, "state_delta", None)
                is_final = getattr(event, "is_final_response", None)
                is_final_val = is_final() if callable(is_final) else False
                
                debug_msg = f"[DEBUG EVENT] type={type(event).__name__}, author={author}, content={evt_content}, parts={parts}, actions={actions}, state_delta={evt_state_delta}, is_final={is_final_val}"
                if os.environ.get("EMA_DEBUG_EVENTS") == "1":
                    print(debug_msg)
                else:
                    logging.debug(debug_msg)
                
                if allow_hitl:
                    # Check for function_call in parts first (HITL)
                    has_hitl = False
                    hitl_payload = None
                    hitl_message = ""
                    
                    if evt_content and hasattr(evt_content, "parts") and evt_content.parts:
                        for part in evt_content.parts:
                            if hasattr(part, "function_call") and part.function_call:
                                fn_call = part.function_call
                                fn_name = getattr(fn_call, "name", "")
                                if fn_name in ("adk_request_input", "adk_request_confirmation", "request_approval_node"):
                                    args = getattr(fn_call, "args", {})
                                    args_dict = dict(args) if hasattr(args, "items") else {}
                                    
                                    hitl_message = args_dict.get("message", "Human approval requested")
                                    payload_raw = args_dict.get("payload", {})
                                    hitl_payload = payload_raw
                                    if isinstance(payload_raw, str):
                                        try:
                                            hitl_payload = json.loads(payload_raw)
                                        except Exception:
                                            pass
                                    has_hitl = True
                                    break
                                    
                    if has_hitl:
                        return {
                            "status": "paused",
                            "payload": hitl_payload,
                            "message": hitl_message
                        }
                    
                    # Check if event is RequestInput (pauses for HITL)
                    if isinstance(event, RequestInput):
                        payload_raw = getattr(event, "payload", {})
                        hitl_payload = payload_raw
                        if isinstance(payload_raw, str):
                            try:
                                hitl_payload = json.loads(payload_raw)
                            except Exception:
                                pass
                        return {
                            "status": "paused",
                            "payload": hitl_payload,
                            "message": getattr(event, "message", "Human approval requested")
                        }
                    
                # Check if event is final response
                if hasattr(event, "is_final_response") and event.is_final_response():
                    if author not in {"router_agent", "correction_agent", "rewrite_agent", "explanation_agent", "organizer_agent"}:
                        text_val = ""
                        if evt_content and hasattr(evt_content, "parts") and evt_content.parts:
                            text_val = safe_str(evt_content.parts[0].text)
                        if safe_str(text_val).strip():
                            return {
                                "status": "completed",
                                "message": text_val
                            }
    except asyncio.TimeoutError:
        print(f"[DEBUG] Workflow execution timed out after {timeout_s} seconds.")
        return {"status": "error", "message": f"Workflow execution timed out after {timeout_s} seconds."}
            
    return {"status": "no_event", "message": "Workflow finished without response."}

async def run_analysis_async(text: str, invocation_id: str):
    runner = st.session_state.runner
    session_service = st.session_state.session_service
    
    # Initialize the session
    try:
        await session_service.create_session(
            app_name="english_memory_agent",
            user_id="local_user",
            session_id="session_analysis"
        )
    except Exception:
        pass  # Session already exists
        
    content = types.Content(role='user', parts=[types.Part(text=text)])
    state_delta = {
        "intent": "analyze_new_english_input",
        "english_input": text,
        "search_query": "",
        "approved": False
    }
    events = runner.run_async(
        user_id="local_user",
        session_id="session_analysis",
        invocation_id=invocation_id,
        new_message=content,
        state_delta=state_delta
    )
    return await _iter_workflow_events(events, allow_hitl=True)

def run_analysis(text: str, invocation_id: str):
    try:
        return asyncio.run(run_analysis_async(text, invocation_id))
    except Exception as e:
        return {"status": "error", "message": str(e)}

def persist_card_from_analysis(analysis: dict, original_text: str) -> dict:
    """Save a card to the DB directly from the HITL analysis result.

    We bypass ADK's workflow resume here: across Streamlit reruns each
    asyncio.run() spins up a fresh event loop, and ADK's paused-invocation
    state is bound to the loop that produced it — so resuming fails silently
    and nothing gets persisted. The analysis payload already contains
    everything the DB needs; write it straight through.
    """
    card_payload = dict(analysis or {})
    card_payload["original_input"] = original_text
    tags_val = card_payload.get("tags")
    if isinstance(tags_val, list):
        card_payload["tags"] = ", ".join(safe_str(t) for t in tags_val)
    return save_card(card_payload)


# ------------------ Tab 1: Analyze English ------------------
with tab1:
    st.subheader("✍️ Analyze New English Input")
    st.write("Enter an English sentence. The ADK 2.0 Graph Workflow will verify privacy, correct errors, translate explanation to Chinese, and present a card preview for your approval before saving.")
    
    # Render progress bar
    render_workflow_status()
    
    user_input = st.text_area(
        "Enter English Sentence:", 
        height=80, 
        placeholder="e.g. He go to school yesterday and meet his friend...",
        key="user_input_field"
    )
    
    if st.button("Run AI Analysis", key="btn_analyze", use_container_width=True):
        if not use_enterprise and not api_key:
            st.error("Missing GOOGLE_API_KEY in environment or .env file.")
        elif use_enterprise and (not os.environ.get("GOOGLE_CLOUD_PROJECT") or not os.environ.get("GOOGLE_CLOUD_LOCATION")):
            st.error("Missing GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION in enterprise mode.")
        elif not agent_ready:
            st.error(f"Agent failed to initialize. Error details: {agent_error}")
        elif not user_input.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Executing ADK 2.0 Workflow..."):
                # Clear old state
                st.session_state.analysis_result = None
                st.session_state.privacy_results = None
                st.session_state.approval_requested = False
                st.session_state.workflow_message = None
                
                # Start new invocation
                inv_id = f"inv-{str(uuid.uuid4())[:8]}"
                st.session_state.invocation_id = inv_id
                st.session_state.original_text = user_input
                
                # Run the workflow
                res = run_analysis(user_input, inv_id)
                
                if res.get("status") == "paused":
                    st.session_state.analysis_result = res.get("payload")
                    st.session_state.privacy_results = privacy_scan(user_input)
                    st.session_state.approval_requested = True
                elif res.get("status") == "completed":
                    st.session_state.workflow_message = res.get("message")
                    st.session_state.privacy_results = privacy_scan(user_input)
                elif res.get("status") == "error":
                    st.error(f"Workflow execution error: {res.get('message')}")
                    
    # Display results if available
    if st.session_state.analysis_result or st.session_state.workflow_message:
        p_res = st.session_state.privacy_results
        
        st.markdown("### 📊 Analysis Results")
        
        if st.session_state.workflow_message:
            st.markdown(f'<div class="bento-card" style="border-left: 4px solid #10B981; background-color: #ECFDF5;"><div class="bento-content" style="color: #065F46; font-weight: 500;">{st.session_state.workflow_message}</div></div>', unsafe_allow_html=True)
            
        if st.session_state.analysis_result:
            res = st.session_state.analysis_result
            card_type = safe_str(res.get("card_type", "expression_card"))
            card_type_display = card_type.replace('_', ' ').title()
            
            # Bento Grid
            col1, col2 = st.columns(2)
            
            with col1:
                # 1. Metadata Card
                details_html = f"""
                <div class="bento-card">
                    <div class="bento-header">📊 Card Metadata</div>
                    <div class="bento-content">
                        <p><strong>Card Type:</strong> <span class="badge">{card_type_display}</span></p>
                """
                if card_type == "error_card":
                    err_type = res.get('error_type')
                    if err_type:
                        details_html += f'<p><strong>Error Type:</strong> <span class="badge badge-orange">{err_type}</span></p>'
                elif card_type == "word_card":
                    pos = res.get('part_of_speech')
                    if pos:
                        details_html += f'<p><strong>Part of Speech:</strong> <span class="badge badge-sec">{pos}</span></p>'
                    definition = res.get('definition')
                    if definition:
                        details_html += f'<p><strong>Definition:</strong> {safe_str(definition)}</p>'
                elif card_type == "expression_card":
                    key_expr = res.get('key_expression')
                    if key_expr:
                        details_html += f'<p><strong>Key Expression:</strong> <code>{safe_str(key_expr)}</code></p>'
                        
                details_html += f'<p><strong>Scenario:</strong> {safe_str(res.get("scenario"))}</p>'
                
                tags_val = res.get("tags")
                if isinstance(tags_val, list):
                    tags_str = ", ".join(safe_str(t) for t in tags_val)
                else:
                    tags_str = safe_str(tags_val)
                if tags_str:
                    details_html += f'<p><strong>Tags:</strong> {", ".join([f"<span class=\"badge badge-gray\">{t.strip()}</span>" for t in tags_str.split(",") if t.strip()])}</p>'
                    
                details_html += """
                    </div>
                </div>
                """
                st.markdown(details_html, unsafe_allow_html=True)
                
                # 2. Input/Correction Card
                if card_type == "error_card":
                    corrected = res.get('corrected_version') or "No correction needed"
                    correction_html = f"""
                    <div class="bento-card">
                        <div class="bento-header">🔧 Correction</div>
                        <div class="bento-content">
                            <p style="margin-bottom: 0.5rem; font-size: 0.9rem; color: #64748B;">Original Input:</p>
                            <div class="original-box">{safe_str(st.session_state.original_text)}</div>
                            <p style="margin-bottom: 0.5rem; font-size: 0.9rem; color: #64748B;">Corrected Version:</p>
                            <div class="corrected-box">{safe_str(corrected)}</div>
                        </div>
                    </div>
                    """
                else:
                    correction_html = f"""
                    <div class="bento-card">
                        <div class="bento-header">📝 Input Expression</div>
                        <div class="bento-content">
                            <div class="original-box" style="border-left-color: #4F46E5; font-size: 1.1rem; font-weight: 500;">{safe_str(st.session_state.original_text)}</div>
                        </div>
                    </div>
                    """
                st.markdown(correction_html, unsafe_allow_html=True)
                
                # 3. Chinese Explanation Card
                explanation = res.get("chinese_explanation") or "无解析内容。"
                explanation_html = f"""
                <div class="bento-card">
                    <div class="bento-header">💡 Chinese Explanation / 中文解析</div>
                    <div class="bento-content" style="font-size: 1rem; border-left: 4px solid #0D9488; padding-left: 1rem; background-color: #F0FDFA; border-radius: 4px; padding-top: 0.75rem; padding-bottom: 0.75rem;">
                        {explanation}
                    </div>
                </div>
                """
                st.markdown(explanation_html, unsafe_allow_html=True)
                
            with col2:
                # 4. Rewrites Card
                natural = safe_str(res.get('natural_version'))
                formal = safe_str(res.get('formal_version'))
                header_text = "Example Sentences" if card_type in ("word_card", "expression_card") else "Alternative Rewrites"

                rewrites_html = f"""
                <div class="bento-card">
                    <div class="bento-header">✨ {header_text}</div>
                    <div class="bento-content">
                        <div style="margin-bottom: 1rem;">
                            <span style="font-size: 0.85rem; font-weight: 600; color: #0D9488; display: block;">🗣️ NATURAL (CONVERSATIONAL)</span>
                            <span style="font-size: 1.05rem; color: #0F172A; font-weight: 500;">{natural}</span>
                        </div>
                        <div>
                            <span style="font-size: 0.85rem; font-weight: 600; color: #D97706; display: block;">💼 FORMAL (PROFESSIONAL)</span>
                            <span style="font-size: 1.05rem; color: #0F172A; font-weight: 500;">{formal}</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(rewrites_html, unsafe_allow_html=True)
                
                # 5. Privacy Results Card
                if p_res:
                    safe = p_res["safe_to_save"]
                    status_text = "Safe (No sensitive data detected)" if safe else "Sensitive information flagged!"
                    status_color = "#10B981" if safe else "#EF4444"
                    bg_color = "#ECFDF5" if safe else "#FEF2F2"
                    border_color = "#A7F3D0" if safe else "#FCA5A5"
                    text_color = "#065F46" if safe else "#991B1B"
                    
                    risks_html = ""
                    if not safe:
                        risks_html = "<ul>"
                        for r in p_res["risks"]:
                            risks_html += f"<li>{r}</li>"
                        risks_html += "</ul>"
                        
                    privacy_html = f"""
                    <div class="bento-card">
                        <div class="bento-header">🔒 Privacy Scan</div>
                        <div class="bento-content">
                            <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 0.75rem; color: {text_color}; font-weight: 500; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.2rem;">{"✓" if safe else "⚠"}</span> {status_text}
                            </div>
                            {risks_html}
                        </div>
                    </div>
                    """
                    st.markdown(privacy_html, unsafe_allow_html=True)
                    
                # 6. JSON Card Preview
                st.markdown('<div class="bento-card" style="margin-bottom: 0.5rem;"><div class="bento-header">💾 Memory Card JSON Preview</div></div>', unsafe_allow_html=True)
                st.json(res)
                
            # 2. HITL Approval Step
            st.markdown("---")
            if st.session_state.approval_requested:
                banner_html = """
                <div class="hitl-banner">
                    <div class="hitl-title">👉 Human-in-the-Loop Confirmation Required</div>
                    <div class="hitl-body">Do you want to save this generated memory card to your personal database? You can inspect the results above before confirming.</div>
                </div>
                """
                st.markdown(banner_html, unsafe_allow_html=True)
                
                col_yes, col_no = st.columns([1, 1])
                with col_yes:
                    if st.button("Confirm Save 💾", key="btn_confirm_yes", use_container_width=True):
                        with st.spinner("Saving card..."):
                            save_res = persist_card_from_analysis(
                                st.session_state.analysis_result,
                                st.session_state.original_text,
                            )
                        if save_res.get("status") == "success":
                            st.session_state.workflow_message = (
                                f"✅ Card saved successfully! ID: {save_res.get('card_id')}"
                            )
                        else:
                            st.session_state.workflow_message = (
                                f"❌ Failed to save card: {save_res.get('message')}"
                            )
                        st.session_state.analysis_result = None
                        st.session_state.approval_requested = False
                        st.rerun()
                with col_no:
                    if st.button("Discard Card 🗑️", key="btn_confirm_no", use_container_width=True):
                        st.session_state.workflow_message = "Saving skipped by user."
                        st.session_state.analysis_result = None
                        st.session_state.approval_requested = False
                        st.rerun()


# ------------------ Tab 2: Search Memory ------------------
with tab2:
    st.subheader("🔍 Search Memory Database")
    st.write("Find saved expressions and errors by typing keywords in English or Chinese, tags, scenarios, or error types.")
    
    search_query = st.text_input("Enter Search Term:", placeholder="e.g. bullet, Tense, business...")
    
    if search_query:
        results = search_cards(search_query)
    else:
        results = list_recent_cards(limit=20)
        
    st.write(f"Showing {len(results)} matching cards.")
    
    for c in results:
        raw_ctype = c.get("card_type", "expression_card")
        ctype = raw_ctype.replace('_', ' ').title()
        orig = safe_str(c.get("original_input"))
        c_id = c.get("id")
        
        with st.container(border=True):
            col_type, col_date = st.columns([3, 1])
            with col_type:
                st.markdown(f"### 🏷️ ID {c_id} — **{ctype}**")
            with col_date:
                st.markdown(f"<span style='color: #64748B; font-size: 0.85rem; float: right;'>📅 {c.get('created_at')}</span>", unsafe_allow_html=True)
                
            st.markdown(f"**Original Input / 输入原句:**")
            st.info(orig)
            
            if raw_ctype == "error_card":
                corrected = c.get('corrected_version')
                if corrected:
                    st.markdown(f"**Corrected Version / 修改后:** :green[**{corrected}**]")
                err_type = c.get('error_type')
                if err_type:
                    st.markdown(f"**Error Type / 错误类型:** `<span class='badge badge-orange'>{err_type}</span>`", unsafe_allow_html=True)
            elif raw_ctype == "word_card":
                key_expr = c.get('key_expression') or orig
                st.markdown(f"**Word / 单词:** `**{key_expr}**`")
                pos = c.get('part_of_speech')
                if pos:
                    st.markdown(f"**Part of Speech / 词性:** `{pos}`")
                definition = c.get('definition')
                if definition:
                    st.markdown(f"**English Definition / 英文释义:** *{definition}*")
            else:
                key_expr = c.get('key_expression')
                if key_expr:
                    st.markdown(f"**Key Expression / 核心表达:** `**{key_expr}**`")
                    
            st.markdown(f"**Chinese Explanation / 中文解析:**")
            st.markdown(f"<div style='border-left: 4px solid #0D9488; padding-left: 1rem; color: #134E4A; background-color: #F0FDFA; padding-top: 0.5rem; padding-bottom: 0.5rem; border-radius: 4px;'>{c.get('chinese_explanation')}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_rew1, col_rew2 = st.columns(2)
            with col_rew1:
                st.markdown(f"🗣️ **Natural (Conversational):**\n{c.get('natural_version')}")
            with col_rew2:
                st.markdown(f"💼 **Formal (Professional):**\n{c.get('formal_version')}")
                
            st.markdown(f"**Scenario / 场景:** `{c.get('scenario')}` | **Tags / 标签:** `{c.get('tags')}`")


# ------------------ Tab 3: Review Quiz ------------------
with tab3:
    st.subheader("🎯 English Memory Review Quiz")
    st.write("Generate interactive quizzes from recently saved memory cards to test your knowledge.")
    
    quiz_limit = st.slider("Number of quiz questions:", min_value=1, max_value=10, value=3)
    
    if st.button("Generate Quiz", key="btn_gen_quiz", use_container_width=True):
        recent = list_recent_cards(limit=50)
        if not recent:
            st.warning("No cards found in the database. Please add cards in the 'Analyze English' tab first!")
            st.session_state.quiz_questions = []
        else:
            quiz_data = generate_review_quiz_from_cards(recent)
            st.session_state.quiz_questions = quiz_data.get("questions", [])[:quiz_limit]
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()
            
    if st.session_state.quiz_questions:
        st.write("---")
        for i, q in enumerate(st.session_state.quiz_questions):
            with st.container(border=True):
                st.markdown(f"### 📝 Question {i+1} <span style='font-size: 0.9rem; color: #64748B;'>({q['question_type'].replace('_', ' ').title()})</span>", unsafe_allow_html=True)
                st.markdown(f"**Question:** {q['question_text']}")
                
                if q.get("options"):
                    st.markdown("**Options:**")
                    for opt in q["options"]:
                        st.markdown(f"- {opt}")
                
                ans_key = f"q_{q['card_id']}_{i}"
                st.session_state.quiz_answers[ans_key] = st.text_input(
                    "Your Answer:",
                    key=ans_key,
                    placeholder="Type your answer (or letter choice A/B/C)..."
                )
                st.write("")
            
        if st.button("Submit Answers", key="btn_submit_answers", use_container_width=True):
            st.session_state.quiz_submitted = True
            st.rerun()
            
        if st.session_state.quiz_submitted:
            st.markdown("### 📊 Quiz Results & Feedback")
            for i, q in enumerate(st.session_state.quiz_questions):
                with st.container(border=True):
                    st.markdown(f"#### Question {i+1} Review")
                    ans_key = f"q_{q['card_id']}_{i}"
                    user_ans = st.session_state.quiz_answers.get(ans_key, "")
                    
                    is_correct = user_ans.strip().lower() == q['correct_answer'].strip().lower()
                    
                    if is_correct:
                        st.success("🎉 Correct!")
                    else:
                        st.error("❌ Needs practice")
                        
                    st.write(f"**Your Answer:** `{user_ans}`")
                    st.write(f"**Reference Answer:** :green[`{q['correct_answer']}`]")
                    st.markdown(f"**Explanations/Context:**\n{q['explanation']}")


# ------------------ Tab 4: Recent Cards ------------------
with tab4:
    st.subheader("📋 Recent Saved Cards")
    st.write("Review recently saved memory cards or delete entries by ID.")
    
    recent_list = list_recent_cards(limit=10)
    
    if not recent_list:
        st.info("No saved cards found.")
    else:
        for c in recent_list:
            c_id = c.get("id")
            c_type = c.get("card_type", "").replace('_', ' ').title()
            orig = c.get("original_input", "")
            
            with st.container(border=True):
                col_info, col_action = st.columns([6, 1])
                with col_info:
                    st.markdown(f"**ID {c_id}** | **[{c_type}]** : `{orig[:120]}...`")
                with col_action:
                    if st.button("Delete 🗑️", key=f"btn_del_recent_{c_id}", use_container_width=True):
                        del_res = delete_card(c_id)
                        if del_res["status"] == "success":
                            st.success("Deleted!")
                            st.rerun()
                        else:
                            st.error(del_res["message"])
