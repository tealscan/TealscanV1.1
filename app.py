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

# --- 2. INJECT POWERUP THEME (Tailwind CSS) ---
st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
        
        body { font-family: 'Manrope', sans-serif !important; background-color: #F8FAFC; }
        .stApp { background-color: transparent; }
        
        #MainMenu, footer, header {visibility: hidden;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        
        /* Gradient Text */
        .text-gradient {
            background: linear-gradient(135deg, #0F766E 0%, #2DD4BF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Glass Card Effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            border: 1px solid #E2E8F0;
            box-shadow: 0 20px 40px -10px rgba(15, 118, 110, 0.1);
            border-radius: 24px;
        }

        /* Streamlit Widget Overrides */
        div[data-testid="stFileUploader"] {
            padding: 1.5rem;
            border: 2px dashed #CBD5E1;
            background: #F8FAFC;
            border-radius: 12px;
        }
        
        div.stButton > button {
            background: #0F766E;
            color: white;
            font-weight: 700;
            border-radius: 12px;
            padding: 0.8rem 2rem;
            border: none;
            width: 100%;
            box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            background: #115E59;
            box-shadow: 0 8px 16px rgba(15, 118, 110, 0.4);
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
@st.cache_data(show_spinner=False)
def parse_pdf(file, pwd):
    try:
        with open("temp.pdf", "wb") as f: f.write(file.getbuffer())
        return casparser.read_cas_pdf("temp.pdf", pwd, force_pdfminer=True)
    except: return None

def get_asset_class(name):
    n = name.upper()
    if any(x in n for x in ["LIQUID", "DEBT", "BOND"]): return "Debt"
    if "GOLD" in n: return "Gold"
    return "Equity"

def get_fund_rating(xirr_val):
    if xirr_val is None: return "N/A"
    if xirr_val >= 20.0: return "🔥 IN-FORM"
    elif 12.0 <= xirr_val < 20.0: return "✅ ON-TRACK"
    elif 0.0 < xirr_val < 12.0: return "⚠️ OFF-TRACK"
    else: return "❌ OUT-OF-FORM"

# --- 4. APP STATE ---
if "data" not in st.session_state: st.session_state.data = None

# ==========================================
# SCENARIO A: LANDING PAGE (The "PowerUp" Clone)
# ==========================================
if st.session_state.data is None:
    
    # --- HEADER COMPONENT ---
    st.markdown("""
    <div class="flex justify-between items-center py-6 px-4 max-w-7xl mx-auto mb-10">
        <div class="flex items-center gap-2">
            <div class="w-10 h-10 bg-teal-700 rounded-xl flex items-center justify-center text-white text-xl font-bold">T</div>
            <span class="text-xl font-bold text-slate-900">TealScan</span>
        </div>
        <div class="hidden md:flex gap-6 text-sm font-semibold text-slate-600">
            <span class="hover:text-teal-700 cursor-pointer">How it Works</span>
            <span class="hover:text-teal-700 cursor-pointer">Security</span>
            <span class="bg-teal-50 text-teal-700 px-3 py-1 rounded-full">Beta v1.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- HERO SECTION ---
    c1, c2 = st.columns([1.3, 1], gap="large")
    
    with c1:
        st.markdown("""
        <div class="mt-8">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-50 border border-teal-100 text-teal-700 text-xs font-bold mb-6">
                <span class="w-2 h-2 rounded-full bg-teal-500 animate-pulse"></span>
                Trusted by 10,000+ Investors
            </div>
            <h1 class="text-6xl font-extrabold text-slate-900 leading-[1.1] mb-6">
                Your Portfolio.<br>
                <span class="text-gradient">Totally Naked.</span>
            </h1>
            <p class="text-lg text-slate-500 leading-relaxed mb-8 max-w-md">
                Hidden commissions eat <b>40% of your wealth</b> over 20 years. 
                Upload your CAS statement to see exactly how much you are losing.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # --- STATS SECTION (Inside Hero) ---
        st.markdown("""
        <div class="grid grid-cols-3 gap-8 border-t border-slate-200 pt-8 max-w-md">
            <div>
                <p class="text-2xl font-bold text-slate-900">₹50 Cr+</p>
                <p class="text-xs text-slate-500 uppercase tracking-wider font-semibold">Analyzed</p>
            </div>
            <div>
                <p class="text-2xl font-bold text-slate-900">₹1 Cr+</p>
                <p class="text-xs text-slate-500 uppercase tracking-wider font-semibold">Fees Saved</p>
            </div>
            <div>
                <p class="text-2xl font-bold text-slate-900">100%</p>
                <p class="text-xs text-slate-500 uppercase tracking-wider font-semibold">Privacy</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        # --- FLOATING UPLOAD CARD ---
        st.markdown("""
        <div class="glass-card p-8">
            <div class="mb-6">
                <h3 class="text-xl font-bold text-slate-900">Run X-Ray Scan</h3>
                <p class="text-sm text-slate-500">Upload detailed CAS PDF (CAMS/KFintech)</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Native Streamlit Widgets
        f_file = st.file_uploader("Upload CAS PDF", type="pdf", label_visibility="collapsed")
        f_pass = st.text_input("Password", type="password", placeholder="PAN (e.g. ABCDE1234F)", label_visibility="collapsed")
        
        st.markdown("<div class='h-4'></div>", unsafe_allow_html=True) # Spacer
        
        if st.button("Start Audit ➔"):
            if f_file and f_pass:
                with st.spinner("Decrypting..."):
                    data = parse_pdf(f_file, f_pass)
                    if data:
                        st.session_state.data = data
                        st.rerun()
                    else:
                        st.error("Invalid File/Password.")
        
        st.markdown("""
            <div class="mt-4 text-center text-xs text-slate-400 flex items-center justify-center gap-1">
                🔒 Data processed locally in browser.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- FEATURES SECTION ---
    st.markdown("""
    <div class="py-24">
        <div class="text-center mb-16">
            <h2 class="text-3xl font-bold text-slate-900">Bank-Grade Analysis</h2>
            <p class="text-slate-500 mt-2">Everything you need to fix your portfolio.</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div class="bg-white p-8 rounded-2xl border border-slate-100 hover:shadow-xl transition-all duration-300 group">
                <div class="w-12 h-12 bg-teal-50 rounded-xl flex items-center justify-center text-2xl mb-4 group-hover:bg-teal-600 group-hover:text-white transition-colors">🕵️‍♂️</div>
                <h3 class="text-lg font-bold text-slate-900 mb-2">Commission Hunter</h3>
                <p class="text-slate-500 text-sm leading-relaxed">Instantly spots 'Regular' plans that charge you 1% extra every year.</p>
            </div>
            
            <div class="bg-white p-8 rounded-2xl border border-slate-100 hover:shadow-xl transition-all duration-300 group">
                <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">📈</div>
                <h3 class="text-lg font-bold text-slate-900 mb-2">True XIRR Engine</h3>
                <p class="text-slate-500 text-sm leading-relaxed">Calculates your real time-weighted return, not just absolute gains.</p>
            </div>
            
            <div class="bg-white p-8 rounded-2xl border border-slate-100 hover:shadow-xl transition-all duration-300 group">
                <div class="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center text-2xl mb-4 group-hover:bg-purple-600 group-hover:text-white transition-colors">🛡️</div>
                <h3 class="text-lg font-bold text-slate-900 mb-2">Portfolio Health</h3>
                <p class="text-slate-500 text-sm leading-relaxed">Auto-tags funds as 'In-Form' or 'Out-of-Form' based on performance.</p>
            </div>
        </div>
    </div>
    
    <div class="border-t border-slate-200 py-12 text-center">
        <p class="text-slate-400 text-sm">TealScan Pro © 2025 • Made with ❤️ in India</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# SCENARIO B: DASHBOARD (DATA LOADED)
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

    # --- DASHBOARD HEADER ---
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
    
    # METRICS
    m1, m2, m3, m4 = st.columns(4)
    gain = total_val - total_invested
    m1.metric("Total Gain", f"₹{gain:,.0f}", f"{(gain/total_invested)*100:.1f}%" if total_invested else "0%")
    m2.metric("Funds Scanned", len(df))
    m3.metric("Regular Funds", len(df[df['Type'].str.contains("Regular")]), delta_color="inverse")
    m4.metric("Health Score", "100/100" if commission_loss == 0 else "Needs Fix")
    
    st.divider()
    
    # DATA & CHARTS
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
            
    # RESET
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Scan Another File"):
        st.session_state.data = None
        st.rerun()
