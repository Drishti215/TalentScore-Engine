import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import plotly.graph_objects as go
import io

st.set_page_config(page_title="TalentScore Engine", layout="wide")
st.title(" TalentScore Engine – Resume Checker Dashboard")

# --- Helper Functions ---
def get_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return df[name]
    return None

def safe_read_csv(uploaded_file, name):
    if uploaded_file is None:
        return pd.DataFrame()
    try:
        df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8-sig")))
        return df
    except Exception as e:
        st.error(f"Error reading {name} file: {e}")
        return pd.DataFrame()

# --- Sidebar Uploads ---
st.sidebar.markdown("##  Upload Your Files")
resume_file = st.sidebar.file_uploader(" Resume CSV", type=["csv"])
job_file = st.sidebar.file_uploader(" Job Description CSV", type=["csv"])
resume_sections_file = st.sidebar.file_uploader(" Resume Sections CSV", type=["csv"])

# --- Tabs Layout ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " ATS Match",
    " Skill Gap",
    " Recruiter Attention",
    " Keyword Insights",
    " AI Suggestions"
])

overall_score = 0

# --- ATS Match Tab ---
with tab1:
    st.subheader("ATS Match Analysis")
    resumes = safe_read_csv(resume_file, "Resume")
    jobs = safe_read_csv(job_file, "Job")
    if not resumes.empty and not jobs.empty:
        resume_texts = get_column(resumes, ["resume_text", "text", "resume"])
        job_texts = get_column(jobs, ["job_description", "description", "job"])
        if resume_texts is not None and job_texts is not None:
            results = []
            for rid, rtext in resume_texts.items():
                for jid, jtext in job_texts.items():
                    rwords = set(str(rtext).lower().split())
                    jwords = set(str(jtext).lower().split())
                    score = len(rwords & jwords) / max(len(jwords), 1)
                    results.append({"Resume": rid+1, "Job": jid+1, "Match %": round(score*100, 2)})
            df_results = pd.DataFrame(results)
            col1, col2 = st.columns([2,1])
            with col1:
                st.dataframe(df_results, use_container_width=True)
            with col2:
                avg_match = df_results["Match %"].mean()
                st.metric(label="Average ATS Match", value=f"{avg_match:.2f}%")
                overall_score += avg_match * 0.4

# --- Skill Gap Tab ---
with tab2:
    st.subheader("Skill Gap Analysis")
    resumes = safe_read_csv(resume_file, "Resume")
    jobs = safe_read_csv(job_file, "Job")
    if not resumes.empty and not jobs.empty:
        resume_texts = get_column(resumes, ["resume_text", "text", "resume"])
        job_texts = get_column(jobs, ["job_description", "description", "job"])
        if resume_texts is not None and job_texts is not None:
            gap_results = []
            for rid, rtext in resume_texts.items():
                for jid, jtext in job_texts.items():
                    resume_skills = set(str(rtext).lower().split())
                    job_skills = set(str(jtext).lower().split())
                    missing = job_skills - resume_skills
                    extra = resume_skills - job_skills
                    gap_results.append({
                        "Resume": rid+1,
                        "Job": jid+1,
                        "Missing Skills": ", ".join(missing) if missing else "None",
                        "Extra Skills": ", ".join(extra) if extra else "None"
                    })
            st.dataframe(pd.DataFrame(gap_results), use_container_width=True)
            overall_score += 30 if gap_results[0]["Missing Skills"] == "None" else 15

# --- Recruiter Attention Tab ---
with tab3:
    st.subheader("Recruiter Attention Map")
    sections = safe_read_csv(resume_sections_file, "Resume Sections")
    if not sections.empty and "section" in sections.columns and "text" in sections.columns:
        section_lengths = sections.groupby("section")["text"].apply(lambda x: x.str.len().sum())
        total = section_lengths.sum()
        attention = (section_lengths / total * 100).round(2)
        col1, col2 = st.columns([2,1])
        with col1:
            st.dataframe(attention.reset_index(), use_container_width=True)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(attention, labels=attention.index, autopct='%1.1f%%', startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
        for section, pct in attention.items():
            if pct < 10:
                st.warning(f" Add more detail to {section} ({pct}%).")
            elif pct > 50:
                st.info(f"ℹ️ {section} dominates recruiter attention ({pct}%).")
            else:
                st.success(f"{section} section is balanced ({pct}%).")
        overall_score += 30

# --- Keyword Insights Tab ---
with tab4:
    st.subheader("Keyword Insights")
    resumes = safe_read_csv(resume_file, "Resume")
    jobs = safe_read_csv(job_file, "Job")
    if not resumes.empty and not jobs.empty:
        resume_texts = get_column(resumes, ["resume_text", "text", "resume"])
        job_texts = get_column(jobs, ["job_description", "description", "job"])
        if resume_texts is not None and job_texts is not None:
            resume_text = " ".join(resume_texts.astype(str)).lower()
            job_text = " ".join(job_texts.astype(str)).lower()
            resume_counts = Counter(resume_text.split())
            job_counts = Counter(job_text.split())
            common_keywords = set(resume_counts.keys()) & set(job_counts.keys())
            missing_keywords = set(job_counts.keys()) - set(resume_counts.keys())
            top_common = sorted([(w, resume_counts[w]) for w in common_keywords], key=lambda x: -x[1])[:10]
            if top_common:
                st.bar_chart(pd.DataFrame(top_common, columns=["Keyword", "Count"]).set_index("Keyword"))
            else:
                st.info("No common keywords found.")
            st.write("### Missing Keywords")
            st.write(", ".join(list(missing_keywords)[:10]) if missing_keywords else "None")

# --- AI Suggestions Tab ---
with tab5:
    st.subheader("AI Suggestions")
    suggestions = []
    if overall_score < 60:
        suggestions.append(" Improve ATS match by tailoring resume keywords.")
    elif overall_score >= 80:
        suggestions.append(" Resume is strong! Add measurable achievements.")
    else:
        suggestions.append(" Resume looks balanced. Keep refining with specifics.")
    for s in suggestions:
        st.write(f"- {s}")

# --- Gauge Chart for Overall Score ---
st.markdown("##  Overall Resume Score")
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=overall_score,
    title={'text': "TalentScore"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "green"},
        'steps': [
            {'range': [0, 50], 'color': "lightcoral"},
            {'range': [50, 75], 'color': "gold"},
            {'range': [75, 100], 'color': "lightgreen"}
        ],
    }
))
st.plotly_chart(fig, use_container_width=True)

# --- Sidebar Overall Score ---
st.sidebar.markdown("##  TalentScore")
st.sidebar.metric(label="Overall Resume Score", value=f"{round(overall_score,2)}/100")
