# app.py
import streamlit as st
import requests

st.set_page_config(page_title="Multi-Modal Assistant", layout="centered")
st.title("🧠 Multi-Modal Assistant (Text + Image)")

# Input fields
query = st.text_input("Enter your question (optional):", "")
uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg", "webp"])

if st.button("Ask", type="primary"):
    if query.strip() == "" and uploaded_file is None:
        st.warning("Please enter a question or upload an image.")
    else:
        with st.spinner("Thinking..."):
            try:
                files = None
                data = {"question": query}

                if uploaded_file is not None:
                    files = {
                        "image": (uploaded_file.name, uploaded_file, uploaded_file.type)
                    }

                response = requests.post(
                    "http://127.0.0.1:8000/multimodal-query",
                    data=data,
                    files=files
                )

                if response.status_code == 200:
                    result = response.json()
                    if "response" in result:
                        st.subheader("Response")
                        st.write(result["response"])
                    else:
                        st.error("No response found: " + str(result))
                else:
                    st.error(f"Request failed with status {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"Error: {str(e)}")
