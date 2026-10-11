import streamlit as st

def render():
    st.title("Progress and review")
    sessions=st.session_state.sessions
    if not sessions: st.info("Your completed topics and quiz history will appear here."); return
    for item in reversed(sessions):
        with st.expander(f"{item['title']} · {item.get('subject') or 'Uncategorized'}"):
            st.markdown(f"**Completed topics:** {', '.join(item.get('completed_topics',[])) or 'None yet'}")
            st.markdown(f"**Quiz attempts:** {item.get('quiz_attempts',0)}")
            if item.get("score"):
                st.markdown(f"**Latest score:** {item['score']['percent']:.0f}% ({item['score']['score']}/{item['score']['total']})")
                st.markdown("**Review next:** "+(", ".join(item.get("missed_topics",[])) or "No missed topics in latest attempt"))
            for index, attempt in enumerate(item.get("quiz_history",[]),1):
                st.caption(f"Attempt {index}: {attempt['score']}/{attempt['total']} ({attempt['percent']:.0f}%)")
            for topic in item.get("topics",[]):
                slides=", ".join(map(str,topic.get("slide_refs",[])))
                st.caption(f"{topic['name']} · slides {slides or '—'}")
