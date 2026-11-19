import streamlit as st
import pandas as pd
import datetime
import urllib.parse

st.set_page_config(page_title="நம்ம Smart Business Billing", page_icon="🏪")

# 1. பொதுவான மெமரி
@st.cache_resource
def get_business_db():
    return {
        "bills": [],
        "catalog": {
            "🛒 மளிகை & சூப்பர் மார்க்கெட்": {
                "பொன்னி அரிசி (1 Kg)": 65,
                "துவரம் பருப்பு (1 Kg)": 140,
                "சமையல் எண்ணெய் (1 Litre)": 135,
                "சர்க்கரை (1 Kg)": 45
            },
            "👕 துணிக்கடை (Textile)": {
                "காட்டன் சட்டை (Cotton Shirt)": 650,
                "ஜீன்ஸ் பேண்ட் (Jeans)": 950,
                "பட்டுப் புடவை (Silk Saree)": 2500,
                "டி-ஷர்ட் (T-Shirt)": 350
            },
            "🍽️ ஹோட்டல் (Hotel / Restaurant)": {
                "மசாலா தோசை (Masala Dosa)": 70,
                "இட்லி செட் (2 Nos)": 30,
                "சிக்கன் பிரியாணி (Chicken Biryani)": 180,
                "பில்டர் காபி (Filter Coffee)": 25
            }
        }
    }

db = get_business_db()

# 2. கடை பெயர் மற்றும் வகை தேர்வு (Sidebar / Top Setup)
st.title("🏪 நம்ம Smart Business Billing")
col_top1, col_top2 = st.columns(2)
with col_top1:
    shop_name = st.text_input("உங்கள் கடை பெயர்:", "ஸ்ரீ முருகன் ஸ்டோர்ஸ்")
with col_top2:
    shop_type = st.selectbox("கடை வகையைத் தேர்ந்தெடுக்கவும்:", list(db["catalog"].keys()))

st.caption(f"✨ **{shop_name}** ({shop_type}) — பேப்பர் இல்லாத ஸ்மார்ட் வாட்ஸ்அப் பில்லிங்!")

tab1, tab2, tab3 = st.tabs(["🧾 ஸ்மார்ட் பில் (New Bill)", "➕ பொருள் / விலை சேர்க்க", "📊 இன்றைய கணக்கு (Report)"])

# --- டேப் 1: கடை வகைக்கேற்ப மாறும் வித்தியாசமான பில்லிங் ---
with tab1:
    c_name = st.text_input("வாடிக்கையாளர் பெயர்:", "Customer")
    c_phone = st.text_input("வாட்ஸ்அப் எண் (பில் அனுப்ப - Optional):", "")
    
    items_dict = db["catalog"][shop_type]
    selected_item = st.selectbox("பொருள் / உணவு / துணி:", list(items_dict.keys()))
    base_price = items_dict[selected_item]
    
    extra_note = ""
    discount_pct = 0
    
    # கடை வகைக்கேற்ப சிறப்பு வசதிகள்!
    if "மளிகை" in shop_type:
        qty = st.number_input("அளவு (Kg / Packet):", min_value=0.25, value=1.0, step=0.25)
        extra_note = f"அளவு: {qty} Kg/Unit"
    elif "துணிக்கடை" in shop_type:
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            size = st.selectbox("அளவு (Size):", ["S", "M", "L", "XL", "XXL", "Free Size"])
        with col_t2:
            qty = st.number_input("எண்ணிக்கை:", min_value=1, value=1)
        with col_t3:
            discount_pct = st.number_input("தள்ளுபடி (%):", min_value=0, max_value=80, value=0)
        extra_note = f"Size: {size} | தள்ளுபடி: {discount_pct}%"
    else: # ஹோட்டல்
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            table_no = st.selectbox("டேபிள் / வகை:", ["Table 1", "Table 2", "Table 3", "பார்சல் (Parcel)"])
        with col_h2:
            qty = st.number_input("எண்ணிக்கை:", min_value=1, value=1)
        extra_note = f"{table_no}"

    # மொத்தத் தொகை கணக்கீடு
    gross_total = base_price * qty
    discount_amt = (gross_total * discount_pct) / 100
    final_total = round(gross_total - discount_amt, 2)
    
    st.markdown(f"### 💰 மொத்தத் தொகை: **₹{final_total}**")
    if discount_pct > 0:
        st.caption(f"(அசல் விலை: ₹{gross_total} | தள்ளுபடி: -₹{discount_amt})")
        
    if st.button("✅ பில் உருவாக்கு (Generate Bill)", type="primary", use_container_width=True):
        now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        db["bills"].append({
            "நேரம்": now,
            "கடை வகை": shop_type,
            "வாடிக்கையாளர்": c_name,
            "பொருள்": f"{selected_item} ({extra_note})",
            "தொகை (₹)": final_total
        })
        
        st.success(f"🎉 பில் பதிவாகிவிட்டது! மொத்தம்: **₹{final_total}**")
        
        # வாட்ஸ்அப் பில் லிங்க் உருவாக்கம்!
        bill_msg = (
            f"🧾 *{shop_name} - E-Bill*\n"
            f"📅 தேதி: {now}\n"
            f"👤 வாடிக்கையாளர்: {c_name}\n"
            f"🛍️ பொருள்: {selected_item} ({extra_note})\n"
            f"💰 *மொத்தத் தொகை: ₹{final_total}*\n"
            f"நன்றி! மீண்டும் வருக 🙏"
        )
        encoded_msg = urllib.parse.quote(bill_msg)
        wa_link = f"https://wa.me{c_phone.strip()}?text={encoded_msg}" if c_phone.strip() else f"https://wa.me{encoded_msg}"
        
        st.markdown(f"📲 **[இங்கே கிளிக் செய்து வாட்ஸ்அப்பில் பில் அனுப்பவும் (Send WhatsApp Bill)]({wa_link})**")

# --- டேப் 2: புதிய பொருள் & விலை சேர்த்தல் ---
with tab2:
    st.subheader(f"➕ {shop_type} - புதிய பொருள் சேர்க்க")
    with st.form("add_product"):
        p_name = st.text_input("புதிய பொருள் / உணவு / துணி பெயர்:")
        p_price = st.number_input("விலை (₹):", min_value=1, value=100)
        if st.form_submit_button("பட்டியலில் சேர்க்கவும்"):
            if p_name:
                db["catalog"][shop_type][p_name] = p_price
                st.success(f"✅ **{p_name} (₹{p_price})** வெற்றிகரமாகச் சேர்க்கப்பட்டுவிட்டது!")

# --- டேப் 3: இன்றைய மொத்த கணக்கு ---
with tab3:
    st.subheader("📊 இன்றைய மொத்த விற்பனை கணக்கு")
    if db["bills"]:
        df = pd.DataFrame(db["bills"])
        st.metric("இன்றைய மொத்த வசூல்", f"₹{df['தொகை (₹)'].sum()}")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 எக்செல் ரிப்போர்ட் டவுன்லோட் (CSV)", csv, "Shop_Sales_Report.csv", "text/csv")
    else:
        st.info("ℹ️ இன்று இன்னும் பில்கள் எதுவும் போடப்படவில்லை.")
