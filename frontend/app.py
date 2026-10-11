import streamlit as st
from services.backend_client import health
from pages import dashboard, upload, workspace, quiz, progress

st.set_page_config(page_title="AI Lecture Tutor", page_icon="🎓", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1,h2,h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.03em; }
.block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 4rem; }
[data-testid="stMetric"] { background: #f5f8ff; border: 1px solid #e5ebf5; padding: 1rem; border-radius: 14px; }
div.stButton > button[kind="primary"] { border-radius: 10px; }
</style>""", unsafe_allow_html=True)
if "sessions" not in st.session_state: st.session_state.sessions = []
if "selected_lecture" not in st.session_state: st.session_state.selected_lecture = None
if "chat" not in st.session_state: st.session_state.chat = {}
if "nav_page" not in st.session_state: st.session_state.nav_page = "Dashboard"
with st.sidebar:
    st.markdown("# 🎓 Lecture Tutor")
    st.caption("Learn from your own course material")
    page = st.radio("Navigate", ["Dashboard", "Upload & Analyze", "Learning Workspace", "Quiz & Assessment", "Progress & Review"], key="nav_page", label_visibility="collapsed")
    status = health()
    if status.get("status") == "ok":
        st.success("Backend online · " + ("model ready" if status.get("model_loaded") else "model not loaded"))
    elif status.get("status") == "unconfigured": st.warning("Backend not configured")
    else: st.error("Backend offline")
    st.caption("Colab may stop. A public frontend also needs a separately configured backend service.")
if page == "Dashboard": dashboard.render()
elif page == "Upload & Analyze": upload.render()
elif page == "Learning Workspace": workspace.render()
elif page == "Quiz & Assessment": quiz.render()
else: progress.render()
