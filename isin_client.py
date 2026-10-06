"""Read Takasbank's VB list without depending on the web interface."""
from io import StringIO
from urllib.parse import urlparse, parse_qs

import pandas as pd
import requests
from bs4 import BeautifulSoup

SOURCE_URL = 'https://www.takasbank.com.tr/tr/kaynaklar/isin-kodlari/VB'


def _page(session, url):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')


def fetch_isins(progress=None, session=None):
    if session is None:
        with requests.Session() as session:
            return fetch_isins(progress, session)
    first = _page(session, SOURCE_URL)
    pages = {1}
    def discover(soup):
        for anchor in soup.select('a[href]'):
            link = urlparse(anchor['href'])
            if link.path and link.path.rstrip('/') != urlparse(SOURCE_URL).path:
                continue
            for value in parse_qs(link.query).get('page', []):
                if value.isdigit():
                    pages.add(int(value))
    discover(first)
    frames, number = [], 1
    while number <= max(pages):
        if max(pages) > 500 or min(pages) < 1:
            raise ValueError('Unexpected pagination; refusing an unbounded crawl.')
        soup = first if number == 1 else _page(session, f'{SOURCE_URL}?page={number}')
        discover(soup)
        table = soup.find('table')
        if table is None:
            raise ValueError(f'No ISIN table on page {number}; the source may have changed.')
        frame = pd.read_html(StringIO(str(table)))[0]
        if frame.empty or 'Sözleşme Cinsi' not in frame:
            raise ValueError(f'Unexpected ISIN table on page {number}.')
        frames.append(frame)
        if progress:
            progress(number / max(pages))
        number += 1
    return pd.concat(frames, ignore_index=True).drop_duplicates(ignore_index=True)


def search_contracts(frame, keyword):
    if not keyword:
        return frame.iloc[:0]
    futures = frame['Sözleşme Cinsi'].astype('string').str.contains('VIS', case=False, na=False, regex=False)
    matches = frame.astype('string').apply(
        lambda column: column.str.contains(keyword, case=False, na=False, regex=False)).any(axis=1)
    return frame[futures & matches]
