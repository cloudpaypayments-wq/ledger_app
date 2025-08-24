import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_FILE = "ledger.csv"

# ---------- Helper functions ----------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["date","customer","inr_paid","usd_received","realized_rate","profit_usd","profit_inr"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def add_transaction(date, customer, inr_paid, usd_received, realized_rate):
    expected_usd = inr_paid / realized_rate if realized_rate > 0 else 0
    profit_usd = usd_received - expected_usd
    profit_inr = profit_usd * realized_rate
    new_row = pd.DataFrame([{
        "date": date,
        "customer": customer,
        "inr_paid": inr_paid,
        "usd_received": usd_received,
        "realized_rate": realized_rate,
        "profit_usd": profit_usd,
        "profit_inr": profit_inr
    }])
    df = load_data()
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

def money(x):
    return f"₹{x:,.2f}"

def usd(x):
    return f"${x:,.2f}"

def format_profit(profit_usd, realized_rate):
    try:
        if pd.isnull(profit_usd):
            return ""
        if profit_usd >= 0:
            return f"Profit {usd(profit_usd)} ({money(profit_usd * realized_rate)})"
        else:
            return f"To Collect {usd(abs(profit_usd))} ({money(abs(profit_usd) * realized_rate)})"
    except Exception:
        return ""

# ---------- Streamlit App ----------
st.set_page_config(page_title="Customer Ledger", layout="wide")
st.title("💰 Customer Ledger App")

menu = st.sidebar.radio("Menu", ["Add Transaction","Transactions","Summaries"])

if menu == "Add Transaction":
    st.header("➕ Add New Transaction")
    with st.form("add_form"):
        date = st.date_input("Date", datetime.today())
        customer = st.text_input("Customer Name")
        inr_paid = st.number_input("INR Paid", min_value=0.0, step=1000.0)
        usd_received = st.number_input("USD Received", min_value=0.0, step=100.0)
        realized_rate = st.number_input("Realized Rate (₹/USD)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            add_transaction(date, customer, inr_paid, usd_received, realized_rate)
            st.success("Transaction added successfully!")

elif menu == "Transactions":
    st.header("📒 All Transactions")
    df = load_data()
    if df.empty:
        st.info("No transactions yet.")
    else:
        show = df.copy()
        show["Result"] = show.apply(lambda r: format_profit(r["profit_usd"], r["realized_rate"]), axis=1)
        
        for idx, row in show.iterrows():
            st.write(f"**{row['date']}** | {row['customer']} | Paid {money(row['inr_paid'])} | Received {usd(row['usd_received'])} | Rate {row['realized_rate']} | {format_profit(row['profit_usd'], row['realized_rate'])}")
            
            if st.button(f"❌ Delete Transaction {idx}", key=f"del_{idx}"):
                st.warning("Are you sure you want to delete this transaction?")
                if st.button(f"✅ Yes, delete {idx}", key=f"yes_{idx}"):
                    df = df.drop(idx)
                    save_data(df)
                    st.success("Transaction deleted!")
                    st.experimental_rerun()
                if st.button("❌ Cancel", key=f"no_{idx}"):
                    st.info("Delete cancelled.")

        # Download all transactions
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download All Transactions (CSV)",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv"
        )

elif menu == "Summaries":
    st.header("📊 Customer Summaries")
    df = load_data()
    if df.empty:
        st.info("No transactions yet.")
    else:
        grp = df.groupby("customer").agg({
            "inr_paid":"sum",
            "usd_received":"sum",
            "profit_usd":"sum",
            "profit_inr":"sum",
            "realized_rate":"mean",
            "date":"count"
        }).reset_index().rename(columns={"date":"txns"})
        
        grp["Result"] = grp.apply(lambda r: format_profit(r["profit_usd"], r["realized_rate"]), axis=1)
        st.dataframe(grp[["customer","txns","inr_paid","usd_received","Result"]], use_container_width=True, hide_index=True)

        # Download summary
        csv_summary = grp.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Customer Summary (CSV)",
            data=csv_summary,
            file_name="summary.csv",
            mime="text/csv"
        )

        st.subheader("Overall Summary")
        total_inr = df["inr_paid"].sum()
        total_usd = df["usd_received"].sum()
        total_profit_usd = df["profit_usd"].sum()
        avg_realized_rate = (df["inr_paid"].sum()/df["usd_received"].sum()) if df["usd_received"].sum() > 0 else None
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total INR Paid", money(total_inr))
        c2.metric("Total USD Received", usd(total_usd))
        c3.metric("Avg Realized Rate", f"{avg_realized_rate:,.2f}" if avg_realized_rate else "-")
        c4.metric("Result", format_profit(total_profit_usd, avg_realized_rate if avg_realized_rate else 1))
