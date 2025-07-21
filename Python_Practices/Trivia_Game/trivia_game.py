import random

num = int(input("How many question you want to answer?\n"))
print(f"This amount of question(s) will be asked --> {num}" )

questions = {
    "What is the shortname for python?" : "py",
    "What is the shortname for defination" : "def",
    "How much ring(s) Michael Jordan do have?" : "6",
    "What is the shortname for python?" : "py",
    "How much ring(s) Michael Jordan do have?" : "6",
    "1" : "2",
    "3" : "4",
    "What is the capital of Japan" : "Tokyo",
    "a" : "b",
    "c" : "d"
}

allrandom = {
    "How much ring(s) Michael Jordan do have?" : "6",
    "What is the shortname for python?" : "py",
    
}

sport = {
    "How much ring(s) Michael Jordan do have?" : "6",
    "1" : "2",
    "3" : "4"

}

mathmatics = {
    "What is the capital of Japan" : "Tokyo",
    "a" : "b",
    "c" : "d"
    
}

python = {
    "What is the shortname for python?" : "py",
    "What is the shortname for defination" : "def"
}


def python_trivia_game():
    category_input = input("In Which Title You Want to Answer Questions:\nALL RANDOM\nSPORT\nMATHMATICS\nPYTHON\n").lower().strip()
    print(f"You chose {category_input}")
    if category_input == "all random":
        question_dict = allrandom
    elif category_input == "sport":
        question_dict = sport
    elif category_input == "mathmatics":
        question_dict = mathmatics
    elif category_input == "python":
        question_dict = python
    else:
        question_dict = questions
    question_list = list(question_dict.keys())
    total_question = min(num, len(question_list))
    score = 0

    selected_questions = random.sample(question_list, total_question)

    for idx, ask in enumerate(selected_questions):
        print(f"{idx + 1}. {ask}")
        user_answer = input("Your Answer: ").lower().strip()
        correct_answer = question_dict[ask]
        if user_answer == correct_answer.lower():
            print("Correct!\n")
            score += 1
        else:
            print(f"Wrong. The correct answer is {correct_answer}")

    print(f"You answered all questions and here is your final score --> {score}/{total_question}")

python_trivia_game()