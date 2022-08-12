import streamlit as st
from datetime import datetime
from datetime import time

w1 = st.time_input("Label 1", time(8, 45))
st.write("Value 1:", w1)

w2 = st.time_input("Label 2", datetime(2019, 7, 6, 21, 15))
st.write("Value 2:", w2)

w3 = st.time_input("Label 3", time(8, 45), disabled=True)
st.write("Value 3:", w3)

if st._is_running_with_streamlit:

    def on_change():
        st.session_state.time_input_changed = True

    st.time_input("Label 4", key="time_input4", on_change=on_change)

    st.write("Value 4:", st.session_state.time_input4)
    st.write("time input changed:", "time_input_changed" in st.session_state)
