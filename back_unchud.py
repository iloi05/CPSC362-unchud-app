# This file holds the back-end code for Unchud

from pydantic import BaseModel
from fastapi import FastAPI
from datetime import datetime
# from zoneinfo import ZoneInfo
import time
import schedule
from plyer import notification


#this creates the fast api application
app = FastAPI()



#this created the data model which fast api will reference for what an assignment is 
#BaseModel basically helps by making sure an assignment follows the parameters for an assignment
#and also assists in creating dummy assignments when we want to test our functions
class AssignmentData(BaseModel):
    due_date: str
    due_time: str
    class_name: str
    assignment_name: str

class Assignment:
    # variables for all functions
    def __init__(self):
        self.assignment = {}
        self.moneyCounter = max(0.0)

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
    def convert(self):
        # convert the time to a 24 hour format
        return datetime.strptime(time, "%I:%M %p").strftime("%H:%M")      

    # main functions for the program
    def add_assignment(self, due_date, due_time, class_name, assignment_name):

        

        if not self.check_date(due_date):
            return {"success": False, 
                    "message: ": "Invalid date format. Please use YYYY-MM-DD."}
        
        

        if not self.check_time(due_time):
            return {"success": False, 
                    "message": "Invalid time format. Please use HH:MM AM/PM."}
        


        if class_name not in self.assignment:
            self.assignment[class_name] = {}

        if due_date not in self.assignment[class_name]:
            self.assignment[class_name][due_date] = {}

        if due_time not in self.assignment[class_name][due_date]:
            self.assignment[class_name][due_date][due_time] = {}

        if assignment_name not in self.assignment[class_name][due_date][due_time]:
            self.assignment[class_name][due_date][due_time] = f"{assignment_name}"
            return {"success": True, 
                    "message": f"You added {assignment_name} to your assignments! Time to unchud"}
        else:
            return {"sucess": False, 
                    "message": "Assignment already exists"}



    def mark_assignment(self, due_date, due_time, class_name, assignment_name):
        if class_name not in self.assignment:
            return {"success": False, "message": "Class not found."}

        if not self.check_date(due_date):
                    return {"success": False, 
                            "message: ": "Invalid date format. Please use YYYY-MM-DD."}  
        
        if not self.check_time(due_time):
                    return {"success": False, 
                        "message": "Invalid time format. Please use HH:MM AM/PM."}

        

        if assignment_name not in self.assignment[class_name][due_date][due_time]:
            return {"success": False, "message": "Assignment not found."}
        else:
            success = f"Congrats! You completed {assignment_name} for {class_name}! You get money for not being a chud! :D"
            self.assignment[class_name][due_date][due_time].remove(assignment_name)
            if datetime.now() < datetime.strptime(due_date + " " + due_time, "%Y-%m-%d %I:%M %p"):
                self.moneyCounter += 50
                success += f" You've gained ${self.moneyCounter:.2f} for completing this assignment early!"
            elif datetime.now() == datetime.strptime(due_date + " " + due_time, "%Y-%m-%d %I:%M %p"):
                self.moneyCounter += 25
                success += f" You've gained ${self.moneyCounter:.2f} for completing this assignment on time!"
            elif datetime.now() > datetime.strptime(due_date + " " + due_time, "%Y-%m-%d %I:%M %p"):
                if self.moneyCounter == 0:
                    success += f" Your balance is now at ${self.moneyCounter:.2f}. Better start completing assignments on time so you don't go into debt and become a chud! :)"
                else:
                    self.moneyCounter -= 0.10
                    success += f" You've lost $0.10 for completing this assignment late. Your remaining balance is ${self.moneyCounter:.2f}."
            else:
                self.moneyCounter -= 5
                if self.moneyCounter == 0:
                    success += f" Your balance is now at ${self.moneyCounter:.2f}. Better start completing assignments on time so you don't go into debt and become a chud! :)"
                else:
                    success += f" You've lost $5.00 for completing this assignment late. Your remaining balance is ${self.moneyCounter:.2f}."
                return {"success": True, "message": success}
        

    #    # may need to change the way the dictionary is formatted [class][duedate][time][assignment]
    #    current = datetime.now()
    #    dueDate = input("What is the due date of the assignment you want to mark? (YYYY-MM-DD): ")
    #    # idiot proofing the user input for date and time
    #    if self.check_date(dueDate):
    #        if dueDate in self.assignment:
    #            dueTime = input("What is the due time of the assignment you want to mark? (HH:MM AM/PM): ")
    #            if self.check_time(dueTime):
    #                if dueTime in self.assignment[dueDate]:
    #                    className = input("What class is the assignment for? ")
    #                    if className in self.assignment[dueDate][dueTime]:
    #                        assignmentName = input("What is the name of the assignment you want to mark? ")
    #                        if assignmentName in self.assignment[dueDate][dueTime][className]:
    #                            print(f"Congrats! You completed {assignmentName} for {className}!")
    #                            # turning work in early or on time gives big money
    #                            if current < dueDate and current < dueTime:
    #                                self.moneyCounter += 50
    #                                print(f"You've gained ${self.moneyCounter} for completing this assignment early!")
    #                            elif current == dueDate and current < dueTime:
    #                                self.moneyCounter += 25
    #                                print(f"You've gained ${self.moneyCounter} for completing this assignment on time!")
    #                            elif current == dueDate and current == dueTime:
    #                                self.moneyCounter += 15
    #                                print(f"You barely made it! You've gained ${self.moneyCounter} for completing this assignment just in time!")
    #                            elif current == dueDate and current > dueTime:
    #                                # if user turns in work late, they lose money
    #                                self.moneyCounter -= 0.10
    #                                print(f"Dang... should've done this earlier. You've lost $0.10 for completing this assignment late.")
    #                                print(f"You remaining balance is ${self.moneyCounter}.")
    #                            elif current > dueDate and current > dueTime:
    #                                self.moneyCounter -= 5
    #                                print(f"Aw man... you missed the deadline. You've lost $5.00 for completing this assignment late.")
    #                                print(f"You remaining balance is ${self.moneyCounter}.")
    #                            self.assignment[dueDate][dueTime][className].remove(assignmentName)
    #                        else:
    #                            print("Assignment not found.")
    #                    else:
    #                        print("Class not found.")
    #                else:
    #                    print("Due time not found.")
    #            else:
    #                print("Invalid time format. Please use HH:MM AM/PM.")
    #                return
    #        else:
    #            print("Due date not found.")
    #    else:
    #        print("Invalid date format. Please use YYYY-MM-DD.")
    #        return

    def setNotif(self, due_date, due_time, class_name, assignment_name, timePick):
        if class_name not in self.assignment:
            return {"success": False, "message": "Class not found."}
        
        if due_date not in self.assignment[class_name]:
            return {"success": False, "message": "Due date not found."}
        
        if due_time not in self.assignment[class_name][due_date]:
            return {"success": False, "message": "Due time not found."}
        
        if assignment_name not in self.assignment[class_name][due_date][due_time]:
            return {"success": False, "message": "Assignment not found."}
        
        if not self.check_time(timePick):
            return {"success": False, "message": "Invalid time format. Please use HH:MM AM/PM."}
        else:
            notif = (f" STOP CHUDDING! You have {assignment_name} for {class_name} due at {due_time} on {due_date}.")
            cTime = self.convert(timePick)
            schedule.every().day.at(cTime).do(notification.notify, title="Unchud Reminder", message=notif)
            return {"success": True, "message": f"You will be notified daily at {timePick} about {assignment_name} for {class_name}."}
    #    cName = input("What class is this assignment for? ")
    #    aName = input("What is the name of the assignment you want to be notified about? ")
    #    if cName not in self.assignment:
    #        print("Class not found.")
    #        return
    #    
    #    for due_date in self.assignment[cName]:
    #        for due_time in self.assignment[cName][due_date]:
    #            for assignment in self.assignment[cName][due_date][due_time]:
    #                if aName == assignment:
    #                    timePick = input("What time do you want to be notified daily? (HH:MM AM/PM): ")
    #                    if self.check_time(timePick):
    #                        notif = (f" STOP CHUDDING! You have {assignment} for {cName} due at {due_time} on {due_date}.")
    #                        print(f"You will be notified daily at {timePick} about {assignment} for {cName}.")
    #                        cTime = self.convert(timePick)
    #                        schedule.every().day.at(cTime).do(notification.notify, title="Unchud Reminder", message=notif)
    #                        return
    #                    else:
    #                        print("Invalid time format. Please use HH:MM AM/PM.")
    #                        return
    #    print("Assignment not found.")

    def money_counter(self):
        if self.moneyCounter < 0:
            return {"success": True, "message": f"You're in debt! Your current balance is ${self.moneyCounter}. Start completing assignments to pay it off and not be a chud!"}
        else:
            return {"success": True, "message": f"Your current balance is ${self.moneyCounter}."}


    
    
    
    
    def showAssignments(self):
        for class_name, due_dates in self.assignment.items():
            print(f"---{class_name}---")

            for due_date, due_times in due_dates.items():
                print(f"---{due_date}---")
                for due_time, assignment in due_times.items():
                    print(f"{due_time} - {assignment}")

#code below creates object in backend for us to utilize fastapi and data model 

tracker = Assignment()

#below is our API endpoint, this is how we interact with our backend functions through the API 

@app.post("/add_assignment")
def add_assignment(data: AssignmentData):
    result = tracker.add_assignment(data.due_date, data.due_time, data.class_name, data.assignment_name)
    return result

@app.post("/mark_assignment")
def mark_assignment(data: AssignmentData):
    result = tracker.mark_assignment(data.due_date, data.due_time, data.class_name, data.assignment_name)
    return result

@app.post("/set_notif")
def set_notif(data: AssignmentData, timePick: str):
    result = tracker.setNotif(data.due_date, data.due_time, data.class_name, data.assignment_name, timePick)
    return result


        





        



        
        