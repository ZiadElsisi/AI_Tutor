import streamlit as st
from services.backend_client import call, BackendError

def render():
    st.title("Quiz and assessment")
    sessions=st.session_state.sessions
    if not sessions: st.info("Upload a lecture to generate a quiz."); return
    labels={x["title"]+" · "+x["lecture_id"][:6]:x for x in sessions}
    selected=st.selectbox("Lecture",list(labels)); lecture=labels[selected]
    topics=[x["name"] for x in lecture.get("topics",[])]
    a,b,c=st.columns(3)
    count=a.slider("Questions",1,10,5); difficulty=b.selectbox("Difficulty",["easy","medium","hard"]); topic=c.selectbox("Topic",["All topics"]+topics)
    if st.button("Generate quiz",type="primary"):
        with st.spinner("Writing questions from your slides…"):
            try:
                data=call("POST",f"/lectures/{lecture['lecture_id']}/quiz",timeout=120,json={"count":count,"difficulty":difficulty,"topic":None if topic=="All topics" else topic})
                st.session_state.active_quiz={"lecture_id":lecture["lecture_id"],"quiz_id":data["quiz_id"],"questions":data["questions"]}
            except BackendError as exc: st.error(str(exc))
    quiz=st.session_state.get("active_quiz")
    if quiz and quiz["lecture_id"]==lecture["lecture_id"]:
        with st.form("quiz-answers"):
            answers=[]
            for i,q in enumerate(quiz["questions"]):
                st.markdown(f"**{i+1}. {q['question']}**")
                answer=st.radio("Choose an answer",range(len(q["options"])),format_func=lambda x,opts=q["options"]:opts[x],key=f"q-{quiz['quiz_id']}-{i}",label_visibility="collapsed")
                answers.append(answer)
                st.caption(f"{q['difficulty'].capitalize()} · {q['topic']} · Slides {', '.join(map(str,q['slide_refs'])) or '—'}")
            submitted=st.form_submit_button("Submit answers",type="primary")
        if submitted:
            try:
                result=call("POST",f"/lectures/{lecture['lecture_id']}/evaluate",json={"quiz_id":quiz["quiz_id"],"answers":answers})
                st.session_state.last_result=result; st.session_state.last_quiz_key=lecture["lecture_id"]
                lecture["quiz_attempts"]+=1; lecture["score"]=result; lecture["missed_topics"]=result["suggested_review_topics"]
                lecture.setdefault("quiz_history",[]).append(result)
            except BackendError as exc: st.error(str(exc))
    result=st.session_state.get("last_result")
    if result and st.session_state.get("last_quiz_key")==lecture["lecture_id"]:
        st.metric("Score",f"{result['score']} / {result['total']} ({result['percent']:.0f}%)")
        for i,item in enumerate(result["feedback"]):
            status = "✅ Correct" if item["correct"] else f"↩️ Review {item['topic']}"
            st.markdown(f"{status} · **Question {i+1}**")
            st.write(item["explanation"])
            if item["slide_refs"]: st.caption("Review slides: "+", ".join(map(str,item["slide_refs"])))
        if result["suggested_review_topics"]: st.info("Suggested review: "+", ".join(result["suggested_review_topics"]))
