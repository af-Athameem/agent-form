import streamlit as st
import streamlit_nested_layout
import requests


st.set_page_config(
    page_title="Agent Form", 
    layout="wide", 
    initial_sidebar_state="expanded"
    )


# GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"

## Redirect to login if  not authintcated
# if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
#     st.warning("🔒 Please log in first.")
#     st.switch_page("pages/login.py")  


# Streamlit UI
st.markdown("""
    <style>
        .main {
            background-color: #f4f4f9;
        }
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .css-1aumxhk {
            padding: 2rem;
        }
        .stTable {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            font-size: 14px;
        }
        .dataframe th, .dataframe td {
            padding: 10px;
            text-align: left;
        }
        .dataframe thead th {
            background-color: #4CAF50;
            color: white;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: #f9f9f9;
        }
        .dataframe tbody tr:hover {
            background-color: #f1f1f1;
        }
        h1, h2, h3, h4 {
            color: #333;
        }
        .remove-btn>button {
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
        }
        .remove-btn>button:hover {
            background-color: #D43F3F;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

## Fetch token and site ID
# TOKEN = st.session_state.get("token")
# SITE_ID = st.session_state.get("site_id")

# if not TOKEN or not SITE_ID:
#     st.error("🔑 Authentication required. Please log in.")
# else:
#     headers = {"Authorization": f"Bearer {TOKEN}"}

st.header("Agent Form")

# Ensure session state is initialized
if "use_cases" not in st.session_state:
    st.session_state["use_cases"] = []
if "target_sections" not in st.session_state:
    st.session_state["target_sections"] = []

# Input for Business/Institution Name
business_name = st.text_input(
    "Business/Institution Name", 
    help="Please Enter Full Name. No abbreviations", 
    key="question_input"
)
# Collapsible expander for Target Section and Use Cases
with st.expander("Specific Target Section", expanded=False):

    # Input for Target Section (No predefined options)
    target = st.text_input(
        "Specific Target Section", 
        help="Please be clear as possible", 
        key="target_section"
    )
    
    # Input field to add use cases dynamically
    with st.expander("Use Cases", expanded=True):
        use_case = st.text_input("Add Use Case", help="Type a use case and press Enter")
        # Description
        description = st.text_area(
            "Provide a brief description for each use case",
            help="General Description for all use cases associated with the target section"
        )
        # Current Proccess
        current = st.text_area(
            "What is your current process for handling these use cases?",
            help="Provide as much detail as possible (e.g. 'Step X')"
        )
        #Business Value
        value = st.slider(
            "On a scale of 1 to 10, how valuable are these use cases to the organization?",
            1,10, 
            help= "1 = LOW , 10 = HIGH"
        )
        #User Impact
        impact = st.slider( 
            "On a scale of 1 to 10, how significantly are these use cases impact end users?",
            1,10,
            help= "1 = LOW , 10 = HIGH"
        )
        #Feasibilitiy
        feasibility = st.selectbox(
            "How feasible is this use case to implement?", 
            [" ", "High", "Medium", "Low"], 
            )
    
        # Frequency of Use
        frequency_of_use = st.selectbox(
            "How often will this use case be used?", 
            ["", "Daily", "Weekly", "Monthly", "Rarely"], 
        )   
    
        # Complexity
        complexity = st.selectbox(
            "How difficult is this use case to implement?", 
            ["","High", "Medium", "Low"]
        )
    
        #Risk & Dependencies 
        risks_dependencies = st.text_area(
        "Describe any risks or dependencies associated with this use case."
        )
    
        #Compliance
        compliance = st.text_area(
            "Does this use case have any regulatory or compliance requirements?",
            help= "If not sure please enter 'N/A'"
        )
    
        # Priority
        priority = st.selectbox(
            "How important is this use case compared to others?", 
            ["","High", "Medium", "Low"], 
        )
    

    # Button to add the entered use case to the list
    if st.button("Add Use Case"):
        if use_case and use_case not in st.session_state["use_cases"]:
            st.session_state["use_cases"].append(use_case)
            st.rerun()  # Refresh UI 
            
# Button to add a Specific Target Section
if st.button("Add Specific Target Section"):
    if target and target not in st.session_state["target_section"]:
        st.session_state["target_section"].append(target)
        st.rerun()

st.subheader("Upload Files")
st.write("Please attach any associated files that may help better comprehend your needs.")
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)



