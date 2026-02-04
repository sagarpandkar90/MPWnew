import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path


def rakt_namne_pdf():
    st.title("Blood Smear Report - MPW Format")

    # 1. Page Count Input
    num_pages = st.number_input("Number of Pages:", min_value=1, max_value=100, value=1)

    # 2. Font Loading (Required for Marathi/English rendering)
    BASE_DIR = Path(__file__).resolve().parent
    font_path = BASE_DIR / "fonts" / "NotoSerifDevanagari-VariableFont_wdth,wght.ttf"

    if not font_path.exists():
        st.warning("⚠️ Font file missing. Using default font.")
        font_b64 = ""
        use_custom_font = False
    else:
        font_b64 = base64.b64encode(font_path.read_bytes()).decode()
        use_custom_font = True

    # 3. HTML/JS with PDF logic
    font_config = ""
    if use_custom_font:
        font_config = f"""
        pdfMake.vfs["Marathi.ttf"] = "{font_b64}";
        pdfMake.fonts = {{
            MarathiFont: {{
                normal: "Marathi.ttf",
                bold: "Marathi.ttf"
            }}
        }};
        """
        default_font = "MarathiFont"
    else:
        default_font = "Roboto"

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
        {font_config}

        function getReportSection() {{
            return [
                // Page Border - Wrapping all content
                {{
                    table: {{
                        widths: ['*'],
                        body: [
                            [
                                {{
                                    stack: [
                                        // Main Heading
                                        {{ 
                                            text: "For Reporting of Blood Smears by MPW / HA / Passive Agency", 
                                            style: 'mainHeading',
                                            margin: [5, 5, 5, 5]
                                        }},

                                        // Second Line - Name of Section, Population, and Name of PHC
                                        {{
                                            columns: [
                                                {{ text: "Name of Section: ____________________________________________________", fontSize: 11, width: 400 }},
                                                {{ text: "Population: ___________________", fontSize: 11, width: 200 }},
                                                {{ text: "Name of P.H.C.: ____________________", fontSize: 11, width: 200}}
                                            ],
                                            margin: [5, 0, 5, 3]
                                        }},

                                        // Third Line - Headquarter and Code No
                                        {{
                                            columns: [
                                                {{ text: "Headquarter: _____________________________", fontSize: 11, width: '*' }},
                                                {{ text: "Code No.: ___________________________", fontSize: 11, width: '*' }}
                                            ],
                                            margin: [5, 0, 5, 5]
                                        }},

                                        // Main Table
                                        {{
                                            table: {{
                                                headerRows: 3,
                                                widths: [50, 30, 130, 130, 20, 20, 35, 55, 50, 15, 15, 18, 15, 15, 30, 35],
                                                body: [
                                                    // First Header Row - Main Columns with Result(9) spanning
                                                    [
                                                        {{ text: "Village", rowSpan: 3, style: 'tableHeader', margin: [0, 45, 0, 0] }},
                                                        {{ text: "House\\nNo.", rowSpan: 3, style: 'tableHeader', margin: [0, 35, 0, 0]  }},
                                                        {{ text: "Name of the Head\\n of Family", rowSpan: 3, style: 'tableHeader', margin: [0, 35, 0, 0] }},
                                                        {{ text: "Name of the\\nPatient", rowSpan: 3, style: 'tableHeader', margin: [0, 35, 0, 0] }},
                                                        {{ text: "Age", rowSpan: 3, style: 'tableHeader', margin: [0, 45, 0, 0]  }},
                                                        {{ text: "Sex", rowSpan: 3, style: 'tableHeader', margin: [0, 45, 0, 0]  }},
                                                        {{ text: "Sr.No.\\n of\\nBlood Smear", rowSpan: 3, style: 'tableHeader', margin: [0, 15, 0, 0]   }},
                                                        {{ text: "Treatment\\nNo. of Tablets\\nGiven\\n(4-Amino\\nQuinoline)", rowSpan: 3, style: 'tableHeader' }},
                                                        {{ text: "Date of\\nCollection", rowSpan: 3, style: 'tableHeader', margin: [0, 35, 0, 0] }},
                                                        {{ text: "Result (9)", colSpan: 5, style: 'tableHeader' }},
                                                        {{}}, {{}}, {{}}, {{}},
                                                        {{ text: "Mixed\\nIndicate\\nStage", rowSpan: 3, style: 'tableHeader', margin: [0, 15, 0, 0]  }},
                                                        {{ text: "If +\\nProgressive\\n+ve\\nCase No.", rowSpan: 3, style: 'tableHeader' }}
                                                    ],
                                                    // Second Header Row - F, V, M under Result(9)
                                                    [
                                                        {{text: "Village"}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}}, {{}},
                                                        {{ text: "F", colSpan: 3, style: 'subHeader' }},
                                                        {{}}, {{}},
                                                        {{ text: "V", rowSpan: 2, style: 'subHeader' }},
                                                        {{ text: "M", rowSpan: 2, style: 'subHeader' }},
                                                        {{}},
                                                        {{}}
                                                    ],
                                                    // Third Header Row - R, G, RG under F and Column Numbers
                                                    [
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{ text: "R", style: 'subColumnHeader' }},
                                                        {{ text: "G", style: 'subColumnHeader' }},
                                                        {{ text: "RG", style: 'subColumnHeader' }},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}}
                                                    ],
[
                                                        {{ text: "1", style: 'columnNumber' }},
                                                        {{ text: "2", style: 'columnNumber' }},
                                                        {{ text: "3", style: 'columnNumber' }},
                                                        {{ text: "4", style: 'columnNumber' }},
                                                        {{ text: "(5a)", style: 'columnNumber' }},
                                                        {{ text: "(5b)", style: 'columnNumber' }},
                                                        {{ text: "6", style: 'columnNumber' }},
                                                        {{ text: "7", style: 'columnNumber' }},
                                                        {{ text: "8", style: 'columnNumber' }},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{}},
                                                        {{ text: "10", style: 'columnNumber' }},
                                                        {{ text: "11", style: 'columnNumber' }}
                                                    ],                                                    
                                                    // Data Rows (14 empty rows for data entry)
                                                    ...Array(14).fill([
                                                        {{ text: "", margin: [0, 8, 0, 8] }},
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        "",
                                                        ""
                                                    ])
                                                ]
                                            }},
                                            layout: {{
                                                hLineWidth: function(i, node) {{ return 0.5; }},
                                                vLineWidth: function(i, node) {{ return 0.5; }},
                                                hLineColor: function(i, node) {{ return '#000000'; }},
                                                vLineColor: function(i, node) {{ return '#000000'; }}
                                            }},
                                            margin: [5, 0, 5, 8]
                                        }},

                                        // Footer Section with three columns
                                        {{
                                            columns: [
                                                {{
                                                    width: '*',
                                                    stack: [
                                                        {{ text: "____________________", fontSize: 11, alignment: 'left', margin: [0, 15, 0, 0] }},
                                                        {{ text: "Signature Microscopist", fontSize: 11, alignment: 'left' }}

                                                    ]
                                                }},
                                                {{
                                                    width: '*',
                                                    stack: [
                                                        {{ text: "____________________", fontSize: 11, alignment: 'center', margin: [0, 15, 0, 0] }},
                                                        {{ text: "Date of Examination", fontSize: 11, alignment: 'center' }}

                                                    ]
                                                }},
                                                {{
                                                    width: '*',
                                                    stack: [
                                                        {{ text: "______________________________", fontSize: 11, alignment: 'right', margin: [0, 15, 0, 0] }},
                                                        {{ text: "Signature of MPW / HA / HS / Others", fontSize: 11, alignment: 'right' }}

                                                    ]
                                                }}
                                            ],
                                            margin: [5, 0, 5, 5]
                                        }}
                                    ],
                                    border: [true, true, true, true]
                                }}
                            ]
                        ]
                    }},
                    layout: {{
                        hLineWidth: function(i, node) {{ return 1; }},
                        vLineWidth: function(i, node) {{ return 1; }},
                        hLineColor: function(i, node) {{ return '#000000'; }},
                        vLineColor: function(i, node) {{ return '#000000'; }}
                    }}
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
                pageMargins: [10, 35, 10, 5], // Left, Top (binding margin), Right, Bottom
                defaultStyle: {{ 
                    font: "{default_font}", 
                    fontSize: 7 
                }},
                styles: {{
                    mainHeading: {{ 
                        fontSize: 18, 
                        bold: true, 
                        alignment: 'center' 
                    }},
                    tableHeader: {{ 
                        fontSize: 10, 
                        bold: true, 
                        alignment: 'center',
                        fillColor: '#E8E8E8'
                    }},
                    subHeader: {{ 
                        fontSize: 10, 
                        bold: true, 
                        alignment: 'center',
                        fillColor: '#F0F0F0'
                    }},
                    subColumnHeader: {{ 
                        fontSize: 10, 
                        bold: true, 
                        alignment: 'center',
                        fillColor: '#F5F5F5'
                    }},
                    columnNumber: {{ 
                        fontSize: 10, 
                        alignment: 'center',
                        fillColor: '#F8F8F8'
                    }}
                }},
                content: content
            }};

            if (action === 'download') {{
                pdfMake.createPdf(docDefinition).download("Blood_Smear_Report_MPW.pdf");
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