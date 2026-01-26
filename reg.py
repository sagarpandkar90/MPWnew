import streamlit as st
import pandas as pd
import base64
import json
from pathlib import Path
import streamlit.components.v1 as components


def create_all_columns():
    """Create all possible columns for all registers"""
    cols = set()

    # पाणी नमुने
    cols.update(["अ.क्र.", "गाव", "UID", "स्रोत", "शेरा"])
    months = ["एप्रिल", "मे", "जून", "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर", "जानेवारी",
              "फेब्रुवारी", "मार्च"]
    for m in months:
        cols.update([f"{m} नमुना", f"{m} निष्कर्ष"])

    # मिठ नमुने
    cols.update(["गावाचे नाव", "दुकानदाराचे नाव", "मोबाईल नंबर", "कंपनीचे नाव",
                 "Batch Number", "Manuf. दिनांक", "Expiry दिनांक",
                 "तपासणीसाठी घेतलेला दिनांक", "तपासणीसाठी दिलेला दिनांक"])

    # AFP
    cols.update(["नाव", "लिंग", "वय", "पूर्ण लसीकरण", "संपूर्ण लसीकरण",
                 "कोणत्या भागास लुळेपणा", "पत्ता", "दिनांक", "दवाखान्याचे नाव",
                 "Stool Sample घे. दिनांक", "Stool Sample तपासणी दिनांक", "निष्कर्ष"])

    # गप्पी/डास
    cols.update(["गप्पी मासे सोडल्याचे ठिकाण", "डास उत्पत्तीचे ठिकाण", "कायम", "हंगामी"])

    # शाळा
    cols.update(["शाळेचे नाव"])
    age_groups = ["१ ली", "२ री", "३ री", "४ थी", "५ वी", "६ वी", "७ वी", "८ वी", "९ वी", "१० वी", "११ वी", "१२ वी"]
    for g in age_groups:
        cols.update([f"{g} मुले", f"{g} मुली"])
    cols.update(["एकूण - मुले", "एकूण - मुली"])

    # अंगणवाडी
    cols.update(["अंगणवाडीचे नाव"])
    age_groups_ang = ["० – १ वर्ष", "१ – २ वर्ष", "२ – ३ वर्ष", "३ – ६ वर्ष"]
    for g in age_groups_ang:
        cols.update([f"{g} - मुले", f"{g} - मुली"])
    cols.update(["एकूण - मुले", "एकूण - मुली"])

    # कुष्ठ
    cols.update(["लक्षणे", "निदान", "कुष्ठरुग्णाचे संपूर्ण नाव", "मो. नंबर",
                 "चालू दिनांक", "P.B.", "M.B.", "उपचार कालावधी",
                 "उपचार देणाऱ्याचे नाव व संपर्क क्रमांक"])

    # OT
    cols.update(["O.T. चाचणी घेतल्याचे ठिकाण", "वेळ", "निष्कर्ष +ve", "निष्कर्ष -ve",
                 "केलेली कार्यवाही"])

    # मोतीबिंदू
    cols.update(["शस्त्रक्रिया झालेला रुग्ण", "डोळा उजवा", "डोळा डावा",
                 "शस्त्रक्रिया झालेलं ठिकाण", "संशयित मोतीबिंदू रुग्णाचे नाव"])

    # TCL
    cols.update(["ग्रामपंचायतीचे नाव", "TCL उत्पादनाचे नाव", "उत्पादन Batch Number",
                 "उत्पादन दिनांक", "मुदत बाह्य दिनांक", "नमुना घेतल्याचा दि.",
                 "तपासणीसाठी पाठवलेला दि."])

    # क्षय
    cols.update(["मासिक", "वार्षिक", "संशयित क्षयरुग्णाचे नाव", "घेतलेला दिनांक",
                 "पाठवलेला दिनांक", "Lab No", "क्षयरुग्णाचे नाव", "वजन",
                 "Start of Treatment", "थुंकी", "एक्स-रे", "IP", "CP",
                 "End of Treatment", "Mobile Number"])

    # इतर आवश्यक सामान्य कॉलम्स
    cols.update(["वय", "लिंग", "शेरा", "दिनांक", "अ.क्र.", "गावाचे नाव"])

    return sorted(list(cols))


def generate_combined_html(register_sets, data_json, font_b64):
    """Generate complete HTML for PDF generation"""

    # Calculate page numbers for index
    index_data = []
    current_page = 3  # Cover(1), Index(2), first register cover starts at 3

    for reg_name, info in register_sets.items():
        if info['sets'] > 0:
            start_page = current_page
            # 1 for cover page + (sets * pages_per_set)
            total_pages = 1 + (info['sets'] * info['pages_per_set'])
            end_page = start_page + total_pages - 1
            index_data.append({
                'name': reg_name,
                'start': start_page,
                'end': end_page
            })
            current_page = end_page + 1

    return f"""
<html>
<head>
<meta charset="UTF-8"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
</head>
<body>

<button onclick="previewPDF()" style="padding:10px 20px;background:#2196F3;color:white;border:none;border-radius:6px;margin-right:10px;font-size:16px; cursor: pointer;">Preview PDF</button>
<button onclick="downloadPDF()" style="padding:10px 20px;background:#4CAF50;color:white;border:none;border-radius:6px;font-size:16px; cursor: pointer;">Download PDF</button>

<script>
pdfMake.vfs["Marathi.ttf"] = "{font_b64}";
pdfMake.fonts = {{
    MarathiFont: {{
      normal:"Marathi.ttf", bold:"Marathi.ttf", italics:"Marathi.ttf", bolditalics:"Marathi.ttf"
    }}
}};

const tableData = {data_json};
const registerSets = {json.dumps(register_sets, ensure_ascii=False)};
const indexData = {json.dumps(index_data, ensure_ascii=False)};
const content = [];

// Utility function to generate content (Includes Footer/Page Numbering and Margins)
function generateContent(pdfContent) {{
    const docDefinition = {{
        content: pdfContent,
        defaultStyle: {{
            font: 'MarathiFont', 
            fontSize: 12
        }},
        pageMargins: [50, 30, 30, 30],

        footer: function(currentPage, pageCount) {{
             if (currentPage >= 2) {{ 
                return {{
                    text: currentPage.toString(), 
                    alignment: 'center',
                    fontSize: 10,
                    margin: [0, 10, 0, 0] 
                }};
            }}
             return null;
        }}
    }};
    return docDefinition;
}}

// Cover Page
content.push({{
    text:"आरोग्य विभाग\\nनोंदवही संग्रह",
    fontSize:50,
    bold:true,
    alignment:"center",
    margin:[0,220,0,0],
    pageBreak: "after"
}});

// Index Page
content.push({{
    text:"अनुक्रमणिका",
    fontSize:30,
    bold:true,
    alignment:"center",
    margin:[0,20,0,30]
}});

const indexTableBody = [[
    {{text:"अ.क्र.", bold:true, alignment:"center"}},
    {{text:"रजिस्टरचे नाव", bold:true, alignment:"center"}},
    {{text:"पृष्ठ क्रमांक", bold:true, alignment:"center"}}
]];

indexData.forEach((item, idx) => {{
    indexTableBody.push([
        {{text:(idx+1).toString(), alignment:"center"}},
        {{text:item.name, alignment:"left"}},
        {{text:item.start + " ते " + item.end, alignment:"center"}}
    ]);
}});

content.push({{
    table:{{
        headerRows:1,
        widths:[40, "*", 100],
        body:indexTableBody
    }},
    layout:{{
        hLineWidth:()=>1,
        vLineWidth:()=>1,
        paddingTop:()=>8,
        paddingBottom:()=>8
    }},
    pageBreak: "after"
}});

function buildSimpleTable(title, cols, widths) {{
    content.push({{text:title, alignment:"center", bold:true, fontSize:16, margin:[0,5,0,5]}});
    const headerRow = cols.map(c => ({{text:c, bold:true, alignment:"center"}}));
    const body = [headerRow];
    for(let r=0; r<26; r++) {{
        const row = cols.map(c => ({{text: tableData[r]?.[c] || "", alignment:"center", margin:[0,10,0,10]}}));
        body.push(row);
    }}
    content.push({{
        table:{{headerRows:1, widths:widths, body:body}},
        layout:{{hLineWidth:()=>0.7, vLineWidth:()=>0.7, paddingTop:()=>3, paddingBottom:()=>3}}
    }});
}}

// पाणी नमुने रजिस्टर
if(registerSets["पाणी नमुने तपासणी रजिस्टर"].sets > 0) {{
    content.push({{
        text:"पाणी नमुने तपासणी\\nरजिस्टर",
        fontSize:55,
        bold:true,
        alignment:"center",
        margin:[0,200,0,0],
        pageBreak: "after"
    }});

    function buildPaniTable(fixedCols, months, widths, addShara, heading) {{
        const headerRow1 = [];
        const headerRow2 = [];

        for(const c of fixedCols) {{
            headerRow1.push({{text:c, bold:true, alignment:"center", rowSpan:2}});
            headerRow2.push("");
        }}

        for(const m of months) {{
            headerRow1.push({{text:m, colSpan:2, alignment:"center", bold:true}});
            headerRow1.push({{}});
            headerRow2.push({{text:"नमुना", bold:true, alignment:"center"}});
            headerRow2.push({{text:"निष्कर्ष", bold:true, alignment:"center"}});
        }}

        if(addShara) {{
            headerRow1.push({{text:"शेरा", rowSpan:2, alignment:"center", bold:true}});
            headerRow2.push("");
        }}

        const blankRows = [];
        for(let r=0; r<26; r++) {{
            const row = [];
            for(const c of fixedCols) {{
                row.push({{text: tableData[r]?.[c] || "", alignment:"center", margin:[0,9,0,9]}});
            }}
            for(const m of months) {{
                row.push({{text: tableData[r]?.[m+" नमुना"] || "", alignment:"center", margin:[0,9,0,9]}});
                row.push({{text: tableData[r]?.[m+" निष्कर्ष"] || "", alignment:"center", margin:[0,9,0,9]}});
            }}
            if(addShara) {{
                row.push({{text: tableData[r]?.["शेरा"] || "", alignment:"center", margin:[0,9,0,9]}});
            }}
            blankRows.push(row);
        }}

        content.push({{text: heading, alignment:"center", fontSize:16, bold:true, margin:[0,8,0,8]}});
        content.push({{
            table:{{headerRows:2, widths:widths, body:[headerRow1, headerRow2, ...blankRows]}},
            layout:{{hLineWidth:()=>0.7, vLineWidth:()=>0.7, paddingTop:()=>4, paddingBottom:()=>4}}
        }});
    }}

    for(let i=0; i<registerSets["पाणी नमुने तपासणी रजिस्टर"].sets; i++) {{
        buildPaniTable(["अ.क्र.","गाव","UID","स्रोत"], ["एप्रिल","मे"], [20,82,50,110,42,42,42,42], false, "पाणी नमुने तपासणी रजिस्टर- एप्रिल/मे");
        content.push({{text:"", pageBreak:"after"}});
        buildPaniTable([], ["जून","जुलै","ऑगस्ट","सप्टेंबर"], [42,42,42,42,42,42,42,42,84], true, "पाणी नमुने तपासणी रजिस्टर- जून ते सप्टेंबर");
        content.push({{text:"", pageBreak:"after"}});
        buildPaniTable(["अ.क्र.","गाव","UID","स्रोत"], ["ऑक्टोबर","नोव्हेंबर"], [20,82,50,110,42,42,42,42], false, "पाणी नमुने तपासणी रजिस्टर- ऑक्टोबर/नोव्हेंबर");
        content.push({{text:"", pageBreak:"after"}});
        buildPaniTable([], ["डिसेंबर","जानेवारी","फेब्रुवारी","मार्च"], [42,42,42,42,42,42,42,42,84], true, "पाणी नमुने तपासणी रजिस्टर- डिसेंबर ते मार्च");
        if(i < registerSets["पाणी नमुने तपासणी रजिस्टर"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// मिठ नमुने रजिस्टर
if(registerSets["मिठ नमुने तपासणी रजिस्टर"].sets > 0) {{
    content.push({{text:"मिठ नमुने तपासणी\\nरजिस्टर",fontSize:55,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    const mithPages = [
        {{cols:["अ.क्र    .","गावाचे नाव","दुकानदाराचे नाव","मोबाईल नंबर","कंपनीचे नाव"], widths:[25,110,110,85,120]}},
        {{cols:["Batch Number","Manuf. दिनांक","Expiry दिनांक","तपासणीसाठी घेतलेला दिनांक","तपासणीसाठी दिलेला दिनांक","शेरा"], widths:[53,63,63,80,80,100]}}
    ];

    for(let i=0; i<registerSets["मिठ नमुने तपासणी रजिस्टर"].sets; i++) {{
        mithPages.forEach((p, idx) => {{
            buildSimpleTable("मिठ नमुने तपासणी रजिस्टर", p.cols, p.widths);
            if(!(i === registerSets["मिठ नमुने तपासणी रजिस्टर"].sets-1 && idx === 1)) content.push({{text:"", pageBreak:"after"}});
        }});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// AFP रुग्ण नोंद रजिस्टर
if(registerSets["AFP रुग्ण नोंद रजिस्टर"].sets > 0) {{
    content.push({{text:"AFP रुग्ण नोंद\\nरजिस्टर",fontSize:55,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    const afpPages = [
        {{cols:["अ.क्र       .","नाव","लिंग","वय","पूर्ण लसीकरण","संपूर्ण लसीकरण","कोणत्या भागास लुळेपणा"], widths:[20,165,35,35,40,40,95]}},
        {{cols:["पत्ता","दिनांक","दवाखान्याचे नाव","Stool Sample घे.दिनांक","Stool Sample त.दिनांक","निष्कर्ष"], widths:[100,50,100,50,50,90]}}
    ];

    for(let i=0; i<registerSets["AFP रुग्ण नोंद रजिस्टर"].sets; i++) {{
        afpPages.forEach((p, idx) => {{
            buildSimpleTable("AFP रुग्ण नोंद रजिस्टर", p.cols, p.widths);
            if(!(i === registerSets["AFP रुग्ण नोंद रजिस्टर"].sets-1 && idx === 1)) content.push({{text:"", pageBreak:"after"}});
        }});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// गप्पी मासे
if(registerSets["गप्पी मासे पैदास केंद्र माहिती"].sets > 0) {{
    content.push({{text:"गप्पी मासे पैदास केंद्र\\nमाहिती",fontSize:50,bold:true,alignment:"center",margin:[0,220,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["गप्पी मासे पैदास केंद्र माहिती"].sets; i++) {{
        buildSimpleTable("गप्पी मासे पैदास केंद्र माहिती", ["अ.क्र.","गावाचे नाव","गप्पी मासे सोडल्याचे ठिकाण","कायम","हंगामी"], [30,123,173,60,60]);
        if(i < registerSets["गप्पी मासे पैदास केंद्र माहिती"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// डास उत्पत्ती
if(registerSets["डास उत्पत्ती ठिकाणांची माहिती"].sets > 0) {{
    content.push({{text:"डास उत्पत्ती ठिकाणांची\\nमाहिती",fontSize:50,bold:true,alignment:"center",margin:[0,220,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["डास उत्पत्ती ठिकाणांची माहिती"].sets; i++) {{
        buildSimpleTable("डास उत्पत्ती ठिकाणांची माहिती", ["अ.क्र.","गावाचे नाव","डास उत्पत्तीचे ठिकाण","कायम","हंगामी"], [20,87,235,50,50]);
        if(i < registerSets["डास उत्पत्ती ठिकाणांची माहिती"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// शाळा पटसंख्या
if(registerSets["शाळेतील मुलामुलींची पटसंख्या"].sets > 0) {{
    content.push({{text:"शाळेतील मुलामुलींची पटसंख्या",fontSize:55,bold:true,alignment:"center",margin:[0,180,0,0], pageBreak:"after"}});

    function buildShalaTable(fixedCols, ageGroups, widths, addTotal, heading) {{
        const headerRow1 = [];
        const headerRow2 = [];

        if(fixedCols.length > 0) {{
            headerRow1.push({{text:"अ.क्र.", bold:true, alignment:"center", rowSpan:2}},
                            {{text:"गावाचे नाव", bold:true, alignment:"center", rowSpan:2}},
                            {{text:"शाळेचे नाव", bold:true, alignment:"center", rowSpan:2}});
            headerRow2.push("", "", "");
        }}

        for(const g of ageGroups) {{
            headerRow1.push({{text:g, colSpan:2, alignment:"center", bold:true}}, {{}});
            headerRow2.push({{text:"मुले", bold:true, alignment:"center"}}, {{text:"मुली", bold:true, alignment:"center"}});
        }}

        if(addTotal) {{
            headerRow1.push({{text:"एकूण", colSpan:2, alignment:"center", bold:true}}, {{}});
            headerRow2.push({{text:"मुले", bold:true, alignment:"center"}}, {{text:"मुली", bold:true, alignment:"center"}});
        }}

        const blankRows = [];
        for(let r=0; r<25; r++) {{
            const row = [];
            if(fixedCols.length > 0) {{
                row.push({{text: tableData[r]?.["अ.क्र."] || "", alignment:"center", margin:[0,8,0,8]}});
                row.push({{text: tableData[r]?.["गावाचे नाव"] || "", alignment:"center", margin:[0,8,0,8]}});
                row.push({{text: tableData[r]?.["शाळेचे नाव"] || "", alignment:"center", margin:[0,8,0,8]}});
            }}
            for(const g of ageGroups) {{
                row.push({{text: tableData[r]?.[g + " मुले"] || "", alignment:"center", margin:[0,8,0,8]}});
                row.push({{text: tableData[r]?.[g + " मुली"] || "", alignment:"center", margin:[0,8,0,8]}});
            }}
            if(addTotal) {{
                row.push({{text: tableData[r]?.["एकूण - मुले"] || "", alignment:"center", margin:[0,8,0,8]}});
                row.push({{text: tableData[r]?.["एकूण - मुली"] || "", alignment:"center", margin:[0,8,0,8]}});
            }}
            blankRows.push(row);
        }}

        content.push({{text: heading, alignment:"center", fontSize:18, bold:true, margin:[0,8,0,8]}});
        content.push({{
            table:{{headerRows:2, widths:widths, body:[headerRow1, headerRow2, ...blankRows]}},
            layout:{{hLineWidth:()=>0.8, vLineWidth:()=>0.8, paddingTop:()=>5, paddingBottom:()=>5}}
        }});
    }}

    for(let i=0; i<registerSets["शाळेतील मुलामुलींची पटसंख्या"].sets; i++) {{
        buildShalaTable(["अ.क्र.", "गावाचे नाव", "शाळेचे नाव"], ["१ ली", "२ री", "३ री", "४ थी", "५ वी"], [20,75,100,19,19,19,19,19,19,19,19,19,19], false, "शाळेतील मुलामुलींची पटसंख्या (पान १)");
        content.push({{text:"", pageBreak:"after"}});
        buildShalaTable([], ["६ वी", "७ वी", "८ वी", "९ वी", "१० वी", "११ वी", "१२ वी"], [22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,22,34,34], true, "शाळेतील मुलामुलींची पटसंख्या (पान २)");
        if(i < registerSets["शाळेतील मुलामुलींची पटसंख्या"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// अंगणवाडी
if(registerSets["अंगणवाडी मुलामुलींची पटसंख्या"].sets > 0) {{
    content.push({{text:"अंगणवाडी मुलामुलींची\\nपटसंख्या",fontSize:46,bold:true,alignment:"center",margin:[0,180,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["अंगणवाडी मुलामुलींची पटसंख्या"].sets; i++) {{
        const h1 = [
            {{text:"अ.क्र.", bold:true, alignment:"center", rowSpan:2}},
            {{text:"गावाचे नाव", bold:true, alignment:"center", rowSpan:2}},
            {{text:"अंगणवाडीचे नाव", bold:true, alignment:"center", rowSpan:2}},
            {{text:"० – १ वर्ष", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"१ – २ वर्ष", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"२ – ३ वर्ष", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"३ – ६ वर्ष", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"एकूण", colSpan:2, alignment:"center", bold:true}}, {{}}
        ];

        const h2 = ["", "", "", {{text:"मुले", bold:true}}, {{text:"मुली", bold:true}}, {{text:"मुले", bold:true}}, {{text:"मुली", bold:true}}, {{text:"मुले", bold:true}}, {{text:"मुली", bold:true}}, {{text:"मुले", bold:true}}, {{text:"मुली", bold:true}}, {{text:"मुले", bold:true}}, {{text:"मुली", bold:true}}];

        const body = [h1, h2];
        for(let r=0; r<25; r++) {{
            const row = [
                {{text: tableData[r]?.["अ.क्र."] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["गावाचे नाव"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["अंगणवाडीचे नाव"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["० – १ वर्ष - मुले"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["० – १ वर्ष - मुली"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["१ – २ वर्ष - मुले"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["१ – २ वर्ष - मुली"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["२ – ३ वर्ष - मुले"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["२ – ३ वर्ष - मुली"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["३ – ६ वर्ष - मुले"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["३ – ६ वर्ष - मुली"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["एकूण - मुले"] || "", alignment:"center", margin:[0,8,0,8]}},
                {{text: tableData[r]?.["एकूण - मुली"] || "", alignment:"center", margin:[0,8,0,8]}}
            ];
            body.push(row);
        }}

        content.push({{text:"अंगणवाडी मुलामुलींची पटसंख्या",alignment:"center",fontSize:15,bold:true,margin:[0,10,0,10]}});
        content.push({{
            table:{{headerRows:2, widths:[25,80,90,19,19,19,19,19,19,19,19,20,20], body:body}},
            layout:{{hLineWidth:()=>0.8, vLineWidth:()=>0.8, paddingTop:()=>5, paddingBottom:()=>5}}
        }});
        if(i < registerSets["अंगणवाडी मुलामुलींची पटसंख्या"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// संशयित कुष्ठरुग्ण नोंदवही
if(registerSets["संशयित कुष्ठरुग्ण नोंदवही"].sets > 0) {{
    content.push({{text:"संशयित कुष्ठरुग्ण\\nनोंदवही",fontSize:50,bold:true,alignment:"center",margin:[0,220,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["संशयित कुष्ठरुग्ण नोंदवही"].sets; i++) {{
        buildSimpleTable("संशयित कुष्ठरुग्ण नोंदवही", ["अ.क्र.","गावाचे नाव","संशयित कुष्ठरुग्णाचे नाव","वय"],[30,180,205,40]);
        content.push({{text:"", pageBreak:"after"}});
        buildSimpleTable("संशयित कुष्ठरुग्ण नोंदवही", ["लिंग","लक्षणे","निदान"], [40,220,215]);
        if(i < registerSets["संशयित कुष्ठरुग्ण नोंदवही"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// O.T. चाचणी
if(registerSets["O.T. चाचणी रजिस्टर"].sets > 0) {{
    content.push({{text:"O.T. चाचणी रजिस्टर",fontSize:50,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["O.T. चाचणी रजिस्टर"].sets; i++) {{
        const h1 = [
            {{text:"अ.क्र.", rowSpan:2, alignment:"center", bold:true}},
            {{text:"दिनांक", rowSpan:2, alignment:"center", bold:true}},
            {{text:"O.T. चाचणी घेतल्याचे ठिकाण", rowSpan:2, alignment:"center", bold:true}},
            {{text:"वेळ", rowSpan:2, alignment:"center", bold:true}},
            {{text:"निष्कर्ष", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"केलेली कार्यवाही", rowSpan:2, alignment:"center", bold:true}}
        ];
        const h2 = [{{}}, {{}}, {{}}, {{}}, {{text:"+ve", alignment:"center", fontSize:10}}, {{text:"-ve", alignment:"center", fontSize:10}}, {{}}];

        const body = [h1, h2];
        for(let r=0; r<26; r++) {{
            body.push([
                {{text: tableData[r]?.["अ.क्र."] || "", alignment:"center", margin:[0,8.5,0,8.5]}},
                {{text: tableData[r]?.["दिनांक"] || "", alignment:"center", fontSize:7, margin:[0,8.5,0,8.5]}},
                {{text: tableData[r]?.["O.T. चाचणी घेतल्याचे ठिकाण"] || "", alignment:"center", margin:[0,8.5,0,8.5]}},
                {{text: tableData[r]?.["वेळ"] || "", alignment:"center", margin:[0,8.5,0,8.5]}},
                {{text: tableData[r]?.["निष्कर्ष +ve"] || "", alignment:"center", fontSize:7, margin:[0,8.5,0,8.5]}},
                {{text: tableData[r]?.["निष्कर्ष -ve"] || "", alignment:"center", fontSize:7, margin:[0,8.5,0,8.5]}},
                {{text: tableData[r]?.["केलेली कार्यवाही"] || "", alignment:"center", margin:[0,8.5,0,8.5]}}
            ]);
        }}

        content.push({{text:"O.T. चाचणी रजिस्टर",alignment:"center",bold:true,fontSize:18,margin:[0,8,0,8]}});
        content.push({{
            table:{{headerRows:2, widths:[20,55,170,40,25,25,105], body:body}},
            layout:{{hLineWidth:()=>0.7, vLineWidth:()=>0.7, paddingTop:()=>4, paddingBottom:()=>4}}
        }});
        if(i < registerSets["O.T. चाचणी रजिस्टर"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// मोतीबिंदू शस्त्रक्रिया नोंदवही
if(registerSets["मोतीबिंदू शस्त्रक्रिया नोंदवही"].sets > 0) {{
    content.push({{text:"मोतीबिंदू शस्त्रक्रिया\\nनोंदवही",fontSize:50,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["मोतीबिंदू शस्त्रक्रिया नोंदवही"].sets; i++) {{
        const h1 = [
            {{text:"अ.क्र.", rowSpan:2, alignment:"center", bold:true}},
            {{text:"गावाचे नाव", rowSpan:2, alignment:"center", bold:true}},
            {{text:"शस्त्रक्रिया झालेला रुग्ण", rowSpan:2, alignment:"center", bold:true}},
            {{text:"वय", rowSpan:2, alignment:"center", bold:true}},
            {{text:"लिंग", rowSpan:2, alignment:"center", bold:true}},
            {{text:"डोळा", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"शस्त्रक्रिया झालेलं ठिकाण", rowSpan:2, alignment:"center", bold:true}},
            {{text:"दिनांक", rowSpan:2, alignment:"center", bold:true}}
        ];
        const h2 = [{{}}, {{}}, {{}}, {{}}, {{}}, {{text:"उजवा", alignment:"center", fontSize:10}}, {{text:"डावा", alignment:"center", fontSize:10}}, {{}}, {{}}];

        const body = [h1, h2];
        for(let r=0; r<26; r++) {{
            body.push([
                {{text: tableData[r]?.["अ.क्र."] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["गावाचे नाव"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["शस्त्रक्रिया झालेला रुग्ण"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["वय"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["लिंग"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["डोळा उजवा"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["डोळा डावा"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["शस्त्रक्रिया झालेलं ठिकाण"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["दिनांक"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}}
            ]);
        }}

        content.push({{text:"मोतीबिंदू शस्त्रक्रिया नोंदवही",alignment:"center",bold:true,fontSize:18,margin:[0,8,0,8]}});
        content.push({{
            table:{{headerRows:2, widths:[20,65,115,20,20,20,20,115,40], body:body}},
            layout:{{hLineWidth:()=>0.7, vLineWidth:()=>0.7, paddingTop:()=>4, paddingBottom:()=>4}}
        }});
        if(i < registerSets["मोतीबिंदू शस्त्रक्रिया नोंदवही"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// संशयित मोतीबिंदू रुग्ण नोंदवही
if(registerSets["संशयित मोतीबिंदू रुग्ण नोंदवही"].sets > 0) {{
    content.push({{text:"संशयित मोतीबिंदू रुग्ण\\nनोंदवही",fontSize:48,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["संशयित मोतीबिंदू रुग्ण नोंदवही"].sets; i++) {{
        const h1 = [
            {{text:"अ.क्र.", rowSpan:2, alignment:"center", bold:true}},
            {{text:"गावाचे नाव", rowSpan:2, alignment:"center", bold:true}},
            {{text:"संशयित मोतीबिंदू रुग्णाचे नाव", rowSpan:2, alignment:"center", bold:true}},
            {{text:"वय", rowSpan:2, alignment:"center", bold:true}},
            {{text:"लिंग", rowSpan:2, alignment:"center", bold:true}},
            {{text:"डोळा", colSpan:2, alignment:"center", bold:true}}, {{}}
        ];
        const h2 = [{{}}, {{}}, {{}}, {{}}, {{}}, {{text:"उजवा", alignment:"center", fontSize:10}}, {{text:"डावा", alignment:"center", fontSize:10}}];

        const body = [h1, h2];
        for(let r=0; r<26; r++) {{
            body.push([
                {{text: tableData[r]?.["अ.क्र."] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["गावाचे नाव"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["संशयित मोतीबिंदू रुग्णाचे नाव"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["वय"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["लिंग"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["डोळा उजवा"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}},
                {{text: tableData[r]?.["डोळा डावा"] || "", alignment:"center", fontSize:11, margin:[0,9,0,9]}}
            ]);
        }}

        content.push({{text:"संशयित मोतीबिंदू रुग्ण नोंदवही",alignment:"center",bold:true,fontSize:18,margin:[0,8,0,8]}});
        content.push({{
            table:{{headerRows:2, widths:[25,90,175,35,35,35,35], body:body}},
            layout:{{hLineWidth:()=>0.7, vLineWidth:()=>0.7, paddingTop:()=>4, paddingBottom:()=>4}}
        }});
        if(i < registerSets["संशयित मोतीबिंदू रुग्ण नोंदवही"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// कुष्ठरुग्ण नोंदवही
if(registerSets["कुष्ठरुग्ण नोंदवही"].sets > 0) {{
    content.push({{text:"कुष्ठरुग्ण नोंदवही",fontSize:52,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["कुष्ठरुग्ण नोंदवही"].sets; i++) {{
        // Page 1
        buildSimpleTable("कुष्ठरुग्ण नोंदवही - रुग्ण माहिती", ["अ.क्र.","गावाचे नाव","कुष्ठरुग्णाचे संपूर्ण नाव","वय","लिंग","मो. नंबर","निदान"], [20,70,145,25,25,80,70]);
        content.push({{text:"", pageBreak:"after"}});

        // Page 2
        const h1 = [
            {{text:"चालू दिनांक", rowSpan:2, alignment:"center", bold:true}},
            {{text:"उपचार", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"P.B.", rowSpan:2, alignment:"center", bold:true}},
            {{text:"M.B.", rowSpan:2, alignment:"center", bold:true}},
            {{text:"उपचार कालावधी", rowSpan:2, alignment:"center", bold:true}},
            {{text:"उपचार देणाऱ्याचे नाव व संपर्क क्रमांक", rowSpan:2, alignment:"center", bold:true}},
            {{text:"शेरा", rowSpan:2, alignment:"center", bold:true}}
        ];
        const h2 = [{{}}, {{text:"सुरु", alignment:"center", fontSize:10}}, {{text:"समाप्त", alignment:"center", fontSize:10}}, {{}}, {{}}, {{}}, {{}}, {{}}];

        const body = [h1, h2];
        for(let r=0; r<26; r++) {{
            body.push([
                {{text: tableData[r]?.["चालू दिनांक"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["उपचार सुरु"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["उपचार समाप्त"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["P.B."] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["M.B."] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["उपचार कालावधी"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["उपचार देणाऱ्याचे नाव व संपर्क क्रमांक"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["शेरा"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}}
            ]);
        }}

        content.push({{text:"कुष्ठरुग्ण नोंदवही - उपचार माहिती (पान २)",alignment:"center",bold:true,fontSize:18,margin:[0,8,0,8]}});
        content.push({{
            table:{{headerRows:2, widths:[40,40,40,30,30,50,130,70], body:body}},
            layout:{{hLineWidth:()=>0.7, vLineWidth:()=>0.7, paddingTop:()=>4, paddingBottom:()=>4}}
        }});

        if(i < registerSets["कुष्ठरुग्ण नोंदवही"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// TCL नमुना तपासणी नोंदवही
if(registerSets["T.C.L नमुना तपासणी नोंदवही"].sets > 0) {{
    content.push({{text:"T.C.L नमुना तपासणी\\nनोंदवही",fontSize:50,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["T.C.L नमुना तपासणी नोंदवही"].sets; i++) {{
        // Page 1
        buildSimpleTable("T.C.L नमुना तपासणी नोंदवही", ["अ.क्र.","ग्रामपंचायतीचे नाव","TCL उत्पादनाचे नाव","उत्पादन Batch Number","उत्पादन दिनांक"], [25,115,150,85,70]);
        content.push({{text:"", pageBreak:"after"}});

        // Page 2
        buildSimpleTable("T.C.L नमुना तपासणी नोंदवही", ["अ.क्र.","मुदत बाह्य दिनांक","नमुना घेतल्याचा दि.","तपासणीसाठी पाठवलेला दि.","निष्कर्ष", "शेरा"], [25,63,63,63,80,150]);
        if(i < registerSets["T.C.L नमुना तपासणी नोंदवही"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// संशयित क्षयरुग्ण नोंदवही
if(registerSets["संशयित क्षयरुग्ण नोंदवही"].sets > 0) {{
    content.push({{text:"संशयित क्षयरुग्ण\\nनोंदवही",fontSize:50,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["संशयित क्षयरुग्ण नोंदवही"].sets; i++) {{
        // Page 1
        buildSimpleTable("संशयित क्षयरुग्ण नोंदवही (पान १)", ["अ.क्र.","गावाचे नाव","संशयित क्षयरुग्णाचे नाव","लिंग","वय","मोबाईल नंबर"], [20,100,160,30,30,95]);
        content.push({{text:"", pageBreak:"after"}});

        // Page 2
        const h1 = [
            {{text:"दिनांक", rowSpan:2, alignment:"center", bold:true}},
            {{text:"नमुना", colSpan:2, alignment:"center", bold:true}}, {{}},
            {{text:"Lab No", rowSpan:2, alignment:"center", bold:true}},
            {{text:"निष्कर्ष", rowSpan:2, alignment:"center", bold:true}},
            {{text:"शेरा", rowSpan:2, alignment:"center", bold:true}}
        ];
        const h2 = [{{}}, {{text:"घेतलेला दिनांक", alignment:"center", fontSize:10}}, {{text:"पाठवलेला दिनांक", alignment:"center", fontSize:10}}, {{}}, {{}}, {{}}];

        const body = [h1, h2];
        for(let r=0; r<27; r++) {{
            body.push([
                {{text: tableData[r]?.["दिनांक"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["घेतलेला दिनांक"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["पाठवलेला दिनांक"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["Lab No"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["निष्कर्ष"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}},
                {{text: tableData[r]?.["शेरा"] || "", alignment:"center", fontSize:10, margin:[0,8,0,8]}}
            ]);
        }}

        content.push({{text:"संशयित क्षयरुग्ण नोंदवही (पान २)",alignment:"center",bold:true,fontSize:18,margin:[0,8,0,8]}});
        content.push({{
            table:{{headerRows:2, widths:[60,60,60,60,60,150], body:body}},
            layout:{{hLineWidth:()=>0.7, vLineWidth:()=>0.7, paddingTop:()=>4, paddingBottom:()=>4}}
        }});

        if(i < registerSets["संशयित क्षयरुग्ण नोंदवही"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// उपचाराखालील क्षयरुग्ण नोंदवही
if(registerSets["उपचाराखालील क्षयरुग्ण नोंदवही"].sets > 0) {{
    content.push({{text:"उपचाराखालील क्षयरुग्ण\\nनोंदवही",fontSize:50,bold:true,alignment:"center",margin:[0,200,0,0], pageBreak:"after"}});

    for(let i=0; i<registerSets["उपचाराखालील क्षयरुग्ण नोंदवही"].sets; i++) {{
        // Page 1
        buildSimpleTable("उपचाराखालील क्षयरुग्ण नोंदवही (पान १)", ["मासिक","वार्षिक","गावाचे नाव","क्षयरुग्णाचे नाव","लिंग","वय","वजन","Start of Treatment"], [30,30,80,140,25,25,30,64]);
        content.push({{text:"", pageBreak:"after"}});

        // Page 2
        buildSimpleTable("उपचाराखालील क्षयरुग्ण नोंदवही (पान २)", ["थुंकी","एक्स-रे","IP","CP","End of Treatment", "Mobile Number", "शेरा"], [40,50,40,40,75,85,100]);
        if(i < registerSets["उपचाराखालील क्षयरुग्ण नोंदवही"].sets-1) content.push({{text:"", pageBreak:"after"}});
    }}
    content.push({{text:"", pageBreak:"after"}});
}}

// Final functions to create PDF and download/preview
function previewPDF() {{
    try {{
        const docDefinition = generateContent(content);
        pdfMake.createPdf(docDefinition).open();
    }} catch (e) {{
        alert("PDF तयार करताना त्रुटी आली. कृपया कन्सोल तपासा. Error: " + e.message);
        console.error("PDF Generation Error:", e);
    }}
}}
function downloadPDF() {{
    try {{
        const docDefinition = generateContent(content);
        pdfMake.createPdf(docDefinition).download('आरोग्य-नोंदवही-संग्रह.pdf');
    }} catch (e) {{
        alert("PDF तयार करताना त्रुटी आली. कृपया कन्सोल तपासा. Error: " + e.message);
        console.error("PDF Generation Error:", e);
    }}
}}
</script>
</body>
</html>
"""


def combined_all_registers():
    st.set_page_config(layout="wide", page_title="आरोग्य नोंदवही जनरेटर")
    st.title("सर्व रजिस्टर एकत्रित जनरेटर")
    st.markdown("---")

    # All register definitions
    all_registers = [
        {"name": "पाणी नमुने तपासणी रजिस्टर", "pages_per_set": 4},
        {"name": "मिठ नमुने तपासणी रजिस्टर", "pages_per_set": 2},
        {"name": "AFP रुग्ण नोंद रजिस्टर", "pages_per_set": 2},
        {"name": "गप्पी मासे पैदास केंद्र माहिती", "pages_per_set": 1},
        {"name": "डास उत्पत्ती ठिकाणांची माहिती", "pages_per_set": 1},
        {"name": "शाळेतील मुलामुलींची पटसंख्या", "pages_per_set": 2},
        {"name": "अंगणवाडी मुलामुलींची पटसंख्या", "pages_per_set": 1},
        {"name": "संशयित कुष्ठरुग्ण नोंदवही", "pages_per_set": 2},
        # Changed to 2 pages for consistency (as per JS implementation)
        {"name": "O.T. चाचणी रजिस्टर", "pages_per_set": 1},
        {"name": "मोतीबिंदू शस्त्रक्रिया नोंदवही", "pages_per_set": 1},
        {"name": "संशयित मोतीबिंदू रुग्ण नोंदवही", "pages_per_set": 1},
        {"name": "कुष्ठरुग्ण नोंदवही", "pages_per_set": 2},
        {"name": "T.C.L नमुना तपासणी नोंदवही", "pages_per_set": 2},
        {"name": "संशयित क्षयरुग्ण नोंदवही", "pages_per_set": 2},
        {"name": "उपचाराखालील क्षयरुग्ण नोंदवही", "pages_per_set": 2}
    ]

    st.subheader("प्रत्येक रजिस्टरसाठी किती संच हवे ते भरा: 📝")
    st.write("*(प्रत्येक संचात त्या रजिस्टरची सर्व पाने येतील)*")

    # Input for each register
    register_sets = {}
    cols = st.columns(3)
    for idx, reg in enumerate(all_registers):
        with cols[idx % 3]:
            sets = st.number_input(
                f"**{reg['name']}**",
                min_value=0,
                value=7,
                step=1,
                key=reg['name'],
                help=f"प्रत्येक संचात {reg['pages_per_set']} पाने"
            )
            register_sets[reg['name']] = {
                'sets': sets,
                'pages_per_set': reg['pages_per_set']
            }

    st.markdown("---")

    # Create empty data
    all_cols = create_all_columns()
    df = pd.DataFrame({c: [""] * 25 for c in all_cols})
    # Data is prepared for JSON injection (No special encoding needed if the data is simple/small)
    data_json = json.dumps(df.to_dict(orient="records"), ensure_ascii=False)

    # Load font
    font_path = Path("fonts/NotoSerifDevanagari-VariableFont_wdth,wght.ttf")
    if not font_path.exists():
        st.error(
            "❌ **फॉन्ट गहाळ आहे:** `fonts/NotoSerifDevanagari-VariableFont_wdth,wght.ttf` ही फाईल तुमच्या Streamlit ॲपच्या 'fonts' फोल्डरमध्ये असणे आवश्यक आहे.")
        return
    # Base64 Encode the font file
    font_b64 = base64.b64encode(font_path.read_bytes()).decode()

    # Generate HTML
    full_html = generate_combined_html(register_sets, data_json, font_b64)

    # Display the HTML component
    components.html(full_html, height=800, scrolling=True)


if __name__ == "__main__":
    combined_all_registers()