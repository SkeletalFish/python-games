import sys
import os
import importlib

import Games
games = []
for module in Games.__all__:
    if module != "__init__":
        games.append(importlib.import_module("Games."+module,"Games"))

SECTION_BREAK = "#"*64
LINE_BREAK = "_"*64

def yesno(prompt):
    input_ok = False
    while input_ok == False:
        output = input(prompt)
        output = output.upper()
        if output == "Y" or output == "N":
            input_ok = True
        else:
            print("Please enter Y or N.")
    return output

class Main(): # Main class, runs the menu and game loops, run automatically when the program is run
    def __init__(self):
        self.display_menu()
    def display_menu(self): # Displays the menus
        exit_program = False
        while not exit_program:
            print(SECTION_BREAK)
            print("Main Menu")
            print("1: Select Game")
            print("0: Exit")
            print(LINE_BREAK)
            valid_input_1 = False
            while not valid_input_1:
                selected_option = input("Please choose an option: ")
                if selected_option == "0":
                    print(SECTION_BREAK)
                    confirm = yesno("Are you sure you wish to exit? [Y/N] ")
                    if confirm == "Y":
                        #sys.exit(0)
                        valid_input_1 = True
                        exit_program = True
                elif selected_option == "1":
                    valid_input_1 = True
                    print(SECTION_BREAK)
                    print("Select Game")
                    for i in range(0,len(games)):
                        print(str(i+1) + ": " + games[i].__name__.split(".")[1].replace("_"," "))
                    print("0: Back")
                    print(LINE_BREAK)
                    valid_input_2 = False
                    while not valid_input_2:
                        selected_option = input("Please choose a game: ")
                        try:
                            val = int(selected_option)
                            if val == 0:
                                valid_input_2 = True
                            elif val in range(1,len(games)+1):
                                valid_input_2 = True
                                self.play_game(val)
                            else:
                                print("Invalid option")
                        except ValueError:
                            print("Invalid option")
                else:
                    print("Invalid option")
        print(SECTION_BREAK)
                            
    def play_game(self, game): # Runs a specified game
        if game in range(1,len(games)+1):
            games[game-1].Main()
            
    def debug(self):
        pass

Main() # Runs the main program debug loop
