# This file holds the back-end code for Unchud

from datetime import datetime, timezone

class Assignment:
    # variables for all functions
    def __init__(self):
        self.assignment = {}
        self.moneyCounter = 0

    # helper functions to check date and time
    def check_date(self, date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    def check_time(self, time):
        try:
            datetime.strptime(time, "%H:%M %p")
            return True
        except ValueError:
            return False

    # main functions for the program
    def add_assignment(self):
        assignment = input("Assignment name: ")

    def mark_assignment(self):
        current = datetime.now()
        due_date = input("When is this assignment due? (YYYY-MM-DD): ")
        if not self.check_date(due_date):
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
        due_time = input("What time is this assignment due? (HH:MM AM/PM): ")
        if not self.check_time(due_time):
            print("Invalid time format. Please use HH:MM AM/PM.")
            return
        class_name = input("What class is this assignment for? ")
        assignment_name = input("What is the name of this assignment? ")

        if due_date in self.assignment:
            if class_name in self.assignment[due_date]:
                if assignment_name in self.assignment[due_date][class_name]:
                    self.assignment[due_date][due_time][class_name][assignment_name]["completed"] = True
                    print(f"Congrats! You've finished {assignment_name} for {class_name}! :D")
                    if self.assignment[due_date][due_time] < current:
                        self.moneyCounter += 50
                    elif self.assignment[due_date][due_time] > current:
                        self.moneyCounter += 25
                    elif self.assignment[due_date][due_time] == current:
                        self.moneyCounter += 10
                    print(f"You now have ${self.moneyCounter} in your account!")
                    self.assignment[due_date][due_time][class_name][assignment_name]["completed"].remove()
                





        
        