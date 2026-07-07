"""ADK 2.0 Workflow graph for the English Memory Agent.

Wires the specialized sub-agents (router, correction, rewrite, explanation,
organizer) and the local tools (SQLite CRUD, privacy scan, quiz generation)
into a single graph: the router node classifies user intent and the graph
edges dispatch to the matching flow node. The analysis branch ends in a
human-in-the-loop approval step (RequestInput) so nothing is persisted
without explicit user confirmation.
"""
import os

if os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").lower() == "true":
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    if "GOOGLE_CLOUD_PROJECT" in os.environ:
        os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ["GOOGLE_CLOUD_PROJECT"].strip('"\'')

from google.adk import Workflow, Event, Context
from google.adk.events import RequestInput
from google.adk.apps import App
from google.adk.workflow import node

from english_memory_agent.agents import (
    router_agent,
    correction_agent,
    rewrite_agent,
    explanation_agent,
    organizer_agent
)
from english_memory_agent.agents.schemas import RouterIntent
from english_memory_agent.tools import (
    init_db,
    save_card,
    search_cards,
    list_recent_cards,
    delete_card,
    privacy_scan,
    generate_review_quiz_from_cards
)

# Initialize database at module load
init_db()

# 1. Routing Node
@node(rerun_on_resume=True)
async def router_node(ctx: Context, node_input: str):
    """Classifies user intent and sets state parameters."""
    intent_res = await ctx.run_node(router_agent, node_input)
    
    # Extract values from intent_res safely
    if isinstance(intent_res, dict):
        intent = intent_res.get("intent", "")
        search_query = intent_res.get("search_query", "")
        card_id = intent_res.get("card_id")
    else:
        intent = getattr(intent_res, "intent", "")
        search_query = getattr(intent_res, "search_query", "")
        card_id = getattr(intent_res, "card_id", None)
    
    # Store parameters in session state
    ctx.state["intent"] = intent
    ctx.state["search_query"] = search_query
    ctx.state["card_id"] = card_id
    ctx.state["original_text"] = node_input
    
    return Event(route=intent, output=intent_res)

# 2. Analysis Flow Node
@node(rerun_on_resume=True)
async def analysis_flow_node(ctx: Context, node_input: RouterIntent):
    """Runs the grammar correction, rewrite styles, and explanation sequence."""
    original_text = ctx.state.get("original_text", "")
    
    # Run sub-agent checks
    correction_res = await ctx.run_node(correction_agent, original_text)
    
    rewrite_input = f"Original: {original_text}\nCorrection Notes: {correction_res}"
    rewrite_res = await ctx.run_node(rewrite_agent, rewrite_input)
    
    explanation_input = f"Original: {original_text}\nCorrection Notes: {correction_res}"
    explanation_res = await ctx.run_node(explanation_agent, explanation_input)
    
    # Aggregate and structure into a card
    organizer_input = (
        f"Original: {original_text}\n"
        f"Correction: {correction_res}\n"
        f"Rewrites: {rewrite_res}\n"
        f"Explanation: {explanation_res}"
    )
    card_res = await ctx.run_node(organizer_agent, organizer_input)
    
    # Parse card dict
    card_dict = card_res.model_dump() if hasattr(card_res, "model_dump") else card_res
    
    # Run privacy check locally
    p_res = privacy_scan(original_text)
    
    # Store in context state for the save_decision_node
    ctx.state["pending_card"] = card_dict
    ctx.state["privacy_res"] = p_res
    
    return Event(output={"card": card_dict, "privacy": p_res})

# 3. Human Approval HITL Node
@node(rerun_on_resume=False)
async def request_approval_node(ctx: Context, node_input: dict):
    """Yields RequestInput to pause the workflow and request human confirmation."""
    p_res = node_input.get("privacy", {})
    if not p_res.get("safe_to_save", True):
        # Unsafe text blocks saving
        yield "blocked"
        return
        
    # Pause workflow to ask user for confirmation
    user_decision = yield RequestInput(
        message="Do you want to save this memory card to the database? (yes/no)",
        payload=node_input.get("card")
    )
    yield user_decision


# 4. Save Decision Node
@node(rerun_on_resume=True)
async def save_decision_node(ctx: Context, node_input: str):
    """Executes database saving or skips it depending on user approval."""
    if node_input == "blocked":
        return Event(message="Privacy check failed. Saving blocked.")
        
    if str(node_input).strip().lower() == "yes":
        card_data = ctx.state.get("pending_card")
        if card_data:
            # Map original input to the saved dict
            card_payload = dict(card_data)
            card_payload["original_input"] = ctx.state.get("original_text", "")
            
            # Map list tags to string
            if isinstance(card_payload.get("tags"), list):
                card_payload["tags"] = ", ".join(card_payload["tags"])
                
            res = save_card(card_payload)
            if res.get("status") == "success":
                return Event(message=f"Card saved successfully! ID: {res['card_id']}", output=res)
            return Event(message=f"Failed to save card: {res.get('message')}", output=res)
        return Event(message="Error: No pending card found in state.")
    else:
        return Event(message="Saving skipped by user.")

# 5. Search Node
@node
async def search_flow_node(ctx: Context, node_input: RouterIntent):
    """Searches memory database."""
    query = ctx.state.get("search_query")
    results = search_cards(query)
    return Event(output=results, message=f"Found {len(results)} matching cards.")

# 6. Review Node
@node
async def review_flow_node(ctx: Context, node_input: RouterIntent):
    """Generates review quiz questions."""
    cards = list_recent_cards(limit=50)
    quiz = generate_review_quiz_from_cards(cards)
    # Cap the conversational (ADK Web / CLI) output at 10 questions; the
    # Streamlit UI calls the quiz tool directly and applies its own slider limit.
    quiz["questions"] = quiz["questions"][:10]
    quiz["total_questions"] = len(quiz["questions"])
    return Event(output=quiz)

# 7. Delete Node
@node
async def delete_flow_node(ctx: Context, node_input: RouterIntent):
    """Deletes card from database."""
    card_id = ctx.state.get("card_id")
    res = delete_card(card_id)
    return Event(output=res, message=res["message"])

# 8. List Node
@node
async def list_flow_node(ctx: Context, node_input: RouterIntent):
    """Lists recent cards."""
    results = list_recent_cards(limit=10)
    return Event(output=results)

# Assemble ADK 2.0 Workflow Graph
root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", router_node),
        (router_node, {
            "analyze_new_english_input": analysis_flow_node,
            "search_memory": search_flow_node,
            "generate_review": review_flow_node,
            "delete_card": delete_flow_node,
            "list_recent_cards": list_flow_node
        }),
        (analysis_flow_node, request_approval_node),
        (request_approval_node, save_decision_node)
    ]
)

app = App(
    root_agent=root_agent,
    name="english_memory_agent"
)
