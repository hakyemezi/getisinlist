from pathlib import Path
import pandas as pd
import pytest
import requests
from isin_client import fetch_isins, search_contracts

TABLE = '<table><tr><th>Sözleşme Cinsi</th><th>Name</th></tr><tr><td>VIS</td><td>[test]</td></tr></table>'


class Session:
    def __init__(self, pages): self.pages, self.calls = iter(pages), []
    def get(self, url, timeout):
        self.calls.append((url, timeout))
        html = next(self.pages)
        class Response:
            content = html.encode()
            def raise_for_status(self): pass
        return Response()


def test_no_pagination_is_one_page():
    session = Session([TABLE])
    frame = fetch_isins(session=session)
    assert len(frame) == 1
    assert len(session.calls) == 1
    assert session.calls[0][1] == 30


def test_missing_middle_page_does_not_return_partial():
    session = Session([TABLE + '<a href="?page=2">2</a>', '<html>Unavailable</html>'])
    with pytest.raises(ValueError, match='page 2'): fetch_isins(session=session)


def test_follows_next_page_links():
    session = Session([TABLE + '<a href="?page=2">Next</a>',
                       TABLE + '<a href="?page=3">Next</a>', TABLE])
    assert len(fetch_isins(session=session)) == 1
    assert len(session.calls) == 3


def test_literal_search_handles_regex_and_missing_values():
    frame = pd.DataFrame({'Sözleşme Cinsi': ['VIS', 'VIS', None], 'Name': ['[test]', None, '[test]']})
    assert search_contracts(frame, '[').index.tolist() == [0]
    assert search_contracts(frame, '').empty


def test_timeout_propagates():
    class Failed:
        def get(self, *a, **kw): raise requests.Timeout('timeout')
    with pytest.raises(requests.Timeout): fetch_isins(session=Failed())


def test_app_reports_source_failure(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import isin_client
    def fail(**kwargs): raise ValueError('Source unavailable')
    monkeypatch.setattr(isin_client, 'fetch_isins', fail)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'getisinlist.py').run()
    assert not app.exception
    assert 'Source unavailable' in app.error[0].value
