import streamlit as st
from services.backend_client import call, BackendError

def render():
    st.title("Upload and analyze a lecture")
    st.write("Upload text-based PDF slides or a PowerPoint deck. The backend extracts text and preserves slide numbers.")
    title=st.text_input("Lecture title", key="lecture-title")
    subject=st.text_input("Subject (optional)", key="lecture-subject")
    file=st.file_uploader("Lecture slides", type=["pdf","pptx"], help="Maximum 20 MiB. Scanned image-only PDFs are not OCR processed.", key="lecture-file")
    submitted=st.button("Analyze lecture", type="primary", key="analyze-lecture")
    if submitted:
        if file is None:
            st.error("Choose a PDF or PowerPoint file first.")
            return
        if file.size > 20*1024*1024: st.error("File exceeds the 20 MiB limit."); return
        with st.spinner("Extracting slides and building a lecture index…"):
            try:
                result=call("POST","/lectures/analyze",timeout=180, files={"file":(file.name,file.getvalue(),file.type)}, data={"title":title or file.name,"subject":subject})
                item={**result,"completed_topics":[],"quiz_attempts":0,"quiz_history":[],"missed_topics":[]}
                st.session_state.sessions.append(item); st.session_state.selected_lecture=result["lecture_id"]
                st.success(f"Analyzed {result['slide_count']} slides.")
            except BackendError as exc: st.error(str(exc))
    selected=st.session_state.get("selected_lecture")
    if selected:
        session=next((x for x in st.session_state.sessions if x["lecture_id"]==selected),None)
        if session:
            st.subheader("Analysis preview")
            st.markdown(f"**{session['title']}** · {session.get('subject') or 'Subject not set'} · {session['slide_count']} slides")
            for topic in session.get("topics",[]):
                with st.expander(f"{topic['name']} · slides {', '.join(map(str,topic['slide_refs'])) or '—'}"):
                    st.write("Subtopics: " + (", ".join(topic["subtopics"]) or "None extracted"))
            if session.get("learning_objectives"):
                st.markdown("**Learning objectives**")
                for objective in session["learning_objectives"]: st.markdown(f"- {objective}")
            with st.expander("Extracted text preview"): st.text(session.get("preview",""))
