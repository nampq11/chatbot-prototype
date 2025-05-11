import streamlit as st

def load_css(filepath: str):
    with open(filepath, 'r') as file:
        st.markdown(f'<style>{file.read()}</style>', unsafe_allow_html=True) 