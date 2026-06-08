import pytest
from datetime import datetime, timedelta

from controllers.analytics_controller import AnalyticsController
from controllers.session_controller import SessionController


@pytest.fixture
def analytics():
    return AnalyticsController()


@pytest.fixture
def sessions():
    return SessionController()


def test_daily_stats(analytics, sessions):
    # создаём 2 сессии за сегодня
    sid1 = sessions.start_session(topic_id=1)
    sessions.end_session(sid1, duration=25, focus=80, energy=70, interest=90)

    sid2 = sessions.start_session(topic_id=1)
    sessions.end_session(sid2, duration=15, focus=60, energy=50, interest=70)

    stats = analytics.get_daily_stats(datetime.now())

    assert stats["total_sessions"] == 2
    assert stats["total_minutes"] == 40
    assert stats["avg_focus"] == 70  # (80 + 60) / 2


def test_weekly_stats(analytics, sessions):
    # создаём сессию 3 дня назад
    date = datetime.now() - timedelta(days=3)
    sid = sessions._create_manual_session(
        topic_id=1,
        start=date,
        end=date + timedelta(minutes=30),
        duration=30,
        focus=50,
        energy=60,
        interest=70
    )

    stats = analytics.get_weekly_stats(datetime.now())

    assert stats["total_sessions"] >= 1
    assert stats["total_minutes"] >= 30


def test_topic_stats(analytics, sessions):
    # создаём сессии по разным темам
    sid1 = sessions.start_session(topic_id=1)
    sessions.end_session(sid1, duration=20, focus=80, energy=70, interest=90)

    sid2 = sessions.start_session(topic_id=2)
    sessions.end_session(sid2, duration=10, focus=60, energy=50, interest=70)

    stats = analytics.get_topic_stats()

    assert 1 in stats
    assert 2 in stats
    assert stats[1]["minutes"] == 20
    assert stats[2]["minutes"] == 10
