import pytest
from controllers.topic_controller import TopicController

def test_create_topic():
    c = TopicController()
    topic_id = c.create_topic("Математика")
    topic = c.get_topic(topic_id)
    assert topic.name == "Математика"

def test_rename_topic():
    c = TopicController()
    tid = c.create_topic("Старое")
    c.rename_topic(tid, "Новое")
    assert c.get_topic(tid).name == "Новое"

def test_delete_topic_cascade():
    c = TopicController()
    tid = c.create_topic("Тема")
    c.delete_topic(tid)
    assert c.get_topic(tid) is None
