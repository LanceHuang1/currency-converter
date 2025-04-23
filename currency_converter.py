import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 擷取台灣銀行匯率資料（包含所有貨幣）
@st.cache_data
def fetch_rates():
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"title": "牌告匯率"}).tbody
    rows = table.find_all("tr")

    rates = {}
    for row in rows:
        currency_name = row.find("div", {"class": "visible-phone"}).get_text(strip=True)
        currency_code = currency_name[:3]
        cash_rate = row.find_all("td")[2].text.strip()
        if cash_rate != '-':
            rates[currency_code] = float(cash_rate)
    return rates

# 匯率換算邏輯：以 TWD 為中介
def convert(amount, from_currency, to_currency, rates):
    if from_currency == to_currency:
        return amount
    if from_currency != 'TWD':
        amount = amount * rates[from_currency]  # 換成台幣
    if to_currency != 'TWD':
        amount = amount / rates[to_currency]    # 台幣換目標
    return amount

# ===== Streamlit UI =====
st.set_page_config(page_title="即時匯率換算器", layout="centered")
st.title("💱 即時匯率換算器（台灣銀行）")

rates = fetch_rates()
currency_options = list(rates.keys())

st.write("🔄 匯率資料來源：台灣銀行")
st.write("📅 更新時間：", datetime.now().strftime("%Y-%m-%d %H:%M"))

amount = st.number_input("💰 輸入金額", value=1.0)
from_currency = st.selectbox("來源貨幣", currency_options, index=currency_options.index("USD") if "USD" in currency_options else 0)
to_currency = st.selectbox("目標貨幣", currency_options, index=currency_options.index("TWD") if "TWD" in currency_options else 1)

if st.button("進行換算"):
    result = convert(amount, from_currency, to_currency, rates)
    st.success(f"{amount} {from_currency} ➜ {result:.4f} {to_currency}")

# 匯率資料表
with st.expander("📊 顯示即時匯率表"):
    df = pd.DataFrame.from_dict(rates, orient='index', columns=['本行買入（TWD）'])
    df.index.name = '幣別'
    st.dataframe(df)
