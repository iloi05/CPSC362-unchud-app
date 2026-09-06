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
    def check_assignment(self):
        print(self.assignment)

    # main functions for the program
    def add_assignment(self):
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

        if due_date not in self.assignment:
            self.assignment[due_date] = {}

        if due_time not in self.assignment[due_date]:
            self.assignment[due_date][due_time] = {}

        if class_name not in self.assignment[due_date][due_time]:
            self.assignment[due_date][due_time][class_name] = {}

        if assignment_name not in self.assignment[due_date][due_time][class_name]:
            self.assignment[due_date][due_time][class_name][assignment_name] = {}
            print(f"You added {assignment_name} to your assignments! Time to unchud")
        else:
            print("Assignment already exists")
            return

        



    def mark_assignment(self):
        current = datetime.now()
        dueDate = input("What is the due date of the assignment you want to mark? (YYYY-MM-DD): ")
        if self.check_date(dueDate):
            if dueDate in self.assignment:
                dueTime = input("What is the due time of the assignment you want to mark? (HH:MM AM/PM): ")
                if self.check_time(dueTime):
                    if dueTime in self.assignment[dueDate]:
                        className = input("What class is the assignment for? ")
                        if className in self.assignment[dueDate][dueTime]:
                            assignmentName = input("What is the name of the assignment you want to mark? ")
                            if assignmentName in self.assignment[dueDate][dueTime][className]:
                                print(f"Congrats! You completed {assignmentName} for {className}!")
                                if current < dueDate and current < dueTime:
                                    self.moneyCounter += 50
                                    print(f"You've gained ${self.moneyCounter} for completing this assignment early!")
                                elif current == dueDate and current < dueTime:
                                    self.moneyCounter += 25
                                    print(f"You've gained ${self.moneyCounter} for completing this assignment on time!")
                                elif current == dueDate and current == dueTime:
                                    self.moneyCounter += 15
                                    print(f"You barely made it! You've gained ${self.moneyCounter} for completing this assignment just in time!")
                                elif current == dueDate and current > dueTime:
                                    self.moneyCounter += 5
                                    print(f"Dang... should've done this earlier, you got docked a couple dollars. You've gained ${self.moneyCounter} for completing this assignment late.")
                                elif current > dueDate and current > dueTime:
                                    self.moneyCounter -= 0.10
                                    print(f"Aw man... you missed the deadline. You've lost ${self.moneyCounter} for completing this assignment late.")
                                self.assignment[dueDate][dueTime][className].remove(assignmentName)
                            else:
                                print("Assignment not found.")
                        else:
                            print("Class not found.")
                    else:
                        print("Due time not found.")
                else:
                    print("Invalid time format. Please use HH:MM AM/PM.")
                    return
            else:
                print("Due date not found.")
        else:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
        



        
        