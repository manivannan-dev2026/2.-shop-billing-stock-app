import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import os

st.set_page_config(page_title="Namma Smart Business Billing", page_icon="🏪")

# 1. நிரந்தர ஃபைல் சேமிப்பு அமைப்பு (Permanent Storage)
BILLS_FILE = "saved_bills.csv"
ITEMS_FILE = "saved_items.csv"

def load_items():
    if os.path.exists(ITEMS_FILE):
        return pd.read_csv(ITEMS_FILE)
    else:
        default_data = [
            {"Category": "Grocery / மளிகை", "Item": "பொன்னி அரிசி (1 Kg)", "Price": 65},
            {"Category": "Grocery / மளிகை", "Item": "துவரம் பருப்பு (1 Kg)", "Price": 140},
            {"Category": "Textile / துணிக்கடை", "Item": "காட்டன் சட்டை (Shirt)", "Price": 650},
            {"Category": "Textile / துணிக்கடை", "Item": "பட்டுப் புடவை (Saree)", "Price": 2500},
            {"Category": "Hotel / ஹோட்டல்", "Item": "மசாலா தோசை (Dosa)", "Price": 70},
            {"Category": "Hotel / ஹோட்டல்", "Item": "சிக்கன் பிரியாணி (Biryani)", "Price": 180}
        ]
        df = pd.DataFrame(default_data)
        df.to_csv(ITEMS_FILE, index=False)
        return df

def load_bills():
    if os.path.exists(BILLS_FILE):
        return pd.read_csv(BILLS_FILE)
    return pd.DataFrame(columns=["Date", "Shop", "Category", "Customer", "Item", "Qty", "Total"])

items_df = load_items()
bills_df = load_bills()

# 2. மேல் மூலையில் மொழி மாற்றும் பட்டன் (தமிழ் / English)
lang = st.radio("🌐 மொழி / Language:", ["தமிழ்", "English"], horizontal=True)

txt = {
    "தமிழ்": {
        "title": "🏪 நம்ம Smart Business Billing",
        "shop": "கடை பெயர்:",
        "cat": "கடை வகை:",
        "t1": "🧾 பில் போட", "t2": "➕ பொருள் சேர்க்க", "t3": "📊 நிரந்தர கணக்கு",
        "cust": "வாடிக்கையாளர் பெயர்:",
        "phone": "வாட்ஸ்அப் எண் (Optional):",
        "item": "பொருள் / உணவு / துணி:",
        "qty": "எண்ணிக்கை / அளவு:",
        "total": "மொத்தத் தொகை:",
        "btn": "✅ பில் சேமிக்கவும் (Save Bill)",
        "wa": "📲 வாட்ஸ்அப்பில் பில் அனுப்பவும்"
    },
    "English": {
        "title": "🏪 Namma Smart Business Billing",
        "shop": "Shop Name:",
        "cat": "Business Category:",
        "t1": "🧾 New Bill", "t2": "➕ Add Item", "t3": "📊 Permanent Report",
        "cust": "Customer Name:",
        "phone": "WhatsApp Number (Optional):",
        "item": "Select Product / Item:",
        "qty": "Quantity / Weight:",
        "total": "Total Amount:",
        "btn": "✅ Save & Generate Bill",
        "wa": "📲 Send Bill on WhatsApp"
    }
}[lang]

st.title(txt["title"])

col1, col2 = st.columns(2)
with col1:
    shop_name = st.text_input(txt["shop"], "Sri Murugan Stores")
with col2:
    selected_cat = st.selectbox(txt["cat"], items_df["Category"].unique())

tab1, tab2, tab3 = st.tabs([txt["t1"], txt["t2"], txt["t3"]])

# --- டேப் 1: பில் போடுதல் ---
with tab1:
    c_name = st.text_input(txt["cust"], "Customer")
    c_phone = st.text_input(txt["phone"], "")
    
    cat_items = items_df[items_df["Category"] == selected_cat]
    item_names = cat_items["Item"].tolist()
    chosen_item = st.selectbox(txt["item"], item_names)
    
    unit_price = cat_items[cat_items["Item"] == chosen_item]["Price"].values[0]
    qty = st.number_input(txt["qty"], min_value=0.5, value=1.0, step=0.5)
    
    total_amt = round(unit_price * qty, 2)
    st.markdown(f"### 💰 {txt['total']} **₹{total_amt}**")
    
    if st.button(txt["btn"], type="primary", use_container_width=True):
        now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        new_bill = pd.DataFrame([{
            "Date": now, "Shop": shop_name, "Category": selected_cat,
            "Customer": c_name, "Item": chosen_item, "Qty": qty, "Total": total_amt
        }])
        updated_bills = pd.concat([bills_df, new_bill], ignore_index=True)
        updated_bills.to_csv(BILLS_FILE, index=False) # நிரந்தரமாக சேமிக்கிறோம்!
        
        st.success(f"🎉 பில் நிரந்தரமாகச் சேமிக்கப்பட்டது! (₹{total_amt})")
        
        msg = urllib.parse.quote(f"🧾 *{shop_name}*\nDate: {now}\nCustomer: {c_name}\nItem: {chosen_item} x {qty}\n*Total: ₹{total_amt}*")
        wa_url = f"https://wa.me{c_phone.strip()}?text={msg}" if c_phone.strip() else f"https://wa.me{msg}"
        st.markdown(f"**[{txt['wa']}]({wa_url})**")

# --- டேப் 2: நிரந்தரமாகப் புதிய பொருள் சேர்த்தல் ---
with tab2:
    with st.form("add_new_item"):
        new_p = st.text_input("புதிய பொருள் பெயர் / New Item Name:")
        new_price = st.number_input("விலை / Price (₹):", min_value=1, value=100)
        if st.form_submit_button("Save Item Permanently"):
            if new_p:
                new_row = pd.DataFrame([{"Category": selected_cat, "Item": new_p, "Price": new_price}])
                updated_items = pd.concat([items_df, new_row], ignore_index=True)
                updated_items.to_csv(ITEMS_FILE, index=False) # நிரந்தரமாக சேமிக்கிறோம்!
                st.success(f"✅ **{new_p} (₹{new_price})** நிரந்தரமாகச் சேர்க்கப்பட்டுவிட்டது! பக்கத்தை Refresh செய்து பாருங்கள்.")

# --- டேப் 3: நிரந்தர விற்பனை கணக்கு ---
with tab3:
    latest_bills = load_bills()
    if not latest_bills.empty:
        st.metric("மொத்த விற்பனை (Total Sales)", f"₹{latest_bills['Total'].sum()}")
        st.dataframe(latest_bills, use_container_width=True)
        csv_dl = latest_bills.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 Download Excel Report (CSV)", csv_dl, "Permanent_Sales_Report.csv", "text/csv")
    else:
        st.info("இன்னும் பில்கள் சேமிக்கப்படவில்லை.")
  
