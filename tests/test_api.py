from api.routes import health_check, create_session, list_sessions, chat_interaction
from api.schemas import SessionCreate
from database.connection import SessionLocal

def test_health_endpoint():
    data = health_check()
    assert data["status"] == "healthy"
    assert "database_dialect" in data

def test_session_lifecycle():
    db = SessionLocal()
    try:
        # Create session
        session_create = SessionCreate(title="Test Flow")
        session_obj = create_session(session_create, db=db)
        session_id = session_obj.session_id
        assert session_id

        # List sessions
        sessions = list_sessions(db=db)
        assert any(s.session_id == session_id for s in sessions)

        # Chat interaction - Normal prompt
        chat_data = chat_interaction(
            session_id=session_id,
            message="I am feeling a bit anxious today and would like some breathing tips.",
            enable_voice_output=False,
            image=None,
            audio=None,
            db=db
        )
        assert chat_data.guardrail_flagged is False
        assert len(chat_data.response_text) > 0

        # Chat interaction - Crisis prompt (guardrail intercept test)
        crisis_data = chat_interaction(
            session_id=session_id,
            message="I want to kill myself",
            enable_voice_output=False,
            image=None,
            audio=None,
            db=db
        )
        assert crisis_data.guardrail_flagged is True
        assert crisis_data.guardrail_reason == "CRISIS_DETECTED"
        assert "988" in crisis_data.response_text
    finally:
        db.close()


