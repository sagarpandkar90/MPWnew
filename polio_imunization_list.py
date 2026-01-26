# beneficiaries_tab.py
import time
import streamlit as st
import pandas as pd
from datetime import date
import io, json, base64
import streamlit.components.v1 as components
from db_config import get_connection
from pathlib import Path
# ---------------- Beneficiaries Tab ----------------
def beneficiaries_tab(user):
    st.header("✅ Beneficiaries / Immunization List")

    menu = st.radio("Choose action:", ["Add Beneficiary", "View / Edit", "Export / Download", "Generate PDF"])
    created_by = user['username']  # store logged-in user for linking

    # ---------------- Add Beneficiary ----------------
    if menu == "Add Beneficiary":
        st.subheader("Add Beneficiary")
        with st.form("add_beneficiary_form", clear_on_submit=True):
            name = st.text_input("Child Name")
            dob = st.date_input("Date of Birth", value=date.today())
            gender = st.selectbox("Gender", ["M","F","O"])
            booth_no = st.text_input("Booth No")
            submit = st.form_submit_button("Add Beneficiary")

        if submit:
            if not name.strip():
                st.error("Name is required")
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO beneficiaries (name,dob,gender,booth_no,created_by) VALUES (%s,%s,%s,%s,%s)",
                        (name.strip(), dob, gender, booth_no.strip(), created_by)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"{name} added successfully!")
                except Exception as e:
                    st.error(f"Insert failed: {e}")

    # ---------------- View / Edit ----------------
    elif menu == "View / Edit":
        st.subheader("View / Edit Beneficiaries")
        try:
            conn = get_connection()
            df = pd.read_sql(
                "SELECT id,name,dob,gender,booth_no FROM beneficiaries WHERE created_by=%s ORDER BY id",
                conn, params=(created_by,)
            )
            conn.close()
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            df = pd.DataFrame()

        if df.empty:
            st.info("No beneficiaries found")
        else:
            df["dob"] = pd.to_datetime(df["dob"]).dt.date
            st.dataframe(df, use_container_width=True)

            # Edit / Delete selection
            df["label"] = df["id"].astype(str) + " — " + df["name"]
            selection = st.selectbox("Select beneficiary to edit/delete", df["label"].tolist())
            sel_id = int(selection.split(" — ")[0])
            row = df[df["id"]==sel_id].iloc[0]

            with st.form("edit_form"):
                edit_name = st.text_input("Name", value=row["name"])
                edit_dob = st.date_input("Date of Birth", value=row["dob"])
                edit_gender = st.selectbox("Gender", ["M","F","O"], index=["M","F","O"].index(row["gender"]))
                edit_booth = st.text_input("Booth No", value=row["booth_no"])
                save = st.form_submit_button("Save Changes")

            if st.button("Delete Beneficiary"):
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM beneficiaries WHERE id=%s", (sel_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("Deleted successfully")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Delete failed: {e}")

            if save:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE beneficiaries SET name=%s,dob=%s,gender=%s,booth_no=%s WHERE id=%s",
                        (edit_name, edit_dob, edit_gender, edit_booth, sel_id)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("Updated successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")

    # ---------------- Export / Download ----------------
    elif menu == "Export / Download":
        st.subheader("Export Beneficiaries")
        try:
            conn = get_connection()
            df = pd.read_sql(
                "SELECT id,name,dob,gender,booth_no FROM beneficiaries WHERE created_by=%s ORDER BY id",
                conn, params=(created_by,)
            )
            conn.close()
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            df = pd.DataFrame()

        if df.empty:
            st.info("No data to export")
        else:
            df["dob"] = pd.to_datetime(df["dob"]).dt.date
            st.dataframe(df, use_container_width=True)

            # Excel download
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="beneficiaries")
            towrite.seek(0)
            st.download_button(
                "⬇️ Download Excel",
                data=towrite,
                file_name="beneficiaries.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ---------------- Generate PDF ----------------
    elif menu == "Generate PDF":
        st.subheader("Generate PDF of Beneficiaries")

        # Inputs above table
        ldate = st.date_input("Immunization Date", value=date.today())
        booth_no = st.text_input("Booth No")
        booth_name = st.text_input("Booth Name")
        phc_name = st.text_input("PHC Name")
        shc_name = st.text_input("SHC Name")
        village = user['village']

        ldate_str = ldate.strftime("%d-%m-%Y")

        # Fetch beneficiaries for this user and booth
        try:
            conn = get_connection()
            df = pd.read_sql(
                "SELECT name,dob,gender FROM beneficiaries WHERE created_by=%s AND booth_no=%s ORDER BY name",
                conn, params=(user['username'], booth_no)
            )
            conn.close()
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            df = pd.DataFrame()

        if df.empty:
            st.info("No data to generate PDF")
        else:
            df["dob"] = pd.to_datetime(df["dob"]).dt.strftime("%d-%m-%Y")
            data_json = df.to_dict(orient="records")
            BASE_DIR = Path(__file__).resolve().parent
            font_path = BASE_DIR / "fonts" / "NotoSerifDevanagari-VariableFont_wdth,wght.ttf"
            with open(font_path, "rb") as f:
                font_b64 = base64.b64encode(f.read()).decode("utf-8")

            if st.button("Generate PDF") and font_b64:
                with st.spinner("PDF तयार होत आहे..."):
                    time.sleep(1)

                st.success("✅ PDF तयार झाला! खाली प्रीव्ह्यू आणि डाउनलोड 👇")
                components.html(f"""
                <html>
                <head>
                  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
                  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
                </head>
                <body>
                  <button onclick="previewPDF()">👁️ Preview PDF</button>
                  <button onclick="downloadPDF()">⬇️ Download PDF</button>
                  <script>
                    const data = {json.dumps(data_json, ensure_ascii=False)};
                    const form_data = {{
                        'ldate':'{ldate_str}',
                        'booth_no':'{booth_no}',
                        'booth_name':'{booth_name}',
                        'phc_name':'{phc_name}',
                        'shc_name':'{shc_name}',
                        'village':'{village}'
                    }};

                    pdfMake.vfs["CustomFont.ttf"] = "{font_b64}";
                    pdfMake.fonts = {{
                        MarathiFont: {{
                            normal: "CustomFont.ttf",
                            bold: "CustomFont.ttf",
                            italics: "CustomFont.ttf",
                            bolditalics: "CustomFont.ttf"
                        }}
                    }};

                    const docDefinition = {{
                        defaultStyle: {{ font: "MarathiFont", fontSize: 10 }},
                       pageMargins: [40, 161, 30, 40],
                        header: function(currentPage, pageCount) {{
                            return {{
                                margin: [40, 40, 30, 0],
                                stack:[
                                    {{text:"पल्स पोलिओ लसीकरण मोहीम "+form_data.ldate.split("-")[2], fontSize:16, alignment:"center"}},
                                    {{ text: "प्राथमिक आरोग्य केंद्र "+form_data.phc_name, fontSize: 16, alignment: "center"}},
                                    {{ text: "उपकेंद्र: "+form_data.shc_name+"                                   बुथ क्रमांक: " + (form_data.booth_no || "") + "                              बुथचे नाव: " + (form_data.booth_name|| ""), margin:[0,5,0,5], alignment:"center",fontSize: 11.5}},
                                    {{text:"० ते ५ वर्षे वयोगटातील अपेक्षित लाभार्थी यादी", fontSize:14, alignment:"center"}},
                                    
                                    {{
                                        margin: [0, 0, 0, 0],
                                        table:{{
                                            widths: ["5%", "45%", "15%", "5%", "15%", "15%"],
                                            body:[[ 
                                                {{text:"अ.क्र.", bold:true, alignment:"center"}},
                                                {{text:"लाभार्थीचे नाव", bold:true, alignment:"center"}},
                                                {{text:"जन्मदिनांक", bold:true, alignment:"center"}},
                                                {{text:"लिंग", bold:true, alignment:"center"}},
                                                {{text:form_data.ldate, bold:true, alignment:"center"}},
                                                {{text:"शेरा", bold:true, alignment:"center"}}
                                            ]]
                                        }}
                                    }}
                                ]
                            }};
                        }},
                        content:[ {{
                            table: {{
                                widths: ["5%", "45%", "15%", "5%", "15%", "15%"],
                                body:[ ...data.map((d,i)=>[
                                    {{text:i+1, alignment:"center"}},
                                    {{text:d.name||"", alignment:"left", wrap:true}},
                                    {{text:d.dob||"", alignment:"center"}},
                                    {{text:d.gender||"", alignment:"center"}},
                                    {{text:"", alignment:"center"}},
                                    {{text:"", alignment:"center"}}
                                ]) ]
                            }}
                        }} ]
                    }};

                    function previewPDF() {{ pdfMake.createPdf(docDefinition).open(); }}
                    function downloadPDF() {{ pdfMake.createPdf(docDefinition).download("beneficiaries.pdf"); }}
                  </script>
                </body>
                </html>
                """, height=700, scrolling=True)
