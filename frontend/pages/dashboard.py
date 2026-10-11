import streamlit as st
from services.backend_client import health

def _open_workspace(lecture_id):
    st.session_state.selected_lecture=lecture_id
    st.session_state.nav_page="Learning Workspace"

def render():
    st.title("Your learning, organized")
    st.write("Turn lecture slides into focused study sessions, grounded explanations, and quick checks for understanding.")
    sessions = st.session_state.sessions
    scores = [attempt["percent"] for x in sessions for attempt in x.get("quiz_history",[])]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Lectures studied", len(sessions))
    c2.metric("Quiz attempts", sum(x.get("quiz_attempts",0) for x in sessions))
    c3.metric("Average quiz score", f"{sum(scores)/len(scores):.0f}%" if scores else "—")
    missed = list(dict.fromkeys(t for x in sessions for t in (x.get("missed_topics") or [])))
    c4.metric("Topics to revisit", len(missed))
    a,b = st.columns([1.35,1])
    with a:
        st.subheader("Recent lectures")
        if not sessions: st.info("No lectures yet. Upload slides to create your first learning session.")
        for session in reversed(sessions[-5:]):
            with st.container(border=True):
                st.markdown(f"**{session['title']}** · {session.get('subject') or 'Uncategorized'}")
                st.caption(f"{len(session.get('topics', []))} topics · {session.get('slide_count', 0)} slides")
                st.button("Open workspace", key=f"open-{session['lecture_id']}", on_click=_open_workspace, args=(session["lecture_id"],))
    with b:
        st.subheader("Learning progress")
        total = sum(len(x.get("topics",[])) for x in sessions)
        done = sum(len(x.get("completed_topics",[])) for x in sessions)
        st.progress(done/total if total else 0)
        st.caption(f"{done} of {total} topics marked complete")
        if missed: st.markdown("**Suggested review**\n\n"+"\n".join(f"- {x}" for x in missed[:6]))
        h=health()
        st.subheader("AI service")
        if h.get("status")=="ok" and h.get("model_loaded"): st.success(f"Ready on {h.get('device','runtime')}")
        else: st.warning("For AI analysis, start the configured backend and confirm BACKEND_URL and BACKEND_SECRET in app secrets.")
