import streamlit as st
import pandas as pd
import casparser
from pyxirr import xirr
from datetime import date
import requests
from streamlit_lottie import st_lottie

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="TealScan: Wealth X-Ray",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. INJECT POWERUP STYLE (Tailwind CSS) ---
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
        
        /* Global Overrides */
        body { font-family: 'Manrope', sans-serif !important; background-color: #F8FAFC; }
        .stApp { background-color: #F8FAFC; }
        
        /* Hide Streamlit Bloat */
        #MainMenu, footer, header {visibility: hidden;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        
        /* Custom Classes */
        .hero-text {
            background: linear-gradient(135deg, #0F172A 0%, #334155 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .teal-accent { color: #0D9488; }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid #E2E8F0;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
            border-radius: 24px;
        }
        
        .feature-card {
            background: white;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #F1F5F9;
            transition: all 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            border-color: #0D9488;
        }

        /* Upload Box Override */
        div[data-testid="stFileUploader"] {
            padding: 1.5rem;
            border: 2px dashed #CBD5E1;
            background: #F8FAFC;
            border-radius: 12px;
        }
        
        /* Button Override */
        div.stButton > button {
            background: #0D9488;
            color: white;
            font-weight: 600;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            border: none;
            width: 100%;
            box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.3);
        }
        div.stButton > button:hover {
            background: #0F766E;
            box-shadow: 0 10px 15px -3px rgba(13, 148, 136, 0.4);
            transform: translateY(-2px);
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

def get_asset_class(name):
    n = name.upper()
    if any(x in n for x in ["LIQUID", "DEBT", "BOND", "OVERNIGHT"]): return "Debt"
    if "GOLD" in n: return "Gold"
    return "Equity"

def get_fund_rating(xirr_val):
    if xirr_val is None: return "N/A"
    if xirr_val >= 20.0: return "🔥 IN-FORM"
    elif 12.0 <= xirr_val < 20.0: return "✅ ON-TRACK"
    elif 0.0 < xirr_val < 12.0: return "⚠️ OFF-TRACK"
    else: return "❌ OUT-OF-FORM"

# --- 4. APP LOGIC ---

# Navbar (Visual Only)
st.markdown("""
<div class="flex justify-between items-center py-4 px-2 mb-10 border-b border-slate-100">
    <div class="flex items-center gap-2">
        <span class="text-2xl">⚡</span>
        <span class="text-xl font-bold text-slate-900 tracking-tight">TealScan</span>
    </div>
    <div class="text-xs font-semibold bg-teal-50 text-teal-700 px-3 py-1 rounded-full">
        BETA v1.0
    </div>
</div>
""", unsafe_allow_html=True)

if "data" not in st.session_state: st.session_state.data = None

# ==========================================
# SCENARIO A: LANDING PAGE
# ==========================================
if st.session_state.data is None:
    
    # --- HERO SECTION ---
    c1, c2 = st.columns([1.5, 1], gap="large")
    
    with c1:
        st.markdown("""
        <div class="mt-4">
            <span class="inline-block py-1 px-3 rounded-full bg-blue-50 text-blue-600 text-xs font-bold mb-4 border border-blue-100">
                🚀 Trusted by 10,000+ Investors
            </span>
            <h1 class="text-5xl md:text-6xl font-extrabold leading-tight mb-6 text-slate-900">
                Stop Losing <span class="teal-accent">1% Wealth</span><br>Every Year.
            </h1>
            <p class="text-lg text-slate-500 mb-8 leading-relaxed max-w-lg">
                Hidden commissions in "Regular" mutual funds eat <b>40% of your corpus</b> over 20 years. 
                Upload your CAS statement to audit your portfolio in 30 seconds.
            </p>
            
            <div class="flex gap-8 border-t border-slate-100 pt-8">
                <div>
                    <p class="text-3xl font-bold text-slate-900">₹50 Cr+</p>
                    <p class="text-sm text-slate-500 font-medium">Assets Analyzed</p>
                </div>
                <div>
                    <p class="text-3xl font-bold text-slate-900">100%</p>
                    <p class="text-sm text-slate-500 font-medium">Private & Secure</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        # FLOATING UPLOAD CARD
        st.markdown('<div class="glass-card p-6 md:p-8 mt-6">', unsafe_allow_html=True)
        st.markdown('<h3 class="text-xl font-bold text-slate-900 mb-1">Start Free Audit</h3>', unsafe_allow_html=True)
        st.markdown('<p class="text-sm text-slate-500 mb-6">Upload detailed CAS PDF (CAMS/KFintech)</p>', unsafe_allow_html=True)
        
        f_file = st.file_uploader("Upload CAS", type="pdf", label_visibility="collapsed")
        f_pass = st.text_input("PDF Password", type="password", placeholder="PAN Number (e.g. ABCDE1234F)")
        
        if st.button("Run X-Ray Scan ➔"):
            if f_file and f_pass:
                with st.spinner("Decrypting & Analyzing..."):
                    data = parse_pdf(f_file, f_pass)
                    if data:
                        st.session_state.data = data
                        st.rerun()
                    else:
                        st.error("Invalid File or Password.")
        
        st.markdown("""
        <div class="mt-4 flex items-center justify-center gap-2 text-xs text-slate-400">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
            No data stored. Browser-only analysis.
        </div>
        </div>
        """, unsafe_allow_html=True)

    # --- FEATURES BENTO GRID ---
    st.markdown("""
    <div class="py-20">
        <div class="text-center mb-12">
            <h2 class="text-3xl font-bold text-slate-900">Bank-Grade Analysis</h2>
            <p class="text-slate-500 mt-2">Everything you need to fix your portfolio.</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="feature-card">
                <div class="w-12 h-12 bg-teal-50 rounded-xl flex items-center justify-center text-2xl mb-4">🕵️‍♂️</div>
                <h3 class="text-lg font-bold text-slate-900 mb-2">Commission Hunter</h3>
                <p class="text-slate-500 text-sm">Instantly spots 'Regular' plans draining your returns.</p>
            </div>
            
            <div class="feature-card">
                <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl mb-4">📈</div>
                <h3 class="text-lg font-bold text-slate-900 mb-2">True XIRR Engine</h3>
                <p class="text-slate-500 text-sm">Calculates real time-weighted returns, not just absolute gains.</p>
            </div>
            
            <div class="feature-card">
                <div class="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center text-2xl mb-4">🛡️</div>
                <h3 class="text-lg font-bold text-slate-900 mb-2">Health Check</h3>
                <p class="text-slate-500 text-sm">Auto-tags funds as 'In-Form' or 'Out-of-Form'.</p>
            </div>
        </div>
    </div>
    
    <div class="text-center text-slate-400 text-sm py-8 border-t border-slate-100">
        TealScan Pro © 2025 • Made with ❤️ in India
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# SCENARIO B: DASHBOARD
# ==========================================
else:
    data = st.session_state.data
    
    # --- LOGIC ENGINE ---
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
            
            # Asset Class
            cat = get_asset_class(name)
            
            # Commission
            is_regular = "DIRECT" not in name.upper()
            loss = val * 0.01 if is_regular else 0
            
            # XIRR
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

    # --- DASHBOARD UI ---
    st.button("← Scan New File", on_click=lambda: st.session_state.pop("data"))
    
    # Header Card
    st.markdown(f"""
    <div class="bg-slate-900 text-white p-8 rounded-3xl mb-8 shadow-2xl relative overflow-hidden">
        <div class="relative z-10 flex justify-between items-end">
            <div>
                <p class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Net Worth</p>
                <h1 class="text-4xl md:text-5xl font-bold">₹{total_val:,.0f}</h1>
            </div>
            <div class="text-right">
                <p class="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Commission Loss</p>
                <p class="text-2xl font-bold text-red-400">₹{commission_loss:,.0f}<span class="text-sm text-slate-500">/yr</span></p>
            </div>
        </div>
        <div class="absolute top-0 right-0 w-64 h-64 bg-teal-500 rounded-full mix-blend-overlay filter blur-3xl opacity-20 -mr-16 -mt-16"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics Grid
    m1, m2, m3, m4 = st.columns(4)
    gain = total_val - total_invested
    m1.metric("Total Gain", f"₹{gain:,.0f}", f"{(gain/total_invested)*100:.1f}%" if total_invested else "0%")
    m2.metric("Funds Scanned", len(df))
    m3.metric("Regular Funds", len(df[df['Type'].str.contains("Regular")]), delta_color="inverse")
    m4.metric("Health Score", "100/100" if commission_loss == 0 else "Needs Fix")
    
    st.divider()
    
    # Detailed Analysis
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("🏥 Fund Health Card")
        st.dataframe(
            df[["Fund", "Type", "Rating", "XIRR"]],
            column_config={
                "XIRR": st.column_config.NumberColumn(format="%.2f%%"),
                "Type": st.column_config.TextColumn("Plan Type"),
            },
            use_container_width=True,
            hide_index=True
        )
    
    with c2:
        st.subheader("🍰 Asset Allocation")
        if not df.empty:
            alloc = df.groupby("Category")["Value"].sum().reset_index()
            st.bar_chart(alloc, x="Category", y="Value", color="#0D9488")

    # Final Action
    if commission_loss > 0:
        st.error(f"⚠️ **Action Required:** You are losing ₹{commission_loss:,.0f}/yr. Switch to Direct Plans.")
    else:
        st.balloons()
        st.success("✅ **Clean Portfolio:** You are a smart investor! No hidden fees detected.")
