import streamlit as st
import pandas as pd
import psycopg
from db_config import get_connection


def family_members_tab(user):
    st.title("👨‍👩‍👧‍👦 Family Members")

    # --- Database Connection ---
    conn = get_connection()
    cur = conn.cursor()

    # --- Get Available M No for the User's Village ---
    mno_list = pd.read_sql(
        "SELECT m_no FROM m_no_register WHERE village_name = %s ORDER BY m_no",
        conn, params=(user['village'],)
    )

    if mno_list.empty:
        st.warning("⚠️ कृपया आधी 'M No Register' मध्ये नोंदी जोडा.")
        st.stop()

    # --- Menu for Add/Edit/Delete ---
    st.markdown("### कृपया खालीलपैकी एक पर्याय निवडा:")
    action = st.radio(
        "Select Action",
        ["➕ Add Member", "✏️ Edit Member", "❌ Delete Member"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.divider()

    # ------------------ ADD MEMBER ------------------
    if action == "➕ Add Member":
        st.subheader("🟢 नवीन सदस्य नोंदणी")

        with st.form("add_member_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                mno = st.selectbox("M No निवडा:", mno_list["m_no"])
                member_name = st.text_input("सदस्याचे नाव:")
                age = st.number_input("वय:", min_value=0, step=1)
                gender = st.selectbox("लिंग:", ["Male", "Female", "Other"])
            with col2:
                bp = st.checkbox("BP रुग्ण आहे का?")
                sugar = st.checkbox("Sugar रुग्ण आहे का?")
                other = st.text_input("इतर आजार:")
                mobile = st.text_input("मोबाईल क्रमांक:")

            if st.form_submit_button("💾 सदस्य जोडा"):
                if not member_name.strip():
                    st.warning("⚠️ कृपया सदस्याचे नाव भरा.")
                else:
                    try:
                        cur.execute("""
                            INSERT INTO family_members
                            (village_name, m_no, member_name, age, gender, bp, sugar, other, mobile)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            user["village"], int(mno), member_name, int(age), gender, bp, sugar, other, mobile
                        ))
                        conn.commit()
                        st.success(f"✅ '{member_name}' (M No {mno}) यांची नोंद जतन झाली.")
                    except psycopg.Error as e:
                        conn.rollback()
                        st.error(f"❌ Database Error: {e.pgerror}")

    # ------------------ EDIT MEMBER ------------------
    elif action == "✏️ Edit Member":
        st.subheader("✏️ सदस्य माहिती संपादित करा")

        member_list = pd.read_sql("""
            SELECT id, member_name, m_no FROM family_members
            WHERE village_name = %s ORDER BY m_no
        """, conn, params=(user['village'],))

        if not member_list.empty:
            member_display = member_list.apply(lambda x: f"M No {x['m_no']} - {x['member_name']}", axis=1)
            selected = st.selectbox("संपादनासाठी सदस्य निवडा:", member_display)

            selected_id = int(
                member_list.loc[member_display == selected, "id"].values[0]
            )

            cur.execute("SELECT * FROM family_members WHERE id = %s", (selected_id,))
            rec = cur.fetchone()
            cols = [d[0] for d in cur.description]
            data = dict(zip(cols, rec))

            with st.form("edit_member_form"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("M No", value=data["m_no"], disabled=True)
                    member_name = st.text_input("सदस्याचे नाव:", value=data["member_name"])
                    age = st.number_input("वय:", value=data["age"], min_value=0, step=1)
                    gender = st.selectbox("लिंग:", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(data["gender"]))
                with col2:
                    bp = st.checkbox("BP रुग्ण", value=data["bp"])
                    sugar = st.checkbox("Sugar रुग्ण", value=data["sugar"])
                    other = st.text_input("इतर आजार:", value=data["other"])
                    mobile = st.text_input("मोबाईल क्रमांक:", value=data["mobile"])

                if st.form_submit_button("💾 बदल जतन करा"):
                    try:
                        cur.execute("""
                            UPDATE family_members
                            SET member_name=%s, age=%s, gender=%s, bp=%s, sugar=%s, other=%s, mobile=%s
                            WHERE id=%s
                        """, (member_name, int(age), gender, bp, sugar, other, mobile, selected_id))
                        conn.commit()
                        st.success("✅ सदस्य माहिती यशस्वीरित्या अद्यतनित झाली.")
                        st.rerun()
                    except psycopg.Error as e:
                        conn.rollback()
                        st.error(f"❌ Edit Error: {e.pgerror}")
        else:
            st.info("⛔ सध्या कोणतीही सदस्य नोंद उपलब्ध नाही.")

    # ------------------ DELETE MEMBER ------------------
    elif action == "❌ Delete Member":
        st.subheader("❌ सदस्य हटवा")

        member_list = pd.read_sql("""
            SELECT id, member_name, m_no FROM family_members
            WHERE village_name = %s ORDER BY m_no
        """, conn, params=(user['village'],))

        if not member_list.empty:
            member_display = member_list.apply(lambda x: f"M No {x['m_no']} - {x['member_name']}", axis=1)
            selected = st.selectbox("हटवण्यासाठी सदस्य निवडा:", member_display)

            if st.button("🗑️ सदस्य हटवा"):
                selected_id = int(
                    member_list.loc[member_display == selected, "id"].values[0]
                )
                try:
                    cur.execute("DELETE FROM family_members WHERE id = %s", (selected_id,))
                    conn.commit()
                    st.success("✅ सदस्य नोंद हटवली गेली.")
                    st.rerun()
                except psycopg.Error as e:
                    conn.rollback()
                    st.error(f"❌ Delete Error: {e.pgerror}")
        else:
            st.info("⛔ हटवण्यासाठी कोणतीही सदस्य नोंद नाही.")

    conn.close()
