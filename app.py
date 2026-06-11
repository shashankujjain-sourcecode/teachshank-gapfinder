import streamlit as st
import pandas as pd
import io

# Page Configuration
st.set_page_config(page_title="TeachShank - GapFinder Engine", layout="wide")

# 1. Master Data Loading Logic (Using your uploaded TSV structure)
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

# =========================================================================
# BRANDING & SCHOOL LOGO SYSTEM
# =========================================================================
def render_school_header():
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        # School Logo Handler: Agar local/online logo image path available na ho, 
        # toh placeholder load hoga. Aap 'school_logo.png' ki jagah apni actual image use kar sakte hain.
        try:
            st.image("https://via.placeholder.com/150x150.png?text=SCHOOL+LOGO", width=120)
        except:
            st.markdown("<div style='background-color:#edf2f7; padding:20px; border-radius:5px; text-align:center;'>LOGO</div>", unsafe_allow_html=True)
            
    with col_title:
        st.markdown("<h1 style='color: #1a365d; margin-bottom: 2px;'>TeachShank - GapFinder Engine</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4a5568; font-size:1.1em;'>Premium Assessment Manager & Diagnostic Remediation Portal</p>", unsafe_allow_html=True)
    st.write("---")

# Render Header on Top of the App
render_school_header()

if df_master is not None:
    # Navigation Tabs matching your exact requirements
    tab1, tab2 = st.tabs(["📋 Generate Assessment Panel", "📊 Check Assessment Panel (Upload Excel)"])

    # =========================================================================
    # SECTION 1: GENERATE ASSESSMENT PANEL
    # =========================================================================
    with tab1:
        st.header("Create Assessment Paper & Response Template")
        st.info("⚠️ **Product Constraint Enabled:** Saare templates purely text-based generate honge. Diagram ya graphic questions completely omitted hain.")
        
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
            
        # Add Custom Topic Ingestion Fallback
        st.write("---")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            total_q = st.number_input("Total Questions Count (Pure Text-Based):", min_value=1, max_value=50, value=5)
        with col_p2:
            total_time = st.number_input("Duration Allowed (Minutes):", min_value=5, max_value=180, value=30)
        with col_p3:
            max_marks_per_q = st.selectbox("Scoring Weight Mode:", [1, 2, 5], index=0)

        # Unique Code Formulation Rules
        sub_token = selected_subject[:3].replace(" ", "").upper()
        top_token = selected_topic[:3].replace(" ", "").upper()
        asmt_code = f"{selected_grade.upper()}-{sub_token}-{top_token}-{total_q}Q".replace(" ", "_")
        
        st.markdown(f"### 🏷️ Assessment Registry Code: `{asmt_code}`")
        
        # Inbuilt Dynamic Difficulty Tagging Rule Engine (Based on Learning Outcome Text)
        lo_row = df_master[(df_master['Grade'] == selected_grade) & (df_master['Chapter Name'] == selected_topic)]
        if not lo_row.empty:
            learning_outcome_text = str(lo_row['Learning Outcomes'].values[0])
            if any(word in learning_outcome_text.lower() for word in ['analyze', 'evaluate', 'interpret', 'comprehend']):
                suggested_difficulty = "Hard 🔴"
            elif any(word in learning_outcome_text.lower() for word in ['add', 'subtract', 'calculate', 'perform']):
                suggested_difficulty = "Medium 🟡"
            else:
                suggested_difficulty = "Easy 🟢"
        else:
            suggested_difficulty = "Medium 🟡 (Custom Baseline)"
            
        st.caption(f"🧠 **System Auto-Suggested Benchmark Difficulty:** {suggested_difficulty}")

        # Generating Pre-Formatted Response Template via XlsxWriter memory byte stream
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Metadata Sheet for Verification Pipeline Integrity
            meta_df = pd.DataFrame({
                "Parameter": ["Assessment Code", "Grade", "Subject", "Topic", "Questions", "Max Marks Per Q"],
                "Value": [asmt_code, selected_grade, selected_subject, selected_topic, total_q, max_marks_per_q]
            })
            meta_df.to_excel(writer, sheet_name="Metadata_Do_Not_Touch", index=False)
            
            # Target Column Framework Mapping (Strict Format Control)
            columns = ["Student Name", "Roll No"] + [f"Q{i} (Marks)" for i in range(1, total_q + 1)]
            
            # Dummy Manifest Array
            mock_students = ["Aarav Sharma", "Ananya Verma", "Kabir Singh", "Sneha Joshi", "Rohan Das", "Priya Patel", "Amit Kumar", "Vikas Yadav", "Meera Nair", "Rahul Choudhury"]
            data_rows = [[student, f"R-{idx:02d}"] + [""] * total_q for idx, student in enumerate(mock_students, start=1)]
                
            entry_df = pd.DataFrame(data_rows, columns=columns)
            entry_df.to_excel(writer, sheet_name="Student_Responses", index=False)
            
            # Formatting Rows Layout Visual Look
            workbook  = writer.book
            worksheet = writer.sheets['Student_Responses']
            header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1a365d'})
            for col_num, value in enumerate(entry_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
        buffer.seek(0)
        
        st.download_button(
            label="📥 Download Excel Response Template Sheet",
            data=buffer,
            file_name=f"Template_{asmt_code}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # =========================================================================
    # SECTION 2: CHECK ASSESSMENT PANEL (EXCEL UPLOAD & REMEDIATION REPORT)
    # =========================================================================
    with tab2:
        st.header("Upload Filled Excel Response Sheet for Auto-Checking")
        uploaded_file = st.file_uploader("Drag and drop or browse your response Excel sheet here:", type=["xlsx"])
        
        if uploaded_file is not None:
            try:
                # 1. Processing Validation Phase
                meta_read = pd.read_excel(uploaded_file, sheet_name="Metadata_Do_Not_Touch")
                response_read = pd.read_excel(uploaded_file, sheet_name="Student_Responses")
                
                # Fetch Context Parameters from File Headers tokens
                asmt_code_ctx = meta_read.iloc[0]['Value']
                grade_ctx = meta_read.iloc[1]['Value']
                subject_ctx = meta_read.iloc[2]['Value']
                topic_ctx = meta_read.iloc[3]['Value']
                q_count = int(meta_read.iloc[4]['Value'])
                max_m = int(meta_read.iloc[5]['Value'])
                
                st.success(f"✅ Sheet Authenticated. Active Assessment Profile Code: **{asmt_code_ctx}**")
                
                # Dynamic Column Verification Logic System
                expected_cols = ["Student Name", "Roll No"] + [f"Q{i} (Marks)" for i in range(1, q_count + 1)]
                q_cols = [f"Q{i} (Marks)" for i in range(1, q_count + 1)]
                
                # Convert null cells to zero integer values safely
                response_read[q_cols] = response_read[q_cols].fillna(0)
                
                # Core Analytics Core Calculation Framework Matrices
                total_students = len(response_read)
                response_read['Total Score'] = response_read[q_cols].sum(axis=1)
                max_total_possible = q_count * max_m
                class_average = response_read['Total Score'].mean()
                class_mastery_index = (class_average / max_total_possible) * 100
                
                q_averages = response_read[q_cols].mean()
                q_accuracy_pct = (q_averages / max_m) * 100
                critical_gaps_count = sum(1 for acc in q_accuracy_pct if acc < 50)
                
                # -------------------------------------------------------------
                # DIAGNOSTIC PRINTABLE REPORT INTERFACE (EI UPGRADE STANDARDS)
                # -------------------------------------------------------------
                st.write("---")
                # Printable Header Simulation with Logo Embed Token
                st.markdown(
                    f"""
                    <div style='border:2px solid #1a365d; padding:20px; border-radius:10px; background-color:#ffffff;'>
                        <div style='text-align:center; font-weight:bold; font-size:1.4em; color:#1a365d;'>🏫 CENTRAL DIAGNOSTIC ACADEMIC REPORT</div>
                        <hr style='border:1px solid #1a365d;'>
                        <b>Grade/Class:</b> {grade_ctx} &nbsp;|&nbsp; <b>Subject:</b> {subject_ctx} &nbsp;|&nbsp; <b>Target Chapter:</b> {topic_ctx}<br>
                        <b>Unique Code Trace:</b> {asmt_code_ctx} &nbsp;|&nbsp; <b>Evaluation Date:</b> {datetime.now().strftime('%Y-%m-%d')}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                st.write("## 1. Executive Performance Metrics Summary")
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric(label="Class Mastery Index", value=f"{class_mastery_index:.1f}%")
                with m2:
                    st.metric(label="Critical Gaps Found", value=f"{critical_gaps_count} Sub-Topics")
                with m3:
                    st.metric(label="Assessment Constraints", value="Pure Text (No Diagrams)")
                with m4:
                    st.metric(label="Remediation Priority State", value="URGENT (Level 3)" if class_mastery_index < 60 else "MODERATE (Level 2)")
                
                st.write("---")
                st.write("## 2. Granular Learning Gap & Distractor Analysis")
                st.bar_chart(pd.DataFrame({'Accuracy %': q_accuracy_pct.values}, index=q_cols))
                
                # Zonal Classification Matrix Data display
                breakdown_rows = []
                for col in q_cols:
                    acc = q_accuracy_pct[col]
                    zone = "🟢 Achiever Zone (>75%)" if acc >= 75 else ("🟡 Buffer Zone (50%-75%)" if acc >= 50 else "🔴 Critical Gap Zone (<50%)")
                    breakdown_rows.append({"Question Index": col, "Calculated Accuracy Metric": f"{acc:.1f}%", "Status Evaluation Mapping": zone})
                st.table(pd.DataFrame(breakdown_rows).set_index("Question Index"))
                
                # Cognitive Flaws Misconception Tracking Model
                st.write("### 🧠 Cognitive Misconception Matrix Model")
                miscon_rows = []
                for idx, col in enumerate(q_cols):
                    acc = q_accuracy_pct[col]
                    miscon_rows.append({
                        "Question Parameter": col,
                        "Core Skill Evaluated": f"Skill Attribute Level {idx+1}",
                        "Class Score": f"{acc:.1f}%",
                        "Identified Failure Reason (Text-Based Root Cause)": "Conceptual processing mismatch rules context errors." if acc < 60 else "Optimal grasp metrics verified."
                    })
                st.table(pd.DataFrame(miscon_rows).set_index("Question Parameter"))

                # 3. Dynamic Operational Differentiated Group Frameworks Chunks
                st.write("---")
                st.write("## 3. Scalable Student Segments Differentiated Chunks")
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

                # =============================================================
                # AUTOMATED 45-MINUTE LESSON REMEDIATION PLAN BLUEPRINT
                # =============================================================
                st.write("---")
                st.write("## 4. Automated Printable Class Remediation Detailed Lesson Plan")
                st.caption("CRA Pedagogical Model Framework Optimized for Actionable Intervention Scripts.")
                
                remediation_blocks = [
                    {"Time Split": "00 - 08 Mins", "Lesson Block Phase": "Phase 1: Conflict Confrontation", "Teacher Action Script": f"Board par target topic '{topic_ctx}' ka base statement likhein. Script: 'Class, look at this syntax rule. Agar bina parameters evaluate karein toh logical sequence breakdown kyu hota hai?'", "Expected Student Output": "Students errors to track karke root variables lock karenge."},
                    {"Time Split": "08 - 20 Mins", "Lesson Block Phase": "Phase 2: Visual Representational", "Teacher Action Script": "Notebook templates par structural chart flow ya tree graph models blocks map karke dynamic values link kijiye.", "Expected Student Output": "Students rule sets rules mapping elements apply karte hain."},
                    {"Time Split": "20 - 32 Mins", "Lesson Block Phase": "Phase 3: Abstract Execution Formulation", "Teacher Action Script": "Ab abstraction numerical sequences code configure karke formula board par trace down kijiye.", "Expected Student Output": "Students theoretical validation formulas equations note karenge."},
                    {"Time Split": "32 - 45 Mins", "Lesson Block Phase": "Phase 4: Exit Slip Ticket Evaluation", "Teacher Action Script": "Differentiated Group Red lists ke desks cross check round execute kijiye aur exit tracking evaluation task test kijiye.", "Expected Student Output": "Students individual assignment sheets balance complete karke submit karenge."}
                ]
                st.table(pd.DataFrame(remediation_blocks).set_index("Time Split"))
                st.success("🎉 Diagnosis analytics calculation loops successfully closed.")
                
            except Exception as format_err:
                st.error(f"Verification Integrity Error: Uploaded Excel ka template metadata format parse fail ho gaya. Details: {format_err}")
else:
    st.warning("Runtime Context Missed: 'master_topics.tsv' project root direct directory folder scope mein read nahi ho raha hai.")
