import streamlit as st
import os
import re
from src.auth.user_manager import UserManager
from PIL import Image

def render_auth():
    """Renders the main authentication interface."""


    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🎓 EduBuddy")
        st.caption("Your AI Learning Companion")

    if st.session_state.auth_mode == 'login':
        render_login()
    else:
        render_signup()

def render_login():
    st.subheader("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", width="stretch", type="primary")
        
        if submitted:
            um = UserManager()
            user = um.verify_user(username, password)
            if user:
                # Check for block
                if user.get('error') == 'blocked':
                    st.error("Your account has been blocked. Contact admin.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
            else:
                st.error("Invalid username or password")

    st.markdown("---")
    if st.button("Don't have an account? Sign Up"):
        st.session_state.auth_mode = 'signup'
        st.rerun()

def render_signup():
    st.subheader("Create Account")
    
    # Username Suggestion Logic
    def suggest_username():
        fn = st.session_state.get('signup_fname', '').lower().replace(' ', '')
        ln = st.session_state.get('signup_lname', '').lower().replace(' ', '')
        if fn and ln:
            return f"{fn}.{ln}"
        return ""

    with st.form("signup_form"):
        # Explicit Vertical Stack as requested
        st.markdown("**Personal Details**")
        first_name = st.text_input("First Name *", key='signup_fname')
        last_name = st.text_input("Last Name *", key='signup_lname')
        email = st.text_input("Email")
        contact_info = st.text_input("Contact Info")
        
        st.markdown("**Profile**")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        profession = st.selectbox("Profession", ["Student", "Teacher", "Professional", "Researcher", "Other"])
        
        # Username with suggestion
        st.markdown("**:red[Username *]** (lowercase, e.g. john_doe123)")
        username_input = st.text_input("Username", label_visibility="collapsed", key='signup_username', placeholder="john.doe")
        
        st.markdown("**:red[Password *]**")
        password = st.text_input("Password", type="password", label_visibility="collapsed")

        # Simplified Education/Bio
        bio = st.text_area("Bio", placeholder="Tell us about your learning goals...")
        
        # Profile Pic
        uploaded_file = st.file_uploader("Profile Picture (Round)", type=['jpg', 'png', 'jpeg'])
        
        submitted = st.form_submit_button("Sign Up", width="stretch", type="primary")
        
        if submitted:
            # Auto-convert username to lowercase
            username = username_input.lower().strip()
            
            # Validation
            errors = []
            
            # 1. Required Fields
            if not first_name: errors.append("First Name is required.")
            if not last_name: errors.append("Last Name is required.")
            if not username: errors.append("Username is required.")
            if not password: errors.append("Password is required.")
            
            # 2. Username Rules
            if username:
                if len(username) < 4:
                    errors.append("Username must be at least 4 characters long.")
                
                # Strict Lowercase Check
                if any(c.isupper() for c in username):
                    errors.append("Username must be in lowercase (no uppercase letters).")
                
                # Allow letters, numbers, dots, and underscores
                if not re.match(r'^[a-z0-9_.]+$', username):
                     errors.append("Username can only contain lowercase letters, numbers, dots, and underscores.")

            # 3. Password Rules (Strict)
            if password:
                if len(password) < 8:
                    errors.append("Password must be at least 8 characters long.")
                if not re.search(r"[A-Z]", password):
                    errors.append("Password must contain at least one uppercase letter.")
                if not re.search(r"[a-z]", password):
                    errors.append("Password must contain at least one lowercase letter.")
                if not re.search(r"\d", password):
                    errors.append("Password must contain at least one digit.")
                if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                    errors.append("Password must contain at least one special character.")
            
            # 4. Uniqueness Check
            um = UserManager()
            if username and um.get_user(username):
                errors.append(f"Username '{username}' is already taken.")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Save profile pic if exists
                pic_path = ""
                if uploaded_file:
                    save_dir = "userdata/images"
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    
                    file_ext = uploaded_file.name.split('.')[-1]
                    pic_filename = f"{username}_profile.{file_ext}"
                    pic_path = os.path.join(save_dir, pic_filename)
                    
                    with open(pic_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                user_data = {
                    "username": username,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "contact_info": contact_info,
                    "gender": gender,
                    "profession": profession,
                    "bio": bio,
                    "profile_pic_path": pic_path
                }
                
                if um.create_user(user_data):
                    st.success("Account created successfully! Please login.")
                    st.session_state.auth_mode = 'login'
                    st.rerun()
                else:
                    st.error("An unexpected error occurred during account creation.")

    st.markdown("---")
    if st.button("Already have an account? Login"):
        st.session_state.auth_mode = 'login'
        st.rerun()
