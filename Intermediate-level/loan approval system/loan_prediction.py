import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, r2_score, confusion_matrix

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC

print("=" * 80)
print("LOAN APPROVAL PREDICTION SYSTEM")
print("=" * 80)

# =====================================================
# LOAD DATASET
# =====================================================

df = pd.read_csv("loan_prediction.csv")
print(f"\nDataset Shape: {df.shape}")

if "Loan_ID" in df.columns:
    df.drop("Loan_ID", axis=1, inplace=True)

# =====================================================
# HANDLE MISSING VALUES
# =====================================================

numeric_cols = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History"]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

categorical_cols = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area", "Loan_Status"]

for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].mode()[0])

# =====================================================
# LABEL ENCODING
# =====================================================

label_encoders = {}

cat_cols = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"]

for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

target_encoder = LabelEncoder()
df["Loan_Status"] = target_encoder.fit_transform(df["Loan_Status"])
label_encoders["Loan_Status"] = target_encoder

# =====================================================
# FEATURES & TARGET
# =====================================================

X = df.drop("Loan_Status", axis=1)
y = df["Loan_Status"]

# =====================================================
# FEATURE ENGINEERING
# =====================================================

X["TotalIncome"] = X["ApplicantIncome"] + X["CoapplicantIncome"]
X["Income_Loan_Ratio"] = X["TotalIncome"] / (X["LoanAmount"] + 1)
X["EMI"] = X["LoanAmount"] / (X["Loan_Amount_Term"] + 1)

feature_columns = X.columns.tolist()

# =====================================================
# SCALING
# =====================================================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.20, random_state=42, stratify=y
)

print(f"\nTraining Samples : {len(X_train)}")
print(f"Testing Samples  : {len(X_test)}")

# =====================================================
# MODELS
# =====================================================

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000, random_state=42),
    "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42),
    "SVM": SVC(kernel="rbf", C=1.5, gamma="scale"),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=300, learning_rate=0.05, random_state=42)
}

# =====================================================
# TRAIN MODELS
# =====================================================

results = []
best_model = None
best_model_name = None
best_f1 = 0
best_r2 = 0

print("\n" + "=" * 80)
print("MODEL COMPARISON")
print("=" * 80)

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    results.append([
        name,
        round(accuracy * 100, 2),
        round(precision * 100, 2),
        round(recall * 100, 2),
        round(f1 * 100, 2),
        round(r2, 4)
    ])
    
    print(f"  Accuracy  : {accuracy*100:.2f}%")
    print(f"  Precision : {precision*100:.2f}%")
    print(f"  Recall    : {recall*100:.2f}%")
    print(f"  F1 Score  : {f1*100:.2f}%")
    print(f"  R² Score  : {r2:.4f}")
    
    if f1 > best_f1:
        best_f1 = f1
        best_r2 = r2
        best_model = model
        best_model_name = name

# =====================================================
# RESULTS TABLE
# =====================================================

results_df = pd.DataFrame(
    results,
    columns=["Model", "Accuracy", "Precision", "Recall", "F1 Score", "R² Score"]
)
results_df = results_df.sort_values(by="F1 Score", ascending=False)

print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)
print(results_df.to_string(index=False))

# =====================================================
# BEST MODEL
# =====================================================

print("\n" + "=" * 80)
print("BEST MODEL")
print("=" * 80)
print(f"Model      : {best_model_name}")
print(f"F1 Score   : {best_f1*100:.2f}%")
print(f"R² Score   : {best_r2:.4f}")

# =====================================================
# CONFUSION MATRIX
# =====================================================

pred = best_model.predict(X_test)
cm = confusion_matrix(y_test, pred)
print(f"\nConfusion Matrix:\n{cm}")

# =====================================================
# SAVE MODEL
# =====================================================

model_data = {
    "model": best_model,
    "scaler": scaler,
    "label_encoders": label_encoders,
    "feature_columns": feature_columns,
    "best_model_name": best_model_name,
    "f1_score": round(best_f1 * 100, 2),
    "r2_score": round(best_r2, 4)
}

joblib.dump(model_data, "loan_model.pkl")

print("\n✅ Best Model Saved Successfully")
print("   File: loan_model.pkl")
print("\n" + "=" * 80)
print("TRAINING COMPLETED")
print("=" * 80)