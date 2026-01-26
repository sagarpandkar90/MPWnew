# reports_and_search.py
import streamlit as st
import pandas as pd
import base64
import json
from db_config import get_connection
from streamlit.components.v1 import html as components_html

# ==========================
# 🔧 Helper Functions
# ==========================
def generate_village_report(user, rtype="All Members", mno=None):
    """Fetch filtered records for a village based on type (All, BP, Sugar, Both)."""
    conn = get_connection()
    q = """
        SELECT f.*, m.family_head
        FROM family_members f
        JOIN m_no_register m
        ON f.m_no = m.m_no AND f.village_name = m.village_name
        WHERE f.village_name = %s
    """
    params = [user["village"]]
    if mno:
        q += " AND f.m_no = %s"
        params.append(mno)

    if rtype == "BP Patients":
        q += " AND f.bp = TRUE"
    elif rtype == "Sugar Patients":
        q += " AND f.sugar = TRUE"
    elif rtype == "Both (BP + Sugar)":
        q += " AND f.bp = TRUE AND f.sugar = TRUE"

    df = pd.read_sql(q, conn, params=params)
    conn.close()
    return df

# ==========================
# 📄 PDF Generation for M No-wise
# ==========================
def generate_pdf_make(data_df, font_b64):
    """Generate M No-wise PDF with family head, address, and other fields."""
    data_json = []
    for _, row in data_df.iterrows():
        data_json.append({
            "m_no": str(row["m_no"]),
            "family_head": str(row["family_head"]),
            "member": int(row.get("member_count", 0)),
            "ranjan": int(row.get("ranjan", 0)),
            "balar": int(row.get("balar", 0)),
            "taki": int(row.get("taki", 0)),
            "dera": int(row.get("dera", 0)),
            "freezer": int(row.get("frize", 0)),
            "exta_bhandi": int(row.get("e_bhandi", 0)),
            "address": str(row.get("address", ""))  # new column
        })

    components_html(
        f"""
        <html>
        <head>
            <meta charset='utf-8' />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
        </head>
        <body>
            <div style="margin-bottom:10px;">
                <button onclick="previewPDF()" style="padding:8px 12px; background:#2196F3; color:white; border:none; border-radius:6px; cursor:pointer; margin-right:8px;">👁️ Preview PDF</button>
                <button onclick="downloadPDF()" style="padding:8px 12px; background:#4CAF50; color:white; border:none; border-radius:6px; cursor:pointer;">⬇️ Download PDF</button>
            </div>
            <script>
                const data = {json.dumps(data_json, ensure_ascii=False)};
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
                  defaultStyle: {{ font: "MarathiFont", fontSize: 12 }},  // slightly smaller font
                  pageMargins: [40,15,15,15],
                  header: function(currentPage, pageCount) {{
                      return {{
                        
                      }};
                  }},
                  footer: function(currentPage, pageCount) {{
                      return {{ text: currentPage.toString(), alignment: 'center', margin:[0,10,0,0], fontSize:9 }};
                  }},
                  content: [
                      {{
                        table: {{
                            headerRows: 1,   // ⭐ THIS makes heading repeat on every page
                            widths: ['7%','40%','7%','7%','7%','7%','7%','7%','10%'],  // adjusted for Address
                            body: [
                                [
                                  {{ text: 'M-No', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'कुटुंब प्रमुखाचे नाव', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'ए. सदस्य', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'रांजण', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'बॅलर', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'टाकी', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'डेरा', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'फ्रिज', bold:true, alignment:'center', fontSize: 14 }},
                                  {{ text: 'इतर भांडी', bold:true, alignment:'center', fontSize: 14 }}
                                ],
                                ...data.map(d => [
                                    {{ text: d['m_no'], alignment:'center' }},
                                    {{ text: d['family_head'] }},
                                    {{ text: d['member'], alignment:'center' }},
                                    {{ text: d['ranjan'], alignment:'center' }},
                                    {{ text: d['balar'], alignment:'center' }},
                                    {{ text: d['taki'], alignment:'center' }},
                                    {{ text: d['dera'], alignment:'center' }},
                                    {{ text: d['freezer'], alignment:'center' }},
                                    {{ text: d['exta_bhandi'], alignment:'center' }}
                                ])
                            ]
                        }}
                      }}
                  ]
                }};
                function previewPDF() {{ pdfMake.createPdf(docDefinition).open(); }}
                function downloadPDF() {{ pdfMake.createPdf(docDefinition).download('m_no_register.pdf'); }}
            </script>
        </body>
        </html>
        """, height=700, scrolling=True
    )


# ==========================
# 📄 Village-wise PDF (all members)
# ==========================
def generate_village_pdf(user, font_b64):
    """Generate village-wise PDF with all family members grouped by M No."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT f.*, m.m_no
        FROM family_members f
        JOIN m_no_register m
        ON f.m_no = m.m_no AND f.village_name = m.village_name
        WHERE f.village_name = %s
        ORDER BY f.m_no, f.member_name
    """, conn, params=[user["village"]])
    conn.close()

    if df.empty:
        st.warning("⚠️ No family data found for this village.")
        return

    data_json = []
    for _, row in df.iterrows():
        data_json = []
        for row in df.itertuples(index=False):
            data_json.append({
                "m_no": str(row.m_no),
                "member_name": str(row.member_name),
                "age": str(getattr(row, 'age', '')),
                "gender": str(getattr(row, 'gender', '')),
                "bp": "होय" if getattr(row, 'bp', False) else "नाही",
                "sugar": "होय" if getattr(row, 'sugar', False) else "नाही",
                "other": str(getattr(row, 'other', '')),
                "mobile": str(getattr(row, 'mobile', ''))
            })

    components_html(
        f"""
        <html>
        <head>
            <meta charset='utf-8' />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
        </head>
        <body>
            <div style="margin-bottom:10px;">
                <button onclick="previewPDF()" style="padding:8px 12px; background:#2196F3; color:white; border:none; border-radius:6px; cursor:pointer; margin-right:8px;">👁️ Preview PDF</button>
                <button onclick="downloadPDF()" style="padding:8px 12px; background:#4CAF50; color:white; border:none; border-radius:6px; cursor:pointer;">⬇️ Download PDF</button>
            </div>
            <script>
                const data = {json.dumps(data_json, ensure_ascii=False)};
                pdfMake.vfs["CustomFont.ttf"] = "{font_b64}";
                pdfMake.fonts = {{
                  MarathiFont: {{
                    normal: "CustomFont.ttf",
                    bold: "CustomFont.ttf",
                    italics: "CustomFont.ttf",
                    bolditalics: "CustomFont.ttf"
                  }}
                }};
                const bodyData = [
                    [
                        {{ text: 'M-No', bold:true, alignment:'center' }},
                        {{ text: 'सदस्याचे नाव', bold:true, alignment:'center' }},
                        {{ text: 'वय', bold:true, alignment:'center' }},
                        {{ text: 'लिंग', bold:true, alignment:'center' }},
                        {{ text: 'BP', bold:true, alignment:'center' }},
                        {{ text: 'Sugar', bold:true, alignment:'center' }},
                        {{ text: 'इतर आजार', bold:true, alignment:'center' }},
                        {{ text: 'मोबाईल', bold:true, alignment:'center' }}
                    ]
                ];
                data.forEach(d => {{
                    bodyData.push([
                        {{ text: d['m_no'], alignment:'center' }},
                        {{ text: d['member_name'] }},
                        {{ text: d['age'], alignment:'center' }},
                        {{ text: d['gender'], alignment:'center' }},
                        {{ text: d['bp'], alignment:'center' }},
                        {{ text: d['sugar'], alignment:'center' }},
                        {{ text: d['other'] }},
                        {{ text: d['mobile'] }}
                    ]);
                }});
                const docDefinition = {{
                  defaultStyle: {{ font: "MarathiFont" }},
                  pageMargins: [30,50,30,40],
                  header: function(currentPage, pageCount) {{
                      return {{
                          text: 'Village-wise Family Members Report - {user["village"]}',
                          alignment:'center', margin:[0,10,0,0], bold:true
                      }};
                  }},
                  footer: function(currentPage, pageCount) {{
                      return {{ text: currentPage.toString(), alignment:'center', margin:[0,10,0,0], fontSize:9 }};
                  }},
                  content: [
                    {{ table: {{ headerRows: 1, widths: ['7%','32%','6%','7%','6%','9%','12%','16%'], body: bodyData }} }}
                  ]
                }};
                function previewPDF() {{ pdfMake.createPdf(docDefinition).open(); }}
                function downloadPDF() {{ pdfMake.createPdf(docDefinition).download('village_family_report.pdf'); }}
            </script>
        </body>
        </html>
        """, height=700, scrolling=True
    )

# ==========================
# Main Reports Page
# ==========================
def reports_page():
    st.title("📊 Reports & PDF Generator")
    user = st.session_state.get("user", {"username":"Guest","village":"Default"})

    tab1, tab2 = st.tabs(["📈 Reports & Search", "📄 PDF Reports"])

    # -------------------------
    # Tab 1: Reports & CSV
    # -------------------------
    with tab1:
        rtype = st.radio("Select Report Type", ["All Members","BP Patients","Sugar Patients","Both (BP + Sugar)"], horizontal=True)
        mno = st.text_input("Search by M No (optional)")
        df = generate_village_report(user, rtype, mno)
        st.write(f"Total Records: {len(df)}")
        if df.empty:
            st.warning("⚠️ No data found.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, file_name="village_report.csv", mime="text/csv")

    # -------------------------
    # Tab 2: PDF Reports
    # -------------------------
    with tab2:
        st.markdown("### 📄 Generate PDF Reports")
        font_path = "../MPWNew/fonts/NotoSerifDevanagari-VariableFont_wdth,wght.ttf"
        with open(font_path, "rb") as f:
            font_b64 = base64.b64encode(f.read()).decode()

        choice = st.radio("Select PDF Type", ["M No-wise PDF", "Village-wise PDF"], horizontal=True)

        if st.button("📄 Generate PDF"):
            if choice == "M No-wise PDF":
                conn = get_connection()
                df_font = pd.read_sql("SELECT * FROM m_no_register WHERE village_name=%s ORDER BY m_no", conn, params=[user["village"]])
                conn.close()
                generate_pdf_make(df_font, font_b64)
            else:  # Village-wise PDF
                generate_village_pdf(user, font_b64)
