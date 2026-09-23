# This file holds the back-end code for Unchud

from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, date
from pydantic import BaseModel
import schedule
from plyer import notification
# pip install email-validator
from email_validator import validate_email, EmailNotValidError


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

class NotificationData(BaseModel):
    timePick: str
    # for email notifications
    email: str

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
    def convert(self, time):
        # convert the time to a 24 hour format
        return datetime.strptime(time, "%I:%M %p").strftime("%H:%M")

    def check_email(self, email):
        try:
            emailAddy = validate_email(email, check_deliverability=True)
            normalized_email = emailAddy.ascii_email
            return True, normalized_email
        except EmailNotValidError as e:
            return False, str(e)

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
            # Had to change from string to list so we can remove in mark
            assign = self.assignment[class_name][due_date][due_time] = []
            assign.append(assignment_name)
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
            now = datetime.now()
            due = datetime.strptime(due_date + " " + due_time, "%Y-%m-%d %I:%M %p")
            today = date.today()
            curr_time = now.time()
            if now < due:
                self.moneyCounter += 50
                success += f" You've gained ${self.moneyCounter:.2f} for completing this assignment early!"
            elif now == due:
                self.moneyCounter += 25
                success += f" You've gained ${self.moneyCounter:.2f} for completing this assignment on time!"
            elif today == due_date and curr_time > due_time:
                self.moneyCounter -= 0.10
                success += f" You've lost $0.10 for completing this assignment a few minutes late. Your remaining balance is ${self.moneyCounter:.2f}."
            elif today > due_date:
                self.moneyCounter -= 5
                success += f" You've lost $5 for completing this assignment late. Your remaining balance is ${self.moneyCounter:.2f}."
                if self.moneyCounter == 0:
                    success += f" Your balance is now at ${self.moneyCounter:.2f}. Better start completing assignments on time so you don't go into debt and become a chud! :)"
            return {"success": True, "message": success}
           
        


    def setNotif(self, timePick, email):
        if not self.assignment:
            return {"success": False, "message": f"You have no assignments to be notified about :)."}
        else:
            if self.check_date(email):
                # less specific message encourages more app use
                notif = (f" STOP CHUDDING! You have assignemnts to do!")
                if not self.check_time(timePick):
                    return{"success": False, "message": f"Invalid time format. Please use HH:MM AM/PM."}
                cTime = self.convert(timePick)
                schedule.every().day.at(cTime).do(notification.notify, title="Unchud Reminder", message=notif)
                return {"success": True, "message": f"You will be notified daily at {timePick} about your assignments."}
            else:
                return {"success": False, "message": f"Erm...your email is invalid apparently"}

    #def money_counter(self):
    #    if self.moneyCounter == 0:
    #        return {"success": False, "message": f"Your current balance is ${self.moneyCounter}. Start completing assignments to not be a chud!"}
    #    else:
    #        return {"success": True, "message": f"Your current balance is ${self.moneyCounter}. Great job not being a chud!"}
    
    
    #def showAssignments(self):
    #    for class_name, due_dates in self.assignment.items():
    #        print(f"---{class_name}---")
#
    #        for due_date, due_times in due_dates.items():
    #            print(f"---{due_date}---")
    #            for due_time, assignment in due_times.items():
    #                print(f"{due_time} - {assignment}")

class Game(Assignment):
    def __init__(self, choin):
        self.choin = choin

    def checkBank(self, headwear, face, body, pants, feet):
        self.catalog = {
            headwear : {
                "SR" : 190,
                "R" : 170,
                "N" : 150,
                },
           
            face : {
                "SR": 180,
                "R" : 160,
                "N" : 140
            },
            
            body : {
                "SR" : 200,
                "R" : 180,
                "N" : 160
            },
            
            pants : {
                "SR" : 200,
                "R" : 180,
                "N" : 160
            },
           
            feet : {
                "SR" : 160,
                "R" : 140,
                "N" : 120
            }
        }

    def buy(self):
        choin = Assignment.moneyCounter
        if choin > 0:
            return{"success": True, "message": f"Yippeeee :D! You successfully purchased an clothing item for your avatar!"}
        elif choin == 0 or choin < 0:
            return{"success": False, "message": f"Sorry... :( you don't have enough choins to buy this item. Complete more assginments to be able to purchase items.)"}



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
def set_notif(data: NotificationData):
    result = tracker.setNotif(data.timePick, data.email)
    return result