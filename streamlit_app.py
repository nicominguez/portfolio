import streamlit as st

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


st.set_page_config(page_title="Nicolas Minguez Aguirre")

pg = st.navigation(
    {
        "Projects": [st.Page("blackjack_st.py", title="Blackjack Simulator"), 
                     st.Page("intro_stat_st.py", title="Random Variables")]
    }
)
pg.run()