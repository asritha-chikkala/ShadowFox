# 🔍 Intelligent Autocorrect Keyboard System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![PySpellChecker](https://img.shields.io/badge/Library-PySpellChecker-orange)

## 📌 Project Overview

The **Intelligent Autocorrect Keyboard System** is a desktop-based spell checking and autocorrection application developed using **Python**, **Tkinter**, and **PySpellChecker**.

The system automatically detects misspelled words, suggests corrections, preserves punctuation and capitalization, and provides an interactive graphical user interface for improving text quality.

This project was developed as part of the **Shadow Fox Virtual Internship Program (Beginner Level)**.

---

## ✨ Features

### ✅ Spell Checking

* Detects misspelled words in real-time
* Supports sentence-level correction

### ✅ Intelligent Auto-Correction

* Automatically replaces misspelled words with the most probable correction
* Uses the PySpellChecker library for word correction

### ✅ Suggestions Panel

* Displays up to 5 alternative spelling suggestions
* Allows users to choose alternative corrections

### ✅ Capitalization Preservation

Maintains the original writing style:

* `hello` → `hello`
* `Hello` → `Hello`
* `HELLO` → `HELLO`

### ✅ Punctuation Preservation

Examples:

* `helo!` → `hello!`
* `(helo)` → `(hello)`
* `"helo"` → `"hello"`

### ✅ Interactive GUI

* Modern Tkinter-based user interface
* Easy-to-use correction workflow

### ✅ Statistics Dashboard

Displays:

* Total Words
* Misspelled Words
* Corrections Applied
* Text Quality Score
* Last Correction Time

### ✅ Additional Features

* Copy corrected output to clipboard
* Clear all text instantly
* Double-click suggestion replacement

---

## ⌨️ Keyboard Shortcuts

| Shortcut   | Action           |
| ---------- | ---------------- |
| `Ctrl + R` | Correct Sentence |
| `Ctrl + L` | Clear All Text   |
| `Ctrl + C` | Copy Output      |

---

## 🛠️ Technologies Used

| Technology                  | Purpose                   |
| --------------------------- | ------------------------- |
| Python                      | Core Programming Language |
| Tkinter                     | Graphical User Interface  |
| PySpellChecker              | Spell Correction Engine   |
| Regular Expressions (Regex) | Text Processing           |

---

## 📂 Project Structure

```text
Auto correct keyboard system/
│
├── logic.py          # Core correction engine
├── ui.py             # Tkinter GUI application
└── requirements.txt  # Dependencies (pyspellchecker)
```

---

## ⚙️ Installation

1. Download or clone the project files.

2. Install the required dependency:

```bash
pip install pyspellchecker
```

3. Run the application:

```bash
python ui.py
```

---

## 🚀 How to Use

1. Enter text containing spelling mistakes.
2. Click **Correct Sentence** or press `Ctrl + R`.
3. View the corrected output.
4. Review suggested alternatives in the Suggestions Panel.
5. Double-click any suggestion to replace a word.
6. Copy the corrected text using **Copy Output** or `Ctrl + C`.

---

## 🧪 Test Cases

| Input                | Expected Output       |
| -------------------- | --------------------- |
| `helo world`         | `hello world`         |
| `how are yuo`        | `how are you`         |
| `I lvoe python`      | `I love python`       |
| `This is a tset`     | `This is a test`      |
| `Helo, how are yuo?` | `Hello, how are you?` |

### Paragraph Test

**Input**

```text
Helo how are yuo? I am lerning python progrmming and its realy fun.
```

**Output**

```text
Hello how are you? I am learning python programming and its really fun.
```

---

## 📸 Screenshots

### Main Application Interface

![Main Application](screenshots/main.png)

### Test Case 1

![Statistics Dashboard](screenshots/Test-Case.png)


---





