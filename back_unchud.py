# This file holds the back-end code for Unchud

from datetime import datetime, timezone

import time
import schedule
from plyer import notification

class Assignment:
    # variables for all functions
    def __init__(self):
        self.assignment = {}
        self.moneyCounter = 0

    # helper functions
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
        # may need to change the way the dictionary is formatted [class][duedate][time][assignment]
        current = datetime.now()
        dueDate = input("What is the due date of the assignment you want to mark? (YYYY-MM-DD): ")
        # idiot proofing the user input for date and time
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
                                # turning work in early or on time gives big money
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
                                    # if user turns in work late, they lose money
                                    self.moneyCounter -= 0.10
                                    print(f"Dang... should've done this earlier. You've lost $0.10 for completing this assignment late.")
                                    print(f"You remaining balance is ${self.moneyCounter}.")
                                elif current > dueDate and current > dueTime:
                                    self.moneyCounter -= 5
                                    print(f"Aw man... you missed the deadline. You've lost $5.00 for completing this assignment late.")
                                    print(f"You remaining balance is ${self.moneyCounter}.")
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

def setNotif(self, dueDate, dueTime, className, assignment):
    # test comment
    cName = input("What class is this assignment for? ")
    aName = input("What is the name of the assignment you want to be notified about? ")
    for dueDate in self.assignment:
        for dueTime in self.assignment[dueDate]:
            for className in self.assignment[dueDate][dueTime]:
                if cName == className:
                    for assignment in self.assignment[dueDate][dueTime][className]:
                        if aName == assignment:
                            timePick = input("What time do you want to be notified daily? (HH:MM AM/PM): ")
                            if self.check_time(timePick):
                                schedule.every().day.at(timePick).do(self.send_notification, dueDate, dueTime, className, assignment)
                                print(f"You will be notified daily at {timePick} about {assignment} for {className}.")
                            else:
                                print("Invalid time format. Please use HH:MM AM/PM.")
                                return
                        else:
                            print("Assignment not found.")
                else:
                    print("Class not found.")
    




        



        
        