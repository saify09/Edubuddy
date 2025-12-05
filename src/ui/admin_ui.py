import streamlit as st
import pandas as pd
import plotly.express as px
from src.auth.user_manager import UserManager
from src.utils.analytics_logger import AnalyticsLogger

def render_admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    
    # Security Check
    if st.session_state.user.get('username') != 'admin':
        st.error("Access Denied. You do not have permission to view this page.")
        return

    st.info("Welcome, Administrator. Here is the system overview.")
    
    um = UserManager()
    users = um.get_all_users()
    logger = AnalyticsLogger()
    
    # --- Metrics ---
    total_users = len(users)
    active_users = len([u for u in users if u.get('login_count', 0) > 0])
    blocked_users = len([u for u in users if u.get('is_blocked', 0) == 1])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", total_users)
    col2.metric("Active Users", active_users)
    col3.metric("Blocked Users", blocked_users)
    col4.metric("System Status", "Online", delta="OK")
    
    st.divider()
    
    # --- User Management ---
    st.subheader("👥 User Management")
    
    tab1, tab2 = st.tabs(["User Registry", "Actions"])
    
    with tab1:
        if users:
            df = pd.DataFrame(users)
            
            # Reorder/Rename columns
            display_cols = [
                'username', 'first_name', 'last_name', 'email', 
                'gender', 'profession', 'contact_info',
                'last_login', 'login_count', 'is_blocked'
            ]
            
            # Filter to available columns
            cols = [c for c in display_cols if c in df.columns]
            df = df[cols]
            
            st.dataframe(
                df,
                width="stretch",
                column_config={
                    "username": "Username",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "email": "Email",
                    "gender": "Gender",
                    "contact_info": "Contact",
                    "profession": "Profession",
                    "last_login": st.column_config.DatetimeColumn("Last Login", format="D MMM YYYY, h:mm a"),
                    "login_count": st.column_config.NumberColumn("Logins", help="Number of times logged in"),
                    "is_blocked": st.column_config.CheckboxColumn("Blocked", help="Is user blocked?"),
                },
                hide_index=True
            )
        else:
            st.warning("No users found.")

    with tab2:
        st.markdown("#### Manage Users")
        if users:
            usernames = [u['username'] for u in users if u['username'] != 'admin']
            selected_user = st.selectbox("Select User", usernames)
            
            if selected_user:
                # Get current status
                user_details = um.get_user(selected_user)
                is_blocked = user_details.get('is_blocked', 0)
                
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    if is_blocked:
                        if st.button(f"🔓 Unblock {selected_user}", type="primary", width="stretch"):
                            if um.unblock_user(selected_user):
                                st.success(f"User {selected_user} unblocked.")
                                st.rerun()
                            else:
                                st.error("Failed to unblock user.")
                    else:
                        if st.button(f"🚫 Block {selected_user}", type="primary", width="stretch"):
                            if um.block_user(selected_user):
                                st.warning(f"User {selected_user} blocked.")
                                st.rerun()
                            else:
                                st.error("Failed to block user.")
                
                with c3:
                    if st.button(f"🗑️ Delete {selected_user}", type="secondary", width="stretch"):
                        if um.delete_user(selected_user):
                            st.error(f"User {selected_user} deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete user.")
        else:
            st.info("No users to manage.")

    st.divider()
    
    # --- Analytics ---
    st.subheader("📊 System Analytics")
    
    ac1, ac2 = st.columns(2)
    
    with ac1:
        if users and 'last_login' in df.columns:
            df['last_login'] = pd.to_datetime(df['last_login'], errors='coerce')
            # Group by Date only
            daily_logins = df.groupby(df['last_login'].dt.date).size().reset_index(name='count')
            if not daily_logins.empty:
                # Use Line Chart for Time Series Trend
                fig_login = px.line(daily_logins, x='last_login', y='count', title="Daily Logins Trend", markers=True)
                fig_login.update_layout(xaxis_title="Date", yaxis_title="Login Count")
                st.plotly_chart(fig_login, width="stretch", key="login_chart")
            else:
                st.info("No login data available.")
    
    with ac2:
        st.markdown("**Ingestion Analytics**")
        stats = logger.get_ingestion_stats()
        if stats:
            stats_df = pd.DataFrame(list(stats.items()), columns=['File Type', 'Count'])
            fig_pie = px.pie(stats_df, values='Count', names='File Type', title="Ingested File Types")
            st.plotly_chart(fig_pie, width="stretch", key="ingest_chart")
        else:
            st.info("No ingestion data available yet.")
            
        st.divider()
        st.markdown("### ⚠️ Danger Zone")
        if st.button("🗑️ Delete Insight Data", type="primary"):
            st.warning("Are you sure you want to delete all ingestion logs? This cannot be undone.")
            if st.button("Yes, Delete All Data", type="secondary"):
                if logger.delete_ingestion_logs():
                    st.success("All insight data deleted successfully.")
                    st.rerun()
                else:
                    st.error("Failed to delete data.")

    st.divider()
    st.caption("Admin Panel v2.0 | EduBuddy")
