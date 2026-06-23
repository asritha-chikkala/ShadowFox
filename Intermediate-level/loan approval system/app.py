import streamlit as st
import pandas as pd
import joblib
import numpy as np

st.set_page_config(
    page_title="Loan Approval Predictor",
    page_icon="💰",
    layout="centered"
)

# Load Model
@st.cache_resource
def load_model():
    return joblib.load("loan_model.pkl")

data = load_model()
model = data["model"]
scaler = data["scaler"]
label_encoders = data["label_encoders"]
features = data["feature_columns"]

st.title("💰 Loan Approval Prediction System")
st.markdown("---")

# Create two columns for better layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Applicant Details")
    gender = st.selectbox("Gender", ["Male", "Female"])
    married = st.selectbox("Married", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["0", "1", "2", "3+"])
    education = st.selectbox("Education", ["Graduate", "Not Graduate"])
    self_employed = st.selectbox("Self Employed", ["No", "Yes"])
    property_area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])

with col2:
    st.subheader("Financial Details")
    app_income = st.number_input("Applicant Income ($)", min_value=0, value=5000, step=500)
    co_income = st.number_input("Co-applicant Income ($)", min_value=0, value=0, step=500)
    loan_amount = st.number_input("Loan Amount ($)", min_value=0, value=150, step=10)
    loan_term = st.number_input("Loan Term (Months)", min_value=12, max_value=480, value=360, step=12)
    credit_history = st.selectbox("Credit History (1=Good, 0=Bad)", [1.0, 0.0], format_func=lambda x: "Good" if x == 1.0 else "Bad")

st.markdown("---")

if st.button("🔮 Predict Loan Approval", type="primary"):
    try:
        # Prepare input data
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
        
        # Convert to DataFrame and add engineered features
        X = pd.DataFrame([row])
        X["TotalIncome"] = X["ApplicantIncome"] + X["CoapplicantIncome"]
        X["Income_Loan_Ratio"] = X["TotalIncome"] / (X["LoanAmount"] + 1)
        X["EMI"] = X["LoanAmount"] / (X["Loan_Amount_Term"] + 1)
        
        # Ensure correct feature order
        X = X[features]
        
        # Scale and predict
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]
        
        # Display result
        st.markdown("---")
        st.subheader("Prediction Result")
        
        if prediction == 1:
            st.success(f"✅ Loan Approved")
            st.metric("Confidence", f"{probability[1]*100:.1f}%")
        else:
            st.error(f"❌ Loan Rejected")
            st.metric("Confidence", f"{probability[0]*100:.1f}%")
            
        # Display additional metrics
        st.markdown("---")
        st.caption(f"Model: {data.get('best_model_name', 'Trained Model')} • Cross-Validation Accuracy: {data.get('cross_validation_accuracy', 'N/A')}%")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please ensure the model file is properly trained and saved.")

st.markdown("---")
st.caption("🔬 Loan Approval Prediction using Machine Learning")