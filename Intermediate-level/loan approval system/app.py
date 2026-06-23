import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Loan Approval Predictor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .glass-card-3d {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border-radius: 28px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card-3d::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .glass-card-3d:hover {
        transform: translateY(-5px);
        box-shadow: 0 35px 60px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s ease infinite;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.6);
        font-weight: 300;
        margin-top: 0.5rem;
        letter-spacing: 0.3px;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 16px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        letter-spacing: 0.3px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.1) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .stSelectbox > div, .stNumberInput > div {
        background: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div:hover, .stNumberInput > div:hover {
        border-color: rgba(255, 255, 255, 0.25) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    .stSelectbox label, .stNumberInput label {
        font-weight: 500;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.85rem;
        letter-spacing: 0.3px;
    }
    
    .result-approved-3d {
        background: linear-gradient(135deg, rgba(0, 184, 148, 0.2), rgba(0, 206, 201, 0.1));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(0, 184, 148, 0.3);
        box-shadow: 0 20px 60px rgba(0, 184, 148, 0.15);
        text-align: center;
        color: white;
    }
    
    .result-rejected-3d {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(238, 90, 36, 0.1));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 107, 107, 0.3);
        box-shadow: 0 20px 60px rgba(255, 107, 107, 0.15);
        text-align: center;
        color: white;
    }
    
    .result-title-3d {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .result-subtitle-3d {
        font-size: 1rem;
        opacity: 0.8;
        font-weight: 300;
    }
    
    .metric-card-3d {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card-3d:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value-3d {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f093fb, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label-3d {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.5);
        font-weight: 400;
        margin-top: 0.25rem;
    }
    
    .badge-3d {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(10px);
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.5);
        letter-spacing: 0.5px;
        display: inline-block;
    }
    
    .custom-divider-3d {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
        margin: 2rem 0;
    }
    
    .side-image-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        padding: 0.5rem;
        width: 100%;
    }
    
    .side-image-container img {
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.3s ease;
        width: 100%;
        object-fit: cover;
        max-height: 180px;
    }
    
    .side-image-container img:hover {
        transform: scale(1.02);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
    }
    
    .image-caption {
        color: rgba(255,255,255,0.4);
        font-size: 0.7rem;
        text-align: center;
        letter-spacing: 0.5px;
        margin-top: -0.2rem;
    }
    
    .secure-badge {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 0.6rem;
        text-align: center;
        width: 100%;
        margin-top: 0.3rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .secure-badge span {
        color: rgba(255,255,255,0.3);
        font-size: 0.7rem;
        letter-spacing: 0.5px;
    }
    
    .footer-text {
        text-align: center;
        color: rgba(255,255,255,0.2);
        font-size: 0.7rem;
        letter-spacing: 0.5px;
        padding: 1rem 0;
    }
    
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD MODEL
# =====================================================

@st.cache_resource
def load_model():
    try:
        return joblib.load("loan_model.pkl")
    except FileNotFoundError:
        st.error("⚠️ Model file not found! Please run 'python loan_prediction.py' first.")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Error loading model: {str(e)}")
        st.stop()

data = load_model()
model = data["model"]
scaler = data["scaler"]
label_encoders = data["label_encoders"]
features = data["feature_columns"]

# =====================================================
# HEADER
# =====================================================

col1, col2, col3 = st.columns([2, 0.6, 0.6])

with col1:
    st.markdown("""
    <div>
        <div class="hero-title">Loan Approval</div>
        <div class="hero-subtitle">AI-powered decision support for financial institutions</div>
        <div style="margin-top: 0.8rem;">
            <span class="badge-3d">⚡ Real-time prediction</span>
            <span class="badge-3d" style="margin-left: 0.5rem;">🔒 99.9% uptime</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='text-align:center;'>💳</h1>", unsafe_allow_html=True)

with col3:
    st.markdown("<h1 style='text-align:center;'>🏦</h1>", unsafe_allow_html=True)

st.markdown('<div class="custom-divider-3d"></div>', unsafe_allow_html=True)

# =====================================================
# MAIN FORM & SIDE IMAGES
# =====================================================

col_main1, col_main2 = st.columns([2.2, 1])

with col_main1:
    st.markdown('<div class="glass-card-3d">', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2, gap="large")
    
    with col_left:
        st.markdown('<p style="color: rgba(255,255,255,0.9); font-weight: 600; font-size: 1rem; margin-bottom: 1rem;">👤 Applicant Information</p>', unsafe_allow_html=True)
        
        gender = st.selectbox("Gender", ["Male", "Female"])
        married = st.selectbox("Marital Status", ["Yes", "No"])
        dependents = st.selectbox("Dependents", ["0", "1", "2", "3+"])
        education = st.selectbox("Education", ["Graduate", "Not Graduate"])
        self_employed = st.selectbox("Self Employed", ["No", "Yes"])
        property_area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])
    
    with col_right:
        st.markdown('<p style="color: rgba(255,255,255,0.9); font-weight: 600; font-size: 1rem; margin-bottom: 1rem;">💰 Financial Details</p>', unsafe_allow_html=True)
        
        app_income = st.number_input("Applicant Income ($)", min_value=0, value=5000, step=500)
        co_income = st.number_input("Co-applicant Income ($)", min_value=0, value=0, step=500)
        loan_amount = st.number_input("Loan Amount ($)", min_value=0, value=150, step=10)
        loan_term = st.number_input("Loan Term (Months)", min_value=12, max_value=480, value=360, step=12)
        credit_history = st.selectbox("Credit History", [1.0, 0.0], format_func=lambda x: "✅ Good" if x == 1.0 else "❌ Bad")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# SIDE IMAGES - USING ST.IMAGE (NO BASE64)
# =====================================================

with col_main2:
    st.markdown(
        """
        <div class="glass-card-3d" style="padding:1rem;">
        """,
        unsafe_allow_html=True,
    )

    # Check if images exist, if not use fallback
    if os.path.exists("images/bank.jpg"):
        st.image("images/bank.jpg", use_container_width=True)
    else:
        st.image("https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400&h=280&fit=crop", use_container_width=True)
    
    st.markdown(
        """
        <p class="image-caption">🏦 Smart Loan Decisions</p>
        """,
        unsafe_allow_html=True,
    )

    if os.path.exists("images/analytics.jpg"):
        st.image("images/analytics.jpg", use_container_width=True)
    else:
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=280&fit=crop", use_container_width=True)
    
    st.markdown(
        """
        <p class="image-caption">📊 Data-Driven Insights</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="secure-badge">
            <span>🔐 Secure & Encrypted</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================================
# PREDICT BUTTON
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    predict_button = st.button("🔮 Predict Loan Approval", use_container_width=True)

# =====================================================
# PREDICTION RESULT
# =====================================================

if predict_button:
    try:
        row = {
            "Gender": label_encoders["Gender"].transform([gender])[0],
            "Married": label_encoders["Married"].transform([married])[0],
            "Dependents": label_encoders["Dependents"].transform([dependents])[0],
            "Education": label_encoders["Education"].transform([education])[0],
            "Self_Employed": label_encoders["Self_Employed"].transform([self_employed])[0],
            "Property_Area": label_encoders["Property_Area"].transform([property_area])[0],
            "ApplicantIncome": app_income,
            "CoapplicantIncome": co_income,
            "LoanAmount": loan_amount,
            "Loan_Amount_Term": loan_term,
            "Credit_History": credit_history
        }
        
        X = pd.DataFrame([row])
        X["TotalIncome"] = X["ApplicantIncome"] + X["CoapplicantIncome"]
        X["Income_Loan_Ratio"] = X["TotalIncome"] / (X["LoanAmount"] + 1)
        X["EMI"] = X["LoanAmount"] / (X["Loan_Amount_Term"] + 1)
        X = X[features]
        
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]
        
        st.markdown('<div class="custom-divider-3d"></div>', unsafe_allow_html=True)
        
        col_res1, col_res2 = st.columns([1, 1])
        
        with col_res1:
            if prediction == 1:
                st.markdown("""
                <div class="result-approved-3d">
                    <div class="result-title-3d">✅ Approved</div>
                    <div class="result-subtitle-3d">The application meets approval criteria</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-rejected-3d">
                    <div class="result-title-3d">❌ Rejected</div>
                    <div class="result-subtitle-3d">The application does not meet approval criteria</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_res2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=probability[1] * 100,
                title={"text": "Approval Probability", "font": {"color": "white", "size": 14}},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "rgba(255,255,255,0.3)"},
                    "bar": {"color": "#667eea"},
                    "steps": [
                        {"range": [0, 30], "color": "rgba(255,107,107,0.3)"},
                        {"range": [30, 70], "color": "rgba(254,202,87,0.3)"},
                        {"range": [70, 100], "color": "rgba(0,184,148,0.3)"}
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 4},
                        "thickness": 0.75,
                        "value": 70
                    }
                }
            ))
            fig.update_layout(
                height=280,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter", "color": "rgba(255,255,255,0.7)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="custom-divider-3d"></div>', unsafe_allow_html=True)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        total_income = app_income + co_income
        emi = loan_amount / loan_term if loan_term > 0 else 0
        debt_ratio = (emi / total_income * 100) if total_income > 0 else 0
        
        with col_m1:
            st.markdown(f"""
            <div class="metric-card-3d">
                <div class="metric-value-3d">${total_income:,.0f}</div>
                <div class="metric-label-3d">Total Monthly Income</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown(f"""
            <div class="metric-card-3d">
                <div class="metric-value-3d">${emi:,.0f}</div>
                <div class="metric-label-3d">Estimated Monthly EMI</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m3:
            color = "rgba(0,184,148,1)" if debt_ratio < 30 else "rgba(254,202,87,1)" if debt_ratio < 50 else "rgba(255,107,107,1)"
            st.markdown(f"""
            <div class="metric-card-3d">
                <div class="metric-value-3d" style="background: linear-gradient(135deg, {color}, {color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{debt_ratio:.1f}%</div>
                <div class="metric-label-3d">Debt-to-Income Ratio</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 0.5rem;">
            <span style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">🤖 Model: {data.get('best_model_name', 'Trained Model')} • F1 Score: {data.get('f1_score', 'N/A')}%</span>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"⚠️ An error occurred: {str(e)}")
        st.info("Please ensure the model file is properly trained and saved.")

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div class="footer-text">
    Shadow Fox Internship • Intermediate Level • 2026
</div>
""", unsafe_allow_html=True)