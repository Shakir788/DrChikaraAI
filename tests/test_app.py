import streamlit as st
import os

def test_api_key():
    assert st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY"), "API Key missing"
    print("API Key test passed!")

if __name__ == "__main__":
    test_api_key()