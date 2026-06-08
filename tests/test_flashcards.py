from controllers.flashcard_controller import FlashcardController

def test_create_qa_card():
    c = FlashcardController()
    cid = c.create_flashcard(1, "qa", "Вопрос", "Ответ")
    card = c.get_flashcard(cid)
    assert card.answer == "Ответ"
