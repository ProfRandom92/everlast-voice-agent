# FastAPI Backend for Everlast Voice Agent
# Webhook endpoint for Vapi integration

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
import os
import json
import uuid
from datetime import datetime
import httpx

# Import LangGraph components (from local everlast_agents package)
try:
    from everlast_agents.agent_system import process_message, end_conversation, get_conversation_history, clear_conversation
    from everlast_agents.state import create_initial_state, analyze_sentiment, SentimentState
    from everlast_agents.checkpointer import get_checkpointer, BaseCheckpointer
    print("LangGraph imported successfully from everlast_agents package")
except ImportError as e:
    print(f"LangGraph import error: {e}")
    import traceback
    traceback.print_exc()
    raise

# Supabase client
from supabase import create_client, Client

# Initialize checkpointer
CHECKPOINTER_BACKEND = os.getenv("CHECKPOINTER_BACKEND", "sqlite")
checkpointer: BaseCheckpointer = get_checkpointer(backend=CHECKPOINTER_BACKEND)

app = FastAPI(
    title="Everlast Voice Agent API",
    description="Backend API for Everlast Voice Agent with Vapi integration",
    version="1.0.0"
)

# CORS middleware - configure for production
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://everlast-dashboard.vercel.app",  # Production dashboard
]

# Add additional origins from environment if specified
additional_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
if additional_origins:
    allowed_origins.extend([origin.strip() for origin in additional_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Vapi-Secret"],
)

# ============================================================================
# CONFIGURATION
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
VAPI_SECRET = os.getenv("VAPI_SERVER_SECRET")
CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
CALENDLY_USER_URI = os.getenv("CALENDLY_USER_URI")
CALENDLY_EVENT_TYPE_URI = os.getenv("CALENDLY_EVENT_TYPE_URI")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# In-memory state store (use Redis in production)
conversation_states = {}

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class VapiMessage(BaseModel):
    role: Literal["assistant", "user", "system"]
    content: str

class VapiFunctionCall(BaseModel):
    name: str
    parameters: dict

class VapiWebhookPayload(BaseModel):
    message: Optional[VapiMessage] = None
    function_call: Optional[VapiFunctionCall] = None
    call: Optional[dict] = Field(default=None, description="Call metadata from Vapi")
    phone_number: Optional[str] = Field(default=None, description="Caller phone number")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")

class CalendlyBookingRequest(BaseModel):
    name: str
    email: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    timezone: Optional[str] = "Europe/Berlin"  # Optional timezone parameter

class LeadQualificationData(BaseModel):
    budget: Literal["Ja", "Nein", "Unklar"]
    authority: Literal["Entscheider", "Einfluss", "Keine Entscheidungsbefugnis"]
    need: Literal["Hoch", "Mittel", "Niedrig", "Kein Bedarf"]
    timeline: Literal["Sofort", "1-3 Monate", "3-6 Monate", "> 6 Monate", "Unklar"]
    company_size: Optional[str] = None
    current_tools: Optional[str] = None
    specific_need: Optional[str] = None

class CallSummaryRequest(BaseModel):
    call_outcome: Literal["Termin gebucht", "Rückruf vereinbart", "Nicht interessiert", "Nicht erreicht", "Abgebrochen"]
    lead_score: Literal["A", "B", "C", "N"]
    next_steps: Optional[str] = None
    notes: Optional[str] = None
    sentiment_trend: Optional[Literal["verbessert", "gleich", "verschlechtert"]] = None

class SentimentWebhookPayload(BaseModel):
    """Deepgram sentiment analysis payload"""
    conversation_id: str
    phone_number: str
    sentiment: Literal["positiv", "neutral", "negativ", "frustriert", "begeistert"]
    score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    utterance: str
    timestamp: str

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_or_create_conversation_state(conversation_id: str, phone_number: str):
    """Get existing conversation state or create new one"""
    if conversation_id not in conversation_states:
        conversation_states[conversation_id] = create_initial_state(
            conversation_id=conversation_id,
            phone_number=phone_number
        )
    return conversation_states[conversation_id]

def save_to_supabase(table: str, data: dict):
    """Save data to Supabase"""
    if supabase:
        try:
            result = supabase.table(table).insert(data).execute()
            return result
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            return None
    return None

async def book_calendly_appointment(data: CalendlyBookingRequest) -> dict:
    """Book appointment via Calendly API with dynamic timezone"""
    if not CALENDLY_API_KEY:
        return {"error": "Calendly API key not configured"}

    # Format start time
    start_time = f"{data.date}T{data.time}:00"

    # Use provided timezone or default to Europe/Berlin
    timezone = data.timezone or "Europe/Berlin"

    headers = {
        "Authorization": f"Bearer {CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "event_type": CALENDLY_EVENT_TYPE_URI,
        "start_time": start_time,
        "timezone": timezone,
        "invitee": {
            "email": data.email,
            "first_name": data.name.split()[0] if data.name else "",
            "last_name": " ".join(data.name.split()[1:]) if len(data.name.split()) > 1 else "",
            "text_reminder_number": data.phone
        },
        "questions_and_answers": [
            {
                "question": "Firma",
                "answer": data.company or "Nicht angegeben"
            },
            {
                "question": "Notizen",
                "answer": data.notes or ""
            },
            {
                "question": "Zeitzone",
                "answer": timezone
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.calendly.com/scheduled_events",
                headers=headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Everlast Voice Agent API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "supabase_connected": supabase is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Main webhook endpoint for Vapi integration.
    Handles incoming messages from voice calls and routes through LangGraph.
    Supports checkpointing for return callers (thread_id = phone_number).
    """
    try:
        # Verify Vapi webhook secret if configured
        if VAPI_SECRET:
            vapi_secret_header = request.headers.get("x-vapi-secret")
            if not vapi_secret_header or vapi_secret_header != VAPI_SECRET:
                raise HTTPException(
                    status_code=401,
                    detail="Unauthorized: Invalid or missing webhook secret"
                )

        payload = await request.json()

        # Extract conversation info
        call_data = payload.get("call", {})
        conversation_id = call_data.get("id", str(uuid.uuid4()))
        phone_number = call_data.get("customer", {}).get("number", "unknown")

        # Extract sentiment data from Vapi/Deepgram if available
        sentiment_data = None
        if "analysis" in payload and "sentiment" in payload["analysis"]:
            sentiment_data = {
                "sentiment": payload["analysis"]["sentiment"],
                "score": payload["analysis"].get("score", 0.0),
                "confidence": payload["analysis"].get("confidence", 0.0)
            }

        # Process message from Vapi
        message = payload.get("message", {})
        if message.get("role") == "user":
            user_message = message.get("content", "")

            # Process through LangGraph with checkpointing
            result = await process_message(
                conversation_id=conversation_id,
                phone_number=phone_number,
                message=user_message,
                state=None,  # Will be loaded from checkpoint
                sentiment_data=sentiment_data
            )

            # Get agent response
            agent_response = ""
            if result.get("messages"):
                agent_response = result["messages"][-1].content

            # Get sentiment state for TTS adjustments
            sentiment_state = result.get("caller_sentiment", SentimentState())
            tts_adjustments = sentiment_state.get_tts_adjustments()

            return JSONResponse({
                "response": agent_response,
                "conversation_id": conversation_id,
                "current_agent": result.get("current_agent", "supervisor"),
                "sentiment": result.get("caller_sentiment", {}).current_sentiment if result.get("caller_sentiment") else "neutral",
                "tts_adjustments": tts_adjustments,
                "checkpoint_saved": True
            })

        # Handle function calls from Vapi
        function_call = payload.get("function_call")
        if function_call:
            return await handle_function_call(function_call, conversation_id, phone_number)

        return JSONResponse({"status": "received"})

    except Exception as e:
        print(f"Error in webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_function_call(function_call: dict, conversation_id: str, phone_number: str):
    """Handle function calls from Vapi"""
    function_name = function_call.get("name")
    parameters = function_call.get("parameters", {})

    if function_name == "qualifyLead":
        # Save qualification data
        data = {
            "conversation_id": conversation_id,
            "phone_number": phone_number,
            "budget": parameters.get("budget"),
            "authority": parameters.get("authority"),
            "need": parameters.get("need"),
            "timeline": parameters.get("timeline"),
            "company_size": parameters.get("companySize"),
            "current_tools": parameters.get("currentTools"),
            "specific_need": parameters.get("specificNeed"),
            "created_at": datetime.now().isoformat()
        }
        save_to_supabase("lead_qualifications", data)

        # Update state
        state = conversation_states.get(conversation_id, {})
        if state:
            state["bant"] = {
                "budget": parameters.get("budget"),
                "authority": parameters.get("authority"),
                "need": parameters.get("need"),
                "timeline": parameters.get("timeline")
            }

        return JSONResponse({"status": "qualification_saved"})

    elif function_name == "bookAppointment":
        # Book appointment
        booking_data = CalendlyBookingRequest(
            name=parameters.get("name", ""),
            email=parameters.get("email", ""),
            date=parameters.get("date", ""),
            time=parameters.get("time", ""),
            phone=parameters.get("phone"),
            company=parameters.get("company"),
            notes=parameters.get("notes")
        )

        result = await book_calendly_appointment(booking_data)

        # Save to database
        data = {
            "conversation_id": conversation_id,
            "phone_number": phone_number,
            "name": parameters.get("name"),
            "email": parameters.get("email"),
            "appointment_date": parameters.get("date"),
            "appointment_time": parameters.get("time"),
            "company": parameters.get("company"),
            "notes": parameters.get("notes"),
            "calendly_response": result,
            "created_at": datetime.now().isoformat()
        }
        save_to_supabase("appointments", data)

        return JSONResponse({"status": "appointment_booked", "details": result})

    elif function_name == "recordObjection":
        # Record objection
        data = {
            "conversation_id": conversation_id,
            "phone_number": phone_number,
            "objection_type": parameters.get("objectionType"),
            "objection_text": parameters.get("objectionText"),
            "response_given": parameters.get("responseGiven"),
            "outcome": parameters.get("outcome"),
            "created_at": datetime.now().isoformat()
        }
        save_to_supabase("objections", data)

        return JSONResponse({"status": "objection_recorded"})

    elif function_name == "logConsent":
        # Log consent
        data = {
            "conversation_id": conversation_id,
            "phone_number": parameters.get("phoneNumber", phone_number),
            "consent_given": parameters.get("consentGiven"),
            "consent_type": parameters.get("consentType"),
            "created_at": datetime.now().isoformat()
        }
        save_to_supabase("consent_logs", data)

        return JSONResponse({"status": "consent_logged"})

    elif function_name == "endCallSummary":
        # End call and save summary
        state = await get_conversation_history(phone_number)
        if state:
            final_state = await end_conversation(state, phone_number)

            # Get sentiment trend
            sentiment = final_state.get("caller_sentiment", SentimentState())
            sentiment_trend = "gleich"
            if sentiment.history and len(sentiment.history) >= 2:
                first = sentiment.history[0].get("score", 0)
                last = sentiment.history[-1].get("score", 0)
                if last > first + 0.3:
                    sentiment_trend = "verbessert"
                elif last < first - 0.3:
                    sentiment_trend = "verschlechtert"

            data = {
                "conversation_id": conversation_id,
                "phone_number": phone_number,
                "call_outcome": parameters.get("callOutcome"),
                "lead_score": parameters.get("leadScore"),
                "next_steps": parameters.get("nextSteps"),
                "notes": parameters.get("notes"),
                "summary": final_state.get("summary"),
                "bant_data": final_state.get("bant"),
                "appointment_booked": final_state.get("appointment", {}).get("booked", False),
                "sentiment_start": sentiment.history[0]["sentiment"] if sentiment.history else "neutral",
                "sentiment_end": sentiment.current_sentiment,
                "sentiment_trend": sentiment_trend,
                "guardrails_triggered": len(final_state.get("guardrails", {}).data_integrity_violations) > 0,
                "ended_at": datetime.now().isoformat()
            }
            save_to_supabase("call_summaries", data)

        return JSONResponse({"status": "call_ended"})

    elif function_name == "updateSentiment":
        # Update sentiment from Deepgram analysis
        sentiment_data = {
            "sentiment": parameters.get("sentiment"),
            "score": parameters.get("score"),
            "confidence": parameters.get("confidence")
        }

        # Update checkpoint with sentiment
        state = await get_conversation_history(phone_number)
        if state and "caller_sentiment" in state:
            state["caller_sentiment"].update(
                sentiment=sentiment_data["sentiment"],
                score=sentiment_data["score"],
                confidence=sentiment_data["confidence"]
            )
            await checkpointer.set(phone_number, state)

        return JSONResponse({
            "status": "sentiment_updated",
            "tts_adjustments": parameters.get("ttsAdjustments", {})
        })

    return JSONResponse({"status": "unknown_function"})

@app.post("/calls/end")
async def end_call(request: CallSummaryRequest, conversation_id: str):
    """Manually end a call and save summary"""
    state = conversation_states.get(conversation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get phone number from state for checkpointing
    phone_number = state.get("phone_number", "unknown")
    final_state = await end_conversation(state, phone_number)
    conversation_states[conversation_id] = final_state

    data = {
        "conversation_id": conversation_id,
        "call_outcome": request.call_outcome,
        "lead_score": request.lead_score,
        "next_steps": request.next_steps,
        "notes": request.notes,
        "summary": final_state.get("summary"),
        "ended_at": datetime.now().isoformat()
    }
    save_to_supabase("call_summaries", data)

    return JSONResponse({"status": "success", "lead_score": request.lead_score})

# ============================================================================
# DASHBOARD API ENDPOINTS
# ============================================================================

@app.get("/api/stats/conversion")
async def get_conversion_stats(days: int = 30):
    """Get conversion rate statistics"""
    if not supabase:
        return {"error": "Supabase not configured"}

    try:
        # Get total calls
        calls_result = supabase.table("call_summaries").select("*").execute()
        total_calls = len(calls_result.data) if calls_result.data else 0

        # Get booked appointments
        appointments_result = supabase.table("appointments").select("*").execute()
        booked = len(appointments_result.data) if appointments_result.data else 0

        conversion_rate = (booked / total_calls * 100) if total_calls > 0 else 0

        return {
            "total_calls": total_calls,
            "booked_appointments": booked,
            "conversion_rate": round(conversion_rate, 2)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats/lead-scores")
async def get_lead_score_distribution():
    """Get lead score distribution"""
    if not supabase:
        return {"error": "Supabase not configured"}

    try:
        result = supabase.table("call_summaries").select("lead_score").execute()
        data = result.data if result.data else []

        distribution = {"A": 0, "B": 0, "C": 0, "N": 0}
        for item in data:
            score = item.get("lead_score")
            if score in distribution:
                distribution[score] += 1

        return distribution
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats/recent-calls")
async def get_recent_calls(limit: int = 10):
    """Get recent calls for dashboard"""
    if not supabase:
        return {"error": "Supabase not configured"}

    try:
        result = supabase.table("call_summaries")\
            .select("*")\
            .order("ended_at", desc=True)\
            .limit(limit)\
            .execute()

        return {"calls": result.data if result.data else []}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats/objections")
async def get_objection_stats():
    """Get objection statistics"""
    if not supabase:
        return {"error": "Supabase not configured"}

    try:
        result = supabase.table("objections").select("objection_type, outcome").execute()
        data = result.data if result.data else []

        type_counts = {}
        outcome_counts = {"Überwunden": 0, "Nicht überwunden": 0, "Offen": 0}

        for item in data:
            obj_type = item.get("objection_type", "Andere")
            outcome = item.get("outcome", "Offen")

            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
            if outcome in outcome_counts:
                outcome_counts[outcome] += 1

        return {
            "by_type": type_counts,
            "by_outcome": outcome_counts,
            "total": len(data)
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# SENTIMENT WEBHOOK (Deepgram Integration)
# ============================================================================

@app.post("/vapi/sentiment")
async def sentiment_webhook(request: SentimentWebhookPayload):
    """
    Webhook endpoint for Deepgram sentiment analysis.
    Updates conversation state with sentiment data for adaptive TTS.
    """
    try:
        # Get current state
        state = await get_conversation_history(request.phone_number)

        if state:
            # Update sentiment in state
            sentiment_state = state.get("caller_sentiment", SentimentState())
            sentiment_state.update(
                sentiment=request.sentiment,
                score=request.score,
                confidence=request.confidence
            )
            state["caller_sentiment"] = sentiment_state

            # Save checkpoint
            await checkpointer.set(request.phone_number, state)

            # Get TTS adjustments for response
            tts_adjustments = sentiment_state.get_tts_adjustments()

            return JSONResponse({
                "status": "sentiment_recorded",
                "sentiment": request.sentiment,
                "tts_adjustments": tts_adjustments
            })

        return JSONResponse({
            "status": "no_active_conversation",
            "sentiment": request.sentiment
        })

    except Exception as e:
        print(f"Error in sentiment webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHECKPOINT MANAGEMENT API
# ============================================================================

@app.get("/api/checkpoints/{phone_number}")
async def get_checkpoint(phone_number: str):
    """Get conversation checkpoint for a phone number (return caller support)"""
    try:
        checkpoint = await get_conversation_history(phone_number)
        if checkpoint:
            # Remove sensitive data from response
            safe_checkpoint = {
                "exists": True,
                "conversation_id": checkpoint.get("conversation_id"),
                "current_agent": checkpoint.get("current_agent"),
                "bant": checkpoint.get("bant"),
                "lead_score": checkpoint.get("lead_score"),
                "appointment_booked": checkpoint.get("appointment", {}).get("booked", False),
                "caller_sentiment": checkpoint.get("caller_sentiment", {}).current_sentiment if checkpoint.get("caller_sentiment") else "neutral",
                "last_updated": checkpoint.get("last_checkpoint")
            }
            return safe_checkpoint
        return {"exists": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/checkpoints/{phone_number}")
async def delete_checkpoint(phone_number: str):
    """Delete conversation checkpoint"""
    try:
        await clear_conversation(phone_number)
        return {"status": "deleted", "phone_number": phone_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/checkpoints")
async def list_checkpoints(limit: int = 100):
    """List all active conversation checkpoints"""
    try:
        threads = await checkpointer.list_threads(limit=limit)
        return {
            "active_sessions": len(threads),
            "phone_numbers": threads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SENTIMENT STATS API
# ============================================================================

@app.get("/api/stats/sentiment")
async def get_sentiment_stats(days: int = 30):
    """Get sentiment analysis statistics"""
    if not supabase:
        return {"error": "Supabase not configured"}

    try:
        result = supabase.table("call_summaries")\
            .select("sentiment_start, sentiment_end, sentiment_trend")\
            .gte("ended_at", (datetime.now().replace(day=1)).isoformat())\
            .execute()

        data = result.data if result.data else []

        sentiment_distribution = {"positiv": 0, "neutral": 0, "negativ": 0, "frustriert": 0, "begeistert": 0}
        trends = {"verbessert": 0, "gleich": 0, "verschlechtert": 0}

        for item in data:
            end_sentiment = item.get("sentiment_end", "neutral")
            if end_sentiment in sentiment_distribution:
                sentiment_distribution[end_sentiment] += 1

            trend = item.get("sentiment_trend", "gleich")
            if trend in trends:
                trends[trend] += 1

        return {
            "sentiment_distribution": sentiment_distribution,
            "trend_analysis": trends,
            "total_analyzed": len(data)
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# GUARDRAILS STATS API
# ============================================================================

@app.get("/api/stats/guardrails")
async def get_guardrails_stats(days: int = 30):
    """Get guardrails trigger statistics"""
    if not supabase:
        return {"error": "Supabase not configured"}

    try:
        result = supabase.table("call_summaries")\
            .select("guardrails_triggered")\
            .execute()

        data = result.data if result.data else []

        triggered = sum(1 for item in data if item.get("guardrails_triggered", False))
        total = len(data)

        return {
            "guardrails_triggered": triggered,
            "total_calls": total,
            "trigger_rate": round((triggered / total * 100), 2) if total > 0 else 0
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
