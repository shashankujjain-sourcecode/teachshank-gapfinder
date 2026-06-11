import streamlit as st
import pandas as pd
import io
from datetime import datetime
from fpdf import FPDF

# Page Configuration Setup
st.set_page_config(page_title="TeachShank - Pure Text MCQ & PDF Engine", layout="wide")

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

# ---------------------------------------------------------------------
# 🎯 INTERNAL MCQ QUESTION BANK ENGINE
# ---------------------------------------------------------------------
def get_real_mcq_questions(subject, topic, count):
    questions = []
    
    # Math Context Questions
    if "math" in subject.lower():
        q_pool = [
            {
                "q": "Solve: 45 + 27. What is the correct positional sum value?",
                "a": "72 (Correct calculation)",
                "b": "62 (Distractor Error: Forgot to carry over 1 to the tens place)",
                "c": "612 (Distractor Error: Directly wrote 5+7=12 and 4+2=6 side-by-side)",
                "d": "18"
            },
            {
                "q": "Which number represents three hundred and five in numeric digits?",
                "a": "305 (Correct notation)",
                "b": "350 (Distractor Error: Swapped tens and ones place value)",
                "c": "3005 (Distractor Error: Directly wrote 300 and 5 together)",
                "d": "35"
            },
            {
                "q": "Solve for x: x - 15 = 30. What is the value of x?",
                "a": "45 (Correct additive inverse method)",
                "b": "15 (Distractor Error: Subtracted 15 from 30 instead of adding)",
                "c": "2 (Distractor Error: Divided 30 by 15 instead of shifting sign)",
                "d": "0"
            },
            {
                "q": "Evaluate: 1/2 + 1/4. What is the common scale summation value?",
                "a": "3/4 (Correct LCM calculation)",
                "b": "2/6 (Distractor Error: Added numerators across and denominators across directly)",
                "c": "1/6 (Distractor Error: Multiplied denominators without matching scaling)",
                "d": "1/2"
            },
            {
                "q": "Find the perimeter of a rectangle with length 10 cm and breadth 5 cm without drawing any shapes.",
                "a": "30 cm (Correct application of formula 2*(L+B))",
                "b": "15 cm (Distractor Error: Only added length and breadth once, forgot multiplier)",
                "c": "50 cm (Distractor Error: Multiplied length and breadth, calculated Area instead of Perimeter)",
                "d": "20 cm"
            }
        ]
    # Science / EVS Context Questions
    elif "science" in subject.lower() or "evs" in subject.lower():
        q_pool = [
            {
                "q": "Which nutrient is primarily responsible for body-building and muscle repair in human growth?",
                "a": "Proteins (Correct biochemical function)",
                "b": "Carbohydrates (Distractor Error: Confused body-building with instant energy source)",
                "c": "Vitamins (Distractor Error: Confused growth with disease protection)",
                "d": "Fats"
            },
            {
                "q": "What is the primary gas absorbed by green plants during the process of photosynthesis?",
                "a": "Carbon Dioxide (Correct chemical input)",
                "b": "Oxygen (Distractor Error: Confused output byproduct released with input gas absorbed)",
                "c": "Nitrogen (Distractor Error: Assumed highest atmospheric gas concentration is absorbed)",
                "d": "Hydrogen"
            },
            {
                "q": "Which part of the plant turns into a fruit after successful fertilization occurs?",
                "a": "Ovary (Correct botanical transition)",
                "b": "Ovule (Distractor Error: Confused seed origin with fruit capsule origin)",
                "c": "Petals (Distractor Error: Assumed colorful visual parts become the fruit structure)",
                "d": "Roots"
            },
            {
                "q": "Water boiling at 100 degrees Celsius transitions from liquid state into gas. What type of change is this?",
                "a": "Physical Change (Correct state transformation logic)",
                "b": "Chemical Change (Distractor Error: Assumed heat application creates a new chemical compound)",
                "c": "Irreversible Change (Distractor Error: Assumed steam cannot turn back into water droplets)",
                "d": "Biological Change"
            }
        ]
    # Language / Social Studies Context Questions
    else:
        q_pool = [
            {
                "q": "Identify the proper noun from the given textual phrase sentence block: 'The little girl went to New Delhi.'",
                "a": "New Delhi (Correct identification of specific place name)",
                "b": "girl (Distractor Error: Confused common noun category with proper noun rule)",
                "c": "little (Distractor Error: Selected descriptive adjective instead of naming noun)",
                "d": "went"
            },
            {
                "q": "Choose the correct past tense form of the action verb 'RUN' to fill the blank sentence: 'Yesterday, Rohan ____ to the library.'",
                "a": "ran (Correct irregular past tense derivation)",
                "b": "runned (Distractor Error: Generalization mistake by forcing regular '-ed' suffix)",
                "c": "running (Distractor Error: Selected continuous participle instead of standard past event tense)",
                "d": "runs"
            }
        ]
        
    for i in range(count):
        pool_idx = i % len(q_pool)
        questions.append(q_pool[pool_idx])
        
    return questions

# ---------------------------------------------------------------------
# 📄 PURE PYTHON PDF GENERATION CLASS (WITH BRANDED HEADER & LOGO ALIGNMENT)
# ---------------------------------------------------------------------
class AssessmentPDF(FPDF):
    def __init__(self, school_name, grade, subject, topic, code, time, total_marks):
        super().__init__()
        self.school_name = school_name
        self.grade = grade
        self.subject = subject
        self.topic = topic
        self.code = code
        self.time = time
        self.total_marks = total_marks

    def header(self):
        # Branded Box Layer for School Logo & Names Alignment
        self.set_draw_color(26, 54, 93)
        self.set_line_width(0.8)
        self.rect(10, 10, 190, 35)
        
        # Simulating School Logo Frame Alignment Space on the left margin
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(113, 128, 150)
        self.text(14, 28, "[ SCHOOL LOGO PLACEHOLDER ]")
        
        # Center School Name & Header details
        self.set_text_color(26, 54, 93)
        self.set_font("Helvetica", "B", 16)
        self.set_y(14)
        self.cell(0, 8, self.school_name.upper(), ln=True, align="C")
        
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(74, 85, 104)
        self.cell(0, 6, "CENTRAL MULTIPLE CHOICE ASSESSMENT PAPER", ln=True, align="C")
        
        # Meta Parameters string line
        self.set_font("Helvetica", "", 9)
        meta_line = f"Grade: {self.grade}  |  Subject: {self.subject}  |  Topic: {self.topic}"
        self.cell(0, 5, meta_line, ln=True, align="C")
        
        # Code & Time allocation details
        code_line = f"Assessment Code: {self.code}  |  Time: {self.time} Mins  |  Max Marks: {self.total_marks}"
        self.cell(0, 5, code_line, ln=True, align="C")
        
        self.set_y(50) # Margin spacing from header box layer boundary

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(113, 128, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Generated by TeachShank Educational Core System Security Engine", align="C")

# Header UI Display on Web panel
def render_school_header():
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        try:
            st.image("https://via.placeholder.com/150x150.png?text=SCHOOL+LOGO", width=120)
        except:
            st.markdown("<div style='background-color:#edf2f7; padding:20px; border-radius:5px; text-align:center;'>LOGO</div>", unsafe_allow_html=True)
            
    with col_title:
        st.markdown("<h1 style='color: #1a365d; margin-bottom: 2px;'>TeachShank - GapFinder Engine</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4a5568; font-size:1.1em;'>Premium MCQ Assessment Manager, Auditor Agent & PDF Generator Portal</p>", unsafe_allow_html=True)
    st.write("---")

render_school_header()

if df_master is not None:
    tab1, tab2 = st.tabs(["📋 1. Generate Assessment & MCQ Paper", "📊 2. Check Assessment (Upload Excel)"])

    # =========================================================================
    # TAB 1: GENERATE MCQ ASSESSMENT PANEL (WITH REAL PDF ENGINE)
    # =========================================================================
    with tab1:
        st.header("Create MCQ Assessment Paper & Response Sheets")
        
        col_sch = st.text_input("Enter School Name (For Branded PDF Header Alignment):", value="International Public School")
        
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
            total_q = st.number_input("Total MCQ Questions Count:", min_value=1, max_value=5, value=5, key="t_q")
        with col_p2:
            total_time = st.number_input("Duration Allowed (Minutes):", min_value=5, max_value=180, value=30, key="t_time")
        with col_p3:
            max_marks_per_q = st.selectbox("Marks Per MCQ Question:", [1, 2, 4], index=0, key="m_q")

        # Code Formulation Token
        sub_token = selected_subject[:3].replace(" ", "").upper()
        top_token = selected_topic[:3].replace(" ", "").upper()
        asmt_code = f"{selected_grade.upper()}-{sub_token}-{top_token}-{total_q}MCQ".replace(" ", "_")
        
        st.markdown(f"### 🏷 Unique Assessment Code Generated: `{asmt_code}`")
        
        lo_row = df_master[(df_master['Grade'] == selected_grade) & (df_master['Chapter Name'] == selected_topic)]
        learning_outcome_text = str(lo_row['Learning Outcomes'].values[0]) if not lo_row.empty else "Process core concepts."

        real_questions = get_real_mcq_questions(selected_subject, selected_topic, total_q)

        # 🤖 THE AUDITOR AGENT PANEL
        st.write("---")
        st.markdown("<h3 style='color:#2c5282;'>🤖 Quality Auditor Agent Verification</h3>", unsafe_allow_html=True)
        has_diagram_word = any("diagram" in str(q).lower() or "figure" in str(q).lower() for q in real_questions)
        
        if not has_diagram_word:
            st.success("✅ **Auditor Clearance Approved:** 0 Diagram/Visual tokens found. This paper is 100% text-only MCQ.")
        else:
            st.error("❌ **Auditor Blocked:** Visual elements trace detected in memory pipelines.")

        # EXCEL RESPONSE TEMPLATE BUILDER WITH EXPLICIT DATA ENTRY COLS
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
        
        # ---------------------------------------------------------------------
        # REAL-TIME LIVE COMPILATION OF BRANDED ONSITE PDF FILE IN MEMORY
        # ---------------------------------------------------------------------
        pdf = AssessmentPDF(col_sch, selected_grade, selected_subject, selected_topic, asmt_code, total_time, total_q * max_marks_per_q)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Instructions: Answer all questions. Select choice characters (A,B,C,D) correctly.", ln=True)
        pdf.ln(4)
        
        for idx, q_obj in enumerate(real_questions, start=1):
            pdf.set_font("Helvetica", "B", 10)
            # MultiCell ensures sentences wrap cleanly inside page widths boundaries
            pdf.multi_cell(0, 5, f"Question {idx}: {q_obj['q']}")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 5, f"  (A) {q_obj['a']}", ln=True)
            pdf.cell(0, 5, f"  (B) {q_obj['b']}", ln=True)
            pdf.cell(0, 5, f"  (C) {q_obj['c']}", ln=True)
            pdf.cell(0, 5, f"  (D) {q_obj['d']}", ln=True)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(113, 128, 150)
            pdf.cell(0, 4, f"[Weightage: {max_marks_per_q} Mark]", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)
            
        pdf_output = pdf.output() # Compiles file array strings inside byte stack layers

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
                label="📥 Download Official MCQ Question Paper (PDF)",
                data=bytes(pdf_output),
                file_name=f"MCQ_Question_Paper_{asmt_code}.pdf",
                mime="application/pdf"
            )
        
        # SCREEN PREVIEW OF THE REAL MCQ QUESTION PAPER WITH SCHOOL HEADER
        st.write("---")
        st.markdown("<div style='background-color:#f8fafc; padding:25px; border:1px solid #cbd5e1; border-radius:8px;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'><div style='border:2px dashed #1a365d; display:inline-block; padding:15px; border-radius:5px;'>📷 [ SCHOOL LOGO BOX LAYOUT FRAME ]</div><br><b style='font-size:1.5em; color:#1a365d;'>{col_sch.upper()}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; margin-top:5px; color:#1a365d;'>📄 MULTIPLE CHOICE QUESTION (MCQ) ASSESSMENT PAPER</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'><b>Grade:</b> {selected_grade} &nbsp;|&nbsp; <b>Subject:</b> {selected_subject} &nbsp;|&nbsp; <b>Topic:</b> {selected_topic}<br><b>Time Limit:</b> {total_time} Mins &nbsp;|&nbsp; <b>Max Marks:</b> {total_q * max_marks_per_q} &nbsp;|&nbsp; <b>Code:</b> `{asmt_code}`</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px dashed #cbd5e1;'>", unsafe_allow_html=True)
        st.markdown("**Instructions:** Select the single correct option (A, B, C, or D) for each question. Fills choices into input template files.")
        st.write("")
        
        for idx, q_obj in enumerate(real_questions, start=1):
            st.markdown(f"**Question {idx}:** {q_obj['q']}")
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**(A)** {q_obj['a']}<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;**(B)** {q_obj['b']}<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;**(C)** {q_obj['c']}<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;**(D)** {q_obj['d']}", unsafe_allow_html=True)
            st.markdown(f"<span style='color:#718096; font-size:0.9em;'>[Marks Weightage: {max_marks_per_q} Mark]</span>", unsafe_allow_html=True)
            st.write("")
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: CHECK ASSESSMENT PANEL (EXCEL RESPONSE PROCESSING ENGINE)
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
                
                # CENTRAL BRANDED VISUAL REPORT DISPLAY
                st.write("---")
                st.markdown(
                    f"""
                    <div style='border:2px solid #1a365d; padding:20px; border-radius:10px; background-color:#ffffff; text-align:center;'>
                        <b style='font-size:1.4em; color:#1a365d;'>🏫 TEACHSHANK CENTRAL DIAGNOSTIC ACADEMIC REPORT</b>
                        <hr style='border:1px solid #1a365d; margin: 10px 0;'>
                        <b>Class / Grade:</b> {grade_ctx} &nbsp;|&nbsp; <b>Subject:</b> {subject_ctx} &nbsp;|&nbsp; <b>Target Chapter:</b> {topic_ctx}<br>
                        <b>System Code Unique Trace:</b> {asmt_code_ctx} &nbsp;|&nbsp; <b>Evaluation Date:</b> {datetime.now().strftime('%Y-%m-%d')}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
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
                active_real_qs = get_real_mcq_questions(subject_ctx, topic_ctx, q_count)
                
                for idx, col in enumerate(q_cols, start=1):
                    acc = q_accuracy_pct.iloc[idx-1]
                    b_count = sum(1 for choice in response_read[col] if choice == 'B')
                    distractor_pattern = f"Option B Selected by {b_count} Students" if b_count > 1 else "Scattered mistakes"
                    reason_text = active_real_qs[idx-1]['b']
                    zone = "🟢 Achiever Zone (>75%)" if acc >= 75 else ("🟡 Buffer Zone (50%-75%)" if acc >= 50 else "🔴 Critical Gap Zone (<50%)")
                    breakdown_rows.append({
                        "MCQ Question Link": f"Question {idx}",
                        "Calculated Accuracy": f"{acc:.1f}%",
                        "Dominant Wrong Choice (Distractor)": distractor_pattern,
                        "Identified Failure Root Cause (Misconception Detail)": f"Root Trap: {reason_text}",
                        "Status Evaluation Mapping": zone
                    })
                st.table(pd.DataFrame(breakdown_rows).set_index("MCQ Question Link"))
                
                # Student Chunks Segments Differentiated Grouping Groups
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

                # Automated Differentiated Remediation Lesson Plan Framework Structure
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
