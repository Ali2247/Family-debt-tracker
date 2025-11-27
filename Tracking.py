import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(page_title="Family Debt Tracker", page_icon="💰", layout="wide")

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'fatima_total' not in st.session_state:
    st.session_state.fatima_total = 0.0
if 'nora_total' not in st.session_state:
    st.session_state.nora_total = 0.0
if 'payments' not in st.session_state:
    st.session_state.payments = []

# Main title
st.title("💰 Family Debt Tracker")

# Initialization phase
if not st.session_state.initialized:
    st.header("🔧 Initialize Debt Tracker")
    st.info("Set the total amounts owed to each sister. These amounts cannot be changed later.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fatima_amount = st.number_input(
            "Total amount owed to Fatima (SAR)",
            min_value=0.0,
            step=100.0,
            format="%.2f"
        )
    
    with col2:
        nora_amount = st.number_input(
            "Total amount owed to Nora (SAR)",
            min_value=0.0,
            step=100.0,
            format="%.2f"
        )
    
    if st.button("✅ Initialize Tracker", type="primary", use_container_width=True):
        if fatima_amount > 0 and nora_amount > 0:
            st.session_state.initialized = True
            st.session_state.fatima_total = fatima_amount
            st.session_state.nora_total = nora_amount
            st.success("Tracker initialized successfully!")
            st.rerun()
        else:
            st.error("Please enter valid amounts for both Fatima and Nora.")

# Main application
else:
    # Add reset button in sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                st.session_state.initialized = False
                st.session_state.fatima_total = 0.0
                st.session_state.nora_total = 0.0
                st.session_state.payments = []
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm reset!")
        
        if st.session_state.get('confirm_reset', False):
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()
    
    # Calculate totals
    def calculate_remaining(recipient):
        total = st.session_state.fatima_total if recipient == 'Fatima' else st.session_state.nora_total
        paid = sum(p['amount'] for p in st.session_state.payments if p['recipient'] == recipient)
        return total - paid
    
    def calculate_paid_by_person(payer):
        return sum(p['amount'] for p in st.session_state.payments if p['payer'] == payer)
    
    # Balance Overview
    st.header("📊 Balance Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👩 Fatima")
        fatima_paid = sum(p['amount'] for p in st.session_state.payments if p['recipient'] == 'Fatima')
        fatima_remaining = calculate_remaining('Fatima')
        
        st.metric("Total Owed", f"{st.session_state.fatima_total:,.2f} SAR")
        st.metric("Total Paid", f"{fatima_paid:,.2f} SAR", delta=None)
        st.metric(
            "Remaining", 
            f"{fatima_remaining:,.2f} SAR",
            delta=f"{-fatima_paid:,.2f} SAR" if fatima_paid > 0 else None,
            delta_color="inverse"
        )
    
    with col2:
        st.markdown("### 👩 Nora")
        nora_paid = sum(p['amount'] for p in st.session_state.payments if p['recipient'] == 'Nora')
        nora_remaining = calculate_remaining('Nora')
        
        st.metric("Total Owed", f"{st.session_state.nora_total:,.2f} SAR")
        st.metric("Total Paid", f"{nora_paid:,.2f} SAR", delta=None)
        st.metric(
            "Remaining",
            f"{nora_remaining:,.2f} SAR",
            delta=f"{-nora_paid:,.2f} SAR" if nora_paid > 0 else None,
            delta_color="inverse"
        )
    
    st.divider()
    
    # Individual Contributions
    st.header("👥 Individual Contributions")
    payers = ['Abdullah', 'Ali', 'Moaad', 'Aisha']
    cols = st.columns(4)
    
    for idx, payer in enumerate(payers):
        with cols[idx]:
            paid = calculate_paid_by_person(payer)
            st.metric(payer, f"{paid:,.2f} SAR")
    
    st.divider()
    
    # Payment Form
    st.header("💳 Record New Payment")
    
    with st.form("payment_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            payer = st.selectbox("Who is paying?", payers)
        
        with col2:
            recipient = st.selectbox("Paying to?", ['Fatima', 'Nora'])
        
        with col3:
            amount = st.number_input("Amount (SAR)", min_value=0.0, step=50.0, format="%.2f")
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            day = st.number_input("Day", min_value=1, max_value=31, value=datetime.now().day)
        
        with col5:
            month = st.number_input("Month", min_value=1, max_value=12, value=datetime.now().month)
        
        with col6:
            year = st.number_input("Year", min_value=2020, max_value=2100, value=datetime.now().year)
        
        submitted = st.form_submit_button("✅ Submit Payment", type="primary", use_container_width=True)
        
        if submitted:
            if amount > 0:
                try:
                    date_str = f"{int(day):02d}/{int(month):02d}/{int(year)}"
                    # Validate date
                    datetime.strptime(date_str, "%d/%m/%Y")
                    
                    new_payment = {
                        'id': len(st.session_state.payments) + 1,
                        'payer': payer,
                        'amount': amount,
                        'recipient': recipient,
                        'date': date_str,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    st.session_state.payments.append(new_payment)
                    st.success(f"✅ Payment of {amount:,.2f} SAR from {payer} to {recipient} recorded successfully!")
                    st.rerun()
                except ValueError:
                    st.error("Invalid date. Please enter a valid date.")
            else:
                st.error("Please enter a valid payment amount greater than 0.")
    
    st.divider()
    
    # Payment History
    st.header("📜 Payment History")
    
    if st.session_state.payments:
        # Create DataFrame
        df = pd.DataFrame(st.session_state.payments)
        df = df[['date', 'payer', 'recipient', 'amount']]
        df = df.sort_values('date', ascending=False).reset_index(drop=True)
        df['amount'] = df['amount'].apply(lambda x: f"{x:,.2f} SAR")
        
        # Display table
        st.dataframe(
            df,
            column_config={
                "date": "Date",
                "payer": "Payer",
                "recipient": "Recipient",
                "amount": "Amount"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Summary statistics
        st.subheader("📈 Summary")
        total_paid = sum(p['amount'] for p in st.session_state.payments)
        total_remaining = calculate_remaining('Fatima') + calculate_remaining('Nora')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Payments", f"{total_paid:,.2f} SAR")
        with col2:
            st.metric("Total Remaining", f"{total_remaining:,.2f} SAR")
        with col3:
            num_payments = len(st.session_state.payments)
            st.metric("Number of Payments", num_payments)
    else:
        st.info("No payments recorded yet. Use the form above to record your first payment!")