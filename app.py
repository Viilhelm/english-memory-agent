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

# Design system: Minimalism & Swiss Style (generated via ui-ux-pro-max)
# Tokens: neutral slate structure, single blue accent, semantic green/red/amber,
# Inter typography, 8px spacing rhythm, 1px borders over shadows.
css_styles = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --color-primary: #475569;
    --color-secondary: #64748B;
    --color-accent: #2563EB;
    --color-background: #F8FAFC;
    --color-surface: #FFFFFF;
    --color-foreground: #1E293B;
    --color-muted: #EAEFF3;
    --color-border: #E2E8F0;
    --color-success: #059669;
    --color-success-bg: #ECFDF5;
    --color-destructive: #DC2626;
    --color-destructive-bg: #FEF2F2;
    --radius: 8px;
    --radius-sm: 6px;
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--color-background) !important;
    color: var(--color-foreground);
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--color-foreground) !important;
    letter-spacing: -0.01em;
}

[data-testid="stSidebar"] {
    background-color: var(--color-surface) !important;
    border-right: 1px solid var(--color-border) !important;
}

div[data-testid="stTabBar"] {
    border-bottom: 1px solid var(--color-border);
    margin-bottom: 24px;
}
button[data-baseweb="tab"] {
    font-weight: 500;
    color: var(--color-secondary);
}
button[data-baseweb="tab"]:hover {
    color: var(--color-foreground);
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--color-accent) !important;
    border-bottom-color: var(--color-accent) !important;
    font-weight: 600;
}

.stButton button {
    border-radius: var(--radius-sm);
    font-weight: 500;
    transition: background-color 200ms ease, border-color 200ms ease, color 200ms ease;
}

.bento-card {
    background-color: var(--color-surface);
    border-radius: var(--radius);
    padding: 24px;
    border: 1px solid var(--color-border);
    margin-bottom: 16px;
}

.bento-header {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 16px;
}

.bento-content {
    color: var(--color-foreground);
    line-height: 1.6;
}

.kicker {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--color-secondary);
    display: block;
    margin-bottom: 4px;
}

.badge {
    display: inline-block;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 999px;
    background-color: #EFF6FF;
    color: var(--color-accent);
    margin-right: 8px;
    border: 1px solid #DBEAFE;
}

.badge-sec {
    background-color: var(--color-success-bg);
    color: var(--color-success);
    border: 1px solid #A7F3D0;
}

.badge-orange {
    background-color: #FFFBEB;
    color: #B45309;
    border: 1px solid #FDE68A;
}

.badge-gray {
    background-color: #F1F5F9;
    color: var(--color-primary);
    border: 1px solid var(--color-border);
}

.app-header {
    padding: 8px 0 24px 0;
    border-bottom: 1px solid var(--color-border);
    margin-bottom: 8px;
}
.app-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-foreground);
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.app-subtitle {
    font-size: 1rem;
    color: var(--color-secondary);
    margin-bottom: 16px;
}

.hitl-banner {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-left: 3px solid var(--color-accent);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-top: 8px;
    margin-bottom: 16px;
}
.hitl-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin-bottom: 4px;
}
.hitl-body {
    font-size: 0.9rem;
    color: var(--color-secondary);
}

.corrected-box {
    background-color: var(--color-success-bg);
    border-left: 3px solid var(--color-success);
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    font-size: 1.05rem;
    font-weight: 600;
    color: #065F46;
    margin-bottom: 16px;
}

.original-box {
    background-color: var(--color-background);
    border-left: 3px solid #CBD5E1;
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    font-size: 1rem;
    color: var(--color-foreground);
    margin-bottom: 16px;
}

.explanation-box {
    background-color: var(--color-muted);
    border-radius: var(--radius-sm);
    padding: 16px;
    color: var(--color-foreground);
    line-height: 1.7;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

# Sidebar Check
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
    <div style="width: 40px; height: 40px; border-radius: 8px; background-color: #2563EB; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
    </div>
    <div>
        <div style="font-size: 1rem; font-weight: 700; color: #1E293B; letter-spacing: -0.01em;">Memory Agent</div>
        <div style="font-size: 0.78rem; color: #64748B;">English learning companion</div>
    </div>
</div>
""", unsafe_allow_html=True)

use_enterprise = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").lower() == "true"
if use_enterprise:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip('"\'')
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    if not project_id or not location:
        st.sidebar.warning("Configuration incomplete: GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION is missing in enterprise mode.")
    elif not agent_ready:
        st.sidebar.error(f"Initialization error: {agent_error}")
    else:
        st.sidebar.success("✓ AI service connected")
else:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        st.sidebar.warning("Configuration incomplete: GOOGLE_API_KEY is not set. Please check `.env`.")
    elif not agent_ready:
        st.sidebar.error(f"Initialization error: {agent_error}")
    else:
        st.sidebar.success("✓ AI service connected")


# Privacy Reminder
st.sidebar.markdown("""
---
**Privacy safeguard**

All inputs are scanned for sensitive info (phone numbers, emails, passwords, ID numbers) before anything is saved.
""")

# Demo Input Examples
st.sidebar.markdown("**Try an example**")
examples = [
    "I very like table tennis.",
    "I am interesting in learning Swedish.",
    "I enjoy the sense of accomplishment after exercising.",
    "I was wondering if you could help me with this."
]
for ex in examples:
    st.sidebar.code(ex, language="text")

# Header Section
hero_html = """
<div class="app-header">
    <div class="app-title">English Memory Agent</div>
    <div class="app-subtitle">Correct, rewrite, save, and review your personal English expressions.</div>
    <div>
        <span class="badge badge-gray">Grammar Correction</span>
        <span class="badge badge-gray">Natural Rewrites</span>
        <span class="badge badge-gray">中文解析</span>
        <span class="badge badge-gray">Memory Cards</span>
        <span class="badge badge-gray">Review Quiz</span>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# Streamlit Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Analyze",
    "Search Memory",
    "Review Quiz",
    "Recent Cards"
])


# ------------------ Helper functions for ADK running ------------------
def safe_str(value):
    return "" if value is None else str(value)

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
    st.subheader("Analyze English input")
    st.write("Enter an English sentence or word. It will be checked and corrected, rewritten in natural and formal styles, and explained in Chinese — then you decide whether to save it as a memory card.")

    user_input = st.text_area(
        "English sentence or word",
        height=80,
        placeholder="e.g. He go to school yesterday and meet his friend...",
        key="user_input_field"
    )

    if st.button("Analyze", key="btn_analyze", type="primary", use_container_width=True):
        if not use_enterprise and not api_key:
            st.error("Missing GOOGLE_API_KEY in environment or .env file.")
        elif use_enterprise and (not os.environ.get("GOOGLE_CLOUD_PROJECT") or not os.environ.get("GOOGLE_CLOUD_LOCATION")):
            st.error("Missing GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION in enterprise mode.")
        elif not agent_ready:
            st.error(f"Agent failed to initialize. Error details: {agent_error}")
        elif not user_input.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Analyzing your English..."):
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
                    st.error(f"Analysis failed: {res.get('message')}")
                    
    # Display results if available
    if st.session_state.analysis_result or st.session_state.workflow_message:
        p_res = st.session_state.privacy_results
        
        st.markdown("### Analysis results")
        
        if st.session_state.workflow_message:
            msg = st.session_state.workflow_message
            if "saved successfully" in msg.lower():
                st.success(msg)
            elif msg.lower().startswith("failed"):
                st.error(msg)
            else:
                st.info(msg)
            
        if st.session_state.analysis_result:
            res = st.session_state.analysis_result
            card_type = safe_str(res.get("card_type", "expression_card"))
            card_type_display = card_type.replace('_', ' ').title()
            
            # Layout: core learning content first (left), examples + metadata (right),
            # long-form explanation full width, privacy folded into the save decision.
            col1, col2 = st.columns(2)

            with col1:
                # 1. Main result: correction contrast, or the expression being learned
                if card_type == "error_card":
                    corrected = res.get('corrected_version') or "No correction needed"
                    err_type = res.get('error_type')
                    err_html = f'<p style="margin-top: 12px; margin-bottom: 0;"><strong>Error type:</strong> <span class="badge badge-orange">{err_type}</span></p>' if err_type else ""
                    main_html = f"""
                    <div class="bento-card">
                        <div class="bento-header">Correction</div>
                        <div class="bento-content">
                            <span class="kicker">Original input</span>
                            <div class="original-box">{safe_str(st.session_state.original_text)}</div>
                            <span class="kicker">Corrected version</span>
                            <div class="corrected-box">{safe_str(corrected)}</div>{err_html}
                        </div>
                    </div>
                    """
                else:
                    key_expr = safe_str(res.get('key_expression'))
                    pos_html = ""
                    if card_type == "word_card":
                        pos = res.get('part_of_speech')
                        if pos:
                            pos_html = f'<span class="badge badge-sec">{pos}</span>'
                    definition = safe_str(res.get('definition'))
                    def_html = f'<p style="margin-top: 12px; margin-bottom: 0; color: #475569;">{definition}</p>' if definition else ""
                    if key_expr:
                        main_header = "Word" if card_type == "word_card" else "Key expression"
                        expr_size = "1.35rem" if len(key_expr) <= 60 else "1.05rem"
                        expr_html = f'<div style="font-size: {expr_size}; font-weight: 600; color: #1E293B; margin-bottom: 8px;">{key_expr}</div>'
                    else:
                        # No key expression extracted (e.g. rewrite cards): anchor the
                        # rewrites on the right by showing the sentence they rewrite.
                        main_header = "Your sentence"
                        expr_html = f'<div class="original-box" style="border-left-color: #2563EB; font-size: 1.05rem; font-weight: 500; margin-bottom: 0;">{safe_str(st.session_state.original_text)}</div>'
                    main_html = f"""
                    <div class="bento-card">
                        <div class="bento-header">{main_header}</div>
                        <div class="bento-content">{expr_html}{pos_html}{def_html}</div>
                    </div>
                    """
                st.markdown(main_html, unsafe_allow_html=True)

            with col2:
                # 2. Rewrites / example sentences
                natural = safe_str(res.get('natural_version'))
                formal = safe_str(res.get('formal_version'))
                header_text = "Example sentences" if card_type in ("word_card", "expression_card") else "Alternative rewrites"

                rewrites_html = f"""
                <div class="bento-card">
                    <div class="bento-header">{header_text}</div>
                    <div class="bento-content">
                        <div style="margin-bottom: 16px;">
                            <span class="kicker" style="color: #2563EB;">Natural · Conversational</span>
                            <span style="font-size: 1.05rem; color: #1E293B; font-weight: 500;">{natural}</span>
                        </div>
                        <div>
                            <span class="kicker">Formal · Professional</span>
                            <span style="font-size: 1.05rem; color: #1E293B; font-weight: 500;">{formal}</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(rewrites_html, unsafe_allow_html=True)

                # 3. Compact metadata: type, scenario, tags
                tags_val = res.get("tags")
                if isinstance(tags_val, list):
                    tags_str = ", ".join(safe_str(t) for t in tags_val)
                else:
                    tags_str = safe_str(tags_val)
                tags_html = ""
                if tags_str:
                    chips = " ".join(f'<span class="badge badge-gray">{t.strip()}</span>' for t in tags_str.split(",") if t.strip())
                    tags_html = f'<p style="margin-bottom: 0;"><strong>Tags:</strong> {chips}</p>'
                details_html = f"""
                <div class="bento-card">
                    <div class="bento-header">Card details</div>
                    <div class="bento-content" style="font-size: 0.9rem;">
                        <p><strong>Type:</strong> <span class="badge">{card_type_display}</span></p>
                        <p><strong>Scenario:</strong> {safe_str(res.get("scenario"))}</p>{tags_html}
                    </div>
                </div>
                """
                st.markdown(details_html, unsafe_allow_html=True)

            # 4. Chinese explanation, full width (usually the longest content)
            explanation = res.get("chinese_explanation") or "无解析内容。"
            explanation_html = f"""
            <div class="bento-card">
                <div class="bento-header">中文解析 · Chinese explanation</div>
                <div class="bento-content explanation-box">{explanation}</div>
            </div>
            """
            st.markdown(explanation_html, unsafe_allow_html=True)

            # 5. Save decision, with the privacy scan result folded in as a status line
            st.markdown("---")
            if st.session_state.approval_requested:
                privacy_status_html = ""
                if p_res:
                    if p_res["safe_to_save"]:
                        privacy_status_html = """
                    <div style="margin-top: 12px; background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; padding: 10px 12px; color: #065F46; font-size: 0.85rem; font-weight: 500;"><span style="font-weight: 700;">&#10003;</span> Privacy scan passed — no sensitive data detected</div>"""
                    else:
                        risks_html = "".join(f"<li>{r}</li>" for r in p_res["risks"])
                        privacy_status_html = f"""
                    <div style="margin-top: 12px; background-color: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 6px; padding: 10px 12px; color: #991B1B; font-size: 0.85rem; font-weight: 500;"><span style="font-weight: 700;">!</span> Sensitive information flagged — review before saving<ul style="margin: 8px 0 0 0;">{risks_html}</ul></div>"""
                banner_html = f"""
                <div class="hitl-banner">
                    <div class="hitl-title">Save this memory card?</div>
                    <div class="hitl-body">Review the analysis above, then save this card to your collection — or discard it.</div>{privacy_status_html}
                </div>
                """
                st.markdown(banner_html, unsafe_allow_html=True)
                
                col_yes, col_no = st.columns([1, 1])
                with col_yes:
                    if st.button("Save card", key="btn_confirm_yes", type="primary", use_container_width=True):
                        with st.spinner("Saving card..."):
                            save_res = persist_card_from_analysis(
                                st.session_state.analysis_result,
                                st.session_state.original_text,
                            )
                        if save_res.get("status") == "success":
                            st.session_state.workflow_message = (
                                f"Card saved successfully (ID {save_res.get('card_id')})."
                            )
                        else:
                            st.session_state.workflow_message = (
                                f"Failed to save card: {save_res.get('message')}"
                            )
                        st.session_state.analysis_result = None
                        st.session_state.approval_requested = False
                        st.rerun()
                with col_no:
                    if st.button("Discard", key="btn_confirm_no", use_container_width=True):
                        st.session_state.workflow_message = "Card discarded — nothing was saved."
                        st.session_state.analysis_result = None
                        st.session_state.approval_requested = False
                        st.rerun()

            # 6. Raw card data (developer view, collapsed by default)
            with st.expander("Raw card data (JSON)", expanded=False):
                st.json(res)


# ------------------ Tab 2: Search Memory ------------------
with tab2:
    st.subheader("Search memory")
    st.write("Find saved expressions and errors by typing keywords in English or Chinese, tags, scenarios, or error types.")

    search_query = st.text_input("Search term", placeholder="e.g. bullet, tense, business...")

    if search_query:
        results = search_cards(search_query)
    else:
        results = list_recent_cards(limit=20)

    st.caption(f"{len(results)} matching cards")

    for c in results:
        raw_ctype = c.get("card_type", "expression_card")
        ctype = raw_ctype.replace('_', ' ').title()
        orig = safe_str(c.get("original_input"))
        c_id = c.get("id")

        with st.container(border=True):
            col_type, col_date = st.columns([3, 1])
            with col_type:
                st.markdown(f"<span class='badge'>{ctype}</span> <span style='color: #64748B; font-size: 0.85rem;'>ID {c_id}</span>", unsafe_allow_html=True)
            with col_date:
                st.markdown(f"<span style='color: #64748B; font-size: 0.85rem; float: right;'>{c.get('created_at')}</span>", unsafe_allow_html=True)

            st.markdown(f"<span class='kicker'>Original input · 输入原句</span><div class='original-box'>{orig}</div>", unsafe_allow_html=True)

            if raw_ctype == "error_card":
                corrected = c.get('corrected_version')
                if corrected:
                    st.markdown(f"<span class='kicker'>Corrected · 修改后</span><div class='corrected-box'>{corrected}</div>", unsafe_allow_html=True)
                err_type = c.get('error_type')
                if err_type:
                    st.markdown(f"**Error type / 错误类型:** <span class='badge badge-orange'>{err_type}</span>", unsafe_allow_html=True)
            elif raw_ctype == "word_card":
                key_expr = c.get('key_expression') or orig
                st.markdown(f"**Word / 单词:** `{key_expr}`")
                pos = c.get('part_of_speech')
                if pos:
                    st.markdown(f"**Part of speech / 词性:** {pos}")
                definition = c.get('definition')
                if definition:
                    st.markdown(f"**Definition / 英文释义:** *{definition}*")
            else:
                key_expr = c.get('key_expression')
                if key_expr:
                    st.markdown(f"**Key expression / 核心表达:** `{key_expr}`")

            st.markdown(f"<span class='kicker'>中文解析 · Chinese explanation</span><div class='explanation-box'>{c.get('chinese_explanation')}</div>", unsafe_allow_html=True)
            st.write("")

            col_rew1, col_rew2 = st.columns(2)
            with col_rew1:
                st.markdown(f"<span class='kicker' style='color: #2563EB;'>Natural · Conversational</span>{safe_str(c.get('natural_version'))}", unsafe_allow_html=True)
            with col_rew2:
                st.markdown(f"<span class='kicker'>Formal · Professional</span>{safe_str(c.get('formal_version'))}", unsafe_allow_html=True)

            st.caption(f"Scenario: {c.get('scenario')} · Tags: {c.get('tags')}")


# ------------------ Tab 3: Review Quiz ------------------
with tab3:
    st.subheader("Review quiz")
    st.write("Generate interactive quizzes from recently saved memory cards to test your knowledge.")

    quiz_limit = st.slider("Number of quiz questions", min_value=1, max_value=10, value=3)

    if st.button("Generate quiz", key="btn_gen_quiz", type="primary", use_container_width=True):
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
                st.markdown(f"**Question {i+1}** <span style='font-size: 0.85rem; color: #64748B;'>· {q['question_type'].replace('_', ' ').title()}</span>", unsafe_allow_html=True)
                st.markdown(q['question_text'])

                if q.get("options"):
                    for opt in q["options"]:
                        st.markdown(f"- {opt}")

                ans_key = f"q_{q['card_id']}_{i}"
                st.session_state.quiz_answers[ans_key] = st.text_input(
                    "Your answer",
                    key=ans_key,
                    placeholder="Type your answer (or letter choice A/B/C)..."
                )
                st.write("")

        if st.button("Submit answers", key="btn_submit_answers", type="primary", use_container_width=True):
            st.session_state.quiz_submitted = True
            st.rerun()
            
        if st.session_state.quiz_submitted:
            st.markdown("### Quiz results")
            for i, q in enumerate(st.session_state.quiz_questions):
                with st.container(border=True):
                    st.markdown(f"**Question {i+1} review**")
                    ans_key = f"q_{q['card_id']}_{i}"
                    user_ans = st.session_state.quiz_answers.get(ans_key, "")

                    is_correct = user_ans.strip().lower() == q['correct_answer'].strip().lower()

                    if is_correct:
                        st.success("Correct")
                    else:
                        st.error("Not quite — review the explanation below")

                    st.write(f"**Your answer:** {user_ans}")
                    st.write(f"**Reference answer:** :green[{q['correct_answer']}]")
                    st.markdown(f"**Explanation:**\n{q['explanation']}")


# ------------------ Tab 4: Recent Cards ------------------
with tab4:
    st.subheader("Recent cards")
    st.write("Review recently saved memory cards or delete entries.")

    recent_list = list_recent_cards(limit=10)

    if not recent_list:
        st.info("No saved cards yet. Analyze a sentence in the Analyze tab to create your first card.")
    else:
        for c in recent_list:
            c_id = c.get("id")
            c_type = c.get("card_type", "").replace('_', ' ').title()
            orig = c.get("original_input", "")
            preview = orig if len(orig) <= 120 else orig[:120] + "…"

            with st.container(border=True):
                col_info, col_action = st.columns([6, 1])
                with col_info:
                    st.markdown(f"<span class='badge'>{c_type}</span> <span style='color: #64748B; font-size: 0.85rem;'>ID {c_id}</span><br>{preview}", unsafe_allow_html=True)
                with col_action:
                    if st.button("Delete", key=f"btn_del_recent_{c_id}", use_container_width=True):
                        del_res = delete_card(c_id)
                        if del_res["status"] == "success":
                            st.success("Deleted!")
                            st.rerun()
                        else:
                            st.error(del_res["message"])
