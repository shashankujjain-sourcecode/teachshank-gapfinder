import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# Page Configuration Setup
st.set_page_config(page_title="TeachShank - Pure Text MCQ Engine", layout="wide")

# 1. Master Data Loading Logic (Reads your uploaded TSV file structure)
@st.cache_data
def load_tsv_data():
    try:
        df = pd.read_csv("master_topics.tsv", sep="\t")
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error loading master_topics.tsv: {e}")
        return None

df_master = load_tsv_data()

# Header Branding Function with School Logo Placeholder
def render_school_header():
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        try:
            st.image("https://via.placeholder.com/150x150.png?text=SCHOOL+LOGO", width=120)
        except:
            st.markdown("<div style='background-color:#edf2f7; padding:20px; border-radius:5px; text-align:center;'>LOGO</div>", unsafe_allow_html=True)
            
    with col_title:
        st.markdown("<h1 style='color: #1a365d; margin-bottom: 2px;'>TeachShank - GapFinder Engine</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4a5568; font-size:1.1em;'>Premium MCQ Assessment Manager, Auditor Agent & Diagnostic Portal</p>", unsafe_allow_html=True)
    st.write("---")

# Render Header
render_school_header()

# HARDCODED CLEANING FUNCTION: Purge and rewrite any diagram vocabulary instantly
def sanitize_learning_outcome(text):
    text_str = str(text).lower()
    # List of all dangerous diagrammatic/visual words
    blacklist = [
        "diagram", "figure", "image", "picture", "shape", "color", "draw", "map", 
        "reflection", "eye", "lens", "mirror", "look", "view", "pattern", "geometry", 
        "graph", "plot", "structure", "observe", "visual", "symmetry", "3d", "2d"
    ]
    
    # Check if any blacklisted word exists
    if any(word in text_str for word in blacklist):
        # Permanently purge the visual requirement and rewrite to pure logic/theory
        return "Understand the core conceptual logic, theoretical definitions, and underlying computational/textual properties."
    return text

# Helper function to generate printable text-only raw string for file downloads
def generate_plain_text_paper(grade, subject, topic, code, time, q_count, marks_q, lo_text):
    # Pass through sanitization engine to wipe out any diagram reference
    clean_lo = sanitize_learning_outcome(lo_text)
    
    paper_str = f"SCHOOL NAME PLACEHOLDER\n"
    paper_str += f"--------------------------------------------------\n"
    paper_str += f"CENTRAL ASSESSMENT PAPER (MCQ MODE)\n"
    paper_str += f"Class/Grade: {grade} | Subject: {subject}\n"
    paper_str += f"Topic: {topic}\n"
    paper_str += f"Assessment Code: {code}\n"
    paper_str += f"Time Allowed: {time} Mins | Total Marks: {q_count * marks_q}\n"
    paper_str += f"--------------------------------------------------\n\n"
    paper_str += f"Instructions:\n1. Saare questions MCQ format mein hain. Har question ka ek hi sahi विकल्प (option) hai.\n"
    paper_str += f"2. WARNING: Is paper mein koi bhi diagram, image ya geometric shape nahi hai. Pure text-based answers karein.\n\n"
    
    for i in range(1, q_count + 1):
        paper_str += f"Question {i}: Solve the problem or evaluate the textual concept that satisfies the learning objective: '{clean_lo}' (Variant #{i})\n"
        paper_str += f"  (A) Core conceptual definition and baseline theory metric.\n"
        paper_str += f"  (B) Misconception distraction case variant B (Common Error Logic Area).\n"
        paper_str += f"  (C) Alternative logical numerical sequence execution path.\n"
        paper_str += f"  (D) Completely inverse factual counter-statement property.\n"
        paper_str += f"  [Weightage: {marks_q} Mark]\n\n"
    return paper_str

if df_master is not None:
    tab1, tab2 = st.tabs(["📋 1. Generate Assessment & MCQ Paper", "📊 2. Check Assessment (Upload Excel)"])

    # =========================================================================
    # TAB 1: GENERATE MCQ ASSESSMENT PANEL (WITH HARD FILTER)
    # =========================================================================
    with tab1:
        st.header("Create MCQ Assessment Paper & Response Sheets")
        st.info("🎯 **Strict Diagram-Free Mode Active:** Software ke andar block filter laga hai jo TSV file se diagram waale outcomes ko pakad kar wahi destroy kar deta hai.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            grades = sorted(df_master['Grade'].unique())
            selected_grade = st.selectbox("Select Grade / Class:", grades, key="gen_grade")
        with col2:
            subjects = sorted(df_master[df_master['Grade'] == selected_grade]['Subject'].unique())
            selected_subject = st.selectbox("Select Subject:", subjects, key="gen_sub")
        with col3:
            topics = sorted(df_master[(df_master['Grade'] == selected_grade) & (df_master['Subject'] == selected_subject)]['Chapter Name'].unique())
            selected_topic = st.selectbox("Select Chapter / Topic:", topics, key="gen_topic")
            
        st.write("---")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            total_q = st.number_input("Total MCQ Questions Count:", min_value=1, max_value=50, value=5, key="t_q")
        with col_p2:
            total_time = st.number_input("Duration Allowed (Minutes):", min_value=5, max_value=180, value=30, key="t_time")
        with col_p3:
            max_marks_per_q = st.selectbox("Marks Per MCQ Question:", [1, 2, 4], index=0, key="m_q")

        # Code Formulation
        sub_token = selected_subject[:3].replace(" ", "").upper()
        top_token = selected_topic[:3].replace(" ", "").upper()
        asmt_code = f"{selected_grade.upper()}-{sub_token}-{top_token}-{total_q}MCQ".replace(" ", "_")
        
        st.markdown(f"### 🏷️ Unique Assessment Code Generated: `{asmt_code}`")
        
        # Difficulty Analyzer
        lo_row = df_master[(df_master['Grade'] == selected_grade) & (df_master['Chapter Name'] == selected_topic)]
        if not lo_row.empty:
            raw_lo_text = str(lo_row['Learning Outcomes'].values[0])
            # Pass through our filter to sanitize it instantly
            learning_outcome_text = sanitize_learning_outcome(raw_lo_text)
            
            if any(word in raw_lo_text.lower() for word in ['analyze', 'evaluate', 'interpret', 'comprehend', 'critical']):
                suggested_difficulty = "Hard 🔴"
            elif any(word in raw_lo_text.lower() for word in ['add', 'subtract', 'calculate', 'perform', 'apply']):
                suggested_difficulty = "Medium 🟡"
            else:
                suggested_difficulty = "Easy 🟢"
        else:
            learning_outcome_text = "Understand and process concept blocks."
            suggested_difficulty = "Medium 🟡"
            
        st.caption(f"🧠 **Auto-Suggested Benchmark Difficulty:** {suggested_difficulty}")

        # =====================================================================
        # 🤖 THE AUDITOR AGENT PANEL
        # =====================================================================
        st.write("---")
        st.markdown("<h3 style='color:#2c5282;'>🤖 Quality Auditor Agent Verification</h3>", unsafe_allow_html=True)
        
        raw_paper_for_audit = generate_plain_text_paper(selected_grade, selected_subject, selected_topic, asmt_code, total_time, total_q, max_marks_per_q, learning_outcome_text)
        
        # Absolute safety check strings scan
        blacklist_check_words = ["diagram", "figure", "image", "src=", "drawing", "picture"]
        found_mistakes = [w for w in blacklist_check_words if w in raw_paper_for_audit.lower()]
        
        if len(found_mistakes) == 0:
            st.success("✅ **Auditor Clearance Approved:** 0 Diagram/Visual tokens found. This paper is 100% safe to print in pure text-mode.")
        else:
            st.error(f"❌ **Auditor Blocked:** Dangerous words found: {found_mistakes}. Rewriting pipeline activated.")

        # EXCEL RESPONSE TEMPLATE BUILDER WITH EXPLICIT COLS
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            meta_df = pd.DataFrame({
                "Parameter": ["Assessment Code", "Grade", "Subject", "Topic", "Questions", "Max Marks Per Q"],
                "Value":
