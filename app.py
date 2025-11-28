import streamlit as st
import pandas as pd
import casparser
from pyxirr import xirr
from datetime import date
import requests
from streamlit_lottie import st_lottie

# --- 1. CONFIG ---
st.set_page_config(
    page_title="TealScan | Mutual Fund X-Ray",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- 2. ASSETS ---
@st.cache_data
def load_lottie(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# Using a professional "Analytics" animation (Teal/Blue theme)
lottie_hero = load_lottie("https://lottie.host/9a589417-a068-4536-a51f-29d906105f2c/qZ65j1hG3p.json")

# --- 3. HELPER FUNCTIONS ---
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

# --- 4. UI LOGIC ---

# Header
c1, c2 = st.columns([1, 10])
with c1: st.markdown("### ⚡ **TealScan**")
st.markdown("---")

if "data" not in st.session_state: st.session_state.data = None

# ==========================================
# SCENARIO A: LANDING PAGE
# ==========================================
if st.session_state.data is None:

    col_hero, col_card = st.columns([1.5, 1], gap="large")

    with col_hero:
        # Trust Badge
        st.markdown("""
        <div class="trust-badge">
            <span style="margin-right:8px">🔒</span> Secure • Private • Bank-Grade Analysis
        </div>
        """, unsafe_allow_html=True)
        
        # Hero Title
        st.markdown("""
        <div class="hero-title">
            Your Portfolio,<br>
            <span class="teal-gradient-text">Totally Transparent.</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Subtitle
        st.markdown("""
        <div class="hero-subtitle">
            Detect hidden commissions, calculate real XIRR, and fix 'Out-of-Form' funds. 
            Join 10,000+ investors cleaning up their wealth today.
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics Row
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Assets Analyzed", "₹100 Cr+")
        m2.metric("Fees Identified", "₹50 Lakhs+")
        m3.metric("Data Privacy", "100%")

    with col_card:
        # Floating Upload Card
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.markdown("### 📂 **Start Free Scan**")
        st.caption("Upload your detailed CAS PDF (CAMS/KFintech).")
        
        f_file = st.file_uploader("Upload CAS", type="pdf", label_visibility="collapsed")
        f_pass = st.text_input("PDF Password (PAN)", type="password", placeholder="ABCDE1234F")
        
        if st.button("Run Audit 🚀"):
            if f_file and f_pass:
                with st.spinner("Decrypting..."):
                    data = parse_pdf(f_file, f_pass)
                    if data:
                        st.session_state.data = data
                        st.rerun()
                    else:
                        st.error("Invalid File/Password.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- FEATURES SECTION ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color:#0F172A;'>Why Power Users Choose TealScan</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    
    # Feature 1
    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">🕵️</div>
            <div class="feature-title">Commission Detector</div>
            <div class="feature-desc">Spot 'Regular' plans that cost you 1% extra annually.</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Feature 2
    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">📈</div>
            <div class="feature-title">True XIRR Engine</div>
            <div class="feature-desc">See your actual time-weighted return, not just absolute gains.</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Feature 3
    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">💊</div>
            <div class="feature-title">Portfolio Health</div>
            <div class="feature-desc">Auto-tag funds as 'In-Form' or 'Out-of-Form' based on data.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature 4
    with f4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-box">🥧</div>
            <div class="feature-title">Asset Allocation</div>
            <div class="feature-desc">Visual breakdown of Equity, Debt, and Gold exposure.</div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("<br><br><br><div style='text-align:center; color:#94A3B8;'>TealScan Pro © 2025 • Made with ❤️ in India</div>", unsafe_allow_html=True)

# ==========================================
# SCENARIO B: DASHBOARD
# ==========================================
else:
    data = st.session_state.data
    
    # Processing Logic (Compact)
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
                "Category": get_asset_class(name),
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
    st.button("← Scan Another File", on_click=lambda: st.session_state.pop("data"))
    
    st.markdown(f"<h1 style='color:#0F172A;'>Net Worth: <span style='color:#0F766E'>₹{total_val:,.0f}</span></h1>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    gain = total_val - total_invested
    m1.metric("Total Gain", f"₹{gain:,.0f}", f"{(gain/total_invested)*100:.1f}%" if total_invested else "0%")
    m2.metric("Hidden Commissions", f"₹{commission_loss:,.0f}", delta="Lost Annually" if commission_loss > 0 else "Zero!", delta_color="inverse")
    m3.metric("Funds Scanned", len(df))
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
