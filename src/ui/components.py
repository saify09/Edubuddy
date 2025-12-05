import streamlit as st

def header(title, subtitle):
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #0b3d91;">{title}</h1>
        <p style="font-size: 1.2em; color: #555;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def card_start():
    st.markdown('<div class="card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)

def student_info_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/student-male--v1.png", width=100)
        
        # Editable Student Info
        if 'student_name' not in st.session_state:
            st.session_state.student_name = "Saifuddin Hanif"
        if 'roll_no' not in st.session_state:
            st.session_state.roll_no = "371344"
            
        st.session_state.student_name = st.text_input("Student Name", st.session_state.student_name)
        st.session_state.roll_no = st.text_input("Roll Number", st.session_state.roll_no)
        
        st.markdown("**Trainer:** Sir Nasir Hussain")
        st.markdown("---")
        st.info("**Final Project:** AI & Data Science")
        st.info("**Batch 15:** 03:00 PM - 05:00 PM")
        st.info("**SMIT Campus:** Zaitoon Ashraf IT Park")
