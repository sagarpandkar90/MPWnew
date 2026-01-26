import streamlit as st
import pandas as pd
import psycopg
from db_config import get_connection

# ---------------------------
# 🔧 Helper Functions
# ---------------------------
def get_next_mno(cur, village):
    cur.execute("SELECT COALESCE(MAX(m_no), 0) + 1 FROM m_no_register WHERE village_name = %s", (village,))
    return cur.fetchone()[0]


def fetch_all_records(cur, village):
    query = """
        SELECT id, m_no, family_head AS "कुटुंब प्रमुख",
               member_count AS "सदस्य संख्या", mobile AS "मोबाईल",
               ranjan, balar, taki, dera, frize, e_bhandi
        FROM m_no_register
        WHERE village_name = %s
        ORDER BY m_no
    """
    return pd.read_sql(query, cur.connection, params=(village,))


def delete_record(cur, conn, village, mno):
    cur.execute("DELETE FROM m_no_register WHERE village_name=%s AND m_no=%s", (village, mno))
    conn.commit()


def update_record(cur, conn, record_id, family_head, member_count, mobile, address,
                  ranjan, balar, taki, dera, frize, e_bhandi):
    try:
        cur.execute("""
            UPDATE m_no_register
            SET family_head=%s, member_count=%s, mobile=%s, address=%s,
                ranjan=%s, balar=%s, taki=%s, dera=%s, frize=%s, e_bhandi=%s
            WHERE id=%s
        """, (
            family_head, int(member_count), mobile, address,
            int(ranjan), int(balar), int(taki), int(dera), int(frize), int(e_bhandi),
            int(record_id)
        ))
        conn.commit()
        st.success("✅ Record updated successfully.")
    except Exception as e:
        conn.rollback()
        st.error(f"❌ Edit Error: {e}")


# ---------------------------
# 🏠 Main M No Register Page
# ---------------------------
def m_no_register_tab(user):
    st.title("🏠 M No Register")
    conn = get_connection()
    cur = conn.cursor()

    # Main menu buttons
    st.markdown("### कृपया खालीलपैकी एक पर्याय निवडा:")
    menu = st.radio(
        "Select Action",
        ["➕ Add New Record", "✏️ Edit Record", "❌ Delete Record"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.divider()

    # ------------------ ADD NEW RECORD ------------------
    if menu == "➕ Add New Record":
        st.subheader("🟢 नवीन कुटुंब नोंद जोडा")

        with st.form("add_mno_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                m_no = st.number_input("M No :", format="%d", value=get_next_mno(cur, user["village"]))
                family_head = st.text_input("कुटुंब प्रमुखाचे नाव:")
                member_count = st.number_input("घरातील एकूण सदस्य:", min_value=0, step=1)
                mobile = st.text_input("मोबाईल नंबर:")
                address = st.text_area("पत्ता:")

            with col2:
                st.markdown("#### 🏠 घरातील वस्तू:")
                ranjan = st.number_input("रांजण:", min_value=0, step=1)
                balar = st.number_input("बॅलर:", min_value=0, step=1)
                taki = st.number_input("टाकी:", min_value=0, step=1)
                dera = st.number_input("डेरा:", min_value=0, step=1)
                frize = st.number_input("फ्रिज:", min_value=0, step=1)
                e_bhandi = st.number_input("इतर भांडी:", min_value=0, step=1)

            if st.form_submit_button("💾 जतन करा"):
                if not family_head.strip():
                    st.warning("⚠️ कृपया कुटुंब प्रमुखाचे नाव भरा.")
                else:
                    try:
                        cur.execute("""
                            INSERT INTO m_no_register (
                                village_name, m_no, family_head, member_count, mobile,
                                address, ranjan, balar, taki, dera, frize, e_bhandi, created_by
                            )
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            user["village"], int(m_no), family_head, int(member_count), mobile,
                            address, int(ranjan), int(balar), int(taki), int(dera), int(frize), int(e_bhandi),
                            user["username"]
                        ))
                        conn.commit()
                        st.success(f"✅ M No {m_no} — {family_head} यांची नोंद जतन झाली.")
                    except psycopg.Error as e:
                        conn.rollback()
                        st.error(f"❌ Database Error: {e.pgerror}")

    # ------------------ EDIT RECORD ------------------
    elif menu == "✏️ Edit Record":
        st.subheader("✏️ नोंद संपादित करा")

        try:
            record_list = pd.read_sql(
                "SELECT id, m_no, family_head FROM m_no_register WHERE village_name=%s ORDER BY m_no",
                conn, params=(user["village"],)
            )

            if not record_list.empty:
                selected_row = st.selectbox(
                    "संपादनासाठी M No निवडा:",
                    record_list.apply(lambda x: f"{x['m_no']} - {x['family_head']}", axis=1)
                )
                selected_id = int(record_list.loc[
                    record_list.apply(lambda x: f"{x['m_no']} - {x['family_head']}", axis=1) == selected_row, "id"
                ].values[0])

                cur.execute("SELECT * FROM m_no_register WHERE id=%s", (selected_id,))
                rec = cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                data = dict(zip(columns, rec))

                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("M No", value=data["m_no"], disabled=True)
                        family_head = st.text_input("कुटुंब प्रमुखाचे नाव:", value=data["family_head"])
                        member_count = st.number_input("घरातील एकूण सदस्य:", value=data["member_count"], step=1)
                        mobile = st.text_input("मोबाईल नंबर:", value=data["mobile"])
                        address = st.text_area("पत्ता:", value=data["address"])

                    with col2:
                        ranjan = st.number_input("रांजण:", value=data["ranjan"], step=1)
                        balar = st.number_input("बॅलर:", value=data["balar"], step=1)
                        taki = st.number_input("टाकी:", value=data["taki"], step=1)
                        dera = st.number_input("डेरा:", value=data["dera"], step=1)
                        frize = st.number_input("फ्रिज:", value=data["frize"], step=1)
                        e_bhandi = st.number_input("इतर भांडी:", value=data["e_bhandi"], step=1)

                    if st.form_submit_button("💾 बदल जतन करा"):
                        update_record(cur, conn, selected_id, family_head, member_count, mobile, address,
                                      ranjan, balar, taki, dera, frize, e_bhandi)
                        st.rerun()
            else:
                st.info("⛔ संपादित करण्यासाठी कोणतीही नोंद नाही.")
        except Exception as e:
            st.error(f"❌ Edit Error: {e}")

    # ------------------ DELETE RECORD ------------------
    elif menu == "❌ Delete Record":
        st.subheader("❌ नोंद हटवा")

        try:
            delete_options = pd.read_sql(
                "SELECT m_no FROM m_no_register WHERE village_name=%s ORDER BY m_no",
                conn, params=(user["village"],)
            )
            if not delete_options.empty:
                delete_mno = st.selectbox("हटवण्यासाठी M No निवडा:", delete_options["m_no"])
                if st.button("🗑️ निवडलेली नोंद हटवा"):
                    delete_record(cur, conn, user["village"], delete_mno)
                    st.success(f"🗑️ M No {delete_mno} यांची नोंद हटवली गेली.")
                    st.rerun()
            else:
                st.info("⛔ हटवण्यासाठी कोणतीही नोंद उपलब्ध नाही.")
        except Exception as e:
            st.error(f"❌ Delete Error: {e}")

    conn.close()
