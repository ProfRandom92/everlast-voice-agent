"""
Test examples for Calendly Integration
Run with: python -m pytest test_calendly.py -v
"""

import asyncio
import os
import pytest
from datetime import datetime, timedelta
from calendly_client import (
    CalendlyClient,
    CalendlyBookingResult,
    BookingStatus,
    CalendlyError,
    CalendlyAuthError,
    CalendlyValidationError
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create a Calendly client for testing"""
    # Skip if no API key
    api_key = os.getenv("CALENDLY_API_KEY")
    if not api_key:
        pytest.skip("CALENDLY_API_KEY not set")

    return CalendlyClient(
        api_key=api_key,
        timeout=30
    )


@pytest.fixture
def event_type_uri():
    """Get event type URI from environment"""
    uri = os.getenv("CALENDLY_EVENT_TYPE_URI")
    if not uri:
        pytest.skip("CALENDLY_EVENT_TYPE_URI not set")
    return uri


@pytest.fixture
def user_uri():
    """Get user URI from environment"""
    uri = os.getenv("CALENDLY_USER_URI")
    if not uri:
        pytest.skip("CALENDLY_USER_URI not set")
    return uri


@pytest.fixture
def tomorrow():
    """Get tomorrow's date"""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


# ============================================================================
# BASIC CLIENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization with environment variables"""
    client = CalendlyClient()
    assert client.api_key is not None
    assert client.timeout == 30
    await client.close()


@pytest.mark.asyncio
async def test_client_initialization_missing_key():
    """Test client fails without API key"""
    # Temporarily clear env
    original_key = os.getenv("CALENDLY_API_KEY")
    os.environ["CALENDLY_API_KEY"] = ""

    with pytest.raises(CalendlyAuthError):
        CalendlyClient()

    # Restore
    if original_key:
        os.environ["CALENDLY_API_KEY"] = original_key


@pytest.mark.asyncio
async def test_get_current_user(client):
    """Test getting current user"""
    user = await client.get_current_user()
    assert "uri" in user
    assert "email" in user
    print(f"\nUser: {user.get('name')} ({user.get('email')})")


# ============================================================================
# EVENT TYPES TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_event_types(client):
    """Test getting event types"""
    event_types = await client.get_event_types()
    assert isinstance(event_types, list)
    if event_types:
        first = event_types[0]
        assert first.uri
        assert first.name
        assert first.duration > 0
        print(f"\nFound {len(event_types)} event types")
        print(f"First: {first.name} ({first.duration} min)")


@pytest.mark.asyncio
async def test_get_event_type_by_uri(client, event_type_uri):
    """Test getting specific event type"""
    event_type = await client.get_event_type_by_uri(event_type_uri)
    assert event_type is not None
    assert event_type.uri == event_type_uri
    print(f"\nEvent Type: {event_type.name}")


# ============================================================================
# AVAILABILITY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_available_slots(client, event_type_uri, tomorrow):
    """Test getting available time slots"""
    slots = await client.get_available_slots(
        event_type_uri=event_type_uri,
        start_date=tomorrow,
        end_date=tomorrow
    )

    assert isinstance(slots, list)
    print(f"\nFound {len(slots)} available slots for {tomorrow}")
    if slots:
        print(f"First slot: {slots[0].start_time}")


@pytest.mark.asyncio
async def test_check_slot_availability(client, event_type_uri, tomorrow):
    """Test checking slot availability"""
    # Check for 10:00 AM
    is_available = await client.check_slot_availability(
        event_type_uri=event_type_uri,
        date=tomorrow,
        time="10:00"
    )

    print(f"\nSlot available at {tomorrow} 10:00: {is_available}")
    assert isinstance(is_available, bool)


# ============================================================================
# BOOKING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_book_appointment_success(client, event_type_uri, tomorrow):
    """Test successful booking"""
    # Generate unique email to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    result = await client.book_appointment(
        name="Test User",
        email=f"test.{timestamp}@example.com",
        date=tomorrow,
        time="14:00",
        company="Test Company",
        notes="This is a test booking",
        event_type_uri=event_type_uri
    )

    assert isinstance(result, CalendlyBookingResult)
    assert result.success == True
    assert result.status == BookingStatus.CONFIRMED
    assert result.event_uri is not None
    print(f"\nBooked: {result.start_time}")
    print(f"Event URI: {result.event_uri}")

    # Cleanup: Cancel the booking
    if result.invitee_uri:
        await client.cancel_appointment(result.invitee_uri)
        print("Cancelled test booking")


@pytest.mark.asyncio
async def test_book_appointment_past_date(client, event_type_uri):
    """Test booking fails for past date"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    result = await client.book_appointment(
        name="Test User",
        email="test@example.com",
        date=yesterday,
        time="10:00",
        event_type_uri=event_type_uri
    )

    assert result.success == False
    assert result.status == BookingStatus.ERROR
    assert result.error_code == "PAST_DATE" or result.error_code == "VALIDATION_ERROR"
    print(f"\nCorrectly rejected past date: {result.error_message}")


@pytest.mark.asyncio
async def test_book_appointment_double_booking(client, event_type_uri, tomorrow):
    """Test booking fails for double booking"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"test.{timestamp}@example.com"

    # First booking
    result1 = await client.book_appointment(
        name="Test User",
        email=email,
        date=tomorrow,
        time="15:00",
        event_type_uri=event_type_uri
    )

    assert result1.success == True

    # Second booking for same slot should fail
    result2 = await client.book_appointment(
        name="Another User",
        email=f"another.{timestamp}@example.com",
        date=tomorrow,
        time="15:00",
        event_type_uri=event_type_uri
    )

    assert result2.success == False
    print(f"\nDouble booking prevented: {result2.error_message}")

    # Cleanup
    if result1.invitee_uri:
        await client.cancel_appointment(result1.invitee_uri)


# ============================================================================
# CONVENIENCE FUNCTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_convenience_book_function(event_type_uri, tomorrow):
    """Test convenience book_appointment function"""
    from calendly_client import book_appointment

    # This uses environment variables
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    result = await book_appointment(
        name="Convenience Test",
        email=f"convenience.{timestamp}@example.com",
        date=tomorrow,
        time="16:00",
        company="Test Corp",
        notes="Testing convenience function"
    )

    assert isinstance(result, CalendlyBookingResult)
    print(f"\nConvenience function result: {result.success}")

    # Cleanup
    if result.invitee_uri:
        async with CalendlyClient() as client:
            await client.cancel_appointment(result.invitee_uri)


# ============================================================================
# SCHEDULING LINKS
# ============================================================================

@pytest.mark.asyncio
async def test_create_scheduling_link(client, event_type_uri, user_uri):
    """Test creating scheduling link"""
    link = await client.create_scheduling_link(
        event_type_uri=event_type_uri,
        owner=user_uri
    )

    assert "booking_url" in link or "url" in link
    print(f"\nScheduling link: {link.get('booking_url', link.get('url'))}")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_event_type_uri():
    """Test handling of invalid event type URI"""
    client = CalendlyClient()

    result = await client.book_appointment(
        name="Test",
        email="test@example.com",
        date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        time="10:00",
        event_type_uri="https://api.calendly.com/event_types/invalid-uuid"
    )

    assert result.success == False
    await client.close()


@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager"""
    async with CalendlyClient() as client:
        user = await client.get_current_user()
        assert "uri" in user
        print(f"\nContext manager test passed for user: {user.get('email')}")


# ============================================================================
# MANUAL TESTS (Run with: python test_calendly.py)
# ============================================================================

async def run_manual_tests():
    """Run manual tests with output"""
    print("=" * 60)
    print("CALENDLY INTEGRATION MANUAL TESTS")
    print("=" * 60)

    api_key = os.getenv("CALENDLY_API_KEY")
    if not api_key:
        print("ERROR: CALENDLY_API_KEY not set")
        print("Set it with: export CALENDLY_API_KEY=your_token")
        return

    async with CalendlyClient() as client:
        # Test 1: Get user info
        print("\n1. Testing get_current_user()...")
        try:
            user = await client.get_current_user()
            print(f"   Success! User: {user.get('name')} ({user.get('email')})")
        except Exception as e:
            print(f"   Failed: {e}")

        # Test 2: Get event types
        print("\n2. Testing get_event_types()...")
        try:
            event_types = await client.get_event_types()
            print(f"   Found {len(event_types)} event types")
            for et in event_types[:3]:
                print(f"   - {et.name} ({et.duration} min)")
        except Exception as e:
            print(f"   Failed: {e}")

        # Test 3: Check availability
        print("\n3. Testing get_available_slots()...")
        event_uri = os.getenv("CALENDLY_EVENT_TYPE_URI")
        if event_uri:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                slots = await client.get_available_slots(
                    event_type_uri=event_uri,
                    start_date=tomorrow,
                    end_date=tomorrow
                )
                print(f"   Found {len(slots)} slots for {tomorrow}")
                if slots:
                    print(f"   First available: {slots[0].start_time}")
            except Exception as e:
                print(f"   Failed: {e}")
        else:
            print("   Skipped: CALENDLY_EVENT_TYPE_URI not set")

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Run manual tests
    asyncio.run(run_manual_tests())
