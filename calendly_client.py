"""
Calendly API v2 Client for Everlast Voice Agent
Production-ready client with error handling, retries, and caching
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import httpx
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalendlyError(Exception):
    """Base exception for Calendly API errors"""
    pass


class CalendlyAuthError(CalendlyError):
    """Authentication/Authorization error"""
    pass


class CalendlyNotFoundError(CalendlyError):
    """Resource not found error"""
    pass


class CalendlyValidationError(CalendlyError):
    """Validation error (e.g., double booking)"""
    pass


class CalendlyRateLimitError(CalendlyError):
    """Rate limit exceeded"""
    pass


class BookingStatus(Enum):
    """Booking status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class CalendlyBookingResult:
    """Result of a Calendly booking attempt"""
    success: bool
    status: BookingStatus
    event_uri: Optional[str] = None
    invitee_uri: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    confirmation_url: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    raw_response: Optional[Dict] = field(default=None, repr=False)


@dataclass
class TimeSlot:
    """Represents an available time slot"""
    start_time: str
    end_time: str
    is_available: bool = True


@dataclass
class EventType:
    """Calendly Event Type information"""
    uri: str
    name: str
    duration: int  # in minutes
    description: Optional[str] = None
    color: Optional[str] = None
    active: bool = True
    scheduling_url: Optional[str] = None


class CalendlyClient:
    """
    Production-ready Calendly API v2 Client

    Features:
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Response caching for read operations
    - Comprehensive error handling
    - Type hints throughout
    """

    BASE_URL = "https://api.calendly.com"
    API_VERSION = "v2"

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_uri: Optional[str] = None,
        event_type_uri: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Calendly client

        Args:
            api_key: Calendly API token (or from CALENDLY_API_KEY env var)
            user_uri: Calendly user URI (or from CALENDLY_USER_URI env var)
            event_type_uri: Default event type URI (or from CALENDLY_EVENT_TYPE_URI env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds
        """
        self.api_key = api_key or os.getenv("CALENDLY_API_KEY")
        self.user_uri = user_uri or os.getenv("CALENDLY_USER_URI")
        self.default_event_type_uri = event_type_uri or os.getenv("CALENDLY_EVENT_TYPE_URI")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Initialize with retry strategy
        transport = httpx.AsyncHTTPTransport(
            retries=max_retries,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )

        self.client = httpx.AsyncClient(
            transport=transport,
            timeout=timeout,
            base_url=self.BASE_URL,
            headers=self._get_headers()
        )

        # Cache for event types
        self._event_types_cache: Optional[Tuple[List[EventType], datetime]] = None
        self._cache_ttl = timedelta(minutes=5)

        self._validate_config()

    def _validate_config(self):
        """Validate required configuration"""
        if not self.api_key:
            raise CalendlyAuthError(
                "Calendly API key not configured. "
                "Set CALENDLY_API_KEY environment variable or pass api_key parameter."
            )

        if not self.user_uri:
            logger.warning(
                "CALENDLY_USER_URI not set. "
                "Some operations may require user URI."
            )

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EverlastVoiceAgent/1.0"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for httpx

        Returns:
            Response JSON as dict

        Raises:
            CalendlyError: Various Calendly-specific exceptions
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    **kwargs
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    raise CalendlyRateLimitError("Rate limit exceeded")

                # Handle auth errors
                if response.status_code in (401, 403):
                    raise CalendlyAuthError(
                        f"Authentication failed: {response.text}"
                    )

                # Handle not found
                if response.status_code == 404:
                    raise CalendlyNotFoundError(
                        f"Resource not found: {endpoint}"
                    )

                # Handle validation errors
                if response.status_code == 422:
                    error_data = response.json()
                    message = error_data.get("message", "Validation failed")
                    raise CalendlyValidationError(message)

                # Handle other errors
                response.raise_for_status()

                # Return JSON response
                if response.status_code == 204:
                    return {}
                return response.json()

            except CalendlyRateLimitError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise CalendlyError(f"HTTP error: {e.response.status_code}") from e

            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise CalendlyError(f"Request failed: {str(e)}") from e

        raise CalendlyError("Max retries exceeded")

    async def get_current_user(self) -> Dict[str, Any]:
        """
        Get current user information

        Returns:
            User data including URI
        """
        response = await self._make_request("GET", "/users/me")
        return response.get("resource", {})

    async def get_event_types(
        self,
        active: bool = True,
        user_uri: Optional[str] = None,
        organization_uri: Optional[str] = None
    ) -> List[EventType]:
        """
        Get available event types for the user

        Args:
            active: Only return active event types
            user_uri: Filter by specific user
            organization_uri: Filter by organization

        Returns:
            List of EventType objects
        """
        # Check cache
        if self._event_types_cache:
            cached_data, cached_time = self._event_types_cache
            if datetime.now() - cached_time < self._cache_ttl:
                return cached_data

        params = {}
        if active:
            params["active"] = "true"
        if user_uri:
            params["user"] = user_uri
        elif self.user_uri:
            params["user"] = self.user_uri
        if organization_uri:
            params["organization"] = organization_uri

        response = await self._make_request("GET", "/event_types", params=params)

        event_types = []
        for item in response.get("collection", []):
            event_types.append(EventType(
                uri=item.get("uri", ""),
                name=item.get("name", ""),
                duration=item.get("duration", 30),
                description=item.get("description"),
                color=item.get("color"),
                active=item.get("active", True),
                scheduling_url=item.get("scheduling_url")
            ))

        # Update cache
        self._event_types_cache = (event_types, datetime.now())

        return event_types

    async def get_event_type_by_uri(
        self,
        event_type_uri: str
    ) -> Optional[EventType]:
        """
        Get specific event type by URI

        Args:
            event_type_uri: Full event type URI

        Returns:
            EventType object or None
        """
        try:
            # Extract UUID from URI
            event_type_uuid = event_type_uri.split("/")[-1]
            response = await self._make_request("GET", f"/event_types/{event_type_uuid}")

            item = response.get("resource", {})
            return EventType(
                uri=item.get("uri", ""),
                name=item.get("name", ""),
                duration=item.get("duration", 30),
                description=item.get("description"),
                color=item.get("color"),
                active=item.get("active", True),
                scheduling_url=item.get("scheduling_url")
            )
        except CalendlyNotFoundError:
            return None

    async def get_available_slots(
        self,
        event_type_uri: str,
        start_date: str,
        end_date: Optional[str] = None,
        timezone: str = "Europe/Berlin"
    ) -> List[TimeSlot]:
        """
        Get available time slots for an event type

        Args:
            event_type_uri: Event type URI
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to start_date + 7 days
            timezone: Target timezone

        Returns:
            List of available TimeSlot objects
        """
        if not end_date:
            # Default to 7 days from start
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = start + timedelta(days=7)
            end_date = end.strftime("%Y-%m-%d")

        # Build query params
        params = {
            "event_type": event_type_uri,
            "start_time": f"{start_date}T00:00:00",
            "end_time": f"{end_date}T23:59:59",
            "timezone": timezone
        }

        try:
            response = await self._make_request(
                "GET",
                "/event_type_available_times",
                params=params
            )

            slots = []
            for item in response.get("collection", []):
                slots.append(TimeSlot(
                    start_time=item.get("start_time", ""),
                    end_time=item.get("end_time", ""),
                    is_available=item.get("status", "available") == "available"
                ))

            return slots

        except CalendlyError as e:
            logger.error(f"Failed to get available slots: {e}")
            return []

    async def check_slot_availability(
        self,
        event_type_uri: str,
        date: str,
        time: str,
        timezone: str = "Europe/Berlin"
    ) -> bool:
        """
        Check if a specific slot is available

        Args:
            event_type_uri: Event type URI
            date: Date (YYYY-MM-DD)
            time: Time (HH:MM)
            timezone: Timezone

        Returns:
            True if slot is available
        """
        start_datetime = f"{date}T{time}:00"

        # Get slots for the day
        slots = await self.get_available_slots(
            event_type_uri=event_type_uri,
            start_date=date,
            end_date=date,
            timezone=timezone
        )

        # Check if requested slot exists and is available
        for slot in slots:
            if slot.start_time.startswith(start_datetime) and slot.is_available:
                return True

        return False

    async def create_scheduling_link(
        self,
        event_type_uri: Optional[str] = None,
        owner: Optional[str] = None,
        max_event_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a scheduling link for an event type

        Args:
            event_type_uri: Event type URI (uses default if not specified)
            owner: Owner URI
            max_event_count: Maximum events that can be scheduled

        Returns:
            Scheduling link data
        """
        event_uri = event_type_uri or self.default_event_type_uri

        if not event_uri:
            raise CalendlyValidationError("Event type URI is required")

        payload = {
            "owner": owner or self.user_uri,
            "owner_type": "users",
            "event_type": event_uri
        }

        if max_event_count:
            payload["max_event_count"] = max_event_count

        response = await self._make_request(
            "POST",
            "/scheduling_links",
            json=payload
        )

        return response.get("resource", {})

    async def book_appointment(
        self,
        name: str,
        email: str,
        date: str,
        time: str,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        notes: Optional[str] = None,
        event_type_uri: Optional[str] = None,
        timezone: str = "Europe/Berlin",
        language: str = "de",
        custom_questions: Optional[Dict[str, str]] = None
    ) -> CalendlyBookingResult:
        """
        Book an appointment via Calendly API

        Args:
            name: Full name of invitee
            email: Email address
            date: Date (YYYY-MM-DD)
            time: Time (HH:MM)
            phone: Phone number
            company: Company name
            notes: Additional notes
            event_type_uri: Event type URI (uses default if not specified)
            timezone: Timezone
            language: Language code
            custom_questions: Additional Q&A pairs

        Returns:
            CalendlyBookingResult with success status
        """
        event_uri = event_type_uri or self.default_event_type_uri

        if not event_uri:
            return CalendlyBookingResult(
                success=False,
                status=BookingStatus.ERROR,
                error_message="Event type URI not configured",
                error_code="CONFIG_MISSING"
            )

        # Parse name into first/last
        name_parts = name.strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Format datetime
        start_time = f"{date}T{time}:00"

        # Build questions and answers
        questions_and_answers = []

        if company:
            questions_and_answers.append({
                "question": "Firma",
                "answer": company
            })

        if phone:
            questions_and_answers.append({
                "question": "Telefon",
                "answer": phone
            })

        if notes:
            questions_and_answers.append({
                "question": "Notizen vom Anruf",
                "answer": notes
            })

        # Add custom questions
        if custom_questions:
            for question, answer in custom_questions.items():
                questions_and_answers.append({
                    "question": question,
                    "answer": answer
                })

        # Add language info
        questions_and_answers.append({
            "question": "Sprache",
            "answer": language
        })

        payload = {
            "event_type": event_uri,
            "start_time": start_time,
            "timezone": timezone,
            "language": language,
            "invitee": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            },
            "questions_and_answers": questions_and_answers
        }

        # Add phone for SMS reminders if provided
        if phone:
            payload["invitee"]["text_reminder_number"] = phone

        try:
            response = await self._make_request(
                "POST",
                "/scheduled_events",
                json=payload
            )

            resource = response.get("resource", {})

            # Extract event details
            event_uri = resource.get("uri", "")
            invitees = resource.get("invitees", [])
            invitee_uri = invitees[0].get("uri") if invitees else None

            return CalendlyBookingResult(
                success=True,
                status=BookingStatus.CONFIRMED,
                event_uri=event_uri,
                invitee_uri=invitee_uri,
                start_time=resource.get("start_time"),
                end_time=resource.get("end_time"),
                confirmation_url=resource.get("location", {}).get("join_url"),
                raw_response=response
            )

        except CalendlyValidationError as e:
            error_message = str(e).lower()

            # Check for double booking
            if "already taken" in error_message or "conflict" in error_message:
                return CalendlyBookingResult(
                    success=False,
                    status=BookingStatus.ERROR,
                    error_message="Der Termin ist leider bereits vergeben. Bitte wählen Sie einen anderen Zeitpunkt.",
                    error_code="DOUBLE_BOOKING",
                    raw_response={"error": str(e)}
                )

            # Check for past date
            if "past" in error_message:
                return CalendlyBookingResult(
                    success=False,
                    status=BookingStatus.ERROR,
                    error_message="Der gewählte Zeitpunkt liegt in der Vergangenheit. Bitte wählen Sie eine zukünftige Zeit.",
                    error_code="PAST_DATE",
                    raw_response={"error": str(e)}
                )

            return CalendlyBookingResult(
                success=False,
                status=BookingStatus.ERROR,
                error_message=str(e),
                error_code="VALIDATION_ERROR",
                raw_response={"error": str(e)}
            )

        except CalendlyError as e:
            logger.error(f"Booking failed: {e}")
            return CalendlyBookingResult(
                success=False,
                status=BookingStatus.ERROR,
                error_message="Es ist ein technischer Fehler aufgetreten. Bitte versuchen Sie es später erneut.",
                error_code="API_ERROR",
                raw_response={"error": str(e)}
            )

    async def cancel_appointment(
        self,
        invitee_uri: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Cancel a scheduled appointment

        Args:
            invitee_uri: Invitee URI
            reason: Cancellation reason

        Returns:
            True if cancelled successfully
        """
        try:
            payload = {}
            if reason:
                payload["reason"] = reason

            await self._make_request(
                "POST",
                f"{invitee_uri}/cancellation",
                json=payload
            )
            return True

        except CalendlyError as e:
            logger.error(f"Failed to cancel appointment: {e}")
            return False

    async def get_scheduled_event(
        self,
        event_uri: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get details of a scheduled event

        Args:
            event_uri: Event URI

        Returns:
            Event details or None
        """
        try:
            response = await self._make_request("GET", event_uri)
            return response.get("resource")
        except CalendlyNotFoundError:
            return None

    async def list_scheduled_events(
        self,
        user_uri: Optional[str] = None,
        organization_uri: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List scheduled events

        Args:
            user_uri: Filter by user
            organization_uri: Filter by organization
            start_date: Min start time (ISO 8601)
            end_date: Max start time (ISO 8601)
            status: Filter by status (active, canceled)
            count: Number of results per page

        Returns:
            List of scheduled events
        """
        params = {"count": count}

        if user_uri:
            params["user"] = user_uri
        elif self.user_uri:
            params["user"] = self.user_uri

        if organization_uri:
            params["organization"] = organization_uri
        if start_date:
            params["min_start_time"] = start_date
        if end_date:
            params["max_start_time"] = end_date
        if status:
            params["status"] = status

        response = await self._make_request(
            "GET",
            "/scheduled_events",
            params=params
        )

        return response.get("collection", [])

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# Convenience function for direct booking
async def book_appointment(
    name: str,
    email: str,
    date: str,
    time: str,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    notes: Optional[str] = None,
    timezone: str = "Europe/Berlin"
) -> CalendlyBookingResult:
    """
    Convenience function to book an appointment using environment variables

    Args:
        name: Full name
        email: Email address
        date: Date (YYYY-MM-DD)
        time: Time (HH:MM)
        phone: Phone number
        company: Company name
        notes: Notes
        timezone: Timezone

    Returns:
        CalendlyBookingResult
    """
    async with CalendlyClient() as client:
        return await client.book_appointment(
            name=name,
            email=email,
            date=date,
            time=time,
            phone=phone,
            company=company,
            notes=notes,
            timezone=timezone
        )
