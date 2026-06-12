import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(page_title="TalentScore Engine", layout="wide")
st.title("TalentScore Engine – Resume Checker Dashboard")

# --- Helper to handle flexible column names ---
def get_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return df[name]
    return None

# --- ATS Resume Checker ---
resume_file = st.file_uploader("Upload Resume CSV (with resume_text)", type=["csv"])
job_file = st.file_uploader("Upload Job Description CSV (with job_description)", type=["csv"])

overall_score = 0

if resume_file and job_file:
    resumes = pd.read_csv(resume_file)
    jobs = pd.read_csv(job_file)

    resume_texts = get_column(resumes, ["resume_text", "text", "resume"])
    job_texts = get_column(jobs, ["job_description", "description", "job"])

    if resume_texts is not None and job_texts is not None:
        results = []
        for rid, rtext in resume_texts.items():
            for jid, jtext in job_texts.items():
                rwords = set(str(rtext).lower().split())
                jwords = set(str(jtext).lower().split())
                score = len(rwords & jwords) / max(len(jwords), 1)
                results.append({"resume_id": rid+1, "job_id": jid+1, "match_score": round(score, 4)})

        st.subheader("ATS Match Scores")
        st.dataframe(pd.DataFrame(results))

        # --- Resume-to-Interview Probability Score ---
        prob_results = []
        for row in results:
            score = row["match_score"]
            ats_pass = min(100, round(score * 100, 2))
            shortlist = min(100, round(score * 80, 2))
            interview = min(100, round(score * 60, 2))
            prob_results.append({
                "resume_id": row["resume_id"],
                "job_id": row["job_id"],
                "ATS Pass %": ats_pass,
                "Shortlist %": shortlist,
                "Interview %": interview
            })
        st.subheader("Resume-to-Interview Probability Score")
        st.dataframe(pd.DataFrame(prob_results))

        # --- Skill Gap Analysis ---
        gap_results = []
        for rid, rtext in resume_texts.items():
            for jid, jtext in job_texts.items():
                resume_skills = set(str(rtext).lower().split())
                job_skills = set(str(jtext).lower().split())
                missing = job_skills - resume_skills
                extra = resume_skills - job_skills
                gap_results.append({
                    "resume_id": rid+1,
                    "job_id": jid+1,
                    "Missing Skills": ", ".join(missing) if missing else "None",
                    "Extra Skills": ", ".join(extra) if extra else "None"
                })
        st.subheader("Skill Gap Analysis")
        st.dataframe(pd.DataFrame(gap_results))

        # --- Overall Resume Score ---
        ats_component = results[0]["match_score"] * 40
        gap_component = 30 if gap_results[0]["Missing Skills"] == "None" else 15
        attention_component = 30  # refined later with recruiter attention
        overall_score = min(100, round(ats_component + gap_component + attention_component, 2))

        st.markdown("## Overall Resume Score")
        st.metric(label="Resume Score", value=f"{overall_score}/100")

        # --- Keyword Density Heatmap ---
        resume_text = " ".join(resume_texts.astype(str)).lower()
        job_text = " ".join(job_texts.astype(str)).lower()
        resume_words = resume_text.split()
        job_words = job_text.split()

        resume_counts = Counter(resume_words)
        job_counts = Counter(job_words)

        common_keywords = set(resume_counts.keys()) & set(job_counts.keys())
        missing_keywords = set(job_counts.keys()) - set(resume_counts.keys())

        st.subheader("Keyword Insights")
        st.write("### Top Common Keywords")
        top_common = sorted([(w, resume_counts[w]) for w in common_keywords], key=lambda x: -x[1])[:10]
        if top_common:
            st.bar_chart(pd.DataFrame(top_common, columns=["Keyword", "Count"]).set_index("Keyword"))
        else:
            st.info("No common keywords found.")

        st.write("### Missing Keywords (expected in job description)")
        st.write(", ".join(list(missing_keywords)[:10]) if missing_keywords else "None")

        # --- AI Suggestions ---
        st.subheader("AI Suggestions")
        suggestions = []
        if gap_results[0]["Missing Skills"] != "None":
            suggestions.append(f"Add missing skills: {gap_results[0]['Missing Skills']}")
        if overall_score < 60:
            suggestions.append("Improve ATS match by tailoring resume keywords to job description.")
        if overall_score >= 80:
            suggestions.append("Your resume is strong! Focus on measurable achievements to stand out.")
        if not suggestions:
            suggestions.append("✅ Resume looks balanced. Keep refining with specific achievements.")

        for s in suggestions:
            st.write(f"- {s}")

# --- Recruiter Attention Map ---
resume_sections_file = st.file_uploader("Upload Resume Sections CSV (with section,text)", type=["csv"])

if resume_sections_file:
    resumes = pd.read_csv(resume_sections_file)

    if "section" not in resumes.columns or "text" not in resumes.columns:
        st.error("CSV must have columns: section,text")
    else:
        section_lengths = resumes.groupby("section")["text"].apply(lambda x: x.str.len().sum())
        total = section_lengths.sum()
        attention = (section_lengths / total * 100).round(2)

        st.subheader("Recruiter Attention Map")
        col1, col2 = st.columns([2,1])
        with col1:
            st.dataframe(attention.reset_index())
        with col2:
            fig, ax = plt.subplots()
            ax.pie(attention, labels=attention.index, autopct='%1.1f%%', startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

        st.subheader("Section Ratings")
        for section, pct in attention.items():
            st.write(f"{section}: {pct}%")
            st.progress(int(pct))

        st.subheader("Highlights & Suggestions")
        for section, pct in attention.items():
            if pct < 10:
                st.warning(f"⚠️ Add more detail to {section} (currently {pct}%).")
            elif pct > 50:
                st.info(f"ℹ️ {section} dominates recruiter attention ({pct}%). Consider balancing.")
            else:
                st.success(f"✅ {section} section is balanced ({pct}%).")
