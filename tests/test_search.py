from controllers.search_controller import SearchController

def test_search_notes():
    s = SearchController()
    results = s.search("тест")
    assert isinstance(results, list)
