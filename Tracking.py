import streamlit as st
import pandas as pd
from datetime import datetime
import json

# إعدادات الصفحة
st.set_page_config(page_title="برنامج تتبع الديون العائلية", page_icon="💰", layout="wide")

# تهيئة البيانات
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'fatima_total' not in st.session_state:
    st.session_state.fatima_total = 0.0
if 'nora_total' not in st.session_state:
    st.session_state.nora_total = 0.0
if 'payments' not in st.session_state:
    st.session_state.payments = []

# العنوان الرئيسي
st.title("💰 برنامج تتبع الديون العائلية")

# مرحلة التهيئة
if not st.session_state.initialized:
    st.header("🔧 تهيئة البرنامج")
    st.info("حدد المبالغ المستحقة لكل أخت. هذي المبالغ ما تتغير بعدين.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fatima_amount = st.number_input(
            "المبلغ المستحق لفاطمة (ريال)",
            min_value=0.0,
            value=153000.0,
            step=100.0,
            format="%.2f"
        )
    
    with col2:
        nora_amount = st.number_input(
            "المبلغ المستحق لنورا (ريال)",
            min_value=0.0,
            value=40000.0,
            step=100.0,
            format="%.2f"
        )
    
    if st.button("✅ ابدأ البرنامج", type="primary", use_container_width=True):
        if fatima_amount > 0 and nora_amount > 0:
            st.session_state.initialized = True
            st.session_state.fatima_total = fatima_amount
            st.session_state.nora_total = nora_amount
            st.success("تم تهيئة البرنامج بنجاح!")
            st.rerun()
        else:
            st.error("الرجاء إدخال مبالغ صحيحة لفاطمة ونورا.")

# البرنامج الرئيسي
else:
    # زر إعادة التعيين
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        if st.button("🔄 امسح كل البيانات", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                st.session_state.initialized = False
                st.session_state.fatima_total = 0.0
                st.session_state.nora_total = 0.0
                st.session_state.payments = []
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("اضغط مرة ثانية للتأكيد!")
        
        if st.session_state.get('confirm_reset', False):
            if st.button("إلغاء", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()
    
    # حساب المبالغ
    def calculate_remaining(recipient):
        total = st.session_state.fatima_total if recipient == 'فاطمة' else st.session_state.nora_total
        paid = sum(p['amount'] for p in st.session_state.payments if p['recipient'] == recipient)
        return total - paid
    
    def calculate_paid_by_person(payer):
        return sum(p['amount'] for p in st.session_state.payments if p['payer'] == payer)
    
    # نظرة عامة على الأرصدة
    st.header("📊 نظرة عامة على الأرصدة")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👩 فاطمة")
        fatima_paid = sum(p['amount'] for p in st.session_state.payments if p['recipient'] == 'فاطمة')
        fatima_remaining = calculate_remaining('فاطمة')
        
        st.metric("المبلغ الكلي المستحق", f"{st.session_state.fatima_total:,.2f} ريال")
        st.metric("المبلغ المدفوع", f"{fatima_paid:,.2f} ريال", delta=None)
        st.metric(
            "المتبقي", 
            f"{fatima_remaining:,.2f} ريال",
            delta=f"{-fatima_paid:,.2f} ريال" if fatima_paid > 0 else None,
            delta_color="inverse"
        )
    
    with col2:
        st.markdown("### 👩 نورا")
        nora_paid = sum(p['amount'] for p in st.session_state.payments if p['recipient'] == 'نورا')
        nora_remaining = calculate_remaining('نورا')
        
        st.metric("المبلغ الكلي المستحق", f"{st.session_state.nora_total:,.2f} ريال")
        st.metric("المبلغ المدفوع", f"{nora_paid:,.2f} ريال", delta=None)
        st.metric(
            "المتبقي",
            f"{nora_remaining:,.2f} ريال",
            delta=f"{-nora_paid:,.2f} ريال" if nora_paid > 0 else None,
            delta_color="inverse"
        )
    
    st.divider()
    
    # المساهمات الفردية
    st.header("👥 مساهمات كل شخص")
    payers = ['عبدالله', 'علي', 'معاذ', 'عائشة']
    cols = st.columns(4)
    
    for idx, payer in enumerate(payers):
        with cols[idx]:
            paid = calculate_paid_by_person(payer)
            st.metric(payer, f"{paid:,.2f} ريال")
    
    st.divider()
    
    # نموذج الدفع
    st.header("💳 تسجيل دفعة جديدة")
    
    with st.form("payment_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            payer = st.selectbox("مين اللي دافع؟", payers)
        
        with col2:
            recipient = st.selectbox("دافع لمين؟", ['فاطمة', 'نورا'])
        
        with col3:
            amount = st.number_input("المبلغ (ريال)", min_value=0.0, step=50.0, format="%.2f")
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            day = st.number_input("اليوم", min_value=1, max_value=31, value=datetime.now().day)
        
        with col5:
            month = st.number_input("الشهر", min_value=1, max_value=12, value=datetime.now().month)
        
        with col6:
            year = st.number_input("السنة", min_value=2020, max_value=2100, value=datetime.now().year)
        
        submitted = st.form_submit_button("✅ سجل الدفعة", type="primary", use_container_width=True)
        
        if submitted:
            if amount > 0:
                try:
                    date_str = f"{int(day):02d}/{int(month):02d}/{int(year)}"
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
                    st.success(f"✅ تم تسجيل دفعة {amount:,.2f} ريال من {payer} إلى {recipient} بنجاح!")
                    st.rerun()
                except ValueError:
                    st.error("تاريخ غير صحيح. الرجاء إدخال تاريخ صحيح.")
            else:
                st.error("الرجاء إدخال مبلغ صحيح أكبر من صفر.")
    
    st.divider()
    
    # سجل الدفعات
    st.header("📜 سجل الدفعات")
    
    if st.session_state.payments:
        df = pd.DataFrame(st.session_state.payments)
        df = df[['date', 'payer', 'recipient', 'amount']]
        df = df.sort_values('date', ascending=False).reset_index(drop=True)
        df['amount'] = df['amount'].apply(lambda x: f"{x:,.2f} ريال")
        
        st.dataframe(
            df,
            column_config={
                "date": "التاريخ",
                "payer": "الدافع",
                "recipient": "المستلم",
                "amount": "المبلغ"
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.subheader("📈 ملخص")
        total_paid = sum(p['amount'] for p in st.session_state.payments)
        total_remaining = calculate_remaining('فاطمة') + calculate_remaining('نورا')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المدفوعات", f"{total_paid:,.2f} ريال")
        with col2:
            st.metric("إجمالي المتبقي", f"{total_remaining:,.2f} ريال")
        with col3:
            num_payments = len(st.session_state.payments)
            st.metric("عدد الدفعات", num_payments)
    else:
        st.info("ما فيه دفعات مسجلة بعد. استخدم النموذج فوق لتسجيل أول دفعة!")
