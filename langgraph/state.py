# State Definitions for Everlast Voice Agent
# Enhanced with Sentiment Detection and Checkpointing

from typing import TypedDict, Annotated, Sequence, Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime

# ============================================================================
# SENTIMENT MODELS
# ============================================================================

class SentimentState(BaseModel):
    """Caller sentiment tracking for adaptive responses"""
    current_sentiment: Literal["positiv", "neutral", "negativ", "frustriert", "begeistert"] = Field(
        default="neutral",
        description="Current emotional state of caller"
    )
    sentiment_score: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Sentiment score from -1.0 (negative) to 1.0 (positive)"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in sentiment detection"
    )
    history: list[dict] = Field(
        default_factory=list,
        description="History of sentiment changes"
    )
    last_updated: Optional[str] = Field(
        default=None,
        description="ISO timestamp of last sentiment update"
    )

    def update(self, sentiment: str, score: float, confidence: float):
        """Update sentiment state"""
        self.current_sentiment = sentiment
        self.sentiment_score = score
        self.confidence = confidence
        self.last_updated = datetime.now().isoformat()
        self.history.append({
            "sentiment": sentiment,
            "score": score,
            "timestamp": self.last_updated
        })

    def requires_tone_adjustment(self) -> bool:
        """Check if TTS tone adjustment is needed"""
        return abs(self.sentiment_score) > 0.5 or self.current_sentiment in ["frustriert", "begeistert"]

    def get_tts_adjustments(self) -> dict:
        """Get TTS parameter adjustments based on sentiment"""
        adjustments = {
            "positiv": {"stability": 0.4, "similarity_boost": 0.8, "style": "friendly"},
            "begeistert": {"stability": 0.3, "similarity_boost": 0.9, "style": "excited"},
            "neutral": {"stability": 0.5, "similarity_boost": 0.75, "style": "professional"},
            "negativ": {"stability": 0.6, "similarity_boost": 0.7, "style": "empathetic"},
            "frustriert": {"stability": 0.7, "similarity_boost": 0.65, "style": "calm"}
        }
        return adjustments.get(self.current_sentiment, adjustments["neutral"])

# ============================================================================
# BANT MODELS
# ============================================================================

class BANTState(BaseModel):
    """BANT Qualification Criteria"""
    budget: Optional[Literal["Ja", "Nein", "Unklar"]] = Field(
        default=None,
        description="Budget availability for KI consulting"
    )
    authority: Optional[Literal["Entscheider", "Einfluss", "Keine Entscheidungsbefugnis"]] = Field(
        default=None,
        description="Decision-making authority of the contact"
    )
    need: Optional[Literal["Hoch", "Mittel", "Niedrig", "Kein Bedarf"]] = Field(
        default=None,
        description="Level of need for KI/automation"
    )
    timeline: Optional[Literal["Sofort", "1-3 Monate", "3-6 Monate", "> 6 Monate", "Unklar"]] = Field(
        default=None,
        description="Implementation timeline"
    )

    def is_complete(self) -> bool:
        """Check if all BANT criteria are filled"""
        return all([
            self.budget is not None,
            self.authority is not None,
            self.need is not None,
            self.timeline is not None
        ])

    def score(self) -> int:
        """Calculate BANT score (0-100)"""
        score = 0
        if self.budget == "Ja": score += 25
        elif self.budget == "Unklar": score += 10
        if self.authority == "Entscheider": score += 25
        elif self.authority == "Einfluss": score += 15
        if self.need == "Hoch": score += 25
        elif self.need == "Mittel": score += 15
        if self.timeline in ["Sofort", "1-3 Monate"]: score += 25
        elif self.timeline == "3-6 Monate": score += 10
        return score

class CompanyInfo(BaseModel):
    """Company information collected during call"""
    name: Optional[str] = Field(default=None, description="Company name")
    size: Optional[Literal["1-10", "11-50", "51-200", "201-500", "500+"]] = Field(
        default=None,
        description="Company size in employees"
    )
    industry: Optional[str] = Field(default=None, description="Industry sector")
    current_tools: Optional[str] = Field(
        default=None,
        description="Currently used tools/software"
    )
    website: Optional[str] = Field(default=None, description="Company website")

# ============================================================================
# CONSENT MODELS
# ============================================================================

class ConsentState(BaseModel):
    """GDPR consent tracking"""
    recording: bool = Field(default=False, description="Consent for call recording")
    data_processing: bool = Field(default=False, description="Consent for data processing")
    marketing: bool = Field(default=False, description="Consent for marketing")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp of consent")
    ip_address: Optional[str] = Field(default=None, description="IP address (if available)")

    def record_consent(self, recording: bool = True, data_processing: bool = True):
        """Record consent with timestamp"""
        self.recording = recording
        self.data_processing = data_processing
        self.timestamp = datetime.now().isoformat()

# ============================================================================
# OBJECTION MODELS
# ============================================================================

class ObjectionRecord(BaseModel):
    """Record of an objection raised during call"""
    type: Literal["Preis", "Zeit", "Nicht-Entscheider", "Bereits-Lösung", "Kein-Bedarf", "Misstrauen", "Andere"]
    text: Optional[str] = Field(default=None, description="Exact objection text")
    response_given: Optional[str] = Field(default=None, description="Agent's response")
    outcome: Optional[Literal["Überwunden", "Nicht überwunden", "Offen"]] = Field(
        default="Offen",
        description="Outcome of objection handling"
    )
    timestamp: Optional[str] = Field(default=None, description="When objection was raised")

# ============================================================================
# APPOINTMENT MODELS
# ============================================================================

class AppointmentState(BaseModel):
    """Appointment booking state"""
    booked: bool = Field(default=False)
    name: Optional[str] = Field(default=None, description="Contact name")
    email: Optional[str] = Field(default=None, description="Contact email")
    phone: Optional[str] = Field(default=None, description="Contact phone")
    company: Optional[str] = Field(default=None, description="Company name")
    date: Optional[str] = Field(default=None, description="Appointment date (YYYY-MM-DD)")
    time: Optional[str] = Field(default=None, description="Appointment time (HH:MM)")
    timezone: str = Field(default="Europe/Berlin", description="Timezone")
    event_type: Literal["demo", "consultation", "callback"] = Field(
        default="demo",
        description="Type of appointment"
    )
    notes: Optional[str] = Field(default=None, description="Additional notes")
    calendly_event_id: Optional[str] = Field(default=None, description="Calendly event ID")
    calendly_invitee_id: Optional[str] = Field(default=None, description="Calendly invitee ID")

# ============================================================================
# CALL METADATA MODELS
# ============================================================================

class CallMetadata(BaseModel):
    """Call metadata"""
    call_id: str = Field(description="Unique call identifier")
    phone_number: str = Field(description="Caller phone number")
    start_time: Optional[str] = Field(default=None, description="ISO start timestamp")
    end_time: Optional[str] = Field(default=None, description="ISO end timestamp")
    duration_seconds: Optional[int] = Field(default=None, description="Call duration")
    recording_url: Optional[str] = Field(default=None, description="Recording URL")
    transcript_url: Optional[str] = Field(default=None, description="Transcript URL")
    vapi_call_id: Optional[str] = Field(default=None, description="Vapi call ID")

# ============================================================================
# GUARDRAILS MODEL
# ============================================================================

class GuardrailsState(BaseModel):
    """Track guardrails and safety checks"""
    hallucination_detected: bool = Field(default=False)
    data_integrity_violations: list[str] = Field(default_factory=list)
    sensitive_data_exposed: bool = Field(default=False)
    off_topic_count: int = Field(default=0)
    repetition_count: int = Field(default=0)

# ============================================================================
# MAIN STATE
# ============================================================================

class AgentState(TypedDict):
    """Main conversation state for LangGraph with Sentiment Detection"""
    # Identification
    conversation_id: str
    phone_number: str

    # Agent routing
    current_agent: str  # supervisor, bant_qualifier, objection_handler, calendly_booker, dsgvo_logger

    # Messages
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # Qualification
    bant: BANTState
    company_info: CompanyInfo

    # Scoring
    lead_score: Optional[Literal["A", "B", "C", "N"]]
    lead_score_reason: Optional[str]

    # Objections
    objections: list[ObjectionRecord]

    # Sentiment Analysis (NEW)
    caller_sentiment: SentimentState

    # Guardrails (NEW)
    guardrails: GuardrailsState

    # Appointment
    appointment: AppointmentState

    # Compliance
    consent: ConsentState

    # Call state
    call_started: bool
    call_ended: bool

    # Summary
    summary: Optional[str]
    next_steps: Optional[str]

    # Metadata
    metadata: CallMetadata

    # Checkpoint info
    checkpoint_id: Optional[str]
    last_checkpoint: Optional[str]

# ============================================================================
# SENTIMENT DETECTION FUNCTION
# ============================================================================

def analyze_sentiment(
    text: str,
    current_sentiment: SentimentState
) -> SentimentState:
    """
    Analyze sentiment from text and update state.
    In production, this would use Deepgram's sentiment analysis API.
    """
    # Simple keyword-based detection (placeholder for Deepgram integration)
    positive_words = ["gut", "super", "perfekt", "interessant", "gerne", "ja", "top", "exzellent", "begeistert"]
    negative_words = ["nein", "nicht", "schlecht", "ärgern", "frustrierend", "doof", "blöd", "ärgerlich"]
    frustration_words = ["verdammt", "unverschämt", "wütend", "sauer", "genervt", "reicht"]
    excitement_words = ["wow", "unglaublich", "fantastisch", "amazing", "genial", "toll"]

    text_lower = text.lower()

    # Count matches
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    frust_count = sum(1 for word in frustration_words if word in text_lower)
    exc_count = sum(1 for word in excitement_words if word in text_lower)

    # Determine sentiment
    if frust_count > 0:
        sentiment = "frustriert"
        score = -0.7
    elif exc_count > 0:
        sentiment = "begeistert"
        score = 0.9
    elif neg_count > pos_count:
        sentiment = "negativ"
        score = -0.5
    elif pos_count > neg_count:
        sentiment = "positiv"
        score = 0.5
    else:
        sentiment = "neutral"
        score = 0.0

    # Calculate confidence
    total_matches = pos_count + neg_count + frust_count + exc_count
    confidence = min(total_matches * 0.3, 1.0)

    # Update state
    current_sentiment.update(sentiment, score, confidence)
    return current_sentiment

# ============================================================================
# LEAD SCORING FUNCTION
# ============================================================================

def calculate_lead_score(bant: BANTState, objections: list[ObjectionRecord]) -> tuple[str, str]:
    """
    Calculate lead score based on BANT and objections.

    Returns:
        Tuple of (score: A/B/C/N, reason: str)
    """
    # Count overcome objections
    overcome_count = sum(1 for o in objections if o.outcome == "Überwunden")
    open_count = sum(1 for o in objections if o.outcome == "Offen")

    # Score A: Hot lead
    if (bant.budget == "Ja" and
        bant.authority == "Entscheider" and
        bant.need == "Hoch" and
        bant.timeline in ["Sofort", "1-3 Monate"] and
        open_count == 0):
        return "A", "Budget vorhanden, Entscheider, hoher Bedarf, kurze Timeline"

    # Score B: Warm lead
    elif (bant.need in ["Hoch", "Mittel"] and
          bant.budget in ["Ja", "Unklar"] and
          bant.authority in ["Entscheider", "Einfluss"] and
          bant.timeline in ["Sofort", "1-3 Monate", "3-6 Monate"] and
          open_count <= 1):
        return "B", "Interesse vorhanden, Budget geklärt oder unklar, moderate Timeline"

    # Score C: Cold lead
    elif (bant.need == "Mittel" or
          bant.timeline == "> 6 Monate" or
          bant.budget == "Unklar"):
        return "C", "Geringeres Interesse oder lange Timeline"

    # Score N: Not qualified
    else:
        return "N", "Kein Bedarf oder Budget, nicht qualifiziert"

# ============================================================================
# INITIAL STATE FACTORY
# ============================================================================

def create_initial_state(
    conversation_id: str,
    phone_number: str,
    call_id: Optional[str] = None,
    vapi_call_id: Optional[str] = None
) -> AgentState:
    """Create initial state for a new conversation"""
    return {
        "conversation_id": conversation_id,
        "phone_number": phone_number,
        "current_agent": "supervisor",
        "messages": [],
        "bant": BANTState(),
        "company_info": CompanyInfo(),
        "lead_score": None,
        "lead_score_reason": None,
        "objections": [],
        "caller_sentiment": SentimentState(),  # NEW
        "guardrails": GuardrailsState(),  # NEW
        "appointment": AppointmentState(),
        "consent": ConsentState(),
        "call_started": False,
        "call_ended": False,
        "summary": None,
        "next_steps": None,
        "metadata": CallMetadata(
            call_id=call_id or conversation_id,
            phone_number=phone_number,
            start_time=datetime.now().isoformat(),
            vapi_call_id=vapi_call_id
        ),
        "checkpoint_id": None,
        "last_checkpoint": None
    }
