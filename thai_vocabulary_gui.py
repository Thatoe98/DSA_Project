import tkinter as tk
from tkinter import ttk, messagebox, simpledialog  # Added simpledialog import
from thai_vocabulary import Quiz

class ThaiVocabularyApp:
    def __init__(self, root):
        self.quiz = Quiz()
        self.root = root
        self.root.title("Thai Vocabulary Quiz")
        self.create_widgets()

    def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Title Label
        ttk.Label(self.main_frame, text="Thai Vocabulary Quiz", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        # Buttons
        ttk.Button(self.main_frame, text="Study", command=self.study_words).grid(row=1, column=0, pady=5, sticky="ew")
        ttk.Button(self.main_frame, text="Quiz", command=self.start_quiz).grid(row=2, column=0, pady=5, sticky="ew")
        ttk.Button(self.main_frame, text="Add Word", command=self.add_word).grid(row=3, column=0, pady=5, sticky="ew")
        ttk.Button(self.main_frame, text="Exit", command=self.root.quit).grid(row=4, column=0, pady=5, sticky="ew")

    def study_words(self):
        def show_words():
            difficulty = difficulty_var.get().lower()
            words = self.quiz.get_words_by_difficulty(difficulty)
            if words:
                words_text.set("\n".join(str(word) for word in words))
            else:
                words_text.set(f"No words found for {difficulty.capitalize()} level.")

        study_window = tk.Toplevel(self.root)
        study_window.title("Study Words")
        ttk.Label(study_window, text="Select Difficulty:").grid(row=0, column=0, padx=10, pady=5)
        difficulty_var = tk.StringVar(value="easy")
        ttk.Combobox(study_window, textvariable=difficulty_var, values=["easy", "medium", "hard"]).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(study_window, text="Show Words", command=show_words).grid(row=1, column=0, columnspan=2, pady=5)
        words_text = tk.StringVar()
        ttk.Label(study_window, textvariable=words_text, wraplength=300).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def start_quiz(self):
        def start():
            difficulty = difficulty_var.get().lower()
            quiz_window.destroy()
            self.run_quiz(difficulty)

        quiz_window = tk.Toplevel(self.root)
        quiz_window.title("Start Quiz")
        ttk.Label(quiz_window, text="Select Difficulty:").grid(row=0, column=0, padx=10, pady=5)
        difficulty_var = tk.StringVar(value="easy")
        ttk.Combobox(quiz_window, textvariable=difficulty_var, values=["easy", "medium", "hard"]).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(quiz_window, text="Start", command=start).grid(row=1, column=0, columnspan=2, pady=10)

    def run_quiz(self, difficulty):
        words = self.quiz.get_words_by_difficulty(difficulty)
        if not words:
            messagebox.showinfo("Quiz", f"No words found for {difficulty.capitalize()} level.")
            return

        import random
        selected_words = random.sample(words, min(5, len(words)))
        score = 0

        for word in selected_words:
            # Use simpledialog.askstring for user input
            answer = simpledialog.askstring("Quiz", f"Thai: {word.thai_phonetic}\nYour Answer:")
            if answer and answer.lower() == word.english.lower():
                score += 1

        messagebox.showinfo("Quiz Over", f"Your Score: {score}/{len(selected_words)}")

    def add_word(self):
        def save_word():
            english = english_var.get().strip()
            thai_phonetic = thai_var.get().strip()
            difficulty = difficulty_var.get().lower()
            if difficulty in ["easy", "medium", "hard"]:
                self.quiz.add_word(english, thai_phonetic, difficulty)
                messagebox.showinfo("Success", f"Word '{english}' added successfully!")
                add_window.destroy()
            else:
                messagebox.showerror("Error", "Invalid difficulty level. Please enter 'easy', 'medium', or 'hard'.")

        add_window = tk.Toplevel(self.root)
        add_window.title("Add Word")
        ttk.Label(add_window, text="English Word:").grid(row=0, column=0, padx=10, pady=5)
        english_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=english_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(add_window, text="Thai Pronunciation:").grid(row=1, column=0, padx=10, pady=5)
        thai_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=thai_var).grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(add_window, text="Difficulty:").grid(row=2, column=0, padx=10, pady=5)
        difficulty_var = tk.StringVar(value="easy")
        ttk.Combobox(add_window, textvariable=difficulty_var, values=["easy", "medium", "hard"]).grid(row=2, column=1, padx=10, pady=5)
        ttk.Button(add_window, text="Save", command=save_word).grid(row=3, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ThaiVocabularyApp(root)
    root.mainloop()
