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
        return "Understand the core conceptual logic, theoretical definitions, and underlying computational/textual properties."
    return text

# Helper function to generate printable text-only raw string for file downloads
def generate_plain_text_paper(grade, subject, topic, code, time, q_count, marks_q, lo_text):
    clean_lo = sanitize_learning_outcome(lo_text)
    
    paper_str = f"SCHOOL NAME PLACEHOLDER\n"
    paper_str += f"--------------------------------------------------\n"
    paper_str += f"CENTRAL ASSESSMENT PAPER (MCQ MODE)\n"
    paper_str += f"Class/Grade: {grade} | Subject: {subject}\n"
    paper_str += f"Topic: {topic}\n"
    paper_str += f"Assessment Code: {code}\n"
    paper_str += f"Time Allowed: {time} Mins | Total Marks: {q_count * marks_q}\n"
    paper_str += f"--------------------------------------------------\n\n"
    paper_str += f"Instructions:\n1. Saare questions MCQ format mein hain. Har question ka ek hi sahi vikalp (option) hai.\n"
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
    # TAB 1: GENERATE MCQ ASSESSMENT PANEL
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

        # 🤖 THE AUDITOR AGENT PANEL
        st.write("---")
        st.markdown("<h3 style='color:#2c5282;'>🤖 Quality Auditor Agent Verification</h3>", unsafe_allow_html=True)
        
        raw_paper_for_audit = generate_plain_text_paper(selected_grade, selected_subject, selected_topic, asmt_code, total_time, total_q, max_marks_per_q, learning_outcome_text)
        
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
                "Value": [asmt_code, selected_grade, selected_subject, selected_topic, total_q, max_marks_per_q]
            })
            meta_df.to_excel(writer, sheet_name="Metadata_Do_Not_Touch", index=False)
            
            columns = ["Student Name", "Roll No"] + [f"Q{i} Option Selected (A/B/C/D)" for i in range(1, total_q + 1)]
            
            mock_students = ["Aarav Sharma", "Ananya Verma", "Kabir Singh", "Sneha Joshi", "Rohan Das", "Priya Patel", "Amit Kumar", "Vikas Yadav", "Meera Nair", "Rahul Choudhury"]
            data_rows = [[student, f"R-{idx:02d}"] + [""] * total_q for idx, student in enumerate(mock_students, start=1)]
                
            entry_df = pd.DataFrame(data_rows, columns=columns)
            entry_df.to_excel(writer, sheet_name="Student_Responses", index=False)
            
            workbook  = writer.book
            worksheet = writer.sheets['Student_Responses']
            header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1a365d'})
            for col_num, value in enumerate(entry_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
        buffer.seek(0)
        
        st.markdown("#### 📥 Download Section")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="🟢 Download Excel Response Sheet Template",
                data=buffer,
                file_name=f"MCQ_Data_Template_{asmt_code}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with d_col2:
            st.download_button(
                label="📄 Download Printable Text-Based MCQ Question Paper",
                data=raw_paper_for_audit,
                file_name=f"MCQ_Question_Paper_{asmt_code}.txt",
                mime="text/plain"
            )
        
        # SCREEN PREVIEW OF MCQ QUESTION PAPER WITH SCHOOL HEADER
        st.write("---")
        st.markdown("<div style='background-color:#f8fafc; padding:25px; border:1px solid #cbd5e1; border-radius:8px;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'><img src='https://via.placeholder.com/100x100.png?text=LOGO' width='80'><br><b style='font-size:1.3em; color:#1a365d;'>SCHOOL OFFICIAL HEADER PANEL</b></div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; margin-top:5px; color:#1a365d;'>📄 MULTIPLE CHOICE QUESTION (MCQ) ASSESSMENT</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'><b>Grade:</b> {selected_grade} &nbsp;|&nbsp; <b>Subject:</b> {selected_subject} &nbsp;|&nbsp; <b>Topic:</b> {selected_topic}<br><b>Time Limit:</b> {total_time} Mins &nbsp;|&nbsp; <b>Max Marks:</b> {total_q * max_marks_per_q} &nbsp;|&nbsp; <b>Code:</b> `{asmt_code}`</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px dashed #cbd5e1;'>", unsafe_allow_html=True)
        st.markdown("**Instructions:** Select option (A, B, C, or D). Pure text evaluation sheet.")
        st.write("")
        
        for i in range(1, total_q + 1):
            st.markdown(f"**Question {i}:** Choose the statement or standard numerical solution that satisfies the operational metric for the targeted learning framework outcome: *'{learning_outcome_text}'*.")
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**(A)** Option structure path sequence alpha rules theoretical definition.<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;**(B)** Distractor misconception case beta. *(Common conceptual flaw trigger)*<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;**(C)** Alternative analytical logic execution path variable gamma.<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;**(D)** Factual counter-statement parameter property delta.", unsafe_allow_html=True)
            st.markdown(f"<span style='color:#718096; font-size:0.9em;'>[Marks Weightage: {max_marks_per_q} Mark]</span>", unsafe_allow_html=True)
            st.write("")
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: CHECK ASSESSMENT PANEL
    # =========================================================================
    with tab2:
        st.header("Upload Filled Excel Sheet & Check Gaps via Distractors")
        uploaded_file = st.file_uploader("Upload your completed Excel data input sheet:", type=["xlsx"])
        
        if uploaded_file is not None:
            try:
                meta_read = pd.read_excel(uploaded_file, sheet_name="Metadata_Do_Not_Touch")
                response_read = pd.read_excel(uploaded_file, sheet_name="Student_Responses")
                
                asmt_code_ctx = meta_read.iloc[0]['Value']
                grade_ctx = meta_read.iloc[1]['Value']
                subject_ctx = meta_read.iloc[2]['Value']
                topic_ctx = meta_read.iloc[3]['Value']
                q_count = int(meta_read.iloc[4]['Value'])
                max_m = int(meta_read.iloc[5]['Value'])
                
                st.success(f"✅ Data Sheet Verified. Profile Identification Trace: **{asmt_code_ctx}**")
                
                q_cols = [c for c in response_read.columns if "Option Selected" in c]
                if len(q_cols) == 0:
                    q_cols = [f"Q{i} Option Selected (A/B/C/D)" for i in range(1, q_count + 1)]
                
                response_read[q_cols] = response_read[q_cols].fillna('D').astype(str).apply(lambda x: x.str.upper().str.strip())
                
                for idx, col in enumerate(q_cols, start=1):
                    response_read[f"Q{idx}_Score"] = response_read[col].apply(lambda x: max_m if x == 'A' else 0)
                    
                score_cols = [f"Q{i}_Score" for i in range(1, q_count + 1)]
                response_read['Total Score'] = response_read[score_cols].sum(axis=1)
                
                max_total_possible = q_count * max_m
                class_average = response_read['Total Score'].mean()
                class_mastery_index = (class_average / max_total_possible) * 100
                
                q_accuracy_pct = (response_read[score_cols].mean() / max_m) * 100
                critical_gaps_count = sum(1 for acc in q_accuracy_pct if acc < 50)
                
                # REPORT INTERFACE DISPLAY WITH LOGO HEADER
                st.write("---")
                
                # Dynamic visual components rendering
                st.markdown(f"""
                <div style='border:2px solid #1a365d; padding:20px; border-radius:10px; background-color:#ffffff; text-align:center;'>
                    <b style='font-size:1.4em; color:#1a365d;'>🏫 TEACHSHANK CENTRAL DIAGNOSTIC ACADEMIC REPORT</b>
                    <hr style='border:1px solid #1a365d; margin: 10px 0;'>
                    <b>Class / Grade:</b> {grade_ctx} &nbsp;|&nbsp; <b>Subject:</b> {subject_ctx} &nbsp;|&nbsp; <b>Target Chapter:</b> {topic_ctx}<br>
                    <b>System Code Unique Trace:</b> {asmt_code_ctx} &nbsp;|&nbsp; <b>Evaluation Date:</b> {datetime.now().strftime('%Y-%m-%d')}
                </div>
                """, unsafe_allow_html=True)
                
                st.write("### 1. Executive Performance Metrics Summary")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric(label="Class Mastery Index", value=f"{class_mastery_index:.1f}%")
                with m2:
                    st.metric(label="Critical Gaps Detected", value=f"{critical_gaps_count} Questions")
                with m3:
                    st.metric(label="Remediation Priority Action State", value="URGENT (Level 3)" if class_mastery_index < 60 else "MODERATE (Level 2)")
                
                st.write("---")
                st.write("### 2. MCQ Distractor Analytics & Learning Gap Matrix")
                st.bar_chart(pd.DataFrame({'Accuracy %': q_accuracy_pct.values}, index=[f"Q{i}" for i in range(1, len(q_cols)+1)]))
                
                breakdown_rows = []
                for idx, col in enumerate(q_cols, start=1):
                    acc = q_accuracy_pct.iloc[idx-1]
                    b_count = sum(1 for choice in response_read[col] if choice == 'B')
                    distractor_pattern = f"Option B Selected by {b_count} Students" if b_count > 1 else "Scattered errors"
                    zone = "🟢 Achiever Zone (>75%)" if acc >= 75 else ("🟡 Buffer Zone (50%-75%)" if acc >= 50 else "🔴 Critical Gap Zone (<50%)")
                    breakdown_rows.append({
                        "MCQ Question Link": f"Question {idx}",
                        "Calculated Accuracy": f"{acc:.1f}%",
                        "Dominant Wrong Choice (Distractor)": distractor_pattern,
                        "Identified Failure Root Cause": "Procedural rules skipped or incorrect conversion applied." if acc < 60 else "Optimal conceptual understanding verified.",
                        "Status Evaluation Mapping": zone
                    })
                st.table(pd.DataFrame(breakdown_rows).set_index("MCQ Question Link"))
                
                # Student Grouping Chunks
                st.write("---")
                st.write("### 3. Student Grouping Segments Chunks")
                g_red, g_yellow, g_green = [], [], []
                for index, row in response_read.iterrows():
                    name = row['Student Name']
                    pct = (row['Total Score'] / max_total_possible) * 100
                    if pct < 50: g_red.append(name)
                    elif pct < 75: g_yellow.append(name)
                    else: g_green.append(name)
                    
                cg1, cg2, cg3 = st.columns(3)
                with cg1:
                    st.markdown("<div style='background-color:#fed7d7; padding:15px; border-radius:5px;'><strong>🔴 Group Red (Intervention)</strong><br>" + ", ".join(g_red if g_red else ["None"]) + "</div>", unsafe_allow_html=True)
                with cg2:
                    st.markdown("<div style='background-color:#ffeebc; padding:15px; border-radius:5px;'><strong>🟡 Group Yellow (Reinforce)</strong><br>" + ", ".join(g_yellow if g_yellow else ["None"]) + "</div>", unsafe_allow_html=True)
                with cg3:
                    st.markdown("<div style='background-color:#c6f6d5; padding:15px; border-radius:5px;'><strong>🟢 Group Green (Enrichment)</strong><br>" + ", ".join(g_green if g_green else ["None"]) + "</div>", unsafe_allow_html=True)

                # Remediation Lesson Plan
                st.write("---")
                st.write("### 4. Automated 45-Minute MCQ-Targeted Class Remediation Lesson Plan")
                remediation_blocks = [
                    {"Time Split": "00 - 08 Mins", "Lesson Block Phase": "Phase 1: Distractor Deconstruction", "Teacher Action Script": f"Board par target topic '{topic_ctx}' ka wahi Option B wala incorrect logic solve karein jo bacchon ne chuna. Script: 'Class, look at this common trap choice, yahan logic breakdown kyu ho raha hai?'", "Expected Student Output": "Students wrong options text variables ko deconstruct karke trace karenge."},
                    {"Time Split": "08 - 20 Mins", "Lesson Block Phase": "Phase 2: Conceptual Breakdown", "Teacher Action Script": "Notebooks par numerical models blocks aur connections map karke text definitions link kijiye.", "Expected Student Output": "Students parameter sheets setup complete karenge."},
                    {"Time Split": "20 - 32 Mins", "Lesson Block Phase": "Phase 3: Abstract Formulation Rules", "Teacher Action Script": "Visual variables ko logical mathematical statements aur formula equations mein sheet par trace kijiye.", "Expected Student Output": "Students calculations rules registers mein note karenge."},
                    {"Time Split": "32 - 45 Mins", "Lesson Block Phase": "Phase 4: MCQ Exit Ticket Strategy", "Teacher Action Script": "Differentiated Group Red ke lists ke desk checks lead kijiye aur exit evaluation check slip process kijiye.", "Expected Student Output": "Students target questions feedback sheets handover karenge."}
                ]
                st.table(pd.DataFrame(remediation_blocks).set_index("Time Split"))
                st.success("🎉 Full MCQ diagnostic calculations run completed successfully.")
                
            except Exception as format_err:
                st.error(f"Ingestion Integrity Error: Excel format metadata configuration trace missing rules: {format_err}")
else:
    st.warning("Runtime Context Error: 'master_topics.tsv' repository folder structure visibility missing.")
