from urllib.parse import quote_plus
import re
import streamlit as st
from services.backend_client import call, BackendError

def render():
    st.title("Learning workspace")
    sessions=st.session_state.sessions
    if not sessions: st.info("Upload a lecture first."); return
    labels={x["title"]+" · "+x["lecture_id"][:6]:x for x in sessions}
    current=next((x for x in sessions if x["lecture_id"]==st.session_state.get("selected_lecture")),sessions[-1])
    selected_label=next(label for label,item in labels.items() if item["lecture_id"]==current["lecture_id"])
    chosen=st.selectbox("Lecture",list(labels),index=list(labels).index(selected_label))
    current=labels[chosen]; st.session_state.selected_lecture=current["lecture_id"]
    left,center,right=st.columns([.95,1.25,1.3],gap="medium")
    with left:
        st.subheader("Lecture outline")
        topics=current.get("topics",[])
        topic_names=[x["name"] for x in topics] or [current["title"]]
        topic=st.radio("Choose a topic",topic_names,label_visibility="collapsed",key=f"topic-{current['lecture_id']}")
        matched=next((x for x in topics if x["name"]==topic),{})
        st.caption("Slides: "+(", ".join(map(str,matched.get("slide_refs",[]))) or "see retrieved citations"))
        done=topic in current.get("completed_topics",[])
        if st.button("✓ Mark topic complete" if not done else "Completed", disabled=done):
            current.setdefault("completed_topics",[]).append(topic); st.rerun()
    with center:
        st.subheader("Watch and explore")
        st.caption(f"Search links for **{topic}**")
        search=quote_plus(f"{topic} {current.get('subject') or ''} lecture explanation")
        st.link_button("Search YouTube for this topic",f"https://www.youtube.com/results?search_query={search}",use_container_width=True)
        video=st.text_input("Optional YouTube video URL",key=f"video-url-{current['lecture_id']}")
        match=re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{11})",video)
        if match: st.video(f"https://www.youtube.com/watch?v={match.group(1)}")
        elif video: st.caption("Enter a standard YouTube watch, share, embed, or shorts URL to embed it.")
        st.caption("Search results are provided by YouTube. Transcripts are never assumed; paste available transcript text in the tutor panel if you have access to it.")
    with right:
        st.subheader("AI tutor")
        mode=st.selectbox("Explanation style",["detailed","simple","example","summary"],format_func=lambda x:{"detailed":"Detailed explanation","simple":"Simple explanation","example":"Worked example","summary":"Summarize topic"}[x])
        key=current["lecture_id"]
        history=st.session_state.chat.setdefault(key,[])
        for message in history[-8:]:
            with st.chat_message(message["role"]): st.markdown(message["content"])
        transcript=st.text_area("Optional transcript text",max_chars=12000,placeholder="Paste transcript text only if you have access to it.",key=f"transcript-{current['lecture_id']}")
        question=st.chat_input("Ask about your lecture")
        if question:
            history.append({"role":"user","content":question})
            with st.chat_message("user"): st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Finding relevant slide passages…"):
                    try:
                        data=call("POST",f"/lectures/{key}/ask",timeout=120,json={"question":question,"topic":topic,"mode":mode,"history":history[-8:],"transcript":transcript or None})
                        st.markdown(data["answer"])
                        if data.get("citations"):
                            with st.expander("Slide citations"):
                                for citation in data["citations"]: st.markdown(f"**Slide {citation['slide']}** — {citation['excerpt']}")
                        if data.get("supplementary_note"): st.caption(data["supplementary_note"])
                        history.append({"role":"assistant","content":data["answer"]})
                        del history[:-16]
                    except BackendError as exc: st.error(str(exc)); history.pop()
