import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="நம்ம கடை Billing & Stock App", page_icon="🧾")

st.title("🧾 நம்ம கடை & ஒர்க்ஷாப் Billing App")
st.caption("தினசரி பில்லிங், ஸ்டாக் இருப்பு மற்றும் வரவு-செலவு கணக்கு பார்க்கும் எளிய செயலி!")

# 1. பொதுவான ஸ்டாக் & பில் மெமரி
@st.cache_resource
def get_shop_db():
    return {
        "bills": [],
        "stock": {
            "இன்ஜின் ஆயில் (Engine Oil)": {"price": 350, "qty": 15},
            "பிரேக் ஷூ (Brake Shoe)": {"price": 180, "qty": 8},
            "ஏர் ஃபில்டர் (Air Filter)": {"price": 120, "qty": 4},
            "ஜெனரல் சர்வீஸ் (General Service)": {"price": 500, "qty": 999}
        }
    }

shop_db = get_shop_db()

# மூன்று எளிய டேப்கள்
tab1, tab2, tab3 = st.tabs(["🧾 பில் போட (New Bill)", "📦 ஸ்டாக் பார்க்க (Stock)", "📊 இன்றைய கணக்கு (Report)"])

# --- டேப் 1: புதிய பில் உருவாக்குதல் ---
with tab1:
    st.subheader("🧾 வாடிக்கையாளருக்குப் பில் போடவும்")
    customer_name = st.text_input("வாடிக்கையாளர் பெயர் / வண்டி எண் (Optional):", "Walk-in Customer")
    
    item_list = list(shop_db["stock"].keys())
    selected_item = st.selectbox("பொருள் / சர்வீஸ் தேர்ந்தெடுக்கவும்:", item_list)
    
    item_info = shop_db["stock"][selected_item]
    st.info(f"💰 ஒரு பொருளின் விலை: **₹{item_info['price']}** | 📦 கையிருப்பு (Stock): **{item_info['qty']}**")
    
    qty = st.number_input("எண்ணிக்கை (Quantity):", min_value=1, max_value=100, value=1)
    total_amount = item_info["price"] * qty
    
    st.markdown(f"### மொத்தத் தொகை: **₹{total_amount}**")
    
    if st.button("✅ பில் சேமிக்கவும் (Generate Bill)", type="primary"):
        now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        shop_db["bills"].append({
            "நேரம்": now,
            "வாடிக்கையாளர்": customer_name,
            "பொருள்": selected_item,
            "எண்ணிக்கை": qty,
            "தொகை (₹)": total_amount
        })
        # ஸ்டாக் எண்ணிக்கையைக் குறைக்கிறோம்
        if shop_db["stock"][selected_item]["qty"] >= qty and shop_db["stock"][selected_item]["qty"] != 999:
            shop_db["stock"][selected_item]["qty"] -= qty
            
        st.success(f"🎉 பில் வெற்றிகரமாகப் பதிவு செய்யப்பட்டது! (மொத்தம்: ₹{total_amount})")

# --- டேப் 2: ஸ்டாக் இருப்பு & புதிய பொருள் சேர்த்தல் ---
with tab2:
    st.subheader("📦 கடையின் ஸ்டாக் இருப்பு")
    for name, details in shop_db["stock"].items():
        if details["qty"] <= 5:
            st.error(f"⚠️ **{name}** - விலை: ₹{details['price']} | கையிருப்பு: **{details['qty']} மட்டுமே உள்ளது! (Low Stock)**")
        else:
            st.success(f"✅ **{name}** - விலை: ₹{details['price']} | கையிருப்பு: **{details['qty']}**")
            
    st.divider()
    st.subheader("➕ புதிய பொருள் / சர்வீஸ் சேர்க்க")
    with st.form("add_stock_form"):
        new_item = st.text_input("பொருள் பெயர்:")
        new_price = st.number_input("விலை (₹):", min_value=1, value=100)
        new_qty = st.number_input("கையிருப்பு எண்ணிக்கை:", min_value=1, value=10)
        if st.form_submit_button("ஸ்டாக்கில் சேர்க்கவும்"):
            if new_item:
                shop_db["stock"][new_item] = {"price": new_price, "qty": new_qty}
                st.success(f"✅ **{new_item}** ஸ்டாக்கில் சேர்க்கப்பட்டுவிட்டது!")

# --- டேப் 3: இன்றைய மொத்த கணக்கு & எக்செல் டவுன்லோட் ---
with tab3:
    st.subheader("📊 இன்றைய மொத்த விற்பனை கணக்கு")
    if shop_db["bills"]:
        df_bills = pd.DataFrame(shop_db["bills"])
        total_sales = df_bills["தொகை (₹)"].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("மொத்த பில்கள்", f"{len(df_bills)}")
        col2.metric("மொத்த வசூல்", f"₹{total_sales}")
        
        st.dataframe(df_bills, use_container_width=True)
        
        csv_data = df_bills.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 இன்றைய கணக்கை எக்செல் (CSV) ஃபைலாக டவுன்லோட் செய்",
            data=csv_data,
            file_name="Daily_Shop_Report.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ இன்று இன்னும் பில்கள் எதுவும் போடப்படவில்லை.")
