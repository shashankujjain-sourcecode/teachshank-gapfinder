import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Page Configuration Setup
st.set_page_config(page_title="TeachShank - GapFinder Engine", layout="wide")

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

# Header Branding Function
def render_school_header():
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        try:
            # School Branding Logo Placeholder
            st.image("https://via.placeholder.com/150x150.png?text=SCHOOL+LOGO", width=120)
        except:
            st.markdown("<div style='background-color:#edf2f7; padding:20px; border-radius:5px; text-align:center;'>LOGO</div>", unsafe_allow_html=True)
            
    with col_title:
        st.markdown("<h1 style='color: #1a365d; margin-bottom: 2px;'>TeachShank - GapFinder Engine</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4a5568; font-size:1.1em;'>Premium Assessment Manager & Diagnostic Remediation Portal</p>", unsafe_allow_html=True)
    st.write("---")

# Render Header
render_school_header()

if df_master is not None:
    # 2-Tab Split Architecture matching your operational blueprint
    tab1, tab2 = st.tabs(["📋 1. Generate Assessment & Paper", "📊 2. Check Assessment (Upload Excel)"])

    # =========================================================================
    # TAB 1: GENERATE ASSESSMENT & PAPER
    # =========================================================================
    with tab1:
        st.header("Create Assessment Paper & Response Sheet Template")
        st.info("🚫 **Diagram-Free Constraint Active:** Is system mein ek bhi picture ya diagram wala question nahi aayega. Saare questions pure text-based hain.")
        
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
            total_q = st.number_input("Total Questions Count:", min_value=1, max_value=50, value=5, key="t_q")
        with col_p2:
            total_time = st.number_input("Duration Allowed (Minutes):", min_value=5, max_value=180, value=30, key="t_time")
        with col_p3:
            max_marks_per_q = st.selectbox("Marks Per Question:", [1, 2, 5, 10], index=0, key="m_q")

        # Unique Assessment Registry Code Creation
        sub_token = selected_subject[:3].replace(" ", "").upper()
        top_token = selected_topic[:3].replace(" ", "").upper()
        asmt_code = f"{selected_grade.upper()}-{sub_token}-{top_token}-{total_q}Q".replace(" ", "_")
        
        st.markdown(f"### 🏷️ Assessment Identity Code: `{asmt_code}`")
        
        # Difficulty Tagging Rule Engine based on TSV Learning Outcomes
        lo_row = df_master[(df_master['Grade'] == selected_grade) & (df_master['Chapter Name'] == selected_topic)]
        if not lo_row.empty:
            learning_outcome_text = str(lo_row['Learning Outcomes'].values[0])
            if any(word in learning_outcome_text.lower() for word in ['analyze', 'evaluate', 'interpret', 'comprehend', 'critical']):
                suggested_difficulty = "Hard 🔴"
            elif any(word in learning_outcome_text.lower() for word in ['add', 'subtract', 'calculate', 'perform', 'apply']):
                suggested_difficulty = "Medium 🟡"
            else:
                suggested_difficulty = "Easy 🟢"
        else:
            learning_outcome_text = "Understand and apply the concepts."
            suggested_difficulty = "Medium 🟡"
            
        st.caption(f"🧠 **System Auto-Suggested Difficulty Category:** {suggested_difficulty}")

        # GENERATING EXCEL TEMPLATE ENGINE WITH EXPLICIT DATA ENTRY COLUMNS
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Sheet 1: Core System Metadata Tracking
            meta_df = pd.DataFrame({
                "Parameter": ["Assessment Code", "Grade", "Subject", "Topic", "Questions", "Max Marks Per Q"],
                "Value": [asmt_code, selected_grade, selected_subject, selected_topic, total_q, max_marks_per_q]
            })
            meta_df.to_excel(writer, sheet_name="Metadata_Do_Not_Touch", index=False)
            
            # Sheet 2: Main Entry Matrix (Explicit Data Entry Design)
            columns = ["Student Name", "Roll No"] + [f"Q{i} Marks (Max {max_marks_per_q})" for i in range(1, total_q + 1)]
            
            # Dummy Manifest Array for Easy Reference
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
        st.download_button(
            label="Download Excel Data Input Sheet Template",
            data=buffer,
            file_name=f"Data_Sheet_{asmt_code}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # ---------------------------------------------------------------------
        # VISUAL PRINTABLE QUESTION PAPER DESIGN SECTION
        # ---------------------------------------------------------------------
        st.write("---")
        st.markdown("<div style='background-color:#f8fafc; padding:25px; border:1px solid #cbd5e1; border-radius:8px;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#1a365d; margin-bottom:0px;'>🏫 PRINTABLE ASSESSMENT PAPER</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align:center; margin-top:5px; color:#4a5568;'>{selected_subject.upper()} ASSESSMENT</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'><b>Class / Grade:</b> {selected_grade} | <b>Target Topic:</b> {selected_topic}<br><b>Time Limit:</b> {total_time} Minutes | <b>Maximum Total Marks:</b> {total_q * max_marks_per_q}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px dashed #cbd5e1;'>", unsafe_allow_html=True)
        st.markdown("**Instructions to Students:**\n1. Saare questions ko dhyan se padhein aur solve karein.\n2. Is paper mein koi diagram/picture nahi hai. Apne steps clear notebooks mein mention karein.")
        st.write("")
        
        # Iterating Questions Loops Based on TSV Learning Parameters (Text-Only Mode)
        for i in range(1, total_q + 1):
            st.markdown(f"**Question {i}:** State, solve, or explain a text-based analytical challenge specifically aligned with the learning outcome objective: *'{learning_outcome_text}'*. Show all formulas, equations, and mathematical proofs where applicable. \n\n*(Weightage Score: {max_marks_per_q} Marks)*")
            st.write("")
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: CHECK ASSESSMENT & CALCULATE ANALYSIS GAPS
    # =========================================================================
    with tab2:
        st.header("Upload Filled Excel Sheet & View Deep Diagnostic Insights")
        
        # Quick Clear Instructions for Teachers on Data Headers
        st.markdown("""
        <div style='background-color:#ebf8ff; padding:15px; border-radius:5px; border-left:4px solid #3182ce; margin-bottom:15px;'>
            <strong>📌 Excel Data Entry Rule:</strong><br>
            1. Download ki gayi Excel template ko open karein.<br>
            2. <strong>'Student_Responses'</strong> sheet par jaayein. Wahan pehle do columns <code>Student Name</code> aur <code>Roll No</code> pehle se bhare hain.<br>
            3. Agle columns (Jaise <code>Q1 Marks (Max 1)</code>, <code>Q2 Marks...</code>) mein har student ke prapt scores enter karke file save karein aur niche upload karein.
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload your completed Excel data input sheet:", type=["xlsx"])
        
        if uploaded_file is not None:
            try:
                # Parsing Ingestion Layers
                meta_read = pd.read_excel(uploaded_file, sheet_name="Metadata_Do_Not_Touch")
                response_read = pd.read_excel(uploaded_file, sheet_name="Student_Responses")
                
                # Context Extraction
                asmt_code_ctx = meta_read.iloc[0]['Value']
                grade_ctx = meta_read.iloc[1]['Value']
                subject_ctx = meta_read.iloc[2]['Value']
                topic_ctx = meta_read.iloc[3]['Value']
                q_count = int(meta_read.iloc[4]['Value'])
                max_m = int(meta_read.iloc[5]['Value'])
                
                st.success(f"✅ Data Sheet Verified. Active Identity Profile Trace: **{asmt_code_ctx}**")
                
                # Fetching dynamically modified Question Marks headers from Excel columns array
                q_cols = [c for c in response_read.columns if "Marks" in c and c != "Total Score"]
                if len(q_cols) == 0:
                    q_cols = [f"Q{i} Marks (Max {max_m})" for i in range(1, q_count + 1)]
                
                # Data Scrubbing & Formatting stability converters
                response_read[q_cols] = response_read[q_cols].fillna(0)
                
                # Core Calculations Pipeline Arrays
                total_students = len(response_read)
                response_read['Total Score'] = response_read[q_cols].sum(axis=1)
                max_total_possible = q_count * max_m
                class_average = response_read['Total Score'].mean()
                class_mastery_index = (class_average / max_total_possible) * 100
                
                q_averages = response_read[q_cols].mean()
                q_accuracy_pct = (q_averages / max_m) * 100
                critical_gaps_count = sum(1 for acc in q_accuracy_pct if acc < 50)
                
                # -------------------------------------------------------------
                # DIAGNOSTIC ACADEMIC INSIGHT REPORT LAYOUT
                # -------------------------------------------------------------
                st.write("---")
                st.markdown(
                    f"""
                    <div style='border:2px solid #1a365d; padding:20px; border-radius:10px; background-color:#ffffff;'>
                        <div style='text-align:center; font-weight:bold; font-size:1.4em; color:#1a365d;'>🏫 CENTRAL DIAGNOSTIC ACADEMIC REPORT</div>
                        <hr style='border:1px solid #1a365d;'>
                        <b>Class / Grade:</b> {grade_ctx} &nbsp;|&nbsp; <b>Subject:</b> {subject_ctx} &nbsp;|&nbsp; <b>Topic:</b> {topic_ctx}<br>
                        <b>System Code Trace:</b> {asmt_code_ctx} &nbsp;|&nbsp; <b>Report Generation Date:</b> {datetime.now().strftime('%Y-%m-%d')}
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
                st.write("### 2. Question-Wise Learning Accuracy Distribution")
                st.bar_chart(pd.DataFrame({'Accuracy %': q_accuracy_pct.values}, index=[f"Q{i}" for i in range(1, len(q_cols)+1)]))
                
                # Question Matrix Zonal Analysis Datatable
                breakdown_rows = []
                for idx, col in enumerate(q_cols, start=1):
                    acc = q_accuracy_pct.iloc[idx-1]
                    zone = "🟢 Achiever Zone (>75%)" if acc >= 75 else ("🟡 Buffer Zone (50%-75%)" if acc >= 50 else "🔴 Critical Gap Zone (<50%)")
                    breakdown_rows.append({"Question Matrix Component": f"Question {idx}", "Calculated Accuracy Metric": f"{acc:.1f}%", "Status Evaluation Zone Mapping": zone})
                st.table(pd.DataFrame(breakdown_rows).set_index("Question Matrix Component"))
                
                # Granular Differentiated Groups Segment Chunks Creation Logics
                st.write("---")
                st.write("### 3. Differentiated Student Learning Segments (Grouping Chunks)")
                g_red, g_yellow, g_green = [], [], []
                for index, row in response_read.iterrows():
                    name = row['Student Name']
                    pct = (row['Total Score'] / max_total_possible) * 100
                    if pct < 50: g_red.append(name)
                    elif pct < 75: g_yellow.append(name)
                    else: g_green.append(name)
                    
                cg1, cg2, cg3 = st.columns(3)
                with cg1:
                    st.markdown("<div style='background-color:#fed7d7; padding:15px; border-radius:5px;'><strong>🔴 Group Red (Targeted Intervention)</strong><br>" + ", ".join(g_red if g_red else ["None"]) + "</div>", unsafe_allow_html=True)
                with cg2:
                    st.markdown("<div style='background-color:#ffeebc; padding:15px; border-radius:5px;'><strong>🟡 Group Yellow (Concept Reinforcement)</strong><br>" + ", ".join(g_yellow if g_yellow else ["None"]) + "</div>", unsafe_allow_html=True)
                with cg3:
                    st.markdown("<div style='background-color:#c6f6d5; padding:15px; border-radius:5px;'><strong>🟢 Group Green (Enrichment Peers)</strong><br>" + ", ".join(g_green if g_green else ["None"]) + "</div>", unsafe_allow_html=True)

                # =============================================================
                # ACTIONABLE REMEDIATION INTERVENTION STRATEGY BLUEPRINT
                # =============================================================
                st.write("---")
                st.write("### 4. Automated 45-Minute Class Remediation Lesson Plan")
                st.caption("Concrete-Representational-Abstract (CRA) Educational Pedagogical Standards Structure Blueprint.")
                
                remediation_blocks = [
                    {"Time Split": "00 - 08 Mins", "Lesson Block Phase": "Phase 1: Conflict Confrontation", "Teacher Action Script": f"Board par target topic '{topic_ctx}' ka text statement error note kijiye. Script: 'Class, look at this logical layout sequence, yahan processing breakdown kyu ho raha hai?'", "Expected Student Output": "Students concept error variables ko track karke lock karenge."},
                    {"Time Split": "08 - 20 Mins", "Lesson Block Phase": "Phase 2: Representational Structure", "Teacher Action Script": "Notebook templates par logical properties grids map kijiye aur data flow structure link kijiye.", "Expected Student Output": "Students rule sets visual frameworks sheets par complete karenge."},
                    {"Time Split": "20 - 32 Mins", "Lesson Block Phase": "Phase 3: Abstract Formulation Rules", "Teacher Action Script": "Ab abstraction numerical sequences formula board par write-down karke step validation checks execute kijiye.", "Expected Student Output": "Students computational registers parameters checking verify karenge."},
                    {"Time Split": "32 - 45 Mins", "Lesson Block Phase": "Phase 4: Exit Ticket Evaluation", "Teacher Action Script": "Differentiated Group Red ke lists ke desk check validation tasks lead kijiye aur exit evaluation check sheet update kijiye.", "Expected Student Output": "Students tracking slips feedback complete karke sheet handover karenge."}
                ]
                st.table(pd.DataFrame(remediation_blocks).set_index("Time Split"))
                st.success("🎉 Diagnosis analytics calculation workflows closed successfully.")
                
            except Exception as parse_err:
                st.error(f"Integrity Error: File content structure parse parameters configuration rule se match nahi kar raha hai. Check metadata tabs: {parse_err}")
else:
    st.warning("Data Repository Missed: 'master_topics.tsv' file scope dictionary environment mein visible nahi hai.")
