import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="三角匯率換算", layout="centered")
st.title("💱 三角匯率換算工具（即時）")

# 抓取匯率資料
@st.cache_data
def fetch_rates():
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.find_all('tr')

    rate_dict = {}
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 5:
            currency = row.find('div', {'class': 'visible-phone'}).text.strip()[:3]  # 取得貨幣名稱（例如 USD）
            rate = cells[2].text.strip()  # 即期匯率（買入匯率）
            if rate != '-' and currency != 'TWD':  # 如果匯率不為 - 且不是台幣
                try:
                    rate_dict[currency] = float(rate)
                except ValueError:
                    pass  # 如果匯率轉換錯誤則跳過

    return rate_dict

rates = fetch_rates()

# 顯示抓取到的匯率
st.write(rates)  # 顯示抓取到的匯率，這樣我們可以確認是否正確抓取

currencies = list(rates.keys())

# 幣別選擇
st.subheader("📌 選擇三個幣別")
col1, col2, col3 = st.columns(3)
with col1:
    left_currency = st.selectbox("左幣別", currencies, index=currencies.index("USD") if "USD" in currencies else 0)
with col2:
    mid_currency = st.selectbox("中間幣別（基準）", currencies, index=currencies.index("TWD") if "TWD" in currencies else 1)
with col3:
    right_currency = st.selectbox("右幣別", currencies, index=currencies.index("AED") if "AED" in currencies else 2)

st.divider()

# 輸入金額與來源
st.subheader("💰 輸入金額並選擇來源幣別")
input_col, from_col = st.columns([3, 1])
with input_col:
    input_amount = st.number_input("輸入金額", value=0.0, min_value=0.0, step=0.01)
with from_col:
    input_currency = st.selectbox("來源幣別", [left_currency, mid_currency, right_currency])

# 計算邏輯（使用台幣為中介幣）
def to_twd(amount, currency):
    if currency == "TWD":
        return amount
    return amount * rates[currency]

def from_twd(twd_amount, currency):
    if currency == "TWD":
        return twd_amount
    return twd_amount / rates[currency]

mid_amount = to_twd(input_amount, input_currency)

left_amount = from_twd(mid_amount, left_currency)
right_amount = from_twd(mid_amount, right_currency)

st.divider()
st.subheader("📊 換算結果")

res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric(f"{left_currency}", f"{left_amount:,.2f}")
res_col2.metric(f"{mid_currency}", f"{mid_amount:,.2f}")
res_col3.metric(f"{right_currency}", f"{right_amount:,.2f}")
