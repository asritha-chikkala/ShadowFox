import tkinter as tk
from tkinter import scrolledtext, messagebox, font
from logic import AutocorrectEngine
from datetime import datetime
import re

class AutocorrectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shadow Fox - Autocorrect Keyboard System")
        self.root.geometry("950x700")
        self.root.configure(bg="#f0f0f0")
        
        self.custom_font = font.Font(family="Segoe UI", size=11)
        self.engine = AutocorrectEngine()
        
        self.setup_ui()
    
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🔍 Autocorrect Keyboard System", 
                               font=("Segoe UI", 16, "bold"), 
                               fg="white", bg="#2c3e50")
        title_label.pack(pady=15)
        
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#f0f0f0")
        main_paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        left_frame = tk.Frame(main_paned, bg="#f0f0f0")
        main_paned.add(left_frame, width=500)
        
        right_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL, bg="#ecf0f1")
        main_paned.add(right_paned, width=350)
        
        input_label = tk.Label(left_frame, text="📝 Enter your text (with typos):", 
                               font=("Segoe UI", 12, "bold"), 
                               bg="#f0f0f0", fg="#333333")
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(left_frame, height=8, 
                                                     width=55, 
                                                     font=self.custom_font,
                                                     wrap=tk.WORD,
                                                     relief=tk.GROOVE,
                                                     borderwidth=2)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        button_frame = tk.Frame(left_frame, bg="#f0f0f0")
        button_frame.pack(pady=(0, 15))
        
        self.correct_btn = tk.Button(button_frame, text="✅ Correct Sentence", 
                                     command=self.correct, 
                                     bg="#27ae60", fg="white", 
                                     font=("Segoe UI", 11, "bold"),
                                     padx=20, pady=8,
                                     relief=tk.RAISED,
                                     cursor="hand2")
        self.correct_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="🗑 Clear All", 
                                   command=self.clear, 
                                   bg="#e74c3c", fg="white", 
                                   font=("Segoe UI", 11, "bold"),
                                   padx=20, pady=8,
                                   relief=tk.RAISED,
                                   cursor="hand2")
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.copy_btn = tk.Button(button_frame, text="📋 Copy Output", 
                                  command=self.copy_output, 
                                  bg="#3498db", fg="white", 
                                  font=("Segoe UI", 11, "bold"),
                                  padx=20, pady=8,
                                  relief=tk.RAISED,
                                  cursor="hand2")
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        
        output_label = tk.Label(left_frame, text="✨ Corrected output:", 
                                font=("Segoe UI", 12, "bold"), 
                                bg="#f0f0f0", fg="#333333")
        output_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(left_frame, height=8, 
                                                      width=55, 
                                                      font=self.custom_font,
                                                      wrap=tk.WORD,
                                                      relief=tk.GROOVE,
                                                      borderwidth=2,
                                                      bg="#ffffff")
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        suggestions_frame = tk.Frame(right_paned, bg="#ecf0f1")
        right_paned.add(suggestions_frame, height=400)
        
        suggestions_title = tk.Label(suggestions_frame, text="💡 Spelling Suggestions", 
                                     font=("Segoe UI", 12, "bold"), 
                                     bg="#34495e", fg="white", 
                                     pady=10)
        suggestions_title.pack(fill=tk.X)
        
        suggestions_listbox_frame = tk.Frame(suggestions_frame, bg="#ecf0f1")
        suggestions_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.suggestions_listbox = tk.Listbox(suggestions_listbox_frame, 
                                               font=("Segoe UI", 10), 
                                               bg="#ffffff",
                                               selectmode=tk.SINGLE,
                                               relief=tk.GROOVE,
                                               borderwidth=1,
                                               height=15)
        self.suggestions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        suggestions_scrollbar = tk.Scrollbar(suggestions_listbox_frame, orient=tk.VERTICAL, 
                                              command=self.suggestions_listbox.yview)
        suggestions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.suggestions_listbox.config(yscrollcommand=suggestions_scrollbar.set)
        
        self.suggestions_listbox.bind('<Double-Button-1>', self.replace_selected_word)
        
        self.selected_word_label = tk.Label(suggestions_frame, text="Double-click suggestion to replace", 
                                            font=("Segoe UI", 9, "italic"), 
                                            bg="#ecf0f1", fg="#7f8c8d", pady=5)
        self.selected_word_label.pack(fill=tk.X)
        
        stats_frame = tk.Frame(right_paned, bg="#ecf0f1", relief=tk.RAISED, borderwidth=1)
        right_paned.add(stats_frame, height=180)
        
        stats_title = tk.Label(stats_frame, text="📊 Statistics", 
                               font=("Segoe UI", 12, "bold"), 
                               bg="#2c3e50", fg="white", 
                               pady=8)
        stats_title.pack(fill=tk.X)
        
        stats_display_frame = tk.Frame(stats_frame, bg="#ecf0f1", padx=15, pady=10)
        stats_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_labels = {}
        stats_items = [
            ("📝 Total words:", "0"),
            ("❌ Misspelled words:", "0"),
            ("✅ Corrections applied:", "0"),
            ("📈 Text quality:", "0%"),
            ("⏱ Last corrected:", "Never")
        ]
        
        for label, value in stats_items:
            frame = tk.Frame(stats_display_frame, bg="#ecf0f1")
            frame.pack(fill=tk.X, pady=3)
            tk.Label(frame, text=label, font=("Segoe UI", 10), bg="#ecf0f1", fg="#555555").pack(side=tk.LEFT)
            self.stats_labels[label] = tk.Label(frame, text=value, font=("Segoe UI", 10, "bold"), bg="#ecf0f1", fg="#2c3e50")
            self.stats_labels[label].pack(side=tk.RIGHT)
        
        self.current_suggestions = {}
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                    font=("Segoe UI", 9), bg="#ecf0f1", fg="#7f8c8d")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.root.bind('<Control-c>', lambda e: self.copy_output())
        self.root.bind('<Control-l>', lambda e: self.clear())
        self.root.bind('<Control-r>', lambda e: self.correct())
    
    def update_statistics(self, total_words, misspellings):
        text_quality = ((total_words - misspellings) / total_words * 100) if total_words > 0 else 100
        self.stats_labels["📝 Total words:"].config(text=str(total_words))
        self.stats_labels["❌ Misspelled words:"].config(text=str(misspellings))
        self.stats_labels["✅ Corrections applied:"].config(text=str(misspellings))
        self.stats_labels["📈 Text quality:"].config(text=f"{text_quality:.1f}%")
        self.stats_labels["⏱ Last corrected:"].config(text=datetime.now().strftime("%H:%M:%S"))
        
        color = "#27ae60" if text_quality >= 90 else ("#f39c12" if text_quality >= 70 else "#e74c3c")
        self.stats_labels["📈 Text quality:"].config(fg=color)
    
    def display_suggestions(self, suggestions_dict):
        self.suggestions_listbox.delete(0, tk.END)
        self.suggestion_map = {}
        
        for word, suggestions in suggestions_dict.items():
            if suggestions:
                self.suggestions_listbox.insert(tk.END, f"► {word}")
                idx = self.suggestions_listbox.size() - 1
                self.suggestions_listbox.itemconfig(idx, fg="#e74c3c")
                for i, sug in enumerate(suggestions, 1):
                    self.suggestions_listbox.insert(tk.END, f"   {i}. {sug}")
                    idx = self.suggestions_listbox.size() - 1
                    self.suggestions_listbox.itemconfig(idx, fg="#2c3e50")
                    self.suggestion_map[idx] = (word, sug)
                self.suggestions_listbox.insert(tk.END, "")
    
    def correct(self):
        original = self.input_text.get("1.0", tk.END).strip()
        if not original:
            messagebox.showwarning("No input", "Please enter some text.")
            return
        
        self.status_bar.config(text="Processing...", fg="#e67e22")
        self.root.update()
        
        corrected, corrections, suggestions = self.engine.correct_sentence(original)
        
        misspelled_count = len([w for w in original.split() if w.lower().strip(".,!?;:\"'()") not in self.engine.spell])
        self.update_statistics(len(original.split()), misspelled_count)
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", corrected)
        
        if corrections:
            self.output_text.insert(tk.END, "\n\n" + "─" * 50 + "\n📝 Corrections made:\n")
            for c in corrections:
                self.output_text.insert(tk.END, f"  • {c}\n")
            self.status_bar.config(text=f"✓ Corrected {len(corrections)} word(s)", fg="#27ae60")
            self.display_suggestions(suggestions)
        else:
            if misspelled_count == 0:
                self.output_text.insert(tk.END, "\n\n✅ No misspellings found!")
                self.status_bar.config(text="✓ No corrections needed", fg="#27ae60")
            self.suggestions_listbox.delete(0, tk.END)
    
    def replace_selected_word(self, event):
        selection = self.suggestions_listbox.curselection()
        if not selection:
            return
        
        selected_idx = selection[0]
        
        if selected_idx in self.suggestion_map:
            misspelled, suggestion = self.suggestion_map[selected_idx]
            content = self.input_text.get("1.0", tk.END)
            pattern = r'\b' + re.escape(misspelled) + r'\b'
            new_content = re.sub(pattern, suggestion, content, count=1, flags=re.IGNORECASE)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", new_content)
            self.status_bar.config(text=f"✓ Replaced '{misspelled}' with '{suggestion}'", fg="#27ae60")
            self.root.after(2000, lambda: self.status_bar.config(text="Ready", fg="#7f8c8d"))
            self.correct()
    
    def clear(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.suggestions_listbox.delete(0, tk.END)
        self.status_bar.config(text="Cleared", fg="#7f8c8d")
        
        self.stats_labels["📝 Total words:"].config(text="0")
        self.stats_labels["❌ Misspelled words:"].config(text="0")
        self.stats_labels["✅ Corrections applied:"].config(text="0")
        self.stats_labels["📈 Text quality:"].config(text="0%")
        self.stats_labels["⏱ Last corrected:"].config(text="Never")
        self.stats_labels["📈 Text quality:"].config(fg="#2c3e50")
        
        self.root.after(1000, lambda: self.status_bar.config(text="Ready", fg="#7f8c8d"))
    
    def copy_output(self):
        output = self.output_text.get("1.0", tk.END).strip()
        if output:
            self.root.clipboard_clear()
            self.root.clipboard_append(output)
            self.status_bar.config(text="✓ Copied to clipboard!", fg="#27ae60")
            self.root.after(2000, lambda: self.status_bar.config(text="Ready", fg="#7f8c8d"))
        else:
            messagebox.showinfo("Nothing to copy", "No output to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutocorrectApp(root)
    
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()