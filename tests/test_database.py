from database.connection import SessionLocal, init_db
from database.repository import ChatRepository

def test_database_crud():
    init_db()
    db = SessionLocal()
    try:
        # Create session
        session = ChatRepository.create_session(db, title="Test Exploration Session")
        assert session.session_id is not None
        assert session.session_title == "Test Exploration Session"

        # Add message
        msg1 = ChatRepository.add_message(
            db=db,
            session_id=session.session_id,
            sender_type="user",
            text_content="Hello, I feel stressed today."
        )
        assert msg1.message_id is not None
        assert msg1.text_content == "Hello, I feel stressed today."

        # Add assistant response
        msg2 = ChatRepository.add_message(
            db=db,
            session_id=session.session_id,
            sender_type="assistant",
            text_content="I am here for you. Let's take a deep breath.",
            has_media=True,
            media_type="audio",
            media_url="/uploads/audio/test.mp3"
        )
        assert msg2.has_media is True

        # Fetch history
        history = ChatRepository.get_session_messages(db, session.session_id)
        assert len(history) == 2
        assert history[0].sender_type == "user"
        assert history[1].sender_type == "assistant"
    finally:
        db.close()
