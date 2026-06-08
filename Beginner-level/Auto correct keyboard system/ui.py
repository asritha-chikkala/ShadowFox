import tkinter as tk
from tkinter import scrolledtext, messagebox, font
from autocorrect_core import AutocorrectEngine
from ngram_predictor import NextWordPredictor
from datetime import datetime
import re


class AutocorrectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Autocorrect + Next-Word Prediction System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")

        self.custom_font = font.Font(family="Segoe UI", size=11)
        self.engine = AutocorrectEngine()
        self.predictor = NextWordPredictor()

        self.suggestion_map = {}
        self.current_predictions = []
        self._predict_after_id = None

        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="Autocorrect + Next-Word Prediction Keyboard System",
            font=("Segoe UI", 16, "bold"), fg="white", bg="#2c3e50",
        ).pack(pady=15)

        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#f0f0f0")
        main_paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left_frame = tk.Frame(main_paned, bg="#f0f0f0")
        right_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL, bg="#ecf0f1")
        far_right_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL, bg="#ecf0f1")

        main_paned.add(left_frame, width=450)
        main_paned.add(right_paned, width=360)
        main_paned.add(far_right_paned, width=300)

        tk.Label(left_frame, text="Enter your text (with typos):",
                 font=("Segoe UI", 12, "bold"), bg="#f0f0f0", fg="#333333"
                 ).pack(anchor=tk.W, pady=(0, 5))

        self.input_text = scrolledtext.ScrolledText(
            left_frame, height=10, width=50, font=self.custom_font,
            wrap=tk.WORD, relief=tk.GROOVE, borderwidth=2,
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        btn_frame = tk.Frame(left_frame, bg="#f0f0f0")
        btn_frame.pack(pady=(0, 10))

        for text, cmd, color in [
            ("Correct Sentence", self.correct, "#27ae60"),
            ("Clear All", self.clear, "#e74c3c"),
            ("Copy Output", self.copy_output, "#3498db"),
        ]:
            tk.Button(
                btn_frame, text=text, command=cmd, bg=color, fg="white",
                font=("Segoe UI", 11, "bold"), padx=15, pady=8,
                relief=tk.RAISED, cursor="hand2",
            ).pack(side=tk.LEFT, padx=5)

        tk.Label(left_frame, text="Corrected output:",
                 font=("Segoe UI", 12, "bold"), bg="#f0f0f0", fg="#333333"
                 ).pack(anchor=tk.W, pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            left_frame, height=10, width=50, font=self.custom_font,
            wrap=tk.WORD, relief=tk.GROOVE, borderwidth=2, bg="#ffffff",
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.tag_config("correction", foreground="#e74c3c", font=("Segoe UI", 11, "bold"))

        sug_frame = tk.Frame(right_paned, bg="#ecf0f1")
        right_paned.add(sug_frame, height=360)

        tk.Label(sug_frame, text="Spelling Suggestions",
                 font=("Segoe UI", 12, "bold"), bg="#34495e", fg="white", pady=10,
                 ).pack(fill=tk.X)

        listbox_wrap = tk.Frame(sug_frame, bg="#ecf0f1")
        listbox_wrap.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.suggestions_listbox = tk.Listbox(
            listbox_wrap, font=("Segoe UI", 10), bg="#ffffff",
            selectmode=tk.SINGLE, relief=tk.GROOVE, borderwidth=1, height=14,
        )
        self.suggestions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(listbox_wrap, orient=tk.VERTICAL,
                          command=self.suggestions_listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.suggestions_listbox.config(yscrollcommand=sb.set)
        self.suggestions_listbox.bind("<Double-Button-1>", self.replace_selected_word)

        tk.Label(sug_frame, text="Double-click a suggestion to apply it",
                 font=("Segoe UI", 9, "italic"), bg="#ecf0f1", fg="#7f8c8d", pady=4,
                 ).pack(fill=tk.X)

        pred_frame = tk.Frame(right_paned, bg="#ecf0f1")
        right_paned.add(pred_frame, height=240)

        tk.Label(pred_frame, text="Next-Word Predictions",
                 font=("Segoe UI", 12, "bold"), bg="#16a085", fg="white", pady=10,
                 ).pack(fill=tk.X)

        pred_btn_frame = tk.Frame(pred_frame, bg="#ecf0f1", padx=15, pady=10)
        pred_btn_frame.pack(fill=tk.BOTH, expand=True)

        self.prediction_buttons = []
        for i in range(5):
            btn = tk.Button(
                pred_btn_frame, text="",
                command=lambda idx=i: self.insert_prediction(idx),
                bg="#ecf0f1", fg="#95a5a6", font=("Segoe UI", 10),
                relief=tk.GROOVE, borderwidth=1, cursor="hand2", pady=7,
                state=tk.DISABLED,
            )
            btn.pack(fill=tk.X, pady=3)
            self.prediction_buttons.append(btn)

        stats_frame = tk.Frame(far_right_paned, bg="#ecf0f1", relief=tk.RAISED, borderwidth=1)
        far_right_paned.add(stats_frame, height=300)

        tk.Label(stats_frame, text="Statistics",
                 font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="white", pady=8,
                 ).pack(fill=tk.X)

        stats_display = tk.Frame(stats_frame, bg="#ecf0f1", padx=15, pady=10)
        stats_display.pack(fill=tk.BOTH, expand=True)

        self.stats_labels = {}
        for label, default in [
            ("Total words:", "0"),
            ("Misspelled words:", "0"),
            ("Corrections applied:", "0"),
            ("Text quality:", "100%"),
            ("Last corrected:", "Never"),
        ]:
            row = tk.Frame(stats_display, bg="#ecf0f1")
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10),
                     bg="#ecf0f1", fg="#555555").pack(side=tk.LEFT)
            val_lbl = tk.Label(row, text=default, font=("Segoe UI", 10, "bold"),
                               bg="#ecf0f1", fg="#2c3e50")
            val_lbl.pack(side=tk.RIGHT)
            self.stats_labels[label] = val_lbl

        info_frame = tk.Frame(far_right_paned, bg="#ecf0f1", relief=tk.GROOVE, borderwidth=1)
        far_right_paned.add(info_frame, height=250)

        tk.Label(info_frame, text="How to Use",
                 font=("Segoe UI", 12, "bold"), bg="#8e44ad", fg="white", pady=8,
                 ).pack(fill=tk.X)

        tk.Label(info_frame, justify=tk.LEFT, bg="#ecf0f1", fg="#555555",
                 font=("Segoe UI", 9), pady=10,
                 text=(
                     "\n"
                     "  - Type a sentence in the input box\n\n"
                     "  - Click 'Correct Sentence' or Ctrl+R\n\n"
                     "  - Double-click a suggestion to apply it\n\n"
                     "  - Click any prediction button to insert\n\n"
                     "  - Ctrl+L  ->  clear all\n\n"
                     "  - Ctrl+C  ->  copy corrected output\n"
                 ),
                 ).pack(fill=tk.BOTH, expand=True)

        self.status_bar = tk.Label(
            self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
            font=("Segoe UI", 9), bg="#ecf0f1", fg="#7f8c8d",
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_bindings(self):
        self.input_text.bind("<KeyRelease>", self._schedule_prediction)
        self.root.bind("<Control-r>", lambda e: self.correct())
        self.root.bind("<Control-l>", lambda e: self.clear())

    def _schedule_prediction(self, event=None):
        if self._predict_after_id is not None:
            self.root.after_cancel(self._predict_after_id)
        self._predict_after_id = self.root.after(300, self._run_prediction)

    def _run_prediction(self):
        self._predict_after_id = None
        text = self.input_text.get("1.0", tk.END).strip()
        if text:
            predictions = self.predictor.predict_next(text, top_n=5)
        else:
            predictions = []

        self.current_predictions = predictions
        for i, btn in enumerate(self.prediction_buttons):
            if i < len(predictions):
                word, prob = predictions[i]
                btn.config(
                    text=f"{word}  ({prob:.1f}%)",
                    bg="#ffffff", fg="#2c3e50", state=tk.NORMAL,
                )
            else:
                btn.config(text="", bg="#ecf0f1", fg="#95a5a6", state=tk.DISABLED)

    def insert_prediction(self, index):
        if index < len(self.current_predictions):
            word, _ = self.current_predictions[index]
            current = self.input_text.get("1.0", tk.END).rstrip("\n")
            separator = "" if current.endswith(" ") else " "
            self.input_text.insert(tk.END, separator + word)
            self._set_status(f"Inserted '{word}'", "#27ae60")
            self._run_prediction()

    def correct(self):
        original = self.input_text.get("1.0", tk.END).strip()
        if not original:
            messagebox.showwarning("No input", "Please enter some text first.")
            return

        self._set_status("Processing...", "#e67e22")
        self.root.update()

        corrected, corrections_made, suggestions_dict = \
            self.engine.correct_sentence(original)

        original_tokens = original.split()
        total_words = len([
            t for t in original_tokens
            if re.sub(r"\W", "", t)
        ])
        misspelled_count = len(corrections_made)

        self._update_statistics(total_words, misspelled_count)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)

        correction_targets = set()
        for c in corrections_made:
            parts = c.split(" -> ")
            if len(parts) == 2:
                correction_targets.add(parts[1].lower().strip(".,!?;:\"'()"))

        corrected_words = corrected.split()
        for idx, w in enumerate(corrected_words):
            clean = w.lower().strip(".,!?;:\"'()")
            if clean in correction_targets:
                self.output_text.insert(tk.END, w, "correction")
            else:
                self.output_text.insert(tk.END, w)
            if idx < len(corrected_words) - 1:
                self.output_text.insert(tk.END, " ")

        if corrections_made:
            self.output_text.insert(
                tk.END,
                "\n\n" + "-" * 45 + "\nCorrections made:\n",
            )
            for c in corrections_made:
                self.output_text.insert(tk.END, f"  - {c}\n")
            self._set_status(f"Corrected {len(corrections_made)} word(s)", "#27ae60")
            self._display_suggestions(suggestions_dict)
        else:
            if misspelled_count == 0:
                self.output_text.insert(tk.END, "\n\nNo misspellings found.")
            self._set_status("No corrections needed", "#27ae60")
            self.suggestions_listbox.delete(0, tk.END)

    def _display_suggestions(self, suggestions_dict: dict):
        self.suggestions_listbox.delete(0, tk.END)
        self.suggestion_map = {}

        for word, suggestions in suggestions_dict.items():
            if not suggestions:
                continue
            self.suggestions_listbox.insert(tk.END, f"-> {word}")
            idx = self.suggestions_listbox.size() - 1
            self.suggestions_listbox.itemconfig(idx, fg="#e74c3c", selectbackground="#fdecea")

            for rank, sug in enumerate(suggestions, 1):
                label = f"   {rank}.  {sug}"
                if rank == 1:
                    label += "  (best)"
                self.suggestions_listbox.insert(tk.END, label)
                idx = self.suggestions_listbox.size() - 1
                self.suggestions_listbox.itemconfig(
                    idx,
                    fg="#1a5276" if rank == 1 else "#2c3e50",
                    selectbackground="#d6eaf8",
                )
                self.suggestion_map[idx] = (word, sug)

            self.suggestions_listbox.insert(tk.END, "")

    def replace_selected_word(self, event=None):
        selection = self.suggestions_listbox.curselection()
        if not selection:
            return
        selected_idx = selection[0]
        if selected_idx not in self.suggestion_map:
            return

        misspelled, replacement = self.suggestion_map[selected_idx]
        content = self.input_text.get("1.0", tk.END)
        pattern = r"\b" + re.escape(misspelled) + r"\b"
        new_content = re.sub(pattern, replacement, content, count=1, flags=re.IGNORECASE)
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", new_content.rstrip("\n"))
        self._set_status(f"Replaced '{misspelled}' -> '{replacement}'", "#27ae60")
        self.correct()
        self._run_prediction()

    def _update_statistics(self, total_words: int, misspellings: int):
        quality = ((total_words - misspellings) / total_words * 100) \
                  if total_words > 0 else 100.0
        self.stats_labels["Total words:"].config(text=str(total_words))
        self.stats_labels["Misspelled words:"].config(text=str(misspellings))
        self.stats_labels["Corrections applied:"].config(text=str(misspellings))
        self.stats_labels["Text quality:"].config(text=f"{quality:.1f}%")
        self.stats_labels["Last corrected:"].config(
            text=datetime.now().strftime("%H:%M:%S")
        )
        color = (
            "#27ae60" if quality >= 90 else
            "#f39c12" if quality >= 70 else
            "#e74c3c"
        )
        self.stats_labels["Text quality:"].config(fg=color)

    def _set_status(self, text: str, fg: str = "#7f8c8d", duration_ms: int = 3000):
        self.status_bar.config(text=text, fg=fg)
        if duration_ms:
            self.root.after(duration_ms, lambda: self.status_bar.config(
                text="Ready", fg="#7f8c8d"
            ))

    def clear(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.suggestions_listbox.delete(0, tk.END)
        self.suggestion_map = {}
        self.current_predictions = []
        for btn in self.prediction_buttons:
            btn.config(text="", bg="#ecf0f1", fg="#95a5a6", state=tk.DISABLED)
        for key, default in [
            ("Total words:", "0"), ("Misspelled words:", "0"),
            ("Corrections applied:", "0"), ("Text quality:", "100%"),
            ("Last corrected:", "Never"),
        ]:
            self.stats_labels[key].config(text=default, fg="#2c3e50")
        self._set_status("Cleared", "#7f8c8d", duration_ms=1000)

    def copy_output(self):
        output = self.output_text.get("1.0", tk.END).strip()
        if output:
            self.root.clipboard_clear()
            self.root.clipboard_append(output)
            self._set_status("Copied to clipboard!", "#27ae60")
        else:
            messagebox.showinfo("Nothing to copy", "No output text to copy.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutocorrectApp(root)

    root.update_idletasks()
    w, h = root.winfo_width(), root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()