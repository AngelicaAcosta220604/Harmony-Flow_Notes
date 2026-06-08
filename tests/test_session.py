from controllers.session_controller import SessionController

def test_start_session():
    c = SessionController()
    sid = c.start_session(topic_id=1)
    session = c.get_session(sid)
    assert session.is_active is True
