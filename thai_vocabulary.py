class Word:
    def __init__(self, english, thai_phonetic, difficulty):
        self.english = english
        self.thai_phonetic = thai_phonetic
        self.difficulty = difficulty

    def __str__(self):
        return f"{self.english} = {self.thai_phonetic}"


class Quiz:
    def __init__(self):
        # Make words an instance attribute
        self.words = [
            # Easy Level Words
            Word("Hello", "สวัสดี (sà-wàt-dee)", "easy"),
            Word("Thank you", "ขอบคุณ (khàawp-khun)", "easy"),
            Word("Goodbye", "ลาก่อน (laa-gàawn)", "easy"),
            Word("Water", "น้ำ (náam)", "easy"),
            Word("Dog", "หมา (măa)", "easy"),
            Word("Cat", "แมว (maew)", "easy"),
            
            # Medium Level Words
            Word("Food", "อาหาร (aa-hăan)", "medium"),
            Word("Friend", "เพื่อน (phûuean)", "medium"),
            Word("Family", "ครอบครัว (khrôp-khrua)", "medium"),
            Word("School", "โรงเรียน (rohng-rian)", "medium"),
            Word("Teacher", "ครู (khruu)", "medium"),
            Word("Market", "ตลาด (tà-làat)", "medium"),
            
            # Hard Level Words
            Word("Happiness", "ความสุข (khwaam-sùk)", "hard"),
            Word("Education", "การศึกษา (gaan-sùek-săa)", "hard"),
            Word("Responsibility", "ความรับผิดชอบ (khwaam-ráp-phìt-châawp)", "hard"),
            Word("Environment", "สิ่งแวดล้อม (sìng-wâet-láawm)", "hard"),
            Word("Development", "การพัฒนา (gaan-phát-thá-naa)", "hard"),
            Word("Opportunity", "โอกาส (oo-gàat)", "hard"),
        ]

    def get_words_by_difficulty(self, difficulty):
        # Filter words by difficulty
        return [word for word in self.words if word.difficulty == difficulty]

    def add_word(self, english, thai_phonetic, difficulty):
        # Add a new word to the list
        self.words.append(Word(english, thai_phonetic, difficulty))
        # Sort the words by difficulty
        self.words.sort(key=lambda word: word.difficulty)
        print(f"Word '{english}' added successfully to the {difficulty} level!")


    def start_quiz(self, difficulty):
        # Get words for the selected difficulty
        words = self.get_words_by_difficulty(difficulty)

        if not words:
            print(f"No words found for {difficulty.capitalize()} level.")
            return

        # Adjust the number of words to the available population
        num_words = min(5, len(words))

        print(f"Starting a {difficulty.capitalize()} quiz with {num_words} words!")
        print("-" * 40)

        # Select random words
        import random
        selected_words = random.sample(words, num_words)
        score = 0

        for word in selected_words:
            print(f"Thai: {word.thai_phonetic}")
            answer = input("Your Answer: ").strip()

            if answer.lower() == word.english.lower():
                print("Correct!\n")
                score += 1
            else:
                print(f"Wrong! The correct answer is: {word.english}\n")

        print("-" * 40)
        print(f"Quiz Over! Your Score: {score}/{num_words}")


def main():
    print("Welcome to the Thai Vocabulary Quiz!")
    print("-" * 40)
    quiz = Quiz()
    while True:
        print("1. Study")
        print("2. Quiz")
        print("3. Add a Word")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            difficulty = input("Enter difficulty level (easy, medium, hard): ").strip().lower()
            words = quiz.get_words_by_difficulty(difficulty)
            if words:
                print(f"Words for {difficulty.capitalize()} level:")
                for word in words:
                    print(word)
            else:
                print(f"No words found for {difficulty.capitalize()} level.")
        elif choice == "2":
            difficulty = input("Enter difficulty level (easy, medium, hard): ").strip().lower()
            quiz.start_quiz(difficulty)
        elif choice == "3":
            english = input("Enter the English word: ").strip()
            thai_phonetic = input("Enter the Thai pronunciation: ").strip()
            difficulty = input("Enter difficulty level (easy, medium, hard): ").strip().lower()
            if difficulty in ["easy", "medium", "hard"]:
                quiz.add_word(english, thai_phonetic, difficulty)
            else:
                print("Invalid difficulty level. Please enter 'easy', 'medium', or 'hard'.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()