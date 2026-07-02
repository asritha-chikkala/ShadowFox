# ShadowFox AI & Machine Learning Internship

## 📌 Internship Overview

This repository contains three progressive projects completed during the **ShadowFox AI & Machine Learning Internship**. The projects span from foundational NLP concepts to advanced deep learning model analysis, demonstrating a comprehensive journey from beginner to advanced level.

| Level | Project | Duration |
|-------|---------|----------|
| **Beginner** | Autocorrect + Next-Word Prediction Keyboard System | Level 1 |
| **Intermediate** | Loan Approval Prediction System | Level 2 |
| **Advanced** | GPT-2 Language Model Analysis | Level 3 |

---

## 📁 Project 1: Autocorrect + Next-Word Prediction Keyboard System (Beginner)

### Objective

Develop an NLP-based intelligent keyboard system that detects and corrects spelling mistakes while predicting the next word using contextual language modeling.

### Models Used

- Bigram Model (2-word sequences)
- Trigram Model (3-word sequences)
- Quadgram Model (4-word sequences)
- Fivegram Model (5-word sequences)
- PySpellChecker (Spell correction engine)

### Outcome

- Achieved **13.04% Top-1 Accuracy** in next-word prediction
- Achieved **0.027ms Inference Latency** for real-time predictions
- Built interactive Tkinter GUI with:
  - Real-time spelling suggestions panel
  - Next-word prediction buttons with probability scores
  - Performance metrics dashboard (Top-1, Top-5, Latency)

### Tools & Technologies

Python, Tkinter, NLTK, PySpellChecker, Pickle, Re, Collections

### Key Features

- Spell checking and autocorrection
- Context-based next-word prediction
- Punctuation and capitalization preservation
- Double-click suggestion replacement
- Performance metrics tracking

---

## 📁 Project 2: Loan Approval Prediction System (Intermediate)

### Objective

Develop a machine learning framework to predict loan approval status based on applicant financial and personal information, providing real-time decision support through an interactive web application.

### Models Used

| Model | Type |
|-------|------|
| Logistic Regression | Classification |
| Decision Tree | Classification |
| Random Forest | Classification |
| Support Vector Machine (SVM) | Classification |
| Gradient Boosting | Classification |

### Outcome

- **Best Model:** Random Forest

- Built interactive Streamlit web application with:
  - Real-time predictions with confidence scores
  - Probability gauge visualization
  - Financial health metrics (Income, EMI, Debt-to-Income Ratio)
  - 3D glass-morphism UI with dark theme

### Tools & Technologies

Python, Pandas, NumPy, Scikit-Learn, Streamlit, Plotly, Matplotlib, Seaborn, Joblib, Re

### Key Features

- Real-time loan approval predictions
- Interactive probability gauge
- Financial health analysis dashboard
- 3D glass-morphism user interface
- Feature engineering for improved performance
- Model comparison and selection

---

## 📁 Project 3: GPT-2 Language Model Analysis (Advanced)

### Objective

Conduct an in-depth evaluation of GPT-2 language model's text generation capabilities, analyzing performance across multiple domains with quantitative metrics and visualization.

### Model Used

- **GPT-2** (124M parameters) from Hugging Face Transformers
- **Tokenizer:** GPT-2 Tokenizer

### Domains Tested

| Domain | Lexical Diversity | Perplexity |
|--------|-------------------|------------|
| Technology | 0.630 | 7.31 |
| Healthcare | 0.599 | 4.54 |
| Education | 0.486 | 6.33 |
| Finance | 0.279 | 2.39 |
| Sports | 0.459 | 5.32 |
| Science | 0.498 | 5.74 |

### Outcome

- **Best Domain (Lexical Diversity):** Technology (0.630)
- **Best Domain (Perplexity):** Finance (2.39)
- **Optimal Temperature:** 0.7 for balanced creativity & coherence
- Created 4+ visualizations: Word Cloud, Domain Analysis, Temperature Impact, Perplexity Analysis
- Identified limitations: factual hallucination, repetition, inherent bias

### Tools & Technologies

Python, PyTorch, Hugging Face Transformers, NLTK, Matplotlib, Seaborn, WordCloud, Jupyter Notebook, Re, Collections

### Key Features

- Cross-domain language model evaluation
- Temperature parameter analysis (0.2 - 1.2)
- Quantitative metrics (Lexical Diversity, Perplexity, Unique Word Ratio)
- Research question formulation and experimentation
- Ethical AI analysis and bias assessment
- Interactive data visualizations

### Research Questions Explored

1. How does temperature affect creativity vs. coherence?
2. How well does GPT-2 adapt to different domains?
3. What are the model's limitations and ethical concerns?

---

## 🛠️ Overall Tech Stack

| Category | Tools |
|----------|-------|
| **Programming** | Python |
| **GUI** | Tkinter |
| **Data Processing** | Pandas, NumPy, Re, Collections |
| **NLP** | NLTK, PySpellChecker, Hugging Face Transformers |
| **Deep Learning** | PyTorch |
| **Machine Learning** | Scikit-Learn |
| **Visualization** | Matplotlib, Seaborn, WordCloud, Plotly |
| **Web Framework** | Streamlit |
| **Model Persistence** | Joblib, Pickle |
| **Development** | Jupyter Notebook |

---

