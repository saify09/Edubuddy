import streamlit as st
import os
from PIL import Image

def render_sidebar():
    """Renders the Facebook-style user profile sidebar."""
    user = st.session_state.user
    
    with st.sidebar:
        st.markdown("""
            <style>
            .profile-img {
                border-radius: 50%;
                border: 3px solid #4CAF50;
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 150px;
                height: 150px;
                object-fit: cover;
            }
            .profile-name {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin-top: 10px;
            }
            .profile-info {
                text-align: center;
                color: #888;
                font-size: 14px;
                margin-bottom: 20px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Profile Picture
        # Profile Picture
        pic_path = user.get('profile_pic_path')
        if pic_path and os.path.exists(pic_path):
            import base64
            with open(pic_path, "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
            
            # Use HTML to render round image
            st.markdown(f"""
                <img src="data:image/png;base64,{encoded}" class="profile-img">
            """, unsafe_allow_html=True)
        else:
            # Placeholder with same style
            st.markdown("""
                <div class="profile-img" style="display:flex;align-items:center;justify-content:center;background:#eee;font-size:50px;">
                    👤
                </div>
            """, unsafe_allow_html=True)
            
        # Name and Info
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        if not full_name:
            full_name = user.get('username')
            
        st.markdown(f"<div class='profile-name'>{full_name}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'>{user.get('email', '')}</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # Details
        st.markdown("### 🎓 Bio")
        st.info(user.get('bio', 'Not specified'))
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown("### ⚧ Gender")
            st.text(user.get('gender', 'N/A'))
        with col_info2:
            st.markdown("### 📞 Contact")
            st.text(user.get('contact_info', 'N/A'))
        
        st.markdown("### 💼 Profession")
        st.text(user.get('profession', 'N/A'))
        
        st.divider()
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit"):
                edit_profile_dialog()
                
        with col2:
            if st.button("🚪 Logout"):
                # Clear all session state keys except potentially system ones
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.authenticated = False
                st.rerun()

@st.dialog("Edit Profile")
def edit_profile_dialog():
    user = st.session_state.user
    from src.auth.user_manager import UserManager
    
    with st.form("edit_profile_form"):
        st.markdown("**Personal Details**")
        new_first_name = st.text_input("First Name", value=user.get('first_name', ''))
        new_last_name = st.text_input("Last Name", value=user.get('last_name', ''))
        
        st.markdown("**Contact & Prof**")
        new_email = st.text_input("Email", value=user.get('email', ''))
        new_contact = st.text_input("Contact Info", value=user.get('contact_info', ''))
        new_profession = st.text_input("Profession", value=user.get('profession', ''))
        
        st.markdown("**Other**")
        # Ensure gender index is valid
        gender_opts = ["Male", "Female", "Other"]
        curr_gender = user.get('gender', 'Male')
        idx = gender_opts.index(curr_gender) if curr_gender in gender_opts else 0
        new_gender = st.selectbox("Gender", gender_opts, index=idx)
            
        new_bio = st.text_area("Bio", value=user.get('bio', ''))
        new_address = st.text_area("Address", value=user.get('address', ''))
        
        # Profile Pic Upload
        new_pic = st.file_uploader("Change Profile Picture", type=['jpg', 'png', 'jpeg'])
        
        submitted = st.form_submit_button("Save Changes")
        
        if submitted:
            updates = {
                'first_name': new_first_name,
                'last_name': new_last_name,
                'gender': new_gender,
                'email': new_email,
                'profession': new_profession,
                'contact_info': new_contact,
                'bio': new_bio,
                'address': new_address
            }
            
            # Handle new profile pic
            if new_pic:
                save_dir = "userdata/images"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                
                file_ext = new_pic.name.split('.')[-1]
                # Use timestamp to avoid cache issues
                import time
                pic_filename = f"{user['username']}_profile_{int(time.time())}.{file_ext}"
                pic_path = os.path.join(save_dir, pic_filename)
                
                with open(pic_path, "wb") as f:
                    f.write(new_pic.getbuffer())
                    
                updates['profile_pic_path'] = pic_path
            
            um = UserManager()
            if um.update_user(user['username'], updates):
                # Update session state
                st.session_state.user.update(updates)
                st.success("Profile updated!")
                st.rerun()
            else:
                st.error("Failed to update profile.")
