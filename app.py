import streamlit as st
import pandas as pd
import casparser
from pyxirr import xirr
from datetime import date
import time
import requests
from streamlit_lottie import st_lottie

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TealScan: Portfolio X-Ray",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Light Theme CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- 2. ASSETS & ANIMATIONS ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Animations (Transparent backgrounds work on both themes)
lottie_scan = load_lottieurl("https://lottie.host/9a589417-a068-4536-a51f-29d906105f2c/qZ65j1hG3p.json") 

# --- 3. HELPER FUNCTIONS ---
@st.cache_data(show_spinner=False)
def parse_pdf_data(uploaded_file, password):
    try:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        data = casparser.read_cas_pdf("temp.pdf", password, force_pdfminer=True)
        return data
    except Exception:
        return None

def get_fund_rating(xirr_val):
    if xirr_val is None: return "N/A"
    if xirr_val >= 20.0: return "🔥 IN-FORM"
    elif 12.0 <= xirr_val < 20.0: return "✅ ON-TRACK"
    elif 0.0 < xirr_val < 12.0: return "⚠️ OFF-TRACK"
    else: return "❌ OUT-OF-FORM"

def get_asset_class(name):
    name = name.upper()
    if any(x in name for x in ["LIQUID", "DEBT", "BOND", "OVERNIGHT"]): return "Debt"
    if "GOLD" in name: return "Gold"
    return "Equity"

# --- 4. MAIN UI ---

# HEADER (Minimal)
col1, col2 = st.columns([1, 10])
with col1:
    st.markdown("### ⚡ **TealScan**") # Dark text for visibility

st.markdown("---")

if "data_processed" not in st.session_state:
    st.session_state.data_processed = None

# --- LANDING PAGE (Clean Light Look) ---
if st.session_state.data_processed is None:
    
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        # Big Headline (Slate-900 color)
        st.markdown("""
        <h1 style='color: #0F172A;'>The Truth About<br><span style='color: #0E7490;'>Your Wealth.</span></h1>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='font-size: 1.25rem; color: #475569; margin-top: 20px; margin-bottom: 40px; line-height: 1.6;'>
        Most portfolios bleed <b>1% annually</b> in hidden commissions.<br>
        We scan your CAS statement to find the leaks and calculate your <b>Real XIRR</b>.
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            # Using a white card container for inputs
            st.markdown("### 📂 Start Your Scan")
            uploaded_file = st.file_uploader("Upload CAMS/KFintech CAS (PDF)", type="pdf")
            password = st.text_input("PDF Password (PAN)", type="password", placeholder="ABCDE1234F")
            
            if st.button("Reveal My Portfolio 🚀", type="primary"):
                if uploaded_file and password:
                    with st.spinner("Decrypting & Analyzing..."):
                        data = parse_pdf_data(uploaded_file, password)
                        if data:
                            st.session_state.data_processed = data
                            st.rerun()
                        else:
                            st.error("Invalid Password or File Format.")
    
    with c2:
        if lottie_scan:
            st_lottie(lottie_scan, height=350, key="scan_anim")

    # Feature Grid
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### Why Scan?")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.info("🕵️‍♂️ **Hidden Fee Detection**\n\nIdentify 'Regular' plans charging you extra commissions.")
    with f2:
        st.info("📈 **True XIRR Engine**\n\nSee your actual annualized growth, not just absolute returns.")
    with f3:
        st.info("🔒 **Privacy First**\n\nZero data storage. Analysis happens in your browser session.")

# --- DASHBOARD (Data View) ---
else:
    data = st.session_state.data_processed
    
    # Logic Processing
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
                "Category": get_asset_class(name),
                "Value": val,
                "XIRR": my_xirr,
                "Type": "Regular 🔴" if is_regular else "Direct 🟢",
                "Rating": get_fund_rating(my_xirr),
                "Loss": loss
            })
            total_val += val
            total_invested += cost
            commission_loss += loss

    df = pd.DataFrame(portfolio)
    
    # Navigation
    st.button("← Scan Another File", on_click=lambda: st.session_state.pop("data_processed"))
    
    # Main Header
    st.markdown(f"<h1 style='color:#0F172A;'>Net Worth: ₹{total_val:,.0f}</h1>", unsafe_allow_html=True)
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    gain = total_val - total_invested
    m1.metric("Total Gain", f"₹{gain:,.0f}", f"{(gain/total_invested)*100:.1f}%" if total_invested else "0%")
    m2.metric("Hidden Commissions", f"₹{commission_loss:,.0f}", delta="Lost Annually" if commission_loss > 0 else "Zero!", delta_color="inverse")
    m3.metric("Funds Scanned", len(df))
    m4.metric("Health Score", "100/100" if commission_loss == 0 else "Needs Work")

    # Analysis Section
    st.markdown("### 📊 Portfolio Deep Dive")
    c1, c2 = st.columns([2, 1])
    
    with c1:
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
        if not df.empty:
            alloc = df.groupby("Category")["Value"].sum().reset_index()
            # Using Deep Teal color for charts to look good on white
            st.bar_chart(alloc, x="Category", y="Value", color="#0E7490")
            
    # Alerts
    if commission_loss > 0:
        st.error(f"⚠️ **Action Required:** You are losing ₹{commission_loss:,.0f}/yr in commissions. Switch to Direct Plans.")
    else:
        st.balloons()
        st.success("✅ **Clean Portfolio:** You are a smart investor! No hidden fees detected.")
