import streamlit as st

c1 = st.color_picker("Default Color")
st.write("Color 1", c1)

c2 = st.color_picker("New Color", "#EB144C")
st.write("Color 2", c2)

c3 = st.color_picker("Disabled", disabled=True)
st.write("Color 3", c3)
