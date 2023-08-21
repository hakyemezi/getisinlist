import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

@st.cache_data
def getISIN():
    url = "https://www.takasbank.com.tr/tr/kaynaklar/isin-kodlari/VB"

    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")

    a_tags = soup.find_all("a", rel="noreferrer")
    values = [int(tag.text) for tag in a_tags if tag.text.isdigit()]

    if values:
        max_page_number = max(values)
    else:
        pass

    base_url = "https://www.takasbank.com.tr/tr/kaynaklar/isin-kodlari/VB?page={}"
    all_data = []
    progress_bar = st.progress(0)

    for page_number in range(1, max_page_number + 1):
        url = base_url.format(page_number)
        response = requests.get(url)
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        table = soup.find("table")
        if table:
            df = pd.read_html(str(table))[0]
            all_data.append(df)

        progress_text = f"{int((page_number / max_page_number) * 100)}% completed."
        progress_bar.progress(int((page_number / max_page_number) * 100), text=progress_text)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
    else:
        pass
    return final_df

final_df = getISIN()

search_keyword = st.text_input("Contract Name")

filtered_df = final_df[final_df["Sözleşme Cinsi"].str.contains(search_keyword) & final_df["Sözleşme Cinsi"].str.contains("VIS")]

st.dataframe(filtered_df)

st.dataframe(final_df)
