# ALPHABET -> String lowercase alphabet
# WORDS -> List of words
# HANGMAN -> List of hangman stages
from random import *

ALPHABET = "abcdefghijklmnopqrstuvwxyz "

WORDS = ["ant","baboon","badger","bat","bear","beaver","camel","cat","clam","cobra","cougar","coyote","crow","deer","dog","donkey","duck","eagle","ferret","fox","frog","goat","goose","hawk","lion","lizard","llama","mole","monkey","moose","mouse","mule","newt","otter","owl","panda","parrot","pigeon","python","rabbit","ram","rat","raven","rhino","salmon","seal","shark","sheep","skunk","sloth","snake","spider","stork","swan","tiger","toad","trout","turkey","turtle","weasel","whale","wolf","wombat","zebra"]

HANGMAN = ['''

       
       
       
       
       
       
=========''','''

      +
      |
      |
      |
      |
      |
=========''','''

  +---+
      |
      |
      |
      |
      |
=========''','''

  +---+
  |   |
      |
      |
      |
      |
=========''', '''

  +---+
  |   |
  O   |
      |
      |
      |
=========''', '''

  +---+
  |   |
  O   |
  |   |
      |
      |
=========''', '''

  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''', '''

  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========''', '''

  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========''', '''

  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========''']

# This program WILL NOT RUN until you have added all the specified sub-programs
# Ensure that you test them first!

debug_mode = False

class Main():
    def __init__(self):
        again = True
        while again:
            game_over = False
            correct_letters = " "
            incorrect_letters = ""
            
            players = self.get_players()
            lives = self.get_lives()
            secret_word = self.get_word(players)
            
            if debug_mode == True:
                print(secret_word) # For testing purposes only

            while not game_over:
                self.display_board(secret_word, correct_letters, incorrect_letters,lives)
                guess = self.get_guess(correct_letters + incorrect_letters)
                if self.found_letter(guess, secret_word):
                    correct_letters = correct_letters + guess
                else:
                    incorrect_letters = incorrect_letters + guess
                game_over = self.has_won(secret_word, correct_letters)
                if not game_over:
                    game_over = self.has_lost(incorrect_letters,lives)
                if game_over:
                    self.display_board(secret_word, correct_letters, incorrect_letters,lives)
            again = self.play_again()

    #PROCEDURE display_board(String: p_secret_word, String p_correct_letters, String p_incorrect_letters)
    def display_board(self,p_secret_word, p_correct_letters, p_incorrect_letters, p_lives):
        index = (len(HANGMAN)-1-p_lives)+len(p_incorrect_letters)
        lives_left = p_lives - len(p_incorrect_letters)
        print(HANGMAN[index])
        print("Incorrect guesses: {0:s}".format(p_incorrect_letters))
        word = ""
        for letter in p_secret_word:
            if letter in p_correct_letters:
                word += letter
            else:
                word += "_"
            word += " "
        print(word)
        if self.has_won(p_secret_word, p_correct_letters):
            print("Well done, you guessed it!")
        elif self.has_lost(p_incorrect_letters,p_lives):
            print("Game over, you have run out of guesses!")
            print("The word was \'{0:s}\'".format(p_secret_word))
        else:
            print("Lives left: {0}".format(lives_left))
            
    # FUNCTION get_guess(String p_guessed_letters) RETURNS String
    def get_guess(self,p_guessed_letters):
        input_ok = False
        while input_ok == False:
            output = input("Guess a letter: ")
            output = output.lower()
            if output not in ALPHABET:
                print("Please enter a single lowercase letter")
            elif len(output) != 1:
                print("Please enter a single lowercase letter")
            elif output == " ":
                print("Please enter a single lowercase letter")
            elif output in p_guessed_letters:
                print("You have already guessed \'{0:s}\', try again".format(output))
            else:
                input_ok = True
        return output        

    # FUNCTION found_letter(String p_letter, String: p_search_string) RETURNS Boolean
    def found_letter(self,p_letter, p_search_string):
        if p_letter in p_search_string:
            output = True
        else:
            output = False
        return output

    # FUNCTION has_lost(p_incorrect_letters) RETURNS Boolean
    def has_lost(self,p_incorrect_letters, p_lives):
        if len(p_incorrect_letters) >= p_lives:
            output = True
        else:
            output = False
        return output

    # FUNCTION has_won(String p_secret, String p_correct) RETURNS Boolean
    def has_won(self,p_secret_word, p_correct_letters):
        output = True
        for letter in p_secret_word:
            if letter not in p_correct_letters:
                output = False
        return output

    # FUNCTION get_word(string p_players) RETURNS string
    def get_word(self,p_players):
        if p_players == "1":
            index = randint(0,len(WORDS)-1)
            output = WORDS[index]
        elif p_players == "2":
            index = 0
            while len(WORDS)%4 != 0:
                WORDS.append("")
            while index < (len(WORDS)/4):
                mult = 0
                while mult < 4:
                    if mult == 3:
                        if WORDS[int(index + mult*(len(WORDS)/4))] == "":
                            print("")
                        else:
                            print("{0:>2}: {1:10}".format(int(index + mult*(len(WORDS)/4) + 1), WORDS[int(index + mult*(len(WORDS)/4))]))
                    else:
                        if WORDS[int(index + mult*(len(WORDS)/4))] == "":
                            print("\t")
                        else:
                            print("{0:>2}: {1:10}".format(int(index + mult*(len(WORDS)/4) + 1), WORDS[int(index + mult*(len(WORDS)/4))]), end="\t")                    
                    mult += 1
                index += 1
            input_ok = False
            print(" 0: Custom word")
            while input_ok == False:
                try:
                    output = int(input("Please choose a word using the numbers above: "))
                    if output == 0:
                        word_ok = False
                        while word_ok == False:
                            output = input("Enter a word: ")
                            output = output.lower()
                            word_ok = True
                            for each in output:
                                if each not in ALPHABET:
                                    print("Please enter a word made up of lowercase letters only")
                                    word_ok = False
                                    break
                        input_ok = True
                    else:
                        output = WORDS[output-1]
                        input_ok = True
                except:
                    print("Please enter a valid number")
        else:
            output = None
        return output

    # FUNCTION play_again() RETURNS boolean
    def play_again(self):
        input_ok = False
        while input_ok == False:
            answer = input("Do you wish to play again? [Y/N] ")
            answer = answer.upper()
            if answer in ["YES","Y"]:
                print("___________________________________")
                output = True
                input_ok = True
            elif answer in ["NO","N"]:
                print("Goodbye...")
                output = False
                input_ok = True
            else:
                print("Please enter Y or N")
        return output

    # FUNCTION get_players() RETURNS string
    def get_players(self):
        input_ok = False
        while input_ok == False:
            output = input("1 or 2 players? ")
            if output == "1" or output == "2":
                input_ok = True
            else:
                print("Please enter 1 or 2")
        return output

    def get_lives(self):
        input_ok = False
        while input_ok == False:
            try:
                output = int(input("How many lives? [1 to {0:d}] ".format(len(HANGMAN)-1)))
                if output < 1 or output > len(HANGMAN)-1:
                    print("Please enter a number from 1 to {0:d}".format(len(HANGMAN)-1))
                else:
                    input_ok = True
            except:
                print("Please enter a number from 1 to {0:d}".format(len(HANGMAN)-1))
        return output
if __name__ == "__main__":
    Main()
