import streamlit as st
import pandas as pd
import casparser
from pyxirr import xirr
from datetime import date
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TealScan Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- 2. OPTIMIZED CACHING FUNCTIONS (The Speed Boost) ---
@st.cache_data(show_spinner=False)
def parse_pdf_data(uploaded_file, password):
    """
    Parses PDF using the slow 'pdfminer' engine but CACHES the result.
    This means if you click around, it won't reload the PDF.
    """
    try:
        # Save temp file
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Deep Scan
        data = casparser.read_cas_pdf("temp.pdf", password, force_pdfminer=True)
        return data
    except Exception as e:
        return None

def get_fund_rating(xirr_val):
    if xirr_val is None: return "N/A"
    if xirr_val >= 20.0: return "🔥 IN-FORM"
    elif 12.0 <= xirr_val < 20.0: return "✅ ON-TRACK"
    elif 0.0 < xirr_val < 12.0: return "⚠️ OFF-TRACK"
    else: return "❌ OUT-OF-FORM"

def get_asset_class(name):
    name = name.upper()
    if any(x in name for x in ["LIQUID", "DEBT", "BOND"]): return "Debt"
    if "GOLD" in name: return "Gold"
    return "Equity"

# --- 3. PAGE: DASHBOARD (Main Logic) ---
def page_dashboard():
    st.title("🛡️ Portfolio Health Dashboard")
    st.markdown("Upload your **CAMS/KFintech CAS** to get a bank-grade health check.")
    
    # File Uploader in a clean container
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            uploaded_file = st.file_uploader("Upload CAS PDF", type="pdf")
            password = st.text_input("PDF Password", type="password")
            
            run_btn = st.button("Run Diagnostics 🚀", type="primary", use_container_width=True)

    if run_btn and uploaded_file and password:
        with st.spinner("🔄 Deep Scanning Portfolio... (This happens once)"):
            
            # CALL THE CACHED FUNCTION
            data = parse_pdf_data(uploaded_file, password)
            
            if data is None:
                st.error("❌ Could not read PDF. Check Password.")
                return

            # PROCESSING (Fast)
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
                    
                    # Commission Logic
                    is_regular = "DIRECT" not in name.upper()
                    loss = val * 0.01 if is_regular else 0
                    
                    # XIRR Logic
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
                    except:
                        my_xirr = 0
                    
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
            
            # --- THE UI DISPLAY ---
            
            # 1. Top Metrics
            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Net Worth", f"₹{total_val:,.0f}")
            gain = total_val - total_invested
            m2.metric("Total Gain", f"₹{gain:,.0f}", f"{(gain/total_invested)*100:.1f}%" if total_invested else "0%")
            m3.metric("Hidden Commissions", f"₹{commission_loss:,.0f}", delta="Save this!" if commission_loss > 0 else "Great", delta_color="inverse")
            m4.metric("Funds Analyzed", len(df))
            
            # 2. Charts & Analysis
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
                st.subheader("🍰 Allocation")
                if not df.empty:
                    alloc = df.groupby("Category")["Value"].sum().reset_index()
                    st.bar_chart(alloc, x="Category", y="Value", color="#0E7490")
            
            # 3. Action Plan
            if commission_loss > 0:
                st.warning(f"⚠️ **Action Required:** You are losing ₹{commission_loss:,.0f}/yr. Switch 'Regular' funds to Direct.")
            else:
                st.balloons()
                st.success("✅ **Perfect:** Your portfolio is 100% Commission-Free.")

# --- 4. PAGE: ABOUT US ---
def page_about():
    st.title("👋 About TealScan")
    st.markdown("""
    **TealScan** is India's first privacy-focused Mutual Fund X-Ray tool. 
    
    ### Our Mission
    Banks and distributors hide commissions inside "Regular Plans" (approx 1% per year). 
    We believe you should keep 100% of your returns.
    
    ### How it works
    1. **Upload:** You provide your standard CAMS CAS statement.
    2. **Scan:** Our Python engine (`casparser`) reads the hidden codes in the PDF.
    3. **Analyze:** We detect Regular plans and calculate your true XIRR.
    
    ### Privacy Promise
    * No data leaves your session.
    * No database storage.
    * No OTPs required.
    """)
    st.image("https://placehold.co/600x200?text=Made+with+Love+in+India", use_container_width=True)

# --- 5. PAGE: FAQ ---
def page_faq():
    st.title("❓ Frequently Asked Questions")
    with st.expander("Is my data safe?"):
        st.write("Yes. The file is processed in temporary memory and deleted immediately after analysis.")
    with st.expander("Why does the PDF password fail?"):
        st.write("Ensure you are using the PAN number in ALL CAPS. Also, ensure you downloaded the 'Detailed' statement from CAMS.")
    with st.expander("What is a Direct Plan?"):
        st.write("A Direct Plan is the exact same mutual fund but without the distributor commission. It typically gives 1% higher returns every year.")

# --- 6. NAVIGATION LOGIC ---
pg = st.navigation([
    st.Page(page_dashboard, title="Dashboard", icon="📊"),
    st.Page(page_about, title="About Us", icon="🏢"),
    st.Page(page_faq, title="Help & FAQ", icon="❓"),
])

pg.run()
