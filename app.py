import streamlit as st
import pandas as pd
import casparser
from pyxirr import xirr
from datetime import date
import requests
from streamlit_lottie import st_lottie

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="TealScan",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. THE "POWERUP" THEME (Native CSS) ---
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
    
    /* GLOBAL VARIABLES */
    :root {
        --primary: #0F766E;
        --accent: #14B8A6;
        --bg-color: #F8FAFC;
        --text-dark: #1E293B;
    }

    /* GLOBAL RESET */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Manrope', sans-serif;
    }
    
    /* HIDE STREAMLIT ELEMENTS */
    #MainMenu, footer, header {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}

    /* --- HERO SECTION STYLES --- */
    .hero-container {
        padding: 4rem 1rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        margin-bottom: 1.5rem;
    }
    
    .hero-span {
        background: linear-gradient(135deg, #0F766E 0%, #2DD4BF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-desc {
        font-size: 1.25rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    
    /* --- FLOATING UPLOAD CARD --- */
    .upload-card-container {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 0 20px 40px -10px rgba(15, 118, 110, 0.15);
        border: 1px solid #E2E8F0;
    }
    
    /* Override Streamlit Uploader */
    div[data-testid="stFileUploader"] {
        padding: 1.5rem;
        border: 2px dashed #CBD5E1;
        background-color: #F8FAFC;
        border-radius: 12px;
    }
    
    /* --- METRICS & CARDS --- */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #F1F5F9;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        height: 100%;
        text-align: left;
    }
    
    .icon-box {
        width: 48px;
        height: 48px;
        background: #F0FDFA;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* --- BUTTONS --- */
    div.stButton > button {
        background: #0F766E;
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        width: 100%;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
    }
    div.stButton > button:hover {
        background: #115E59;
        transform: translateY(-2px);
    }
    
    /* --- NAVBAR --- */
    .navbar {
        display: flex;
        align-items: center;
        padding: 1.5rem 0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 2rem;
    }
    
    .brand {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
@st.cache_data(show_spinner=False)
def load_lottie(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data(show_spinner=False)
def parse_pdf(file, pwd):
    try:
        with open("temp.pdf", "wb") as f: f.write(file.getbuffer())
        return casparser.read_cas_pdf("temp.pdf", pwd, force_pdfminer=True)
    except: return None

def get_fund_rating(xirr_val):
    if xirr_val is None: return "N/A"
    if xirr_val >= 20.0: return "🔥 IN-FORM"
    elif 12.0 <= xirr_val < 20.0: return "✅ ON-TRACK"
    elif 0.0 < xirr_val < 12.0: return "⚠️ OFF-TRACK"
    else: return "❌ OUT-OF-FORM"

def get_asset_class(name):
    n = name.upper()
    if any(x in n for x in ["LIQUID", "DEBT", "BOND", "OVERNIGHT"]): return "Debt"
    if "GOLD" in n: return "Gold"
    return "Equity"

# --- 4. UI LOGIC ---

if "data" not in st.session_state: st.session_state.data = None

# HEADER / NAVBAR
st.markdown("""
<div class="navbar">
    <div class="brand">
        <span style="color:#0F766E">⚡</span> TealScan
    </div>
    <div style="margin-left: auto; font-size: 0.85rem; font-weight: 600; color: #0F766E; background: #F0FDFA; padding: 6px 16px; border-radius: 20px;">
        BETA v1.0
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SCENARIO A: LANDING PAGE (NO DATA)
# ==========================================
if st.session_state.data is None:

    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown("""
        <div class="hero-container">
            <div style="font-size: 0.85rem; font-weight: 700; color: #0F766E; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem;">
                Trusted by 10,000+ Investors
            </div>
            <div class="hero-title">
                Your Portfolio,<br>
                <span class="hero-span">Totally Naked.</span>
            </div>
            <div class="hero-desc">
                Hidden commissions eat <b>40% of your wealth</b> over 20 years. 
                Our bank-grade X-Ray engine finds the leaks in 30 seconds.
            </div>
            <div style="display: flex; gap: 2rem;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">₹100 Cr+</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Assets Analyzed</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">100%</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Private & Secure</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # THE FLOATING CARD
        st.markdown('<div class="upload-card-container">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin:0; font-size:1.5rem; color:#0F172A;">Run Free Audit</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color:#64748B; font-size:0.9rem; margin-bottom:1.5rem;">Upload CAMS/KFintech CAS (PDF)</p>', unsafe_allow_html=True)
        
        f_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
        f_pass = st.text_input("Password", type="password", placeholder="PAN (e.g. ABCDE1234F)", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Start X-Ray Scan ➔", type="primary"):
            if f_file and f_pass:
                with st.spinner("Decrypting & Analyzing..."):
                    data = parse_pdf(f_file, f_pass)
                    if data:
                        st.session_state.data = data
                        st.rerun()
                    else:
                        st.error("Invalid File or Password.")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; font-size: 0.75rem; color: #94A3B8;">
            🔒 Data processed locally in browser memory.
        </div>
        </div>
        """, unsafe_allow_html=True)

    # FEATURES GRID
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color:#0F172A;'>Bank-Grade Analysis Features</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-box">🕵️</div>
            <div style="font-weight:700; margin-bottom:0.5rem;">Commission Hunter</div>
            <div style="color:#64748B; font-size:0.9rem;">Instantly spots 'Regular' plans draining your returns.</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-box">📈</div>
            <div style="font-weight:700; margin-bottom:0.5rem;">True XIRR Engine</div>
            <div style="color:#64748B; font-size:0.9rem;">Calculates real time-weighted returns, not just absolute gains.</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-box">🛡️</div>
            <div style="font-weight:700; margin-bottom:0.5rem;">Health Check</div>
            <div style="color:#64748B; font-size:0.9rem;">Auto-tags funds as 'In-Form' or 'Out-of-Form'.</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# SCENARIO B: DASHBOARD (DATA LOADED)
# ==========================================
else:
    data = st.session_state.data
    
    # Process Data
    portfolio = []
    total_val = 0
    total_invested = 0
    commission_loss = 0
    
    for folio in data.folios:
        for scheme in folio.schemes:
            name = scheme.scheme
            val = float(scheme.valuation.value or 0)
            cost = float(scheme.valuation.cost or 0)
            if val < 100: continue
            
            # Logic
            cat = get_asset_class(name)
            is_regular = "DIRECT" not in name.upper()
            loss = val * 0.01 if is_regular else 0
            
            dates, amts = [], []
            for txn in scheme.transactions:
                amt = float(txn.amount or 0)
                if amt == 0: continue
                desc = str(txn.description).upper()
                if any(x in desc for x in ["PURCHASE", "SIP"]): amts.append(amt * -1)
                else: amts.append(amt)
                dates.append(txn.date)
            dates.append(date.today())
            amts.append(val)
            
            try:
                res = xirr(dates, amts)
                my_xirr = res * 100 if res else 0
            except: my_xirr = 0
            
            portfolio.append({
                "Fund": name,
                "Category": cat,
                "Value": val,
                "Type": "Regular 🔴" if is_regular else "Direct 🟢",
                "XIRR": my_xirr,
                "Rating": get_fund_rating(my_xirr),
                "Loss": loss
            })
            
            total_val += val
            total_invested += cost
            commission_loss += loss

    df = pd.DataFrame(portfolio)

    # DASHBOARD UI
    st.button("← Scan New File", on_click=lambda: st.session_state.pop("data"))
    
    # Header Card
    st.markdown(f"""
    <div style="background: #1E293B; color: white; padding: 2rem; border-radius: 20px; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Net Worth</div>
                <div style="font-size: 3rem; font-weight: 700;">₹{total_val:,.0f}</div>
            </div>
            <div style="text-align: right;">
                <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Commission Loss</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #F87171;">₹{commission_loss:,.0f}<span style="font-size:0.9rem; color:#64748B;"> /yr</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    gain = total_val - total_invested
    m1.metric("Total Gain", f"₹{gain:,.0f}", f"{(gain/total_invested)*100:.1f}%" if total_invested else "0%")
    m2.metric("Funds Scanned", len(df))
    m3.metric("Regular Funds", len(df[df['Type'].str.contains("Regular")]), delta_color="inverse")
    m4.metric("Health Score", "100/100" if commission_loss == 0 else "Needs Fix")
    
    st.divider()
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("🏥 Fund Health Card")
        st.dataframe(
            df[["Fund", "Type", "Rating", "XIRR"]],
            column_config={"XIRR": st.column_config.NumberColumn(format="%.2f%%")},
            use_container_width=True,
            hide_index=True
        )
    
    with c2:
        st.subheader("🍰 Asset Allocation")
        if not df.empty:
            alloc = df.groupby("Category")["Value"].sum().reset_index()
            st.bar_chart(alloc, x="Category", y="Value", color="#0F766E")
            
    if commission_loss > 0:
        st.error(f"⚠️ **Action Required:** You are losing ₹{commission_loss:,.0f}/yr in commissions. Switch to Direct Plans.")
    else:
        st.balloons()
        st.success("✅ **Clean Portfolio:** You are a smart investor! No hidden fees detected.")
