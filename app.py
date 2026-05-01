import streamlit as st
from agent import create_agent
import pandas as pd
from datetime import datetime
import base64
from tools import scan_cargo, forecast_capacity, prioritize_operations, assess_risk, fleet_efficiency, inspection_alerts

st.set_page_config(
    page_title="Freight Intelligence System",
    page_icon="",
    layout="wide"
)

def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

logo_b64 = get_image_base64("images/fislogo.png")
pic_b64 = get_image_base64("images/fispic.png")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, .stApp {
        background-color: #0f1623;
        font-family: 'Inter', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding: 0 !important; max-width: 100% !important; }

    .topbar {
        background: #111827;
        border-bottom: 2px solid #1e3a5f;
        padding: 0.75rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .topbar-left { display: flex; align-items: center; gap: 14px; }
    .topbar-name { font-size: 15px; font-weight: 600; color: #f1f5f9; }
    .topbar-sub {
        font-size: 10px; color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1px; text-transform: uppercase; margin-top: 2px;
    }
    .topbar-right { display: flex; align-items: center; gap: 8px; }
    .tb-badge {
        font-size: 11px; color: #64748b;
        background: #1e293b; padding: 5px 12px;
        border-radius: 6px; border: 1px solid #334155;
        font-family: 'JetBrains Mono', monospace;
    }
    .tb-live {
        font-size: 11px; color: #22c55e;
        background: #052e16; padding: 5px 12px;
        border-radius: 6px; border: 1px solid #166534;
        display: flex; align-items: center; gap: 6px;
        font-family: 'JetBrains Mono', monospace;
    }
    .dot { width: 7px; height: 7px; background: #22c55e;
        border-radius: 50%; animation: blink 1.5s infinite; }
    @keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }

    .metrics-bar {
        background: #111827;
        border-bottom: 1px solid #1e3a5f;
        padding: 0.6rem 1.5rem;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
    }
    .m-cell { padding: 0.5rem 1rem; border-right: 1px solid #1e293b; }
    .m-cell:last-child { border-right: none; }
    .m-label {
        font-size: 10px; color: #64748b;
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 4px; font-weight: 500;
    }
    .m-val {
        font-size: 24px; font-weight: 700;
        font-family: 'JetBrains Mono', monospace; line-height: 1;
    }
    .m-sub { font-size: 11px; color: #475569; margin-top: 3px; }
    .c-blue{color:#60a5fa;} .c-red{color:#f87171;}
    .c-amber{color:#fbbf24;} .c-green{color:#4ade80;} .c-purple{color:#a78bfa;}

    .stButton > button {
        background: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        padding: 0.5rem 1rem !important;
        width: auto !important;
    }
    .stButton > button:hover {
        border-color: #3b82f6 !important;
        color: #60a5fa !important;
        background: #1e3a5f !important;
    }

    .sec-label {
        font-size: 10px; font-weight: 600; color: #64748b;
        text-transform: uppercase; letter-spacing: 1px;
        margin: 0.75rem 0 0.5rem 0;
        font-family: 'JetBrains Mono', monospace;
        padding-bottom: 4px; border-bottom: 1px solid #1e293b;
    }

    .qitem {
        background: #1a2540; border: 1px solid #1e293b;
        border-left: 3px solid #2563eb; border-radius: 4px;
        padding: 8px 10px; margin-bottom: 5px;
    }
    .qcat {
        font-size: 9px; color: #475569; text-transform: uppercase;
        letter-spacing: 1px; font-family: 'JetBrains Mono', monospace;
        margin-bottom: 3px;
    }
    .qtext { font-size: 12px; color: #93c5fd;
        font-family: 'JetBrains Mono', monospace; }

    .chat-scroll {
        height: 460px;
        overflow-y: auto;
        overflow-x: hidden;
        scrollbar-width: thin;
        scrollbar-color: #1e3a5f transparent;
        padding: 4px;
    }
    .chat-scroll::-webkit-scrollbar { width: 3px; }
    .chat-scroll::-webkit-scrollbar-thumb {
        background: #1e3a5f; border-radius: 3px;
    }

    .msg-u {
        display: flex; justify-content: flex-end; margin: 8px 0;
    }
    .msg-u-inner {
        background: #2563eb; color: #ffffff;
        padding: 10px 14px;
        border-radius: 16px 16px 4px 16px;
        max-width: 55%; font-size: 13px; line-height: 1.5;
        word-break: break-word;
    }
    .msg-u-label {
        font-size: 10px; color: #bfdbfe; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.8px;
        margin-bottom: 5px; font-family: 'JetBrains Mono', monospace;
    }
    .msg-a {
        display: flex; align-items: flex-start; gap: 12px; margin: 8px 0;
    }
    .msg-a-av {
        width: 32px; height: 32px;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        border-radius: 8px; display: flex; align-items: center;
        justify-content: center; font-size: 13px; font-weight: 700;
        color: white; flex-shrink: 0; margin-top: 2px;
    }
    .msg-a-inner {
        background: #1a2540; border: 1px solid #1e3a5f;
        color: #e2e8f0; padding: 14px 18px;
        border-radius: 4px 16px 16px 16px;
        max-width: 85%; font-size: 13px; line-height: 1.8;
        white-space: pre-wrap; word-break: break-word;
    }
    .msg-a-label {
        font-size: 10px; color: #a78bfa; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.8px;
        margin-bottom: 5px; font-family: 'JetBrains Mono', monospace;
    }

    .streamlit-expanderHeader {
        background: #111827 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important; color: #475569 !important;
        border: 1px solid #1e3a5f !important; border-radius: 6px !important;
    }
    .streamlit-expanderContent {
        background: #0f1623 !important; border: 1px solid #1e3a5f !important;
    }

    .stChatInput > div {
        background: #1a2540 !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 12px !important;
    }
    .stChatInput textarea {
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0 !important; font-size: 13px !important;
        background: transparent !important;
    }

    [data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


def get_stats():
    df = pd.read_csv("inventory.csv")
    df["util"] = (df["Current_Load"] / df["Max_Capacity"]) * 100
    total = len(df)
    critical = len(df[df["util"] > 90])
    warning = len(df[(df["util"] > 70) & (df["util"] <= 90)])
    normal = len(df[df["util"] <= 70])
    avg_util = df["util"].mean()
    return total, critical, warning, normal, avg_util, df


total, critical, warning, normal, avg_util, df = get_stats()

# SESSION STATE
if "agent" not in st.session_state:
    with st.spinner("Initializing agent..."):
        st.session_state.agent = create_agent()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_panel" not in st.session_state:
    st.session_state.show_panel = True

# TOPBAR
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:42px;height:42px;object-fit:contain;border-radius:8px;"/>' if logo_b64 else ''

st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        {logo_html}
        <div>
            <div class="topbar-name">Freight Intelligence System</div>
            <div class="topbar-sub">Autonomous Logistics Agent v1.0</div>
        </div>
    </div>
    <div class="topbar-right">
        <span class="tb-badge">15 Containers</span>
        <span class="tb-live"><span class="dot"></span>ONLINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# METRICS
st.markdown(f"""
<div class="metrics-bar">
    <div class="m-cell">
        <div class="m-label">Total Containers</div>
        <div class="m-val c-blue">{total}</div>
        <div class="m-sub">Active fleet</div>
    </div>
    <div class="m-cell">
        <div class="m-label">Critical Capacity</div>
        <div class="m-val c-red">{critical}</div>
        <div class="m-sub">Above 90% full</div>
    </div>
    <div class="m-cell">
        <div class="m-label">High Utilization</div>
        <div class="m-val c-amber">{warning}</div>
        <div class="m-sub">70–90% range</div>
    </div>
    <div class="m-cell">
        <div class="m-label">Normal Ops</div>
        <div class="m-val c-green">{normal}</div>
        <div class="m-sub">Below 70%</div>
    </div>
    <div class="m-cell">
        <div class="m-label">Avg Utilization</div>
        <div class="m-val c-purple">{avg_util:.1f}%</div>
        <div class="m-sub">Fleet average</div>
    </div>
</div>
""", unsafe_allow_html=True)

# TOGGLE
btn_col, _ = st.columns([1, 6])
with btn_col:
    label = "◀ Hide Panel" if st.session_state.show_panel else "▶ Fleet Panel"
    if st.button(label):
        st.session_state.show_panel = not st.session_state.show_panel
        st.rerun()

# LAYOUT
if st.session_state.show_panel:
    left, right = st.columns([1, 2.5])
else:
    right = st.columns(1)[0]
    left = None

# LEFT PANEL
if st.session_state.show_panel and left:
    with left:
        st.markdown("""
        <div style="display:flex; justify-content:space-between;
        align-items:center; padding:0.4rem 0; margin-bottom:6px;
        border-bottom:1px solid #1e3a5f;">
            <span style="font-size:10px; font-weight:600; color:#64748b;
            text-transform:uppercase; letter-spacing:1.5px;
            font-family:'JetBrains Mono',monospace;">Fleet Status Panel</span>
            <span style="font-size:10px; color:#22c55e;
            font-family:'JetBrains Mono',monospace;">● LIVE</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sec-label">Container Status</div>',
                    unsafe_allow_html=True)

        df_show = df[["Cargo_ID", "Description", "util"]].copy()
        df_show["util"] = df_show["util"].round(1).astype(str) + "%"
        df_show["Description"] = df_show["Description"].str[:22]

        def status(u):
            val = float(u.replace("%", ""))
            if val > 90: return "Critical"
            elif val > 70: return "Warning"
            else: return "Normal"

        df_show["Status"] = df_show["util"].apply(status)
        df_show.columns = ["ID", "Cargo", "Util", "Status"]

        st.dataframe(
            df_show,
            hide_index=True,
            height=300,
            use_container_width=True
        )

        st.markdown('<div class="sec-label">Query Guide</div>',
                    unsafe_allow_html=True)

        queries = [
            ("Scan", "Scan all containers"),
            ("Forecast", "Forecast MAERSK-COLD-02"),
            ("Priority", "Prioritize COSCO containers"),
            ("Risk", "Run a risk assessment"),
            ("Fleet", "Fleet efficiency report"),
            ("Inspection", "Which containers are overdue?"),
            ("Hazmat", "Hazardous cargo risk level"),
            ("Location", "Singapore terminal report"),
            ("Shipping Line", "Status of all MSC containers"),
            ("Route", "Containers going to Rotterdam"),
        ]

        for cat, q in queries:
            st.markdown(f"""
            <div class="qitem">
                <div class="qcat">{cat}</div>
                <div class="qtext">{q}</div>
            </div>
            """, unsafe_allow_html=True)

# CHAT
with right:
    st.markdown("""
    <div style="display:flex; justify-content:space-between;
    align-items:center; padding:0.4rem 0; margin-bottom:6px;
    border-bottom:1px solid #1e3a5f;">
        <span style="font-size:10px; font-weight:600; color:#64748b;
        text-transform:uppercase; letter-spacing:1.5px;
        font-family:'JetBrains Mono',monospace;">Agent Interface</span>
        <span style="font-size:10px; color:#a78bfa;
        font-family:'JetBrains Mono',monospace;">FIS Agent</span>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.chat_history:
        if pic_b64:
            st.markdown(f"""
            <div style="position:relative; border-radius:12px;
            overflow:hidden; margin-bottom:16px; height:200px;">
                <img src="data:image/png;base64,{pic_b64}"
                style="width:100%; height:200px; object-fit:cover; opacity:0.65;"/>
                <div style="position:absolute; inset:0;
                background:linear-gradient(to bottom, transparent 30%, #0f1623);">
                </div>
                <div style="position:absolute; bottom:16px; left:20px;">
                    <div style="font-size:16px; font-weight:600; color:#f1f5f9;
                    font-family:'Inter',sans-serif;">
                    How can I help you today?</div>
                    <div style="font-size:12px; color:#94a3b8; margin-top:4px;
                    font-family:'Inter',sans-serif;">
                    Ask me anything about your global freight operations</div>
                </div>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px;">
                <span style="background:#1a2540; border:1px solid #1e3a5f;
                border-radius:20px; padding:6px 14px; font-size:11px; color:#64748b;
                font-family:'JetBrains Mono',monospace;">Risk assessment</span>
                <span style="background:#1a2540; border:1px solid #1e3a5f;
                border-radius:20px; padding:6px 14px; font-size:11px; color:#64748b;
                font-family:'JetBrains Mono',monospace;">Fleet efficiency</span>
                <span style="background:#1a2540; border:1px solid #1e3a5f;
                border-radius:20px; padding:6px 14px; font-size:11px; color:#64748b;
                font-family:'JetBrains Mono',monospace;">Overdue inspections</span>
                <span style="background:#1a2540; border:1px solid #1e3a5f;
                border-radius:20px; padding:6px 14px; font-size:11px; color:#64748b;
                font-family:'JetBrains Mono',monospace;">Prioritize COSCO</span>
            </div>
            """, unsafe_allow_html=True)

    # CHAT MESSAGES
    if st.session_state.chat_history:
        chat_html = '<div class="chat-scroll">'
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                safe_user = str(message["content"]).replace(
                    '<', '&lt;').replace('>', '&gt;')
                chat_html += (
                    '<div class="msg-u">'
                    '<div class="msg-u-inner">'
                    '<div class="msg-u-label">You</div>'
                    f'{safe_user}'
                    '</div>'
                    '</div>'
                )
            else:
                safe_content = str(message["content"]).replace(
                    '<', '&lt;').replace('>', '&gt;')
                chat_html += (
                    '<div class="msg-a">'
                    '<div class="msg-a-av">F</div>'
                    '<div class="msg-a-inner">'
                    '<div class="msg-a-label">FIS Agent</div>'
                    f'{safe_content}'
                    '</div>'
                    '</div>'
                )
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        for message in st.session_state.chat_history:
            if message["role"] == "assistant" and "steps" in message and message["steps"]:
                with st.expander("View reasoning chain"):
                    for i, step in enumerate(message["steps"]):
                        action, observation = step
                        st.markdown(f"""
                        <div style="font-family:'JetBrains Mono',monospace;
                        font-size:11px; padding:8px 0;
                        border-bottom:1px solid #1e293b; line-height:1.8;">
                            <span style="color:#60a5fa;">step_{i+1}</span> |
                            tool: <span style="color:#fbbf24;">
                            {action.tool}</span><br>
                            <span style="color:#475569;">
                            input: {action.tool_input}</span><br>
                            <span style="color:#4ade80;">
                            output: {str(observation)[:300]}</span>
                        </div>
                        """, unsafe_allow_html=True)

# INPUT
prefill = st.session_state.pop("prefill", "")
user_input = st.chat_input("Message FIS Agent...") or prefill

if user_input:
    simple_words = ["thank you", "thanks", "ok!", "okay!",
                    "cool!", "awesome!", "perfect!", "got it!", "noted!"]
    is_simple = any(user_input.lower().strip() == w for w in simple_words)
    
    direct_map = {
    "scan": scan_cargo,
    "overdue": inspection_alerts,
    "inspection alert": inspection_alerts,
    "inspection": inspection_alerts,
    "fleet efficiency": fleet_efficiency,
    "efficiency report": fleet_efficiency,
    "efficiency": fleet_efficiency,
    "fleet report": fleet_efficiency,
    "risk assessment": assess_risk,
    "risk assesment": assess_risk,
    "risk assess": assess_risk,
    "assess risk": assess_risk,
    "risk": assess_risk,
    "prioritize": prioritize_operations,
    "priority": prioritize_operations,
}
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input})

    if is_simple:
        output = "You're welcome! Let me know if you need anything else about your freight operations."
        steps = []
    else:
        matched_tool = None
        query_lower = user_input.lower()

        if "forecast" not in query_lower:
            for keyword, tool_fn in direct_map.items():
                if keyword in query_lower:
                    matched_tool = tool_fn
                    break

        if matched_tool:
            with st.spinner("Processing..."):
                try:
                    output = str(matched_tool.invoke(user_input))
                    steps = []
                except Exception as e:
                    output = f"Error: {str(e)}"
                    steps = []
        else:
            with st.spinner("Processing..."):
                response = st.session_state.agent.invoke(
                    {"input": user_input})
                output = response["output"]
                steps = response.get("intermediate_steps", [])

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": output,
        "steps": steps
    })
    st.rerun()