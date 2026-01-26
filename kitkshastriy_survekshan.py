import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

def entomological_survey_pdf():
    st.title("दैनिक कीटकशास्त्रीय सर्वेक्षण (PDF Generator)")

    # 1. Page Count Input
    num_pages = st.number_input("किती पेजेस हवी आहेत?", min_value=1, max_value=100, value=1)

    # 2. Font Loading
    BASE_DIR = Path(__file__).resolve().parent
    font_path = BASE_DIR / "fonts" / "NotoSerifDevanagari-VariableFont_wdth,wght.ttf"
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
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .btn-generate {{ background-color: #673AB7; }}
            .btn-preview {{ background-color: #E91E63; }}
            .btn-download {{ background-color: #2196F3; }}
            .btn:hover {{ filter: brightness(1.1); }}
        </style>
    </head>
    <body>
        <button class="btn btn-generate" onclick="generatePDF('preview')">Generate PDF</button>
        <button class="btn btn-preview" onclick="generatePDF('preview')">Preview</button>
        <button class="btn btn-download" onclick="generatePDF('download')">Download PDF</button>

        <script>
        pdfMake.vfs["Marathi.ttf"] = "{font_b64}";
        pdfMake.fonts = {{
            MarathiFont: {{
                normal: "Marathi.ttf",
                bold: "Marathi.ttf"
            }}
        }};

        // Improved formula stack to keep result line exactly below index
        function getFormula(label) {{
            return {{
                stack: [
                    {{
                        columns: [
                            {{ text: label + " =", width: 'auto', fontSize: 8.5, margin: [0, 8, 3, 0] }},
                            {{
                                width: 'auto',
                                stack: [
                                    {{ text: "...........", alignment: 'center', fontSize: 8 }},
                                    {{ canvas: [{{ type: 'line', x1: 0, y1: 1, x2: 45, y2: 1, lineWidth: 1 }}] }},
                                    {{ text: "...........", alignment: 'center', fontSize: 8, margin: [0, 1, 0, 0] }}
                                ] 
                            }},
                            {{ text: " X १००", width: 'auto', fontSize: 8.5, margin: [3, 8, 0, 0] }}
                        ]
                    }},
                    {{ text: "= ............ %", fontSize: 9, margin: [42, 3, 0, 0] }}
                ],
                margin: [0, 0, 15, 0] // Horizontal spacing between indexes
            }};
        }}

        function getSurveySection(isFirstInPage) {{
            const headers = [
                "एम.नं.", "कुटुंब प्रमुखाचे नाव", "घरातील\\nव्यक्तीची\\nसंख्या ", 
                "घरातील\\nकंटेनरची\\nसंख्या", "तपासलेले\\nकंटेनरची\\nसंख्या", 
                "डास/अळ्या\\nआढळून आलेले \\nकंटेनरची संख्या", "रिकामे केलेले\\nकंटेनरची\\nसंख्या"
            ];

            let tableBody = [];
            tableBody.push(headers.map(h => ({{ text: h, bold: true, fontSize: 8, alignment: 'center', fillColor: '#f2f2f2' }})));

            // Minimized row padding to 3.5 for better fit
            for (let i = 1; i <= 10; i++) {{
                tableBody.push([
                    {{ text: "", alignment: 'center', margin: [0, 10, 0, 10 ] }},
                    "", "", "", "", "", ""
                ]);
            }}

            return [
                {{ 
                    text: "दैनिक कीटकशास्त्रीय सर्वेक्षण", 
                    alignment: "center", fontSize: 16, bold: true, 
                    margin: [0, isFirstInPage ? 0 : 10, 0, 5] 
                }},
                {{
                    columns: [
                        {{ text: "गावाचे नांव: _______________", fontSize: 10 }},
                        {{ text: "लोकसंख्या: _________", fontSize: 10 }},
                        {{ text: "दिनांक: _________", fontSize: 10 }}
                    ],
                    margin: [0, 2, 0, 4]
                }},
                {{
                    table: {{
                        headerRows: 1,
                        widths: [25, '*', 35, 35, 35, 65, 65],
                        body: tableBody
                    }}
                }},
                {{
                    margin: [0, 6, 0, 0],
                    columns: [
                        getFormula("हाऊस इंडेक्स"),
                        getFormula("कंटेनर इंडेक्स"),
                        getFormula("ब्रेट्यू इंडेक्स")
                    ]
                }}
            ];
        }}

        function generatePDF(action) {{
            let content = [];
            const totalPages = {num_pages};

            for (let p = 0; p < totalPages; p++) {{
                content.push(...getSurveySection(true));
                content.push(...getSurveySection(false));
                if (p < totalPages - 1) content.push({{ text: "", pageBreak: "after" }});
            }}

            const docDefinition = {{
                pageSize: "A4",
                pageMargins: [50, 20, 20, 15], 
                defaultStyle: {{ font: "MarathiFont", bold: true }},
                content: content
            }};

            if (action === 'download') {{
                pdfMake.createPdf(docDefinition).download("Survey_Form.pdf");
            }} else {{
                pdfMake.createPdf(docDefinition).open();
            }}
        }}
        </script>
    </body>
    </html>
    """

    components.html(html_template, height=130)

if __name__ == "__main__":
    entomological_survey_pdf()