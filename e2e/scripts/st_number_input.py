import streamlit as st


i1 = st.number_input("number input 1")
st.write('value 1: "', i1, '"')

i2 = st.number_input("number input 2", value=1)
st.write('value 2: "', i2, '"')

i3 = st.number_input("number input 3", 1, 10)
st.write('value 3: "', i3, '"')

i4 = st.number_input("number input 4", step=2)
st.write('value 4: "', i4, '"')

i5 = st.number_input("number input 5", max_value=10)
st.write('value 5: "', i5, '"')

i6 = st.number_input("number input 6", disabled=True)
st.write('value 6: "', i6, '"')

if st._is_running_with_streamlit:

    def on_change():
        st.session_state.number_input_changed = True

    st.number_input("number input 7", key="number_input7", on_change=on_change)
    st.write('value 7: "', st.session_state.number_input7, '"')
    st.write("number input changed:", "number_input_changed" in st.session_state)
