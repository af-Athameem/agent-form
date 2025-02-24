import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
from typing import Dict, List

st.set_page_config(
    page_title="Agent Form", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Custom CSS for Enhanced UI
st.markdown("""
    <style>
        .main {
            background-color: #f4f4f9;
            padding: 1.5rem;
        }
        .stButton>button {
            transition: all 0.3s ease;
            border: 1px solid #007BFF;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.3);
        }
        .section-header {
            background: linear-gradient(145deg, #007BFF, #0056b3);
            color: white !important;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .use-case-box {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #007BFF;
        }
        .metric-badge {
            background-color: #e9f5ff;
            color: #007BFF;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 0.2rem;
        }
        .file-uploader .st-emotion-cache-1lnq2i0 {
            border: 2px dashed #007BFF;
            border-radius: 10px;
        }
        .required-field::after {
            content: " *";
            color: red;
        }
        .stProgress .st-emotion-cache-1qrvh5p {
            background-color: #007BFF;
        }
        .vertical-progress {
            height: 200px;
            writing-mode: vertical-lr;
            transform: rotate(180deg);
            margin-top: 20px;
        }
        .progress-container {
            text-align: center;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .main {
                padding: 0.75rem;
            }
            .use-case-box {
                padding: 1rem;
            }
        }
        /* Toast notifications */
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s, fadeOut 0.5s 3.5s forwards;
        }
        .toast-success {
            background-color: #28a745;
        }
        .toast-error {
            background-color: #dc3545;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    </style>
""", unsafe_allow_html=True)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Initialize session state
if "target_sections" not in st.session_state:
    st.session_state["target_sections"] = {}
    
if "show_success" not in st.session_state:
    st.session_state["show_success"] = False
    
if "success_message" not in st.session_state:
    st.session_state["success_message"] = ""

if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True
    st.session_state["welcome_shown"] = False

# Form functions
def reset_form_defaults(section: str):
    """Reset form fields to their default values."""
    # Text fields
    form_values = {
        f"use_case_{section}": "",
        f"description_{section}": "",
        f"current_{section}": "",
        f"risks_{section}": "",
        f"compliance_{section}": "",
        # Numeric fields
        f"value_{section}": 5,
        f"impact_{section}": 5,
        # Dropdowns
        f"feasibility_{section}": "Medium",
        f"frequency_{section}": "Daily",
        f"complexity_{section}": "Medium",
        f"priority_{section}": "Medium"
    }
    
    # Update session state
    for key, value in form_values.items():
        st.session_state[key] = value

def validate_section_case(section: str) -> bool:
    """Validate required fields for a use case in a specific section."""
    if not st.session_state.get(f"use_case_{section}"):
        st.error("Use Case Title is required.")
        return False
    if not st.session_state.get(f"description_{section}"):
        st.error("Description is required.")
        return False
    return True

def validate_submission() -> bool:
    """Validate all required fields before form submission."""
    required_fields = [
        ('business_name', 'Business/Institution Name is required'),
    ]
    
    for field, message in required_fields:
        if not st.session_state.get(field):
            st.error(message)
            return False
            
    if not st.session_state.get("target_sections") or len(st.session_state["target_sections"]) == 0:
        st.error("At least one target section is required")
        return False
        
    # Check that at least one section has at least one use case
    has_use_cases = False
    for section, cases in st.session_state.get("target_sections", {}).items():
        if cases and len(cases) > 0:
            has_use_cases = True
            break
    
    if not has_use_cases:
        st.error("At least one use case is required")
        return False
        
    return True

def add_section():
    """Add a new section using the input from session state."""
    new_section = st.session_state.get("new_section", "").strip()
    if new_section:
        if new_section not in st.session_state["target_sections"]:
            st.session_state["target_sections"][new_section] = []
            st.session_state["success_message"] = f"Section '{new_section}' added successfully!"
            st.session_state["show_success"] = True
            st.session_state["new_section"] = ""  # Clear the input field
        else:
            st.error("Section already exists!")
    else:
        st.error("Please enter a section name")

def delete_section(section: str):
    """Delete a section and all its use cases."""
    if section in st.session_state["target_sections"]:
        del st.session_state["target_sections"][section]
        st.session_state["success_message"] = f"Section '{section}' deleted successfully!"
        st.session_state["show_success"] = True

def add_use_case(section: str, continue_adding: bool = False):
    """Add a use case to the specified section."""
    if validate_section_case(section):
        new_case = {
            "use_case": st.session_state.get(f"use_case_{section}", ""),
            "description": st.session_state.get(f"description_{section}", ""),
            "current_process": st.session_state.get(f"current_{section}", ""),
            "value": st.session_state.get(f"value_{section}", 5),
            "impact": st.session_state.get(f"impact_{section}", 5),
            "feasibility": st.session_state.get(f"feasibility_{section}", "Medium"),
            "frequency": st.session_state.get(f"frequency_{section}", "Daily"),
            "complexity": st.session_state.get(f"complexity_{section}", "Medium"),
            "risks": st.session_state.get(f"risks_{section}", ""),
            "compliance": st.session_state.get(f"compliance_{section}", ""),
            "priority": st.session_state.get(f"priority_{section}", "Medium"),
        }
        
        st.session_state["target_sections"][section].append(new_case)
        
        if continue_adding:
            message = f"Use Case '{new_case['use_case']}' saved! Add another..."
        else:
            message = f"Use Case '{new_case['use_case']}' saved successfully!"
            
        st.session_state["success_message"] = message
        st.session_state["show_success"] = True
        
        # Reset form fields for the next entry
        reset_form_defaults(section)

def delete_use_case(section: str, idx: int):
    """Delete a specific use case from a section."""
    if section in st.session_state["target_sections"]:
        if 0 <= idx < len(st.session_state["target_sections"][section]):
            st.session_state["target_sections"][section].pop(idx)
            st.session_state["success_message"] = "Use case deleted successfully!"
            st.session_state["show_success"] = True

def get_download_link(data, filename, text):
    """Generate a download link for the given data."""
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def export_data_as_json():
    """Export form data as JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_data = {
        "business_name": st.session_state.get("business_name", ""),
        "submission_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target_sections": st.session_state.get("target_sections", {})
    }
    json_str = json.dumps(export_data, indent=2)
    filename = f"agent_form_export_{timestamp}.json"
    
    return get_download_link(json_str, filename, "📥 Download JSON")

def export_data_as_csv():
    """Export form data as CSV."""
    rows = []
    
    for section, use_cases in st.session_state.get("target_sections", {}).items():
        for case in use_cases:
            row = {
                "Business": st.session_state.get("business_name", ""),
                "Section": section,
                "Use Case": case.get("use_case", ""),
                "Description": case.get("description", ""),
                "Current Process": case.get("current_process", ""),
                "Business Value": case.get("value", ""),
                "User Impact": case.get("impact", ""),
                "Feasibility": case.get("feasibility", ""),
                "Frequency": case.get("frequency", ""),
                "Complexity": case.get("complexity", ""),
                "Risks": case.get("risks", ""),
                "Compliance": case.get("compliance", ""),
                "Priority": case.get("priority", "")
            }
            rows.append(row)
    
    if not rows:
        return None
        
    df = pd.DataFrame(rows)
    csv = df.to_csv(index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"agent_form_export_{timestamp}.csv"
    
    return get_download_link(csv, filename, "📥 Download CSV")

# Callbacks for form actions
def on_add_continue_click(section):
    add_use_case(section, continue_adding=True)

def on_save_click(section):
    add_use_case(section, continue_adding=False)

def on_delete_section_click(section):
    delete_section(section)

def on_delete_case_click(section, idx):
    delete_use_case(section, idx)


# Create layout with a progress column on the left and main content on the right
progress_col, main_col = st.columns([1, 18])

# Progress tracker calculation
total_steps = 3
completed_steps = 0

if st.session_state.get("business_name"):
    completed_steps += 1
if st.session_state.get("target_sections") and len(st.session_state["target_sections"]) > 0:
    completed_steps += 1
    
    # Check for at least one use case
    has_use_cases = False
    for section, cases in st.session_state.get("target_sections", {}).items():
        if cases and len(cases) > 0:
            has_use_cases = True
            completed_steps += 1
            break

# Progress percentage calculation
progress_percentage = (completed_steps / total_steps) * 100

# Render progress in the left column
with progress_col:
    st.markdown(f"<h5 style='text-align: center;'>{int(progress_percentage)}%</h2>", unsafe_allow_html=True)
    
    # Use a skinnier vertical progress bar
    progress_container = st.container()
    with progress_container:
        # Create a placeholder with fixed height for the skinny progress bar
        st.markdown(
            f"""
            <div style="height: 200px; position: relative; margin-top: 20px; display: flex; justify-content: center;">
                <div style="position: relative; width: 20px; height: 100%; background-color: #f0f2f6; border-radius: 10px; overflow: hidden;">
                    <div style="position: absolute; bottom: 0; width: 100%; height: {progress_percentage}%; 
                         background-color: #007BFF; border-radius: 10px;"></div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Main content column
with main_col:
    # Success notification
    if st.session_state.get("show_success"):
        st.success(st.session_state.get("success_message", "Operation completed successfully!"))
        st.session_state["show_success"] = False

    # Form header
    st.markdown("<h1 style='text-align: center; color: black;'> 🤖 Agent Form </h1>", unsafe_allow_html=True)

    # Welcome message on first load (only shows once)
    if st.session_state.get("show_welcome") and not st.session_state.get("welcome_shown"):
        st.info("👋 Welcome to the Agent Form! Use this tool to document use cases across your organization. So we can build you an AI Agents that better fit your needs!")
        st.session_state["welcome_shown"] = True

    # Business Information Section
    st.subheader("Business Information", help="Enter your organization details")
    st.text_input(
        "Business/Institution Name", 
        help="Enter the full legal name (No abbreviations)", 
        key="business_name"
    )

    # Target Section Management
    st.subheader("Target Sections", help="Define departments or business areas")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input(
            "Add New Target Section", 
            help="Enter department or business area", 
            key="new_section"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Section", use_container_width=True, on_click=add_section):
            pass  # Logic handled in callback function

    # Display a message if no sections exist
    if not st.session_state["target_sections"]:
        st.info("No sections added yet. Please add at least one section to continue.")

    # Section Display and Use Case Management
    for section, use_cases in list(st.session_state["target_sections"].items()):
        with st.expander(f"📂 {section.upper()}", expanded=True):
            # Section Header with Delete Button
            header_col, button_col = st.columns([5, 1])
            with button_col:
                if st.button(f"🗑️ Delete Section", key=f"del_sec_{section}", 
                            on_click=on_delete_section_click, args=(section,)):
                    pass  # Logic handled in callback function
            
            # Use Case Input Fields
            st.markdown("### Add New Use Case")
            use_case_cols = st.columns(2)
            with use_case_cols[0]:
                st.markdown('<p class="required-field">Use Case Title</p>', unsafe_allow_html=True)
                st.text_input("", key=f"use_case_{section}", label_visibility="collapsed")
                
                st.markdown('<p class="required-field">Description</p>', unsafe_allow_html=True)
                st.text_area("", key=f"description_{section}", label_visibility="collapsed")
                
                st.text_area("Current Process", key=f"current_{section}", 
                            help="Describe how this process is currently handled")
            with use_case_cols[1]:
                st.slider("Business Value (1-10)", 1, 10, key=f"value_{section}", 
                         help="How valuable is this to the business?")
                st.slider("User Impact (1-10)", 1, 10, key=f"impact_{section}", 
                          help="How much will this impact users?")
                st.selectbox("Feasibility", ["High", "Medium", "Low"], 
                            index=1, key=f"feasibility_{section}", 
                            help="How feasible is this to implement?")
                st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "Quarterly", "Rarely"], 
                            index=0, key=f"frequency_{section}", 
                            help="How often is this process performed?")
            
                st.selectbox("Complexity", ["High", "Medium", "Low"], 
                            index=1, key=f"complexity_{section}", 
                            help="How complex is this use case?")
                st.text_area("Risks & Dependencies", key=f"risks_{section}", 
                            help="List any risks or dependencies for this use case")
                with use_case_cols[0]:
                    st.text_area("Compliance Requirements", key=f"compliance_{section}", 
                                help="List any compliance or regulatory requirements")
                    st.selectbox("Priority", ["High", "Medium", "Low"], 
                                index=1, key=f"priority_{section}", 
                                help="What is the priority level?")

            # Add Use Case Buttons
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                if st.button("➕ Add & Continue", 
                            key=f"add_another_{section}",
                            help="Save current use case and clear form for new entry",
                            use_container_width=True,
                            on_click=on_add_continue_click, args=(section,)):
                    pass  # Logic handled in callback function

            with btn_col2:
                if st.button(f"💾 Save Use Case", 
                            key=f"add_case_{section}",
                            help="Save and finalize current use case",
                            use_container_width=True,
                            type="primary",
                            on_click=on_save_click, args=(section,)):
                    pass  # Logic handled in callback function

            # Display Existing Use Cases
            if use_cases:
                st.markdown("#### Existing Use Cases")
                for idx, case in enumerate(use_cases):
                    with st.container():
                        st.markdown(f"""
                        <div class='use-case-box'>
                            <div style="display: flex; justify-content: space-between; align-items: center">
                            <h3>{case.get('use_case', 'Untitled Use Case')}</h3>
                        </div>
                        <p><strong>Description:</strong> {case.get('description', 'No description provided')}</p>
                        <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0;">
                            <span class='metric-badge'>Value: {case.get('value', 'N/A')}/10</span>
                            <span class='metric-badge'>Impact: {case.get('impact', 'N/A')}/10</span>
                            <span class='metric-badge'>Feasibility: {case.get('feasibility', 'N/A')}</span>
                            <span class='metric-badge'>Priority: {case.get('priority', 'N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                        
                        # Server-side delete button
                        delete_col, _ = st.columns([1, 5])
                        with delete_col:
                            if st.button("Delete Use Case", key=f"del_case_{section}_{idx}", 
                                        on_click=on_delete_case_click, args=(section, idx)):
                                pass  # Logic handled in callback function

    # File Upload Section
    st.markdown("## Supporting Documents", help="Upload relevant files for reference")
    uploaded_files = st.file_uploader(
        "Upload relevant documents",
        type=["pdf", "docx", "txt", "csv", "xlsx", "pptx"],
        accept_multiple_files=True,
        key="file_uploader",
        help="Accepted formats: PDF, DOCX, TXT, CSV, XLSX, PPTX"
    )

    if uploaded_files:
        st.markdown("**Uploaded Files:**")
        file_cols = st.columns(3)
        for i, file in enumerate(uploaded_files):
            with file_cols[i % 3]:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <span style="font-weight: bold;">📎 {file.name}</span><br>
                    <span style="font-size: 0.8rem; color: #6c757d;">({file.size//1024} KB)</span>
                </div>
                """, unsafe_allow_html=True)

    # Form Submission and Export
    st.markdown("---")
    submit_col, export_col = st.columns([1, 1])

    with submit_col:
        if st.button("📤 Submit Form", use_container_width=True, type="primary"):
            if validate_submission():
                st.session_state["submission_complete"] = True
                st.success("Form submitted successfully!")
                st.balloons()

    with export_col:
        if st.session_state.get("target_sections") and any(st.session_state["target_sections"].values()):
            export_tabs = st.tabs(["JSON", "CSV"])
            with export_tabs[0]:
                json_link = export_data_as_json()
                st.markdown(json_link, unsafe_allow_html=True)
            with export_tabs[1]:
                csv_link = export_data_as_csv()
                if csv_link:
                    st.markdown(csv_link, unsafe_allow_html=True)
                else:
                    st.info("No data to export yet.")
        else:
            st.info("Add sections and use cases to enable data export.")
