import streamlit as st
import pandas as pd
import json
import base64
import streamlit.components.v1 as components
from pathlib import Path


def mothly_final_report():
    """
    Manual data entry for 8 different health reports with landscape PDF generation
    """

    st.set_page_config(page_title="मासिक आहवाल Data Entry", page_icon="📊", layout="wide")

    st.title("📊 मासिक आहवाल - Manual Data Entry")

    # Common metadata
    st.sidebar.header("मुख्य माहिती")
    month_year = st.sidebar.text_input("महिना/वर्ष", value="मार्च २०२६")
    phc_name = st.sidebar.text_input("प्राथमिक आरोग्य केंद्र", value="शेळगाव")
    taluka = st.sidebar.text_input("तालुका", value="इंदापूर")
    district = st.sidebar.text_input("जिल्हा", value="पुणे")
    sub_center = st.sidebar.text_input("उपकेंद्र", value="")
    population = st.sidebar.text_input("लोकसंख्या", value="")

    # Tab selection for different sheets
    tabs = st.tabs([
        "1️⃣ रक्त नमुना",
        "2️⃣ थुंकी संकलन",
        "3️⃣ कुष्ठरुग्ण",
        "4️⃣ क्षय रुग्ण",
        "5️⃣ कंटेनर सर्वेक्षण",
        "6️⃣ डासउत्पत्ती स्थाने",
        "7️⃣ प्रयोगशाळा",
        "8️⃣ मोतीबिंदू",
        "9️⃣ PDF तयार करा"
    ])

    # Initialize session state for all sheets
    if 'sheet_data' not in st.session_state:
        st.session_state.sheet_data = {}

    # Sheet 1: रक्त नमुना मासिक अहवाल
    with tabs[0]:
        st.subheader("रक्त नमुना मासिक अहवाल")

        # Basic subcenter info - entered once
        st.markdown("### उपकेंद्र माहिती")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            subcenter_sr = st.text_input("अ. क्र.", value="1", key="s1_basic_sr")
        with col2:
            subcenter_name = st.text_input("उपकेंद्राचे नाव", value="", key="s1_basic_name")
        with col3:
            subcenter_pop = st.text_input("लोकसंख्या", value="", key="s1_basic_pop")
        with col4:
            annual_target = st.text_input("रक्त नमुना वार्षिक उद्दिष्ट", value="", key="s1_annual_target")

        st.markdown("---")
        st.markdown("### कर्मचारी माहिती (आरोग्य सेविका व सेवक)")

        num_staff = st.number_input("कर्मचारी संख्या", min_value=1, max_value=20, value=5, key="rows1")

        staff_data = []
        for i in range(num_staff):
            st.markdown(f"**कर्मचारी {i + 1}**")
            cols = st.columns([2, 1, 1, 1, 1])
            row_data = {
                'पदनाम': cols[0].text_input(f"पदनाम (आरोग्य सेविका/सेवक)", value="", key=f"s1_post_{i}"),
                'पहिला_पंधरावडा': cols[1].text_input(f"मासिक पहिला", value="0", key=f"s1_f1_{i}"),
                'दुसरा_पंधरावडा': cols[2].text_input(f"मासिक दुसरा", value="0", key=f"s1_f2_{i}"),
                'प्रगती_पहिला': cols[3].text_input(f"प्रगती पहिला", value="0", key=f"s1_p1_{i}"),
                'प्रगती_दुसरा': cols[4].text_input(f"प्रगती दुसरा", value="0", key=f"s1_p2_{i}"),
            }
            staff_data.append(row_data)

        st.markdown("---")
        st.markdown("### एकूण आशा कार्यकर्ती")
        total_asha_count = st.text_input("एकूण आशा कार्यकर्ती संख्या", value="0", key="s1_total_asha")

        # Get monthly and progress values for ASHA row
        cols_asha = st.columns([2, 1, 1, 1, 1])
        with cols_asha[0]:
            st.text("(मासिक व प्रगती)")
        asha_f1 = cols_asha[1].text_input("मासिक पहिला", value="0", key="s1_asha_f1")
        asha_f2 = cols_asha[2].text_input("मासिक दुसरा", value="0", key="s1_asha_f2")
        asha_p1 = cols_asha[3].text_input("प्रगती पहिला", value="0", key="s1_asha_p1")
        asha_p2 = cols_asha[4].text_input("प्रगती दुसरा", value="0", key="s1_asha_p2")

        # Calculate totals automatically
        total_f1 = sum(int(s['पहिला_पंधरावडा'] or 0) for s in staff_data) + int(asha_f1 or 0)
        total_f2 = sum(int(s['दुसरा_पंधरावडा'] or 0) for s in staff_data) + int(asha_f2 or 0)
        total_monthly = total_f1 + total_f2
        total_p1 = sum(int(s['प्रगती_पहिला'] or 0) for s in staff_data) + int(asha_p1 or 0)
        total_p2 = sum(int(s['प्रगती_दुसरा'] or 0) for s in staff_data) + int(asha_p2 or 0)
        total_progress = total_p1 + total_p2

        st.info(
            f"📊 एकूण रक्तनमुने - मासिक: पहिला={total_f1}, दुसरा={total_f2}, एकूण={total_monthly} | प्रगती: पहिला={total_p1}, दुसरा={total_p2}, एकूण={total_progress}")

        st.session_state.sheet_data['sheet1'] = {
            'title': 'राष्ट्रीय कीटकजन्य रोग नियंत्रण कार्यक्रम, जिल्हा पुणे',
            'subtitle': 'रक्त नमुना मासिक अहवाल',
            'subcenter_sr': subcenter_sr,
            'subcenter_name': subcenter_name,
            'subcenter_pop': subcenter_pop,
            'annual_target': annual_target,
            'staff_data': staff_data,
            'total_asha_count': total_asha_count,
            'asha_data': {
                'f1': asha_f1,
                'f2': asha_f2,
                'p1': asha_p1,
                'p2': asha_p2
            },
            'totals': {
                'f1': str(total_f1),
                'f2': str(total_f2),
                'monthly': str(total_monthly),
                'p1': str(total_p1),
                'p2': str(total_p2),
                'progress': str(total_progress)
            }
        }

    # Sheet 2: थुंकी संकलन अहवाल
    with tabs[1]:
        st.subheader("थुंकी संकलन अहवाल")

        num_rows_2 = st.number_input("नोंदी संख्या", min_value=1, max_value=20, value=5, key="rows2")

        sheet2_data = []
        for i in range(num_rows_2):
            cols = st.columns([1, 2, 2, 2, 1, 1, 1, 1, 1, 1])
            row_data = {
                'अ. क्र.': cols[0].text_input(f"अ.क्र.", value=str(i + 1), key=f"s2_sr_{i}"),
                'गावाचे नाव': cols[1].text_input(f"गाव", value="", key=f"s2_village_{i}"),
                'लोकसंख्या': cols[2].text_input(f"लोकसंख्या", value="", key=f"s2_pop_{i}"),
                'कर्मचारी_मासिक': cols[3].text_input(f"कर्मचारी", value="", key=f"s2_staff_m_{i}"),
                'पुरुष_मासिक': cols[4].text_input(f"पुरुष", value="", key=f"s2_m_m_{i}"),
                'स्त्री_मासिक': cols[5].text_input(f"स्त्री", value="", key=f"s2_f_m_{i}"),
                'एकूण_मासिक': cols[6].text_input(f"एकूण", value="", key=f"s2_t_m_{i}"),
                'पुरुष_वार्षिक': cols[7].text_input(f"पुरुष", value="", key=f"s2_m_y_{i}"),
                'स्त्री_वार्षिक': cols[8].text_input(f"स्त्री", value="", key=f"s2_f_y_{i}"),
                'एकूण_वार्षिक': cols[9].text_input(f"एकूण", value="", key=f"s2_t_y_{i}"),
            }
            sheet2_data.append(row_data)

        st.session_state.sheet_data['sheet2'] = {
            'title': 'थुंकी संकलन अहवाल',
            'data': sheet2_data
        }

    # Sheet 3: कुष्ठरुग्ण मासिक अहवाल
    with tabs[2]:
        st.subheader("कुष्ठरुग्ण मासिक अहवाल")

        num_rows_3 = st.number_input("नोंदी संख्या", min_value=1, max_value=20, value=5, key="rows3")

        sheet3_data = []
        for i in range(num_rows_3):
            cols = st.columns([1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            row_data = {
                'अ. क्र.': cols[0].text_input(f"अ.क्र.", value=str(i + 1), key=f"s3_sr_{i}"),
                'गावाचे नाव': cols[1].text_input(f"गाव", value="", key=f"s3_village_{i}"),
                'लोकसंख्या': cols[2].text_input(f"लोकसंख्या", value="", key=f"s3_pop_{i}"),
                'संबंधित_मुले': cols[3].text_input(f"मुले", value="", key=f"s3_rel_c_{i}"),
                'संबंधित_प्रौढ': cols[4].text_input(f"प्रौढ", value="", key=f"s3_rel_a_{i}"),
                'संबंधित_एकूण': cols[5].text_input(f"एकूण", value="", key=f"s3_rel_t_{i}"),
                'MB_मुले': cols[6].text_input(f"मुले", value="", key=f"s3_mb_c_{i}"),
                'MB_प्रौढ': cols[7].text_input(f"प्रौढ", value="", key=f"s3_mb_a_{i}"),
                'MB_एकूण': cols[8].text_input(f"एकूण", value="", key=f"s3_mb_t_{i}"),
                'PB_मुले': cols[9].text_input(f"मुले", value="", key=f"s3_pb_c_{i}"),
                'PB_प्रौढ': cols[10].text_input(f"प्रौढ", value="", key=f"s3_pb_a_{i}"),
                'PB_एकूण': cols[11].text_input(f"एकूण", value="", key=f"s3_pb_t_{i}"),
                'औषधोपचार_मुले': cols[12].text_input(f"मुले", value="", key=f"s3_tr_c_{i}"),
                'औषधोपचार_प्रौढ': cols[13].text_input(f"प्रौढ", value="", key=f"s3_tr_a_{i}"),
                'औषधोपचार_एकूण': cols[14].text_input(f"एकूण", value="", key=f"s3_tr_t_{i}"),
            }
            sheet3_data.append(row_data)

        st.session_state.sheet_data['sheet3'] = {
            'title': 'कुष्ठरुग्ण मासिक अहवाल',
            'data': sheet3_data
        }

    # Sheet 4: उपचार घेणारी क्षय रुग्ण अहवाल
    with tabs[3]:
        st.subheader("उपचार घेणारी क्षय रुग्ण अहवाल")

        num_rows_4 = st.number_input("नोंदी संख्या", min_value=1, max_value=20, value=5, key="rows4")

        sheet4_data = []
        for i in range(num_rows_4):
            cols = st.columns([1, 2, 2, 2, 1, 1, 1, 1, 1])
            row_data = {
                'अ. क्र.': cols[0].text_input(f"अ.क्र.", value=str(i + 1), key=f"s4_sr_{i}"),
                'गावाचे नाव': cols[1].text_input(f"गाव", value="", key=f"s4_village_{i}"),
                'क्षयरुग्णाचे नाव': cols[2].text_input(f"रुग्ण नाव", value="", key=f"s4_name_{i}"),
                'वय': cols[3].text_input(f"वय", value="", key=f"s4_age_{i}"),
                'लिंग': cols[4].text_input(f"लिंग", value="", key=f"s4_gender_{i}"),
                'कॅटेगरी': cols[5].text_input(f"कॅटेगरी", value="", key=f"s4_cat_{i}"),
                'औषधोपचार_दिनांक': cols[6].text_input(f"दिनांक", value="", key=f"s4_date_{i}"),
                'TB_नंबर': cols[7].text_input(f"TB नं.", value="", key=f"s4_tb_{i}"),
                'कर्मचारी_नाव': cols[8].text_input(f"कर्मचारी", value="", key=f"s4_staff_{i}"),
            }
            sheet4_data.append(row_data)

        st.session_state.sheet_data['sheet4'] = {
            'title': 'उपचार घेणारी क्षय रुग्ण अहवाल',
            'data': sheet4_data
        }

    # Sheet 5: कंटेनर सर्वेक्षण
    with tabs[4]:
        st.subheader("कंटेनर सर्वेक्षण अहवाल")

        num_rows_5 = st.number_input("नोंदी संख्या", min_value=1, max_value=20, value=5, key="rows5")

        sheet5_data = []
        for i in range(num_rows_5):
            cols = st.columns([1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
            row_data = {
                'अ. क्र.': cols[0].text_input(f"अ.क्र.", value=str(i + 1), key=f"s5_sr_{i}"),
                'गावाचे नाव': cols[1].text_input(f"गाव", value="", key=f"s5_village_{i}"),
                'लोकसंख्या': cols[2].text_input(f"लोकसंख्या", value="", key=f"s5_pop_{i}"),
                'एकूण_घरे': cols[3].text_input(f"घरे", value="", key=f"s5_house_{i}"),
                'तपासलेले_घरे': cols[4].text_input(f"तपासले", value="", key=f"s5_check_{i}"),
                'दूषित_घरे': cols[5].text_input(f"दूषित", value="", key=f"s5_cont_{i}"),
                'तपासलेली_भांडी': cols[6].text_input(f"भांडी", value="", key=f"s5_cont_c_{i}"),
                'दूषित_भांडी': cols[7].text_input(f"दूषित भांडी", value="", key=f"s5_cont_cc_{i}"),
                'House_Index': cols[8].text_input(f"HI", value="", key=f"s5_hi_{i}"),
                'Container_Index': cols[9].text_input(f"CI", value="", key=f"s5_ci_{i}"),
                'Breteau_Index': cols[10].text_input(f"BI", value="", key=f"s5_bi_{i}"),
                'रिकामी_भांडी': cols[11].text_input(f"रिकामी", value="", key=f"s5_empty_{i}"),
                'अँबेट_भांडी': cols[12].text_input(f"अँबेट", value="", key=f"s5_abate_{i}"),
            }
            sheet5_data.append(row_data)

        st.session_state.sheet_data['sheet5'] = {
            'title': 'कंटेनर सर्वेक्षण',
            'data': sheet5_data
        }

    # Sheet 6: डासउत्पत्ती स्थाने
    with tabs[5]:
        st.subheader("डासउत्पत्ती स्थानांची गावनिहाय यादी")

        num_rows_6 = st.number_input("नोंदी संख्या", min_value=1, max_value=20, value=5, key="rows6")

        sheet6_data = []
        for i in range(num_rows_6):
            cols = st.columns([1, 2, 2, 1, 1, 3])
            row_data = {
                'अ. क्र.': cols[0].text_input(f"अ.क्र.", value=str(i + 1), key=f"s6_sr_{i}"),
                'उपकेंद्राचे नाव': cols[1].text_input(f"उपकेंद्र", value="", key=f"s6_sub_{i}"),
                'गावाचे नाव': cols[2].text_input(f"गाव", value="", key=f"s6_village_{i}"),
                'कायम': cols[3].text_input(f"कायम", value="", key=f"s6_perm_{i}"),
                'हंगामी': cols[4].text_input(f"हंगामी", value="", key=f"s6_seas_{i}"),
                'ठिकाण': cols[5].text_input(f"ठिकाण", value="", key=f"s6_loc_{i}"),
            }
            sheet6_data.append(row_data)

        st.session_state.sheet_data['sheet6'] = {
            'title': 'डासउत्पत्ती स्थानांची गावनिहाय यादी',
            'data': sheet6_data
        }

    # Sheet 7: प्रयोगशाळा विविध नमुने
    with tabs[6]:
        st.subheader("राज्य अयोग्य प्रयोगशाळा विविध नमुने तपासणी अहवाल")

        num_rows_7 = st.number_input("नोंदी संख्या", min_value=1, max_value=20, value=5, key="rows7")

        sheet7_data = []
        for i in range(num_rows_7):
            cols = st.columns([1, 2, 2, 1, 1, 1, 1, 1, 1])
            row_data = {
                'अ. क्र.': cols[0].text_input(f"अ.क्र.", value=str(i + 1), key=f"s7_sr_{i}"),
                'उपकेंद्राचे नाव': cols[1].text_input(f"उपकेंद्र", value="", key=f"s7_sub_{i}"),
                'जैविक_घेतलेले': cols[2].text_input(f"घेतलेले", value="", key=f"s7_bio_t_{i}"),
                'जैविक_दूषित': cols[3].text_input(f"दूषित", value="", key=f"s7_bio_c_{i}"),
                'रासायनिक_घेतलेले': cols[4].text_input(f"घेतलेले", value="", key=f"s7_chem_t_{i}"),
                'रासायनिक_दूषित': cols[5].text_input(f"दूषित", value="", key=f"s7_chem_c_{i}"),
                'TCL_प्रारंभ': cols[6].text_input(f"प्रारंभ", value="", key=f"s7_tcl_s_{i}"),
                'TCL_खरेदी': cols[7].text_input(f"खरेदी", value="", key=f"s7_tcl_p_{i}"),
                'TCL_खर्च': cols[8].text_input(f"खर्च", value="", key=f"s7_tcl_u_{i}"),
            }
            sheet7_data.append(row_data)

        st.session_state.sheet_data['sheet7'] = {
            'title': 'राज्य अयोग्य प्रयोगशाळा विविध नमुने तपासणी अहवाल',
            'data': sheet7_data
        }

    # Sheet 8: मोतीबिंदू अहवाल
    with tabs[7]:
        st.subheader("मोतीबिंदू मासिक अहवाल")

        num_rows_8 = st.number_input("नोंदी संख्या", min_value=1, max_value=20, value=5, key="rows8")

        sheet8_data = []
        for i in range(num_rows_8):
            cols = st.columns([1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            row_data = {
                'अ. क्र.': cols[0].text_input(f"अ.क्र.", value=str(i + 1), key=f"s8_sr_{i}"),
                'गावाचे नाव': cols[1].text_input(f"गाव", value="", key=f"s8_village_{i}"),
                'लोकसंख्या': cols[2].text_input(f"लोकसंख्या", value="", key=f"s8_pop_{i}"),
                'संबंधित_मुले': cols[3].text_input(f"मुले", value="", key=f"s8_rel_c_{i}"),
                'संबंधित_प्रौढ': cols[4].text_input(f"प्रौढ", value="", key=f"s8_rel_a_{i}"),
                'संबंधित_एकूण': cols[5].text_input(f"एकूण", value="", key=f"s8_rel_t_{i}"),
                'नवीन_मुले': cols[6].text_input(f"मुले", value="", key=f"s8_new_c_{i}"),
                'नवीन_प्रौढ': cols[7].text_input(f"प्रौढ", value="", key=f"s8_new_a_{i}"),
                'नवीन_एकूण': cols[8].text_input(f"एकूण", value="", key=f"s8_new_t_{i}"),
                'शस्त्रक्रिया_मुले': cols[9].text_input(f"मुले", value="", key=f"s8_sur_c_{i}"),
                'शस्त्रक्रिया_प्रौढ': cols[10].text_input(f"प्रौढ", value="", key=f"s8_sur_a_{i}"),
                'शस्त्रक्रिया_एकूण': cols[11].text_input(f"एकूण", value="", key=f"s8_sur_t_{i}"),
            }
            sheet8_data.append(row_data)

        st.session_state.sheet_data['sheet8'] = {
            'title': 'मोतीबिंदू मासिक अहवाल',
            'data': sheet8_data
        }

    # Tab 9: Generate PDF
    with tabs[8]:
        st.subheader("📄 PDF तयार करा")

        st.info("सर्व डेटा भरल्यानंतर येथे PDF तयार करा")

        # Check for font file
        BASE_DIR = Path(__file__).resolve().parent
        font_path = BASE_DIR / "fonts" / "NotoSerifDevanagari-VariableFont_wdth,wght.ttf"

        if not font_path.exists():
            st.error(f"❌ Font file missing at: {font_path}")
            st.info(
                "Please create a 'fonts' folder in the same directory as this script and add the Marathi font file.")
            st.markdown("""
            **Download font from:**
            - [Google Fonts - Noto Serif Devanagari](https://fonts.google.com/noto/specimen/Noto+Serif+Devanagari)
            - Or use any other Devanagari Unicode font (.ttf format)
            """)
            return

        # Read and encode font
        font_b64 = base64.b64encode(font_path.read_bytes()).decode()

        # Prepare all data for PDF
        all_sheets_json = json.dumps(st.session_state.sheet_data, ensure_ascii=False)

        # PDF generation component with local font
        components.html(
            f"""
            <html>
            <head>
              <meta charset="utf-8" />
              <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
              <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
              <style>
                body {{ padding: 20px; font-family: Arial, sans-serif; }}
                .button-container {{ margin: 20px 0; }}
                button {{
                  padding: 14px 28px;
                  margin-right: 10px;
                  border: none;
                  border-radius: 6px;
                  cursor: pointer;
                  font-size: 16px;
                  font-weight: bold;
                  box-shadow: 0 3px 6px rgba(0,0,0,0.3);
                }}
                .preview-btn {{ background: #2196F3; color: white; }}
                .download-btn {{ background: #4CAF50; color: white; }}
                #status {{
                  margin-top: 15px;
                  padding: 12px;
                  border-radius: 4px;
                  display: none;
                }}
              </style>
            </head>

            <body>
              <div class="button-container">
                <button class="preview-btn" onclick="previewPDF()">
                  👁️ Preview PDF
                </button>
                <button class="download-btn" onclick="downloadPDF()">
                  ⬇️ Download PDF
                </button>
              </div>

              <div id="status"></div>

              <script>
                console.log('Script loaded');

                const allData = {all_sheets_json};
                const metadata = {{
                  monthYear: "{month_year}",
                  phcName: "{phc_name}",
                  taluka: "{taluka}",
                  district: "{district}",
                  subCenter: "{sub_center}",
                  population: "{population}"
                }};

                // Register custom Marathi font
                pdfMake.vfs["MarathiFont.ttf"] = "{font_b64}";
                pdfMake.fonts = {{
                  MarathiFont: {{
                    normal: "MarathiFont.ttf",
                    bold: "MarathiFont.ttf",
                    italics: "MarathiFont.ttf",
                    bolditalics: "MarathiFont.ttf"
                  }}
                }};

                console.log('All Data:', allData);
                console.log('Metadata:', metadata);
                console.log('Font loaded successfully');

                function showStatus(msg, color) {{
                  const status = document.getElementById('status');
                  status.innerHTML = msg;
                  status.style.background = color;
                  status.style.display = 'block';
                  setTimeout(() => {{ status.style.display = 'none'; }}, 3000);
                }}

                function createPDFDefinition() {{
                  const content = [];

                  // Sheet 1
                  if (allData.sheet1) {{
                    const s1 = allData.sheet1;
                    const tableBody1 = [];

                    // Title row with top margin
                    content.push({{
                      text: s1.title || 'राष्ट्रीय कीटकजन्य रोग नियंत्रण कार्यक्रम, जिल्हा पुणे',
                      alignment: 'center',
                      bold: true,
                      fontSize: 13,
                      margin: [0, 30, 0, 5]
                    }});

                    // Subcenter and PHC info row
                    content.push({{
                      columns: [
                        {{ text: 'उपकेंद्र: ' + (s1.subcenter_name || ''), fontSize: 11, width: '*' , alignment: 'center'}},
                        {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName + ' तालुका ' + metadata.taluka + ' जिल्हा ' + metadata.district, fontSize: 11, width: '*', alignment: 'center' }}
                      ],
                      margin: [0, 0, 0, 5]
                    }});

                    // Subtitle
                    content.push({{
                      text: s1.subtitle || 'रक्त नमुना मासिक अहवाल',
                      alignment: 'center',
                      bold: true,
                      fontSize: 12,
                      margin: [0, 0, 0, 10]
                    }});

                    // Table headers
                    tableBody1.push([
                      {{ text: 'अ. क्र.', bold: true, fontSize: 9, rowSpan: 2, alignment: 'center' }},
                      {{ text: 'उपकेंद्राचे नाव', bold: true, fontSize: 9, rowSpan: 2, alignment: 'center' }},
                      {{ text: 'लोकसंख्या', bold: true, fontSize: 9, rowSpan: 2, alignment: 'center' }},
                      {{ text: 'कर्मचाऱ्यांचे पदनाम निहाय वर्गवारी', bold: true, fontSize: 9, rowSpan: 2, alignment: 'center' }},
                      {{ text: 'रक्त नमुना वार्षिक उद्दिष्ट', bold: true, fontSize: 9, rowSpan: 2, alignment: 'center' }},
                      {{ text: 'रक्त नमुना मासिक उद्दिष्ट', bold: true, fontSize: 9, colSpan: 3, alignment: 'center' }},
                      {{}},
                      {{}},
                      {{ text: 'प्रगतीपथावर घेतलेले रक्त नमुने जानेवारी २०२६ पासून', bold: true, fontSize: 9, colSpan: 3, alignment: 'center' }},
                      {{}},
                      {{}}
                    ]);

                    // Sub-headers
                    tableBody1.push([
                      {{}},
                      {{}},
                      {{}},
                      {{}},
                      {{}},
                      {{ text: 'पहिला पंधरावडा', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'दुसरा पंधरावडा', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'एकूण', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'पहिला पंधरावडा', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'दुसरा पंधरावडा', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'एकूण', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    // Calculate total rows for rowSpan (staff + ASHA + total samples)
                    const totalRowsForSubcenterInfo = (s1.staff_data ? s1.staff_data.length : 0) + 2;


                    // Data rows - staff members
                    if (s1.staff_data && s1.staff_data.length > 0) {{
                      s1.staff_data.forEach((staff, idx) => {{
                        // Calculate totals
                        const monthlyTotal = (parseInt(staff.पहिला_पंधरावडा || 0) + parseInt(staff.दुसरा_पंधरावडा || 0)).toString();
                        const progressTotal = (parseInt(staff.प्रगती_पहिला || 0) + parseInt(staff.प्रगती_दुसरा || 0)).toString();

                        tableBody1.push([
                          {{ text: idx === 0 ? (s1.subcenter_sr || '1') : '', fontSize: 9, alignment: 'center', rowSpan: idx === 0 ? totalRowsForSubcenterInfo : 1 }},
                          {{ text: idx === 0 ? (s1.subcenter_name || '') : '', fontSize: 9, alignment: 'center', rowSpan: idx === 0 ? totalRowsForSubcenterInfo : 1 }},
                          {{ text: idx === 0 ? (s1.subcenter_pop || '') : '', fontSize: 9, alignment: 'center', rowSpan: idx === 0 ? totalRowsForSubcenterInfo : 1 }},
                          {{ text: staff.पदनाम || '', fontSize: 9, alignment: 'center' }},
                          {{ text: idx === 0 ? (s1.annual_target || '') : '', fontSize: 9, alignment: 'center', rowSpan: idx === 0 ? totalRowsForSubcenterInfo : 1 }},
                          {{ text: staff.पहिला_पंधरावडा || '0', fontSize: 9, alignment: 'center' }},
                          {{ text: staff.दुसरा_पंधरावडा || '0', fontSize: 9, alignment: 'center' }},
                          {{ text: monthlyTotal !== '0' ? monthlyTotal : '0', fontSize: 9, alignment: 'center' }},
                          {{ text: staff.प्रगती_पहिला || '0', fontSize: 9, alignment: 'center' }},
                          {{ text: staff.प्रगती_दुसरा || '0', fontSize: 9, alignment: 'center' }},
                          {{ text: progressTotal !== '0' ? progressTotal : '0', fontSize: 9, alignment: 'center' }}
                        ]);
                      }});
                    }}

                    // Total ASHA workers row - with data in other columns
                    const ashaMonthlyTotal = (parseInt(s1.asha_data?.f1 || 0) + parseInt(s1.asha_data?.f2 || 0)).toString();
                    const ashaProgressTotal = (parseInt(s1.asha_data?.p1 || 0) + parseInt(s1.asha_data?.p2 || 0)).toString();

                    tableBody1.push([
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: 'एकूण आशा कार्यकर्ती\\nसंख्या ' + (s1.total_asha_count || ''), bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: s1.asha_data?.f1 || '0', fontSize: 9, alignment: 'center' }},
                      {{ text: s1.asha_data?.f2 || '0', fontSize: 9, alignment: 'center' }},
                      {{ text: ashaMonthlyTotal !== '0' ? ashaMonthlyTotal : '0', fontSize: 9, alignment: 'center' }},
                      {{ text: s1.asha_data?.p1 || '0', fontSize: 9, alignment: 'center' }},
                      {{ text: s1.asha_data?.p2 || '0', fontSize: 9, alignment: 'center' }},
                      {{ text: ashaProgressTotal !== '0' ? ashaProgressTotal : '0', fontSize: 9, alignment: 'center' }}
                    ]);

                    // Total samples row - with calculated sums
                    tableBody1.push([
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: 'एकूण रक्तनमुने', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: '', alignment: 'center' }}, // Empty cell for rowSpan
                      {{ text: s1.totals ? s1.totals.f1 : '0', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: s1.totals ? s1.totals.f2 : '0', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: s1.totals ? s1.totals.monthly : '0', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: s1.totals ? s1.totals.p1 : '0', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: s1.totals ? s1.totals.p2 : '0', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: s1.totals ? s1.totals.progress : '0', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    content.push({{
                      table: {{ 
                        widths: ['5%', '12%', '10%', '15%', '8%', '8%', '8%', '8%', '8%', '8%', '10%'], 
                        body: tableBody1 
                      }},
                      layout: {{ 
                        hLineWidth: () => 0.5, 
                        vLineWidth: () => 0.5, 
                        paddingLeft: () => 4, 
                        paddingRight: () => 4, 
                        paddingTop: () => 4, 
                        paddingBottom: () => 4 
                      }}
                    }});
                  }}

                  // Sheet 2
                  if (allData.sheet2) {{
                    content.push({{ text: '', pageBreak: 'before' }});
                    const s2 = allData.sheet2;
                    const tableBody2 = [];

                    tableBody2.push([
                      {{ text: s2.title || 'थुंकी संकलन अहवाल', colSpan: 10, alignment: 'center', bold: true, fontSize: 10 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody2.push([
                      {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName, colSpan: 10, alignment: 'center', fontSize: 9 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody2.push([
                      {{ text: 'अ.क्र.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'गाव', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'लोकसंख्या', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'कर्मचारी', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'मा.पुरुष', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'मा.स्त्री', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'मा.एकूण', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'वा.पुरुष', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'वा.स्त्री', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'वा.एकूण', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    if (s2.data) {{
                      s2.data.forEach(row => {{
                        // Check if all values in the row are empty or '0'. If so, skip this row.
                        const hasMeaningfulData = Object.values(row).some(val => val !== '' && val !== '0');
                        if (hasMeaningfulData) {{
                          tableBody2.push(Object.values(row).map(val => ({{ text: val || '', fontSize: 9, alignment: 'center' }})));
                        }}
                      }});
                    }}

                    content.push({{
                      table: {{ widths: Array(10).fill('*'), body: tableBody2 }},
                      layout: {{ hLineWidth: () => 0.5, vLineWidth: () => 0.5, paddingLeft: () => 4, paddingRight: () => 4, paddingTop: () => 4, paddingBottom: () => 4 }}
                    }});
                  }}

                  // Sheet 3
                  if (allData.sheet3) {{
                    content.push({{ text: '', pageBreak: 'before' }});
                    const s3 = allData.sheet3;
                    const tableBody3 = [];

                    tableBody3.push([
                      {{ text: s3.title || 'कुष्ठरुग्ण अहवाल', colSpan: 15, alignment: 'center', bold: true, fontSize: 10 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody3.push([
                      {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName, colSpan: 15, alignment: 'center', fontSize: 9 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody3.push([
                      {{ text: 'अ.क्र.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'गाव', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'लोकसंख्या', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'सं.मुले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'सं.प्रौढ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'सं.एकूण', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'MB मुले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'MB प्रौढ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'MB एकूण', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'PB मुले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'PB प्रौढ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'PB एकूण', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'औ.मुले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'औ.प्रौढ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'औ.एकूण', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    if (s3.data) {{
                      s3.data.forEach(row => {{
                        const hasMeaningfulData = Object.values(row).some(val => val !== '' && val !== '0');
                        if (hasMeaningfulData) {{
                          tableBody3.push(Object.values(row).map(val => ({{ text: val || '', fontSize: 9, alignment: 'center' }})));
                        }}
                      }});
                    }}

                    content.push({{
                      table: {{ widths: Array(15).fill('*'), body: tableBody3 }},
                      layout: {{ hLineWidth: () => 0.5, vLineWidth: () => 0.5, paddingLeft: () => 4, paddingRight: () => 4, paddingTop: () => 4, paddingBottom: () => 4 }}
                    }});
                  }}

                  // Sheet 4
                  if (allData.sheet4) {{
                    content.push({{ text: '', pageBreak: 'before' }});
                    const s4 = allData.sheet4;
                    const tableBody4 = [];

                    tableBody4.push([
                      {{ text: s4.title || 'क्षय रुग्ण अहवाल', colSpan: 9, alignment: 'center', bold: true, fontSize: 10 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody4.push([
                      {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName, colSpan: 9, alignment: 'center', fontSize: 9 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);


                    tableBody4.push([
                      {{ text: 'अ.क्र.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'गाव', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'रुग्ण नाव', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'वय', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'लिंग', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'कॅटेगरी', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'दिनांक', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'TB नं.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'कर्मचारी', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    if (s4.data) {{
                      s4.data.forEach(row => {{
                        const hasMeaningfulData = Object.values(row).some(val => val !== '' && val !== '0');
                        if (hasMeaningfulData) {{
                          tableBody4.push(Object.values(row).map(val => ({{ text: val || '', fontSize: 9, alignment: 'center' }})));
                        }}
                      }});
                    }}

                    content.push({{
                      table: {{ widths: Array(9).fill('*'), body: tableBody4 }},
                      layout: {{ hLineWidth: () => 0.5, vLineWidth: () => 0.5, paddingLeft: () => 4, paddingRight: () => 4, paddingTop: () => 4, paddingBottom: () => 4 }}
                    }});
                  }}

                  // Sheet 5
                  if (allData.sheet5) {{
                    content.push({{ text: '', pageBreak: 'before' }});
                    const s5 = allData.sheet5;
                    const tableBody5 = [];

                    tableBody5.push([
                      {{ text: s5.title || 'कंटेनर सर्वेक्षण', colSpan: 13, alignment: 'center', bold: true, fontSize: 10 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody5.push([
                      {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName, colSpan: 13, alignment: 'center', fontSize: 9 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody5.push([
                      {{ text: 'अ.क्र.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'गाव', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'लोकसंख्या', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'घरे', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'तपासले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'दूषित', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'भांडी', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'दूषित भांडी', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'HI', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'CI', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'BI', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'रिकामी', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'अँबेट', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    if (s5.data) {{
                      s5.data.forEach(row => {{
                          const hasMeaningfulData = Object.values(row).some(val => val !== '' && val !== '0');
                          if (hasMeaningfulData) {{
                            // Convert values to array of objects with text and alignment
                            const rowContent = Object.values(row).map(val => ({{ text: val || '', fontSize: 9, alignment: 'center' }}));
                            tableBody5.push(rowContent);
                          }}
                      }});
                    }}

                    content.push({{
                      table: {{ widths: Array(13).fill('*'), body: tableBody5 }},
                      layout: {{ hLineWidth: () => 0.5, vLineWidth: () => 0.5, paddingLeft: () => 4, paddingRight: () => 4, paddingTop: () => 4, paddingBottom: () => 4 }}
                    }});
                  }}

                  // Sheet 6
                  if (allData.sheet6) {{
                    content.push({{ text: '', pageBreak: 'before' }});
                    const s6 = allData.sheet6;
                    const tableBody6 = [];

                    tableBody6.push([
                      {{ text: s6.title || 'डासउत्पत्ती स्थाने', colSpan: 6, alignment: 'center', bold: true, fontSize: 10 }},
                      {{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody6.push([
                      {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName, colSpan: 6, alignment: 'center', fontSize: 9 }},
                      {{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody6.push([
                      {{ text: 'अ.क्र.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'उपकेंद्र', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'गाव', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'कायम', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'हंगामी', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'ठिकाण', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    if (s6.data) {{
                      s6.data.forEach(row => {{
                        const hasMeaningfulData = Object.values(row).some(val => val !== '' && val !== '0');
                        if (hasMeaningfulData) {{
                          tableBody6.push(Object.values(row).map(val => ({{ text: val || '', fontSize: 9, alignment: 'center' }})));
                        }}
                      }});
                    }}

                    content.push({{
                      table: {{ widths: ['8%','18%','18%','12%','12%','32%'], body: tableBody6 }},
                      layout: {{ hLineWidth: () => 0.5, vLineWidth: () => 0.5, paddingLeft: () => 4, paddingRight: () => 4, paddingTop: () => 4, paddingBottom: () => 4 }}
                    }});
                  }}

                  // Sheet 7
                  if (allData.sheet7) {{
                    content.push({{ text: '', pageBreak: 'before' }});
                    const s7 = allData.sheet7;
                    const tableBody7 = [];

                    tableBody7.push([
                      {{ text: s7.title || 'प्रयोगशाळा', colSpan: 9, alignment: 'center', bold: true, fontSize: 10 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody7.push([
                      {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName, colSpan: 9, alignment: 'center', fontSize: 9 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody7.push([
                      {{ text: 'अ.क्र.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'उपकेंद्र', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'जै.घेतलेले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'जै.दूषित', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'रा.घेतलेले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'रा.दूषित', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'TCL प्रारंभ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'TCL खरेदी', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'TCL खर्च', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    if (s7.data) {{
                      s7.data.forEach(row => {{
                        const hasMeaningfulData = Object.values(row).some(val => val !== '' && val !== '0');
                        if (hasMeaningfulData) {{
                          tableBody7.push(Object.values(row).map(val => ({{ text: val || '', fontSize: 9, alignment: 'center' }})));
                        }}
                      }});
                    }}

                    content.push({{
                      table: {{ widths: Array(9).fill('*'), body: tableBody7 }},
                      layout: {{ hLineWidth: () => 0.5, vLineWidth: () => 0.5, paddingLeft: () => 4, paddingRight: () => 4, paddingTop: () => 4, paddingBottom: () => 4 }}
                    }});
                  }}

                  // Sheet 8
                  if (allData.sheet8) {{
                    content.push({{ text: '', pageBreak: 'before' }});
                    const s8 = allData.sheet8;
                    const tableBody8 = [];

                    tableBody8.push([
                      {{ text: s8.title || 'मोतीबिंदू अहवाल', colSpan: 12, alignment: 'center', bold: true, fontSize: 10 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody8.push([
                      {{ text: 'प्रा. आ. केंद्र ' + metadata.phcName, colSpan: 12, alignment: 'center', fontSize: 9 }},
                      {{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}
                    ]);

                    tableBody8.push([
                      {{ text: 'अ.क्र.', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'गाव', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'लोकसंख्या', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'सं.मुले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'सं.प्रौढ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'सं.एकूण', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'न.मुले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'न.प्रौढ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'न.एकूण', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'श.मुले', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'श.प्रौढ', bold: true, fontSize: 9, alignment: 'center' }},
                      {{ text: 'श.एकूण', bold: true, fontSize: 9, alignment: 'center' }}
                    ]);

                    if (s8.data) {{
                      s8.data.forEach(row => {{
                        const hasMeaningfulData = Object.values(row).some(val => val !== '' && val !== '0');
                        if (hasMeaningfulData) {{
                          tableBody8.push(Object.values(row).map(val => ({{ text: val || '', fontSize: 9, alignment: 'center' }})));
                        }}
                      }});
                    }}

                    content.push({{
                      table: {{ widths: Array(12).fill('*'), body: tableBody8 }},
                      layout: {{ hLineWidth: () => 0.5, vLineWidth: () => 0.5, paddingLeft: () => 4, paddingRight: () => 4, paddingTop: () => 4, paddingBottom: () => 4 }}
                    }});
                  }}

                  return {{
                    pageSize: 'A4',
                    pageOrientation: 'landscape',
                    pageMargins: [15, 15, 15, 15],
                    content: content,
                    defaultStyle: {{
                      font: 'MarathiFont',
                      fontSize: 9 // Increased default font size
                    }}
                  }};
                }}

                function previewPDF() {{
                  try {{
                    showStatus('📄 PDF तयार करत आहे...', '#FFF9C4');
                    console.log('Creating PDF...');
                    const docDef = createPDFDefinition();
                    console.log('PDF Definition:', docDef);
                    pdfMake.createPdf(docDef).open();
                    showStatus('✅ PDF तयार झाली!', '#C8E6C9');
                  }} catch(e) {{
                    showStatus('❌ त्रुटी: ' + e.message, '#FFCDD2');
                    console.error('PDF Error:', e);
                  }}
                }}

                function downloadPDF() {{
                  try {{
                    showStatus('⬇️ PDF डाउनलोड करत आहे...', '#FFF9C4');
                    const docDef = createPDFDefinition();
                    const filename = 'Masik_Ahwal_' + metadata.monthYear.replace(/\\s+/g, '_') + '.pdf';
                    pdfMake.createPdf(docDef).download(filename);
                    showStatus('✅ PDF डाउनलोड झाली!', '#C8E6C9');
                  }} catch(e) {{
                    showStatus('❌ त्रुटी: ' + e.message, '#FFCDD2');
                    console.error('PDF Error:', e);
                  }}
                }}

                console.log('PDF functions ready');
              </script>
            </body>
            </html>
            """,
            height=250
        )


if __name__ == "__main__":
    mothly_final_report()
