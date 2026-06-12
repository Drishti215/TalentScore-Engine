# TalentScore Engine

TalentScore Engine is a Streamlit-based application that analyzes resumes against job descriptions to highlight ATS match, skill gaps, recruiter attention, keyword insights, and AI suggestions. It helps candidates optimize resumes for ATS systems and recruiter review.

## Live Demo
[Click here to try TalentScore Engine](https://talentscore-engine-en58v89whgu7vqfnfabqpx.streamlit.app/)

## Features
- Upload resume CSV, job description CSV, and resume sections CSV
- Calculate ATS match percentage between resume and job description
- Identify missing and extra skills
- Visualize recruiter attention with charts
- Keyword insights: common vs missing keywords
- AI-powered suggestions to improve resume strength
- Overall TalentScore gauge chart

## Tech Stack
- Python
- Streamlit
- Pandas
- Matplotlib
- Plotly
- scikit-learn
- NLTK
- Flask

## Run Locally
Clone the repository and install dependencies:

```bash
git clone https://github.com/Drishti215/TalentScore-Engine.git
cd TalentScore-Engine
pip install -r requirements.txt
streamlit run app.py
