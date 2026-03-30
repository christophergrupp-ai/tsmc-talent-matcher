import streamlit as st
import pandas as pd
import re
import os
from pdfminer.high_level import extract_text

# --- SCORING LOGIC ---
def score_candidate(text):
    text = text.lower()
    score = 50
    reasons = []

    # 1. Elite Match: Fab / Semi (+25)
    if any(w in text for w in ['fab', 'semiconductor', 'cleanroom', 'wafer', 'advanced manufacturing']):
        score += 25
        reasons.append("Elite Industry Exp")

    # 2. Strong Archetype: Data/Call Center (+15)
    if any(w in text for w in ['data processing', 'call center', 'data entry', 'military']):
        score += 15
        reasons.append("Strong Archetype")

    # 3. Numerical Experience (+10)
    # New category for candidates used to working with numbers/audits
    if any(w in text for w in ['accounting', 'bookkeeping', 'audit', 'financial', 'mathematics', 'statistical']):
        score += 10
        reasons.append("Numerical/Detail Exp")

    # 4. Cultural & Training (+20)
    if any(w in text for w in ['bilingual', 'spanish', 'mandarin', 'trainer', 'certification', 'testing']):
        score += 20
        reasons.append("Culture/Training Fit")

    # 5. Stability Penalty (-20)
    if "2025" in text or "2026" in text:
        score -= 20
        reasons.append("Recent Job Switch Risk")

    # 6. Overqualified/STEM Penalty (-30)
    if any(w in text for w in ['masters', 'phd', 'engineering', 'biology', 'physics', 'chemistry']):
        score -= 30
        reasons.append("STEM/Overqualified Flag")

    return score, " | ".join(reasons)

# --- UI SETUP ---
st.set_page_config(page_title="TSMC Talent Matcher", layout="wide")
st.title("TSMC Talent Matcher 🚀")
st.write("Upload candidate resumes (PDF) to rank them based on stability and archetype.")

files = st.file_uploader("Upload Resumes", accept_multiple_files=True, type=['pdf'])

if files:
    results = []
    for f in files:
        with open(f.name, "wb") as temp_file:
            temp_file.write(f.getbuffer())
        text = extract_text(f.name)
        score, notes = score_candidate(text)
        results.append({'Candidate': f.name, 'Score': score, 'Notes': notes})
        os.remove(f.name)

    df = pd.DataFrame(results).sort_values(by='Score', ascending=False)

    # Color Styling for the UI
    def color_rows(val):
        color = '#c6efce' if val >= 80 else '#ffc7ce' if val < 40 else '#ffeb9c'
        return f'background-color: {color}'

    st.dataframe(df.style.applymap(color_rows, subset=['Score']))
    
    # Export Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Ranked List", csv, "Ranked_Candidates.csv", "text/csv")
