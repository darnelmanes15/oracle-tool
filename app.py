import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# --- 1. Page Configuration ---
st.set_page_config(page_title="The Oracle", page_icon="🔮")

st.title("🔮 The Oracle")
st.markdown("Ask me anything about your uploaded manuals.")

# --- 2. Sidebar: Setup & Files ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check if the key is in Streamlit Secrets (The Cloud Vault)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("Authentication: System Key ✅")
    else:
        # If running locally or no secret found, ask the user
        api_key = st.text_input("Google API Key", type="password")

# --- 3. Chat Logic ---
# Initialize chat history in memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. Processing the Question ---
if prompt := st.chat_input("How do I reset the wifi?"):
    
    if not api_key:
        st.error("Please enter an API Key in the sidebar.")
        st.stop()
        
    if not uploaded_files:
        st.error("Please upload at least one PDF manual.")
        st.stop()

    # Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Read the PDFs on the fly
    combined_text = ""
    for pdf in uploaded_files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            combined_text += page.extract_text() or ""

    # Prepare the Prompt for Gemini
    full_prompt = f"""
    You are an expert technical support assistant called 'The Oracle'.
    Answer the question based ONLY on the following context.
    
    CONTEXT:
    {combined_text}
    
    QUESTION:
    {prompt}
    """

    # Get Answer from Gemini
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        with st.chat_message("assistant"):
            with st.spinner("Consulting the scrolls..."):
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                
        # Save Assistant Message
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"Error: {e}")
