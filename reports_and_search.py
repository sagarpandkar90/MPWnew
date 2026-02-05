# reports_and_search.py
from pathlib import Path
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
def generate_pdf_make(df, font_b64):
    """Create Marathi Register PDF with inside binding margins and tall rows"""
    import json

    # Clean DataFrame
    df_clean = df.fillna("").astype(str)
    data_json = json.dumps(df_clean.to_dict(orient="records"), ensure_ascii=False)

    # Months Configuration
    p1_months = ["jan", "feb", "mar", "apr"]
    p1_marathi = ["जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल"]
    p2_months = ["may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    p2_marathi = ["मे", "जून", "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"]

    # Widths for Portrait
    widths_p1 = [30, 145, 45] + [24, 24] * len(p1_marathi)
    widths_p2 = [23, 23] * len(p2_marathi)

    html = f"""
<html>
<head>
<meta charset="UTF-8"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
</head>
<body>

<button onclick="previewPDF()" style="padding:12px 24px; background:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">Generate High-Padding Register</button>

<script>
pdfMake.vfs["Marathi.ttf"] = "{font_b64}";
pdfMake.fonts = {{
  MarathiFont: {{
    normal:"Marathi.ttf", bold:"Marathi.ttf", italics:"Marathi.ttf", bolditalics:"Marathi.ttf"
  }}
}};

const tableData = {data_json};
const content = [];

function buildTable(fixedCols, months, monthKeys, tableData, widths, isSecondPage){{
    const headerRow1 = [];
    const headerRow2 = [];

    // Determine row padding based on page type
    // Page 2 (May-Dec) gets even more height as requested
    const cellMargin = isSecondPage ? [1, 14.3, 1, 14.3] : [1, 5, 1, 5];

    // Header Setup
    for(const c of fixedCols){{
        headerRow1.push({{text:c, bold:true, alignment:"center", rowSpan:2, margin:[1,4,1,4]}});
        headerRow2.push("");
    }}
    for(const m of months){{
        headerRow1.push({{text:m, colSpan:2, alignment:"center", bold:true, margin:[1,4,1,4]}});
        headerRow1.push({{}});
        headerRow2.push({{text:"I", bold:true, alignment:"center", fontSize:10}});
        headerRow2.push({{text:"II", bold:true, alignment:"center", fontSize:10}});
    }}

    const dataRows = [];
    // Calculate total rows to show (fixed at 22 for register feel)
    const rowsToRender = 23;

    for(let r=0; r < rowsToRender; r++){{
        const row = [];
        const rec = tableData[r] || {{}}; // Empty object if no data for this row

        for(const c of fixedCols){{
            let key = "";
            if(c === "एम. नं.") key = "m_no";
            else if(c === "कुटुंब प्रमुखाचे नाव") key = "family_head";
            else key = "member_count";
            row.push({{ text: rec[key] || "", alignment:"center", bold:true, margin:cellMargin }});
        }}

        for(const mk of monthKeys){{
            row.push({{ text: rec[mk + "_1"] || "", alignment:"center", bold:true, margin:cellMargin }});
            row.push({{ text: rec[mk + "_2"] || "", alignment:"center", bold:true, margin:cellMargin }});
        }}
        dataRows.push(row);
    }}

    content.push({{
        table:{{ 
            headerRows:2, 
            widths:widths, 
            body:[headerRow1, headerRow2, ...dataRows] 
        }},
        layout:{{
            hLineWidth: () => 0.7,
            vLineWidth: () => 0.7,
        }},
        // Page 1: Left Bind (40, 20, 15, 35) | Page 2: Right Bind (15, 20, 40, 35)
        margin: isSecondPage ? [45, 20, 15, 35] : [45, 20, 15, 35]
    }});
}}

// Build logic - Process 22 rows at a time
const rowsPerPage = 23;
const totalSets = Math.ceil(tableData.length / rowsPerPage) || 1;

for(let setNum = 0; setNum < totalSets; setNum++){{
    const startIdx = setNum * rowsPerPage;
    const subset = tableData.slice(startIdx, startIdx + rowsPerPage);

    // Page 1: Member Info + Jan-Apr
    buildTable(
        ["एम. नं.", "कुटुंब प्रमुखाचे नाव", "ए.सदस्य संख्या"],
        {json.dumps(p1_marathi, ensure_ascii=False)},
        {json.dumps(p1_months, ensure_ascii=False)},
        subset,
        {json.dumps(widths_p1)},
        false
    );
    content.push({{text:"", pageBreak:"after"}});

    // Page 2: May-Dec (Larger rows)
    buildTable(
        [],
        {json.dumps(p2_marathi, ensure_ascii=False)},
        {json.dumps(p2_months, ensure_ascii=False)},
        subset,
        {json.dumps(widths_p2)},
        true
    );

    if(setNum < totalSets - 1) content.push({{text:"", pageBreak:"after"}});
}}

const docDefinition = {{
    pageSize:"A4",
    pageOrientation: 'portrait',
    pageMargins:[0, 0, 0, 0], 
    defaultStyle:{{ font:"MarathiFont", fontSize:12, bold:true }},
    footer: function(currentPage) {{
        let logicPage = Math.ceil(currentPage / 2);
        return {{ text: logicPage.toString(), alignment: 'center', fontSize: 11, margin: [0, 10, 0, 0] }};
    }},
    content:content
}};

function previewPDF(){{ pdfMake.createPdf(docDefinition).open(); }}
</script>
</body>
</html>
"""

    components_html(html, height=700, scrolling=True)


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
    user = st.session_state.get("user", {"username": "Guest", "village": "Default"})

    tab1, tab2 = st.tabs(["📈 Reports & Search", "📄 PDF Reports"])

    # -------------------------
    # Tab 1: Reports & CSV
    # -------------------------
    with tab1:
        rtype = st.radio("Select Report Type", ["All Members", "BP Patients", "Sugar Patients", "Both (BP + Sugar)"],
                         horizontal=True)
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
        BASE_DIR = Path(__file__).resolve().parent
        font_path = BASE_DIR / "fonts" / "NotoSerifDevanagari-VariableFont_wdth,wght.ttf"
        with open(font_path, "rb") as f:
            font_b64 = base64.b64encode(f.read()).decode()

        choice = st.radio("Select PDF Type", ["M No-wise PDF", "Village-wise PDF"], horizontal=True)

        if st.button("📄 Generate PDF"):
            if choice == "M No-wise PDF":
                conn = get_connection()
                df_font = pd.read_sql("SELECT * FROM m_no_register WHERE village_name=%s ORDER BY m_no", conn,
                                      params=[user["village"]])
                conn.close()
                generate_pdf_make(df_font, font_b64)
            else:  # Village-wise PDF
                generate_village_pdf(user, font_b64)
