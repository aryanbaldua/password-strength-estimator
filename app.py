"""
streamlit demo for the password strength estimator

personal info and password are processed in memory only and never stored
"""

import calendar
import streamlit as st
from main import estimate_strength

st.set_page_config(page_title="Password Strength Estimator", layout="centered")

# color for each strength label
LABEL_COLOR = {
    "weak":   "#e74c3c",  # red
    "ok":     "#f39c12",  # orange
    "strong": "#2ecc71",  # green
}

# hide streamlit's default footer and menu, and define styles for the bar and feedback cards
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .strength-bar-bg {
            background-color: #e0e0e0;
            border-radius: 8px;
            height: 18px;
            width: 100%;
            margin-bottom: 8px;
        }
        .strength-bar-fill {
            height: 18px;
            border-radius: 8px;
            transition: width 0.3s ease;
        }
        .feedback-item {
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 6px;
            background-color: #f8f9fa;
            border-left: 4px solid #ccc;
            font-size: 0.95rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Password Strength Estimator")
st.markdown(
    "<small style='color: gray;'>Inputs are processed in memory only and never stored.</small>",
    unsafe_allow_html=True,
)
st.divider()

st.markdown("### Personal Info <small style='color: gray; font-weight: normal;'>(optional)</small>", unsafe_allow_html=True)
st.caption("Helps detect if your password contains your name or birthday.")

col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("First name", placeholder="e.g. Jane")
with col2:
    last_name = st.text_input("Last name", placeholder="e.g. Doe")

MONTH_OPTIONS = ["—"] + [calendar.month_name[i] for i in range(1, 13)]
DAY_OPTIONS = ["—"] + list(range(1, 32))
YEAR_OPTIONS = ["—"] + list(range(2010, 1919, -1))

col_m, col_d, col_y = st.columns(3)
with col_m:
    month_sel = st.selectbox("Month", MONTH_OPTIONS)
with col_d:
    day_sel = st.selectbox("Day", DAY_OPTIONS)
with col_y:
    year_sel = st.selectbox("Year", YEAR_OPTIONS)

# convert dropdowns to YYYY-MM-DD for the backend, only if all three are set
birthday = ""
if month_sel != "—" and day_sel != "—" and year_sel != "—":
    month_num = list(calendar.month_name).index(month_sel)
    birthday = f"{year_sel}-{month_num:02d}-{int(day_sel):02d}"

st.divider()

st.markdown("### Password")
password = st.text_input("Enter your password", type="password", placeholder="Type your password here...")

# results update in real time as the user types
if password:
    result = estimate_strength(password, first_name, last_name, birthday)
    score = result["score"]
    label = result["label"]
    feedback = result["feedback"]
    color = LABEL_COLOR[label]

    st.divider()

    # label and score side by side
    col_label, col_score = st.columns([2, 1])
    with col_label:
        st.markdown(
            f"<h2 style='color: {color}; margin-bottom: 4px;'>{label.capitalize()}</h2>",
            unsafe_allow_html=True,
        )
    with col_score:
        st.markdown(
            f"<h2 style='text-align: right; color: {color}; margin-bottom: 4px;'>{score}<span style='font-size: 1rem; color: gray;'> / 100</span></h2>",
            unsafe_allow_html=True,
        )

    # colored bar that fills based on score
    st.markdown(f"""
        <div class="strength-bar-bg">
            <div class="strength-bar-fill" style="width: {score}%; background-color: {color};"></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Suggestions")
    for msg in feedback:
        st.markdown(
            f"<div class='feedback-item' style='border-left-color: {color};'>{msg}</div>",
            unsafe_allow_html=True,
        )
