import os
import random
import database

CLEAR = "clear"
NONALPHA = "0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"

def generate_display_quote(words, hidden_indexes):
    display_quote = ""
    for i, word in enumerate(words):
        if i in hidden_indexes:
            for char in word:
                if char not in NONALPHA:
                    display_quote += "_"
                else:
                    display_quote += char
        else:
            display_quote += word
        display_quote += " "
    return display_quote

for source in database.get_sources():
    print(source)
source = input("Which source do you want to study?\n")
mode = int(input("What order do you want to study in?\n1. Random\n2. Chronological\n3. Score based\n"))
quotes = database.get_quotes(source, mode)
# each quote is [id, note, quote]
    
print("Enter the desired probability of a word being hidden")
quote_length_divisor = 1/float(input())

for quote_number, quote in enumerate(quotes):
    os.system(CLEAR)

    words = quote[2].split(" ")
    hidden_indexes = []
    usable_words_count = len([word for word in words if not all([char in NONALPHA for char in word])])
    while len(hidden_indexes) < int(usable_words_count / quote_length_divisor):
        num = random.randint(0, len(words) - 1)
        if all([char in NONALPHA for char in words[num]]):
            continue
        if num not in hidden_indexes:
            hidden_indexes.append(num)
    hidden_indexes.sort()

    print(f"{quote_number+1}/{len(quotes)}\n{quote[1]}\n")
    print(generate_display_quote(words, hidden_indexes))

    correct = 0
    wrong = 0
    for count, index in enumerate(hidden_indexes):
        guess = input(f"\nEnter your guess for gap {count+1}: ")
        if guess.lower() != words[index].lower().strip(NONALPHA):
            if input(f"Incorrect. The real answer was: {words[index].strip(NONALPHA)}") != "x":
                wrong += 1
            else:
                correct += 1
        else:
            correct += 1

        os.system(CLEAR)
        print(f"{quote_number+1}/{len(quotes)}\n{quote[1]}\n")
        print(generate_display_quote(words, hidden_indexes[count + 1:]))

    database.update_score(quote[0], correct, wrong)
