import streamlit as st
import requests

st.title("🎨 Image Style Converter")

uploaded = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])
style = st.selectbox("Select Style", ["anime", "ghibli", "sketch", "portrait"])

if uploaded and st.button("Convert"):
    files = {"image": uploaded}
    data = {"style": style}

    res = requests.post("http://127.0.0.1:5000/convert", files=files, data=data)

    if res.status_code == 200:
        st.image(res.content)