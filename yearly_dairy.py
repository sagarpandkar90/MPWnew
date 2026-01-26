
def dairy():
    import streamlit as st
    import calendar
    import datetime
    from pathlib import Path
    import base64
    import json
    import streamlit.components.v1 as components

    # --- Constants and Helpers ---

    # Marathi translations for months and days
    MARATHI_MONTHS = {
        "January": "जानेवारी", "February": "फेब्रुवारी", "March": "मार्च",
        "April": "एप्रिल", "May": "मे", "June": "जून", "July": "जुलै",
        "August": "ऑगस्ट", "September": "सप्टेंबर", "October": "ऑक्टोबर",
        "November": "नोव्हेंबर", "December": "डिसेंबर"
    }

    MARATHI_DAYS = {
        0: "सोमवार", 1: "मंगळवार", 2: "बुधवार", 3: "गुरुवार",
        4: "शुक्रवार", 5: "शुक्रवार", 6: "रविवार"
    }


    def get_all_dates_for_year(year):
        """Generates a list of all dates for the given year."""
        dates = []
        try:
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 12, 31)
        except ValueError:
            return []

        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += datetime.timedelta(days=1)
        return dates


    def yearly_diary():
        st.set_page_config(layout="wide")
        st.title("📚 वार्षिक डायरी (Yearly Diary) – PDF Creator")

        # ---------------------------
        # Inputs
        # ---------------------------
        cols = st.columns([1, 2])
        year = cols[0].number_input("वर्ष निवडा (Select Year)", min_value=2024, max_value=2100,
                                    value=datetime.date.today().year)


        # ---------------------------
        # Prepare Data
        # ---------------------------
        all_dates = get_all_dates_for_year(year)
        date_data = [
            {
                "date": dt.strftime("%d"),
                "month": MARATHI_MONTHS[calendar.month_name[dt.month]],
                "day": MARATHI_DAYS[dt.weekday()],
                "month_num": dt.month,
                "is_month_start": dt.day == 1
            }
            for dt in all_dates
        ]

        # --- Page Chunking Logic (Kept as before) ---
        pages = []
        current_page_dates = []

        for i, dayData in enumerate(date_data):

            if dayData['is_month_start'] and i != 0:
                if current_page_dates:
                    while len(current_page_dates) % 3 != 0:
                        current_page_dates.append(None)

                    def chunk_temp_dates(data, size):
                        for j in range(0, len(data), size):
                            yield data[j:j + size]

                    pages.extend(list(chunk_temp_dates(current_page_dates, 3)))
                    current_page_dates = []

                current_page_dates.append(dayData)
            else:
                current_page_dates.append(dayData)

        if current_page_dates:
            while len(current_page_dates) % 3 != 0:
                current_page_dates.append(None)

            def chunk_temp_dates(data, size):
                for j in range(0, len(data), size):
                    yield data[j:j + size]

            pages.extend(list(chunk_temp_dates(current_page_dates, 3)))

        chunked_data = pages
        # -------------------------------------------

        # Send the processed data as JSON to the HTML component
        json_js = json.dumps(chunked_data, ensure_ascii=False)

        # ---------------------------
        # Font load (Crucial for Devanagari rendering)
        # ---------------------------
        BASE_DIR = Path(__file__).resolve().parent
        font_path = BASE_DIR / "fonts" / "NotoSerifDevanagari-VariableFont_wdth,wght.ttf"
        if not font_path.exists():
            st.error(
                f"🚨 Font file not found! Please create a 'fonts' folder and place a Devanagari font file (e.g., {font_path.name}) inside it.")
            return

        # Encode font file to base64 for embedding in the PDF
        font_b64 = base64.b64encode(font_path.read_bytes()).decode()

        # ---------------------------
        # PDF Component (HTML, JS, and CSS)
        # ---------------------------

        js_code = f"""
            <html>
            <head>
              <meta charset="utf-8" />
              <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
              <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
            </head>
    
            <body>
              <h4 style="margin-top:0;">PDF Controls</h4>
              <button onclick="previewPDF()" style="padding:10px 15px; background:#2196F3; color:white; border:none; border-radius:6px; margin-right: 10px; cursor: pointer;">👀 Preview PDF</button>
              <button onclick="downloadPDF()" style="padding:10px 15px; background:#4CAF50; color:white; border:none; border-radius:6px; cursor: pointer;">⬇️ Download PDF</button>
    
              <script>
                // --- INJECTING PYTHON VARIABLES ---
                const all_pages_data = {json_js}; 
                const current_year = {year};
                const REGISTER_LINE_COLOR = '#CCCCCC';
                const LINE_SPACING = 18;
                const PADDING_TOP = 20;
                const MAX_WIDTH = 555; 
                const A4_HEIGHT = 780; 
                const DATE_HEADER_HEIGHT = 50; 
                const CONTENT_LEFT_MARGIN = 20; 
                const CONTENT_WIDTH = MAX_WIDTH; 
                const DATE_TEXT_COLOR = '#004d40'; // Dark Teal
                const DIVIDER_LINE_COLOR = '#004d40'; // Dark Teal
                // ----------------------------------
    
                // Set up font for pdfMake
                pdfMake.vfs["Marathi.ttf"] = "{font_b64}";
                pdfMake.fonts = {{
                  MarathiFont: {{
                    normal: "Marathi.ttf",
                    bold: "Marathi.ttf",
                    italics: "Marathi.ttf",
                    bolditalics: "Marathi.ttf"
                  }}
                }};
    
                // --- Full Page Line Generator (Kept as before) ---
                function createFullPageLines() {{
                    const canvases = [];
    
                    const num_lines = Math.floor(A4_HEIGHT / LINE_SPACING);
                    for (let i = 0; i < num_lines; i++) {{
                        canvases.push({{ 
                            type: 'line', 
                            x1: CONTENT_LEFT_MARGIN, 
                            y1: PADDING_TOP + (i * LINE_SPACING), 
                            x2: MAX_WIDTH + CONTENT_LEFT_MARGIN, 
                            y2: PADDING_TOP + (i * LINE_SPACING), 
                            lineWidth: 0.5, 
                            lineColor: REGISTER_LINE_COLOR 
                        }});
                    }}
    
                    return {{ canvas: canvases, absolutePosition: {{ x: 0, y: 0 }} }};
                }}
    
                // --- Daily Section Content Generator (MODIFIED FOR ARTISTIC LINE) ---
                function createDailySection(dayData, is_first_section) {{ 
                    const SECTION_HEIGHT = A4_HEIGHT / 3; 
    
                    if (dayData === null) {{
                        return {{
                            text: '', 
                            border: [false, true, false, true],
                            borderColor: ['#000000', '#003366', '#000000', '#003366'],
                            margin: [0, 0, 0, SECTION_HEIGHT - 1] 
                        }};
                    }}
    
                    const contentStack = [
                        // 1. White background to cover lines *only* under the date/line area
                        {{
                            canvas: [
                                {{
                                    type: 'rect',
                                    x: 0, 
                                    y: 0,
                                    w: CONTENT_WIDTH, 
                                    h: DATE_HEADER_HEIGHT + 1, 
                                    color: 'white',
                                    lineColor: 'white',
                                    lineWidth: 0,
                                }}
                            ],
                            absolutePosition: {{ x: 0, y: -5 }} 
                        }},
                    ];
    
                    // 2. Conditional ARTISTIC Horizontal Divider Lines (Double Line)
                    if (!is_first_section) {{
                        // Thin Top Line (Lighter color/thickness)
                        contentStack.push({{
                            canvas: [
                                {{
                                    type: 'line',
                                    x1: 0,
                                    y1: 0,
                                    x2: CONTENT_WIDTH, 
                                    y2: 0,
                                    lineWidth: 0.75, 
                                    lineColor: '#A9A9A9', // Dark Gray/Lighter Accent
                                }}
                            ],
                            margin: [0, 3, 0, 0] // Pushes the top line down a bit
                        }});
    
                        // Thick Bottom Line (Primary color/thickness)
                        contentStack.push({{
                            canvas: [
                                {{
                                    type: 'line',
                                    x1: 0,
                                    y1: 0,
                                    x2: CONTENT_WIDTH, 
                                    y2: 0,
                                    lineWidth: 1.5, 
                                    lineColor: DIVIDER_LINE_COLOR, // Dark Teal
                                }}
                            ],
                            margin: [0, 0, 0, 0] // Keep this tight
                        }});
                    }}
    
                    // 3. Date/Day Header Text 
                    contentStack.push({{
                        text: `${{dayData.date}} | ${{dayData.month}} ${{current_year}} | ${{dayData.day}}`,
                        fontSize: 18, 
                        bold: true,
                        alignment: 'right', 
                        margin: [0, 5, 0, 5], // Top/Bottom margin for spacing
                        color: DATE_TEXT_COLOR,
                    }});
    
                    // 4. Empty space to control the total section height
                    contentStack.push({{ text: '', margin: [0, 0, 0, SECTION_HEIGHT - DATE_HEADER_HEIGHT - 15] }});
    
                    return {{
                        stack: contentStack,
                        // Section separators (optional, can be removed if artistic lines suffice)
                        border: [false, true, false, true], 
                        borderColor: ['#000000', '#D3D3D3', '#000000', '#D3D3D3'],
                    }};
                }}
    
                // --- PDF Content Builder ---
                const docContent = [];
    
                // 1. Cover Page (REDESIGNED)
    
                // A. Outer Border 
                docContent.push({{
                    canvas: [
                        {{
                            type: 'rect',
                            x: 20, y: 20, 
                            w: 555, h: 742, // A4 dimensions minus margins (595x842 - 20)
                            lineWidth: 5,
                            lineColor: '#004d40', // Dark Teal
                        }},
                         {{
                            type: 'rect',
                            x: 25, y: 25, 
                            w: 545, h: 732, 
                            lineWidth: 1,
                            lineColor: '#ffc107', // Gold Accent
                        }}
                    ],
                    absolutePosition: {{ x: 0, y: 0 }}
                }});
    
                // B. Main Content
                docContent.push({{
                    stack: [
                        
                        {{
                            text: '|| वार्षिक डायरी ||',
                            fontSize: 45, bold: true, alignment: 'center', margin: [0, 280, 0, 50], color: '#004d40' // Dark Teal
                        }},
                        {{
                            text: 'वर्ष : ' + current_year,
                            fontSize: 38, alignment: 'center', margin: [0, 0, 0, 10], color: '#004d40'
                        }}
                    ]
                }});
    
                docContent.push({{ text: '', pageBreak: 'after' }}); 
    
                // 2. Daily Pages & Blank Pages (Kept logic as before, using new design function)
                all_pages_data.forEach((page_days, index) => {{
    
                    // --- MONTH BREAK LOGIC ---
                    if (index > 0 && all_pages_data[index+1] && all_pages_data[index+1][0] && parseInt(all_pages_data[index+1][0].date) === 1) {{
                        const page_content_before = [ createFullPageLines() ];
                        const daily_sections_before = page_days.map((dayData, i) => createDailySection(dayData, i === 0));
                        page_content_before.push({{ stack: daily_sections_before, margin: [0, PADDING_TOP, 0, 0] }});
                        docContent.push({{ stack: page_content_before, margin: [0, 0, 0, 0] }});
    
                        docContent.push({{ text: '', pageBreak: 'after' }});
    
                        // Add 4 Empty Pages (Month Separator)
                        for (let i = 0; i < 2; i++) {{
                            docContent.push({{ 
                                stack: [
                                    createFullPageLines(), 
                                    {{ text: '' }}
                                ],
                                margin: [0, 0, 0, 0],
                                pageBreak: 'after' 
                            }});
                        }}
                        return; 
                    }}
    
                    // --- Daily Page Content (3 sections) ---
                    const page_content = [
                        createFullPageLines() 
                    ];
    
                    const daily_sections = page_days.map((dayData, i) => createDailySection(dayData, i === 0));
    
                    page_content.push({{ 
                        stack: daily_sections,
                        margin: [CONTENT_LEFT_MARGIN, PADDING_TOP, CONTENT_LEFT_MARGIN, 0] 
                    }});
    
                    docContent.push({{ 
                        stack: page_content,
                        margin: [0, 0, 0, 0] 
                    }});
    
                    if (index < all_pages_data.length - 1) {{
                        docContent.push({{ text: '', pageBreak: 'after' }});
                    }}
                }});
    
    
                // --- Final Doc Definition ---
                const docDefinition = {{
                  pageSize: "A4",
                  pageMargins: [20, 20, 20, 20], 
                  defaultStyle: {{ font: "MarathiFont", fontSize: 12 }},
                  content: docContent,
                }};
    
                function previewPDF() {{ pdfMake.createPdf(docDefinition).open(); }}
                function downloadPDF() {{ pdfMake.createPdf(docDefinition).download(`Yearly_Diary_${{current_year}}.pdf`); }}
              </script>
            </body>
            </html>
        """

        components.html(js_code, height=300, scrolling=False)

    yearly_diary()