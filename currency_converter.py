import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="三幣匯率試算", layout="centered")
st.title("💱 美金 ↔️ 台幣 ↔️ 迪拉姆 匯率試算")

# 抓匯率資料（台灣銀行）
@st.cache_data
def fetch_rates():
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.find_all('tr')

    rate_dict = {}
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            currency_name = row.find('div', {'class': 'visible-phone'}).text.strip()[:3]
            rate = cells[2].text.strip()
            if rate != '-':
                rate_dict[currency_name] = float(rate)
    return rate_dict

# 匯率轉換函數
def convert_from_twd(amount, target_currency, rates):
    return amount / rates.get(target_currency, 1)

def convert_to_twd(amount, source_currency, rates):
    return amount * rates.get(source_currency, 1)

# === 主程式 ===
rates = fetch_rates()

usd_rate = rates.get('USD', 0)
aed_rate = rates.get('AED', 0)

col1, col2, col3 = st.columns(3)

with col1:
    usd_amount = st.number_input("💵 美金 (USD)", value=0.0, step=0.01)

with col2:
    twd_amount = st.number_input("🇹🇼 台幣 (TWD)", value=0.0, step=0.01)

with col3:
    aed_amount = st.number_input("🇦🇪 迪拉姆 (AED)", value=0.0, step=0.01)

st.markdown("---")

# 換算按鈕
colA, colB, colC = st.columns(3)

with colA:
    if st.button("← USD ➜ TWD ➜ AED"):
        twd = convert_to_twd(usd_amount, 'USD', rates)
        aed = convert_from_twd(twd, 'AED', rates)
        st.success(f"{usd_amount} USD ≈ {twd:.2f} TWD ≈ {aed:.2f} AED")

with colB:
    if st.button("← TWD ➜"):
        usd = convert_from_twd(twd_amount, 'USD', rates)
        aed = convert_from_twd(twd_amount, 'AED', rates)
        st.success(f"{twd_amount} TWD ≈ {usd:.2f} USD & {aed:.2f} AED")

with colC:
    if st.button("← AED ➜ TWD ➜ USD"):
        twd = convert_to_twd(aed_amount, 'AED', rates)
        usd = convert_from_twd(twd, 'USD', rates)
        st.success(f"{aed_amount} AED ≈ {twd:.2f} TWD ≈ {usd:.2f} USD")
