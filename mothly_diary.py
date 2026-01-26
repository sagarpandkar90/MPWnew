def monthly_diary():
    import streamlit as st
    import pandas as pd
    import calendar
    import datetime
    from pathlib import Path
    import base64
    import json
    import streamlit.components.v1 as components

    st.title("मासिक डायरी – Arogya Sevak")

    # ---------------------------
    # Inputs
    # ---------------------------
    cols = st.columns([1,1,2])
    month_name = cols[0].selectbox(
        "महिना",
        list(calendar.month_name)[1:],
        index=datetime.date.today().month-1
    )
    year = cols[1].number_input("वर्ष", min_value=2000, max_value=2100, value=datetime.date.today().year)
    sevak_name = cols[2].text_input("आरोग्य सेवक नाव")

    upkendra = st.text_input("उपकेंद्राचे नाव")

    # ---------------------------
    # Create date list
    # ---------------------------
    month_num = list(calendar.month_name).index(month_name)
    total_days = calendar.monthrange(year, month_num)[1]

    dates = []
    for d in range(1, total_days + 1):
        dt = datetime.date(year, month_num, d)
        dates.append(dt)

    # Marathi Sunday
    def get_tapshil(dt):
        if dt.weekday() == 6:   # 6 = Sunday
            return "रविवार"
        return ""

    # ---------------------------
    # Prepare DataFrame
    # ---------------------------
    df = pd.DataFrame({
        "भेटीचा दिनांक": [d.strftime("%d-%m-%Y") for d in dates],
        "भेटीचे गाव": ["" for _ in dates],
        "कामाचा तपशील": [get_tapshil(d) for d in dates],
        "शेरा": ["" for _ in dates]
    })

    st.write("### मासिक डायरी (Editable)")
    edited_df = st.data_editor(df, num_rows="dynamic")

    # ---------------------------
    # JSON for pdfMake
    # ---------------------------
    data_json = edited_df.to_dict(orient="records")
    json_js = json.dumps(data_json, ensure_ascii=False)

    # ---------------------------
    # Font load
    # ---------------------------
    font_path = Path("../MPWNew/fonts/NotoSerifDevanagari-VariableFont_wdth,wght.ttf")
    if not font_path.exists():
        st.error("font 'NotoSerifDevanagari-...' missing!")
        return

    font_b64 = base64.b64encode(font_path.read_bytes()).decode()
    month_year_str = f"{month_name} {year}"

    # ---------------------------
    # PDF Component
    # ---------------------------
    components.html(
        f"""
        <html>
        <head>
          <meta charset="utf-8" />
          <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
        </head>

        <body>
          <button onclick="previewPDF()" style="padding:8px 12px; background:#2196F3; color:white; border:none; border-radius:6px;">Preview</button>
          <button onclick="downloadPDF()" style="padding:8px 12px; background:#4CAF50; color:white; border:none; border-radius:6px;">Download</button>

          <script>
            const data = {json_js};

            pdfMake.vfs["Marathi.ttf"] = "{font_b64}";
            pdfMake.fonts = {{
              MarathiFont: {{
                normal: "Marathi.ttf",
                bold: "Marathi.ttf",
                italics: "Marathi.ttf",
                bolditalics: "Marathi.ttf"
              }}
            }};

            // Convert English month to Marathi
            const marathiMonths = {{
              "January":"जानेवारी",
              "February":"फेब्रुवारी",
              "March":"मार्च",
              "April":"एप्रिल",
              "May":"मे",
              "June":"जून",
              "July":"जुलै",
              "August":"ऑगस्ट",
              "September":"सप्टेंबर",
              "October":"ऑक्टोबर",
              "November":"नोव्हेंबर",
              "December":"डिसेंबर"
            }};

            const marathiMonthName = marathiMonths["{month_name}"] + " {year}";

            // Table
            const body = [];
            body.push([
              {{ text: 'भेटीचा दिनांक', bold:true, alignment:'center' }},
              {{ text: 'भेटीचे गाव', bold:true, alignment:'center' }},
              {{ text: 'कामाचा तपशील', bold:true, alignment:'center' }},
              {{ text: 'शेरा', bold:true, alignment:'center' }}
            ]);

            data.forEach(r => {{
              body.push([
                {{ text: r["भेटीचा दिनांक"], alignment:"center" }},
                {{ text: r["भेटीचे गाव"], alignment:"center" }},
                {{ text: r["कामाचा तपशील"], alignment:"center"  }},
                {{ text: r["शेरा"], alignment:"center"  }}
              ]);
            }});

            const docDefinition = {{
              pageSize: "A4",

              // Smaller top margin to reduce header height
              pageMargins: [35, 15, 35, 60],

              // FULL edge border
              background: {{
                canvas: [
                  {{ type: 'rect', x: 8, y: 8, w: 580, h: 826, lineWidth: 1 }}
                ]
              }},

              defaultStyle: {{ font: "MarathiFont", fontSize: 12 }},

              content: [

                // Compact Title
                {{
                  text: "मासिक डायरी",
                  style: "title",
                  alignment: "center",
                  margin:[0,5,0,2]
                }},
                {{
                  text: marathiMonthName,
                  absolutePosition: {{ x: 435, y: 40 }},   // top-right corner
                  fontSize: 14,
                  bold: true
                }},

                {{
                  text: "आरोग्य सेवक नाव: {sevak_name}",
                  margin:[0,0,0,2],
                  fontSize:12
                }},
                {{
                  text: "उपकेंद्र: {upkendra}",
                  margin:[0,0,0,2],
                  fontSize:12
                }},

                {{
                  table: {{
                    widths: ["18%","25%","37%","20%"],
                    body: body
                  }},
                  layout: {{
                    hLineWidth: () => 0.7,
                    vLineWidth: () => 0.7,
                    paddingTop: () => 0.5,
                    paddingBottom: () => 0.5
                  }}
                }}
              ],

              styles: {{
                title: {{ fontSize: 16, bold: true }}
              }}
            }};

            function previewPDF() {{ pdfMake.createPdf(docDefinition).open(); }}
            function downloadPDF() {{ pdfMake.createPdf(docDefinition).download("Masik_Diary.pdf"); }}
          </script>
        </body>
        </html>
        """,
        height=790,
        scrolling=True
    )
