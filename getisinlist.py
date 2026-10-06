import streamlit as st
from isin_client import SOURCE_URL, fetch_isins, search_contracts


def main():
    st.title('Takasbank VB ISIN list')
    st.caption(f'Data source: {SOURCE_URL}')
    st.caption('Search covers VIS futures contracts in the VB list, not a complete fund–ISIN directory. Data is cached for one hour.')

    @st.cache_data(ttl=3600)
    def getISIN():
        progress = st.progress(0.0)
        return fetch_isins(progress=progress.progress)

    if st.button('Refresh source'):
        getISIN.clear()
    try:
        frame = getISIN()
    except Exception as error:
        st.error(f'Could not load the ISIN list: {error}')
        return
    keyword = st.text_input('Contract name (VIS futures only)')
    st.dataframe(search_contracts(frame, keyword), use_container_width=True)
    st.dataframe(frame, use_container_width=True)


if __name__ == '__main__':
    main()
