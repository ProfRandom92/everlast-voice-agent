# LangGraph Multi-Agent System for Everlast Voice Agent
# Supervisor + 4 Specialized Agents with Checkpointing and Sentiment Analysis

from typing import TypedDict, Annotated, Sequence, Optional, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
import operator
import json
import os
from datetime import datetime
from pydantic import BaseModel

# Import state definitions and checkpointer
from state import (
    AgentState, BANTState, CompanyInfo, ConsentState,
    ObjectionRecord, AppointmentState, CallMetadata,
    SentimentState, GuardrailsState, analyze_sentiment,
    calculate_lead_score, create_initial_state
)
from checkpointer import get_checkpointer, BaseCheckpointer

# ============================================================================
# CHECKPOINTER SETUP
# ============================================================================

# Initialize checkpointer based on environment
CHECKPOINTER_BACKEND = os.getenv("CHECKPOINTER_BACKEND", "sqlite")
checkpointer: BaseCheckpointer = get_checkpointer(
    backend=CHECKPOINTER_BACKEND,
    db_path="checkpoints.db" if CHECKPOINTER_BACKEND == "sqlite" else None
)

# ============================================================================
# LLM SETUP
# ============================================================================

llm = ChatAnthropic(
    model="claude-4-sonnet-20251001",
    temperature=0.7,
    max_tokens=1024
)

# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

SUPERVISOR_PROMPT = """Du bist der Supervisor im Everlast Voice Agent System.

Analysiere die Nachricht und entscheide, welcher Agent zuständig sein sollte:

VERFÜGBARE AGENTEN:
1. bant_qualifier - Sammelt Budget, Authority, Need, Timeline
2. objection_handler - Behandelt Einwände und Bedenken
3. calendly_booker - Führt Terminbuchung durch
4. dsgvo_logger - Protokolliert Consent und End-Summary

ROUTING-REGELN:
→ bant_qualifier: Lead zeigt Interesse, Discovery-Phase, BANT unvollständig
→ objection_handler: Einwände wie "zu teuer", "keine Zeit", Bedenken
→ calendly_booker: Lead ist qualifiziert (Score A/B), zeigt Bereitschaft
→ dsgvo_logger: Gesprächsbeginn (Consent), Gesprächsende (Summary)

Berücksichtige das aktuelle Sentiment des Callers für das Routing:
- Bei negativem/frustriertem Sentiment: Priorisiere objection_handler
- Bei begeistertem/positivem Sentiment: Direkt zu calendly_booker wenn qualifiziert

Antworte NUR mit dem Agent-Namen in Kleinbuchstaben."""

BANT_PROMPT = """Du bist Anna, BANT-Qualifier bei Everlast Consulting.

Erfasse natürlich im Gespräch:
- Budget: Hat das Unternehmen Budget?
- Authority: Ist der Gesprächspartner Entscheider?
- Need: Konkreter Bedarf an KI/Automatisierung?
- Timeline: Wann soll umgesetzt werden?

Stelle nie alle Fragen auf einmal. Integriere sie natürlich in den Dialog.
Wenn ein Kriterium erfasst ist, bestätige kurz.

Sprache: Perfektes Hochdeutsch, warm, professionell.

Kontext: Lead hat eine Case Study zur Lead-Reaktivierung gelesen."""

OBJECTION_PROMPT = """Du bist Anna, Objection Handler bei Everlast Consulting.

Behandle Einwände mit dem LAER-Framework:
- Listen: Zuhören
- Acknowledge: Empathie zeigen
- Explore: Hintergründe erfragen
- Respond: Passende Antwort

Sei niemals defensiv. Validiere Bedenken. Bleibe ehrlich.

Häufige Einwände:
- Preis: "Zu teuer" → Auf ROI eingehen, flexible Modelle
- Zeit: "Keine Zeit" → Konkreten Alternativvorschlag
- Nicht-Entscheider: Mit GF verbinden oder Info zusammenstellen
- Bereits-Tool: Als Ergänzung positionieren
- Kein Bedarf: Respektieren, Tür offen halten

Passe deinen Ton an das Sentiment des Callers an:
- Frustriert: Sei besonders geduldig und beruhigend
- Begeistert: Begeistere mit, bleibe professionell"""

CALENDLY_PROMPT = """Du bist Anna, Termin-Manager bei Everlast Consulting.

Buche qualifizierte Leads (Score A/B) zu einem Demo-Termin.

Prozess:
1. Soft-Ask: "Wären Sie offen für ein Gespräch?"
2. Zeit erfragen: Morgens/Nachmittags-Präferenz
3. Konkreten Slot vorschlagen
4. Details erfassen (Name, E-Mail, Firma)
5. Bestätigen und Vorfreude aufbauen

Kalender: Mo-Fr, 9-17 Uhr, 30 Min Slots
Bei Zusage: Daten erfassen, Bestätigung senden

Wenn der Lead begeistert ist (hohes Sentiment), baue Vorfreude auf!
Wenn der Lead noch unsicher ist, gib zusätzliche Sicherheit."""

DSGVO_PROMPT = """Du bist der DSGVO-Logger für Everlast Consulting.

ZUSTÄNDIGKEITEN:
1. Gesprächsbeginn: Consent für Aufzeichnung einholen
2. Gesprächsende: Zusammenfassung erstellen, Daten speichern
3. Auskunftsanfragen: An Datenschutz-Team weiterleiten

CONSENT-FORMULIERUNG:
"Zu Ihrer Information: Dieses Gespräch wird zur Qualitätssicherung aufgezeichnet.
Ihre Daten werden gemäß DSGVO in der EU verarbeitet.
Sie können jederzeit Auskunft oder Löschung verlangen. Ist das in Ordnung?"

SUMMARY-STRUKTUR:
- BANT-Ergebnis
- Lead-Score (A/B/C/N)
- Einwände
- Ergebnis (Termin/Rückruf/Abbruch)
- Sentiment-Entwicklung
- Nächste Schritte"""

# ============================================================================
# GUARDRAILS FUNCTIONS
# ============================================================================

def check_hallucination(response: str, state: AgentState) -> tuple[bool, str]:
    """Check for potential hallucinations in response"""
    # Keywords that might indicate hallucination
    suspicious_patterns = [
        "ich glaube",
        "vielleicht",
        "ich denke",
        "könnte sein",
        "wahrscheinlich",
        "vermutlich"
    ]

    response_lower = response.lower()
    for pattern in suspicious_patterns:
        if pattern in response_lower:
            return True, f"Potential hallucination detected: '{pattern}'"

    return False, ""

def check_data_integrity(state: AgentState, response: str) -> tuple[bool, str]:
    """Check for data integrity issues"""
    violations = []

    # Check if we're contradicting previously stated information
    bant = state.get("bant")
    if bant:
        # Example: If budget was already stated as "Ja", don't ask again
        pass

    return len(violations) > 0, ", ".join(violations)

def apply_guardrails(state: AgentState, response: str) -> tuple[str, GuardrailsState]:
    """Apply guardrails to agent response"""
    guardrails = state.get("guardrails", GuardrailsState())

    # Check for hallucination
    is_hallucination, hall_reason = check_hallucination(response, state)
    if is_hallucination:
        guardrails.hallucination_detected = True
        # Regenerate response with stricter prompt
        response = "Entschuldigung, lassen Sie mich das präziser formulieren. " + response

    # Check data integrity
    has_violations, violations = check_data_integrity(state, response)
    if has_violations:
        guardrails.data_integrity_violations.append(violations)

    # Check for repetition
    messages = state.get("messages", [])
    if len(messages) >= 2:
        last_msgs = [m.content for m in messages[-2:] if hasattr(m, 'content')]
        if response in last_msgs:
            guardrails.repetition_count += 1
            response = "Wie ich bereits erwähnt habe: " + response

    return response, guardrails

# ============================================================================
# SENTIMENT-AWARE AGENT FUNCTIONS
# ============================================================================

def supervisor_agent(state: AgentState) -> dict:
    """Supervisor: Routes to appropriate agent with sentiment awareness"""
    last_message = state["messages"][-1].content if state["messages"] else ""

    # Analyze sentiment
    current_sentiment = state.get("caller_sentiment", SentimentState())
    updated_sentiment = analyze_sentiment(last_message, current_sentiment)

    # Get sentiment for routing decision
    sentiment = updated_sentiment.current_sentiment
    sentiment_score = updated_sentiment.sentiment_score

    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT),
        ("human", f"""Letzte Nachricht: {last_message}

Aktueller Agent: {state['current_agent']}
Call gestartet: {state['call_started']}
Call beendet: {state['call_ended']}

SENTIMENT KONTEXT:
- Aktuelles Sentiment: {sentiment}
- Sentiment-Score: {sentiment_score}
- Verlauf: {updated_sentiment.history}

Berücksichtige das Sentiment beim Routing.""")
    ])

    response = llm.invoke(prompt.format_messages({}))
    target_agent = response.content.strip().lower()

    # Validate target agent
    valid_agents = ["bant_qualifier", "objection_handler", "calendly_booker", "dsgvo_logger"]
    if target_agent not in valid_agents:
        target_agent = "bant_qualifier"  # Default fallback

    # Sentiment-based routing override
    if sentiment in ["frustriert", "negativ"] and target_agent != "objection_handler":
        # Route to objection handler if caller seems frustrated
        if "einwand" in last_message.lower() or "problem" in last_message.lower():
            target_agent = "objection_handler"

    if sentiment == "begeistert" and state.get("bant", BANTState()).is_complete():
        # Route to calendly if enthusiastic and qualified
        target_agent = "calendly_booker"

    return {
        "current_agent": target_agent,
        "caller_sentiment": updated_sentiment,
        "messages": [AIMessage(content=f"[SUPERVISOR → {target_agent}]")]
    }

def bant_qualifier_agent(state: AgentState) -> dict:
    """BANT Qualifier: Collects qualification data"""
    last_message = state["messages"][-1].content

    # Consider sentiment in response
    sentiment = state.get("caller_sentiment", SentimentState())
    tone_hint = ""
    if sentiment.current_sentiment == "frustriert":
        tone_hint = "Der Caller scheint frustriert zu sein. Sei besonders geduldig und empathisch."
    elif sentiment.current_sentiment == "begeistert":
        tone_hint = "Der Caller ist begeistert! Nutze die positive Energie."

    prompt = ChatPromptTemplate.from_messages([
        ("system", BANT_PROMPT + "\n" + tone_hint),
        ("human", f"Letzte Nachricht: {last_message}\n\nBisher erfasst: {state['bant'].model_dump() if state.get('bant') else {}}")
    ])

    response = llm.invoke(prompt.format_messages({}))

    # Apply guardrails
    safe_response, updated_guardrails = apply_guardrails(state, response.content)

    # Try to extract BANT info from context
    bant_update = state.get("bant", BANTState()).model_dump()
    message_lower = last_message.lower()

    # Simple keyword extraction
    if any(word in message_lower for word in ["budget", "geld", "investieren", "eingeplant"]):
        if any(yes in message_lower for yes in ["ja", "haben", "vorhanden"]):
            bant_update["budget"] = "Ja"
        elif any(no in message_lower for no in ["nein", "nicht", "kein"]):
            bant_update["budget"] = "Nein"

    if any(word in message_lower for word in ["entscheide", "geschäftsführer", "gf", "ich bin"]):
        if any(auth in message_lower for auth in ["gf", "geschäftsführer", "inhaber", "entscheide", "mein bereich"]):
            bant_update["authority"] = "Entscheider"

    return {
        "bant": BANTState(**bant_update),
        "guardrails": updated_guardrails,
        "messages": [AIMessage(content=safe_response)]
    }

def objection_handler_agent(state: AgentState) -> dict:
    """Objection Handler: Handles objections"""
    last_message = state["messages"][-1].content

    # Consider sentiment
    sentiment = state.get("caller_sentiment", SentimentState())
    tone_hint = ""
    if sentiment.current_sentiment == "frustriert":
        tone_hint = "WICHTIG: Der Caller ist frustriert! Sei extrem geduldig, bestätige Gefühle, gehe langsam vor."

    prompt = ChatPromptTemplate.from_messages([
        ("system", OBJECTION_PROMPT + "\n" + tone_hint),
        ("human", f"Einwand: {last_message}")
    ])

    response = llm.invoke(prompt.format_messages({}))

    # Apply guardrails
    safe_response, updated_guardrails = apply_guardrails(state, response.content)

    # Record objection
    objection_types = {
        "preis": ["teuer", "budget", "kosten", "geld", "preis"],
        "zeit": ["keine zeit", "später", "busy", "termin"],
        "nicht_entscheider": ["chef", "gf", "abstimmen", "nicht meine"],
        "bereits_loesung": ["haben schon", "nutzen bereits", "chatgpt"],
        "kein_bedarf": ["nicht interessiert", "kein bedarf", "brauchen nicht"],
        "misstrauen": ["hype", "funktioniert nicht", "robeter"]
    }

    obj_type = "Andere"
    message_lower = last_message.lower()
    for obj, keywords in objection_types.items():
        if any(kw in message_lower for kw in keywords):
            obj_type = obj
            break

    # Determine outcome based on sentiment change
    outcome = "Offen"
    if sentiment.sentiment_score > 0:
        outcome = "Überwunden"

    new_objection = ObjectionRecord(
        type=obj_type,
        text=last_message,
        response_given=safe_response,
        outcome=outcome
    )

    return {
        "objections": state.get("objections", []) + [new_objection],
        "guardrails": updated_guardrails,
        "messages": [AIMessage(content=safe_response)]
    }

def calendly_booker_agent(state: AgentState) -> dict:
    """Calendly Booker: Books appointments"""
    last_message = state["messages"][-1].content

    # Consider sentiment for closing technique
    sentiment = state.get("caller_sentiment", SentimentState())
    closing_hint = ""
    if sentiment.current_sentiment == "begeistert":
        closing_hint = "Der Caller ist begeistert! Nutze assumptive close und baue Vorfreude auf."
    elif sentiment.current_sentiment == "neutral":
        closing_hint = "Der Caller ist neutral. Gib zusätzliche Sicherheit und Vorteile."

    prompt = ChatPromptTemplate.from_messages([
        ("system", CALENDLY_PROMPT + "\n" + closing_hint),
        ("human", f"Letzte Nachricht: {last_message}")
    ])

    response = llm.invoke(prompt.format_messages({}))

    # Apply guardrails
    safe_response, updated_guardrails = apply_guardrails(state, response.content)

    # Check for booking intent
    message_lower = last_message.lower()
    booking_keywords = ["termin", "buchen", "reservieren", "passt", "gut", "ja"]
    if any(kw in message_lower for kw in booking_keywords) and not state["appointment"]["booked"]:
        return {
            "appointment": AppointmentState(
                booked=True,
                date="pending",
                time="pending"
            ),
            "guardrails": updated_guardrails,
            "messages": [AIMessage(content=safe_response)]
        }

    return {
        "guardrails": updated_guardrails,
        "messages": [AIMessage(content=safe_response)]
    }

def dsgvo_logger_agent(state: AgentState) -> dict:
    """DSGVO Logger: Handles consent and logging"""
    last_message = state["messages"][-1].content

    # Check if this is start or end of call
    if not state["call_started"]:
        # Start of call - get consent
        prompt = ChatPromptTemplate.from_messages([
            ("system", DSGVO_PROMPT),
            ("human", "Gespräch beginnt. Bitte Consent einholen.")
        ])
        response = llm.invoke(prompt.format_messages({}))

        return {
            "call_started": True,
            "consent": ConsentState(
                recording=True,
                data_processing=True,
                timestamp=datetime.now().isoformat()
            ),
            "messages": [AIMessage(content=response.content)]
        }

    elif state["call_ended"]:
        # End of call - create summary
        bant = state.get("bant", BANTState())
        sentiment = state.get("caller_sentiment", SentimentState())

        # Calculate lead score
        score, reason = calculate_lead_score(bant, state.get("objections", []))

        # Calculate sentiment trend
        sentiment_trend = "gleich"
        if sentiment.history and len(sentiment.history) >= 2:
            first = sentiment.history[0].get("score", 0)
            last = sentiment.history[-1].get("score", 0)
            if last > first + 0.3:
                sentiment_trend = "verbessert"
            elif last < first - 0.3:
                sentiment_trend = "verschlechtert"

        summary = f"""
Gespräch mit {state['phone_number']}
Lead-Score: {score}
BANT: Budget={bant.budget}, Authority={bant.authority}, Need={bant.need}, Timeline={bant.timeline}
Einwände: {len(state.get('objections', []))}
Termin gebucht: {state.get('appointment', {}).get('booked', False)}
Sentiment-Start: {sentiment.history[0]['sentiment'] if sentiment.history else 'neutral'}
Sentiment-Ende: {sentiment.current_sentiment}
Sentiment-Trend: {sentiment_trend}
"""

        return {
            "lead_score": score,
            "lead_score_reason": reason,
            "summary": summary,
            "messages": [AIMessage(content="Gespräch protokolliert. Auf Wiederhören!")]
        }

    return {"messages": []}

# ============================================================================
# ROUTING LOGIC
# ============================================================================

def route_from_supervisor(state: AgentState) -> str:
    """Determine next node based on supervisor decision"""
    return state["current_agent"]

def should_end_call(state: AgentState) -> str:
    """Check if call should end"""
    last_message = state["messages"][-1].content.lower() if state["messages"] else ""

    end_phrases = ["auf wiederhören", "tschüss", "danke", "schönen tag", "bis bald"]
    if any(phrase in last_message for phrase in end_phrases):
        return "dsgvo_logger"

    return "supervisor"

# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("bant_qualifier", bant_qualifier_agent)
workflow.add_node("objection_handler", objection_handler_agent)
workflow.add_node("calendly_booker", calendly_booker_agent)
workflow.add_node("dsgvo_logger", dsgvo_logger_agent)

# Add edges
workflow.set_entry_point("supervisor")

# Supervisor routes to agents
workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "bant_qualifier": "bant_qualifier",
        "objection_handler": "objection_handler",
        "calendly_booker": "calendly_booker",
        "dsgvo_logger": "dsgvo_logger"
    }
)

# All agents return to supervisor (or end)
workflow.add_conditional_edges(
    "bant_qualifier",
    should_end_call,
    {
        "supervisor": "supervisor",
        "dsgvo_logger": "dsgvo_logger"
    }
)

workflow.add_conditional_edges(
    "objection_handler",
    should_end_call,
    {
        "supervisor": "supervisor",
        "dsgvo_logger": "dsgvo_logger"
    }
)

workflow.add_conditional_edges(
    "calendly_booker",
    should_end_call,
    {
        "supervisor": "supervisor",
        "dsgvo_logger": "dsgvo_logger"
    }
)

# DSGVO logger ends the flow
workflow.add_edge("dsgvo_logger", END)

# Compile the graph
graph = workflow.compile()

# ============================================================================
# PUBLIC INTERFACE WITH CHECKPOINTING
# ============================================================================

async def process_message(
    conversation_id: str,
    phone_number: str,
    message: str,
    state: Optional[dict] = None,
    sentiment_data: Optional[dict] = None
) -> dict:
    """
    Process a single message through the agent graph with checkpointing.

    Args:
        conversation_id: Unique conversation ID
        phone_number: Caller's phone number (used as thread_id)
        message: The message to process
        state: Optional previous state (loaded from checkpoint if None)
        sentiment_data: Optional Deepgram sentiment data

    Returns:
        Updated state with agent response
    """
    # Try to load existing state from checkpoint (for return callers)
    if state is None:
        checkpoint = await checkpointer.get(phone_number)
        if checkpoint:
            state = checkpoint
            print(f"Loaded checkpoint for {phone_number}")
        else:
            # Initialize new state
            state = create_initial_state(
                conversation_id=conversation_id,
                phone_number=phone_number
            )
    else:
        # Add message to existing state
        state["messages"] = list(state.get("messages", [])) + [HumanMessage(content=message)]

    # Update sentiment if Deepgram data provided
    if sentiment_data and "caller_sentiment" in state:
        state["caller_sentiment"].update(
            sentiment=sentiment_data.get("sentiment", "neutral"),
            score=sentiment_data.get("score", 0.0),
            confidence=sentiment_data.get("confidence", 0.0)
        )

    # Run through graph
    result = graph.invoke(state)

    # Save checkpoint (thread_id = phone_number)
    await checkpointer.set(phone_number, result)

    return result

async def end_conversation(state: dict, phone_number: str) -> dict:
    """
    End a conversation and generate summary.

    Args:
        state: Current conversation state
        phone_number: Caller's phone number

    Returns:
        Final state with summary
    """
    state["call_ended"] = True
    result = graph.invoke(state)

    # Save final checkpoint
    await checkpointer.set(phone_number, result)

    return result

async def get_conversation_history(phone_number: str) -> Optional[dict]:
    """
    Get conversation history for a return caller.

    Args:
        phone_number: Caller's phone number

    Returns:
        Previous conversation state or None
    """
    return await checkpointer.get(phone_number)

async def clear_conversation(phone_number: str) -> None:
    """Clear conversation checkpoint"""
    await checkpointer.delete(phone_number)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_system():
        # Test the system with checkpointing
        print("Testing Everlast Voice Agent System with Checkpointing...\n")

        # Simulate a conversation
        phone_number = "+49123456789"
        conversation_id = "test-123"

        messages = [
            "Guten Tag",
            "Ja, ich habe die Case Study gelesen",
            "Wir sind 25 Mitarbeiter",
            "Ich bin der Geschäftsführer",
            "Ja, wir haben Budget",
            "Wir wollen schnell starten",
            "Ja, einen Termin buchen wäre gut",
            "max@firma.de"
        ]

        for msg in messages:
            print(f"User: {msg}")
            result = await process_message(
                conversation_id=conversation_id,
                phone_number=phone_number,
                message=msg
            )
            if result.get("messages"):
                print(f"Agent: {result['messages'][-1].content}\n")

        # End conversation
        final_state = await end_conversation(result, phone_number)
        print("\n=== FINAL SUMMARY ===")
        print(final_state.get("summary", "No summary"))
        print(f"Lead Score: {final_state.get('lead_score', 'N/A')}")
        print(f"Sentiment: {final_state.get('caller_sentiment', {}).current_sentiment}")

        # Test return caller (checkpoint reload)
        print("\n=== SIMULATING RETURN CALLER ===")
        history = await get_conversation_history(phone_number)
        if history:
            print(f"Loaded previous conversation with lead score: {history.get('lead_score')}")

    asyncio.run(test_system())
