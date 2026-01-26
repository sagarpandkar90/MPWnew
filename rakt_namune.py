import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

def rakt_namne_pdf():
    st.title("Blood Smear Report - Exact Format")

    # 1. Page Count Input
    num_pages = st.number_input("Number of Pages:", min_value=1, max_value=100, value=1)

    # 2. Font Loading (Required for Marathi/English rendering)
    font_path = Path("../MPWNew/fonts/NotoSerifDevanagari-VariableFont_wdth,wght.ttf")
    if not font_path.exists():
        st.error("⚠️ Font file missing in 'fonts' folder!")
        return
    font_b64 = base64.b64encode(font_path.read_bytes()).decode()

    # 3. HTML/JS with PDF logic
    html_template = f"""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
        <style>
            body {{ font-family: sans-serif; display: flex; gap: 10px; padding: 10px; }}
            .btn {{
                padding: 10px 18px; border: none; border-radius: 6px; 
                cursor: pointer; font-weight: bold; color: white; font-size: 13px;
            }}
            .btn-generate {{ background-color: #673AB7; }}
            .btn-download {{ background-color: #2196F3; }}
        </style>
    </head>
    <body>
        <button class="btn btn-generate" onclick="generatePDF('preview')">Preview PDF</button>
        <button class="btn btn-download" onclick="generatePDF('download')">Download PDF</button>

        <script>
        pdfMake.vfs["Marathi.ttf"] = "{font_b64}";
        pdfMake.fonts = {{
            MarathiFont: {{
                normal: "Marathi.ttf",
                bold: "Marathi.ttf"
            }}
        }};

        function getReportSection() {{
            return [
                {{ text: "For Reporting of Blood Smears by MPW / HA / Passive Agency", style: 'header' }},
                {{ text: "Name of Section: ________________________", margin: [0, 2, 0, 5], fontSize: 8 }},
                {{
                    columns: [
                        {{ text: "Headquater: ____________", fontSize: 8 }},
                        {{ text: "Code No.: ____________", fontSize: 8, alignment: 'right' }}
                    ],
                    margin: [0, 0, 0, 5]
                }},
                {{
                    table: {{
                        headerRows: 4,
                        widths: [20, 28, 50, 45, 12, 12, 35, 30, 28, 14, 14, 14, 18, 18, '*'],
                        body: [
                            // Row 1: Main Headers
                            [
                                {{ text: "House\\nNo.", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Village", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Name of the Head\\nof Family", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Name of the\\nPatient", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Age", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Sex", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Treatment\\nSr.No.\\nBlood\\nSmear", rowSpan: 4, style: 'tHead' }},
                                {{ text: "No. of\\nTablets\\nGiven\\n(4-Amino\\nQuinoline)", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Date of\\nCollec\\ntion", rowSpan: 4, style: 'tHead' }},
                                {{ text: "Result (9)\\nIndicate\\nStage", colSpan: 5, style: 'tHead' }},
                                {{}}, {{}}, {{}}, {{}},
                                {{ text: "If +\\nMixed\\nProgre\\nssive\\nCase\\nNo.", rowSpan: 4, style: 'tHead' }}
                            ],
                            // Row 2: F and M headers (no V mentioned in original)
                            [
                                {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}},
                                {{ text: "F", colSpan: 3, style: 'tHead' }},
                                {{}}, {{}},
                                {{ text: "+ve", colSpan: 2, style: 'tHead' }},
                                {{}},
                                {{}}
                            ],
                            // Row 3: R, G, RG under F, M under +ve
                            [
                                {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}},
                                {{ text: "R", style: 'tHead' }},
                                {{ text: "G", style: 'tHead' }},
                                {{ text: "RG", style: 'tHead' }},
                                {{ text: "M", colSpan: 2, style: 'tHead' }},
                                {{}},
                                {{}}
                            ],
                            // Row 4: Column numbering
                            [
                                {{ text: "2", style: 'numRow' }},
                                {{ text: "1", style: 'numRow' }},
                                {{ text: "3", style: 'numRow' }},
                                {{ text: "4", style: 'numRow' }},
                                {{ text: "(5 a)", style: 'numRow' }},
                                {{ text: "(5 b)", style: 'numRow' }},
                                {{ text: "6", style: 'numRow' }},
                                {{ text: "7", style: 'numRow' }},
                                {{ text: "8", style: 'numRow' }},
                                {{ text: "", style: 'numRow' }},
                                {{ text: "", style: 'numRow' }},
                                {{ text: "", style: 'numRow' }},
                                {{ text: "9", colSpan: 2, style: 'numRow' }},
                                {{}},
                                {{ text: "10", style: 'numRow' }}
                            ],
                            // Data Rows (18 empty rows)
                            ...Array(18).fill([
                                {{ text: " ", margin: [0, 8, 0, 8] }}, "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                            ])
                        ]
                    }},
                    margin: [0, 0, 0, 5]
                }},
                {{
                    columns: [
                        {{
                            width: '*',
                            stack: [
                                {{ text: "Population: ____________", fontSize: 8 }},
                                {{ text: "Name of P.H.C.: ____________", fontSize: 8, margin: [0, 3, 0, 0] }},
                                {{ text: "Date of Examination: ____________", fontSize: 8, margin: [0, 3, 0, 0] }}
                            ]
                        }},
                        {{
                            width: '*',
                            stack: [
                                {{ text: "Signature Microscopist", fontSize: 8, margin: [0, 12, 0, 0], alignment: 'center' }},
                                {{ text: "Signature of MPW / HA / HS / others", fontSize: 8, margin: [0, 12, 0, 0], alignment: 'center' }}
                            ]
                        }}
                    ],
                    margin: [0, 5, 0, 0]
                }}
            ];
        }}

        function generatePDF(action) {{
            let content = [];
            for (let p = 0; p < {num_pages}; p++) {{
                content.push(...getReportSection());
                if (p < {num_pages} - 1) content.push({{ text: "", pageBreak: "after" }});
            }}

            const docDefinition = {{
                pageSize: "A4",
                pageOrientation: "landscape",
                pageMargins: [20, 25, 20, 25],
                defaultStyle: {{ font: "MarathiFont", fontSize: 7 }},
                styles: {{
                    header: {{ fontSize: 10, bold: true, alignment: 'center' }},
                    tHead: {{ fontSize: 6, bold: true, alignment: 'center', fillColor: '#F2F2F2' }},
                    numRow: {{ fontSize: 6, alignment: 'center', fillColor: '#EAEAEA' }},
                    footer: {{ fontSize: 8 }}
                }},
                content: content
            }};

            if (action === 'download') {{
                pdfMake.createPdf(docDefinition).download("Blood_Smear_Report.pdf");
            }} else {{
                pdfMake.createPdf(docDefinition).open();
            }}
        }}
        </script>
    </body>
    </html>
    """
    components.html(html_template, height=150)

if __name__ == "__main__":
    rakt_namne_pdf()