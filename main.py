import streamlit as st
import pandas as pd
import bcrypt
from monthly_repoert import monthly_repo
from xhtml2pdf import pisa
import io
from db_config import get_connection
from kitkshastriy_survekshan import entomological_survey_pdf
from m_no_register import m_no_register_tab
from add_member import family_members_tab
from mothly_diary import monthly_diary
from polio_imunization_list import beneficiaries_tab
from rakt_namune import rakt_namne_pdf
from reg import combined_all_registers
from reports_and_search import reports_page
from yearly_dairy import dairy

st.set_page_config(page_title="Village Health Register", layout="wide")


# ---------------- Helper Functions ----------------
def hash_password(password):
    password = password[:72]
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, stored_hash):
    try:
        return bcrypt.checkpw(password[:72].encode("utf-8"), stored_hash.encode("utf-8"))
    except ValueError:
        return False


def verify_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash, village_name, role FROM users WHERE username=%s", (username,))
    record = cur.fetchone()
    cur.close();
    conn.close()
    if record:
        hashed, village, role = record
        if verify_password(password, hashed):
            return {"username": username, "village": village, "role": role}
    return None


def create_pdf_from_html(html_str):
    pdf_bytes = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_str), dest=pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes


# ---------------- Logout Function ----------------
def logout():
    """Clear user session and reload app"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()  # reload app


# ---------------- Login ----------------
if "user" not in st.session_state:
    st.title("🔐 Login – Village Health Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = verify_user(username, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome {user['username']} ({user['village']})")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# ---------------- Main App ----------------
user = st.session_state.user
st.sidebar.success(f"👤 {user['username']} ({user['village']}) – {user['role']}")

# Logout button in sidebar
if st.sidebar.button("🚪 Logout"):
    logout()

# Tabs for navigation
tabs = ["🏠 M No Register", "👨‍👩‍👧 Family Members", "📊 Reports & Search", "Monthly Diary", "MPW Registers", "💉 Immunization List", "Yearly Dairy", "Entomological Survey", "Monthly Report", "Blood sample register"]
if user["role"].lower() == "admin":
    tabs.append("👥 Admin")

tab = st.sidebar.radio("Navigate", tabs)

# ---------------- M No Register ----------------
if tab == "🏠 M No Register":
    m_no_register_tab(user)

# ---------------- Family Members ----------------
elif tab == "👨‍👩‍👧 Family Members":
    family_members_tab(user)

# ---------------- Reports & Search ----------------
elif tab == "📊 Reports & Search":
    reports_page()
elif tab == "💉 Immunization List":
    beneficiaries_tab(user)
elif tab == "Monthly Diary":
    monthly_diary()
elif tab == "MPW Registers":
    combined_all_registers()
elif tab == "Yearly Dairy":
    dairy()
elif tab == "Entomological Survey":
    entomological_survey_pdf()
elif tab == "Monthly Report":
    monthly_repo()
elif tab == "Blood sample register":
    rakt_namne_pdf()
# ---------------- Admin ----------------
elif tab == "👥 Admin":
    if user["role"].lower() != "admin":
        st.error("🚫 Admin only.")
        st.stop()

    st.header("👥 Admin – Manage Users")

    # Add User Form
    with st.form("add_user"):
        uname = st.text_input("Username")
        upass = st.text_input("Password", type="password")
        vil = st.text_input("Village")
        role = st.selectbox("Role", ["user", "admin"])
        sub = st.form_submit_button("Create User")
        if sub:
            conn = get_connection();
            cur = conn.cursor()
            cur.execute("INSERT INTO users(username,password_hash,village_name,role) VALUES(%s,%s,%s,%s)",
                        (uname, hash_password(upass), vil, role))
            conn.commit();
            cur.close();
            conn.close()
            st.success(f"✅ Added user {uname}")

    # Reset Password Form
    with st.form("reset_user"):
        rname = st.text_input("Username to Reset")
        newpass = st.text_input("New Password", type="password")
        rsub = st.form_submit_button("Reset Password")
        if rsub:
            conn = get_connection();
            cur = conn.cursor()
            cur.execute("UPDATE users SET password_hash=%s WHERE username=%s",
                        (hash_password(newpass), rname))
            conn.commit();
            cur.close();
            conn.close()
            st.success("🔑 Password reset done.")

    # Show all users
    conn = get_connection()
    df = pd.read_sql("SELECT id, username, village_name, role FROM users ORDER BY id", conn)
    st.dataframe(df)
    conn.close()
