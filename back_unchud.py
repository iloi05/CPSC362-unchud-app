# This file holds the back-end code for Unchud

from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, date
from pydantic import BaseModel
import schedule
import json # for game aspect
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

class GameData(BaseModel):
    item: str
    rank: str


class Assignment:
    # variables for all functions
    def __init__(self):
        self.assignment = {}
        self.choin = 0


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
                self.choin += 50
                success += f" You've gained ${self.choin:.2f} for completing this assignment early!"
            elif now == due:
                self.choin += 25
                success += f" You've gained ${self.choin:.2f} for completing this assignment on time!"
            elif today == due_date and curr_time > due_time:
                self.choin -= 0.10
                success += f" You've lost $0.10 for completing this assignment a few minutes late. Your remaining balance is ${self.choin:.2f}."
            elif today > due_date:
                self.choin -= 5
                success += f" You've lost $5 for completing this assignment late. Your remaining balance is ${self.choin:.2f}."
                if self.choin == 0:
                    success += f" Your balance is now at ${self.choin:.2f}. Better start completing assignments on time so you don't go into debt and become a chud! :)"
            return {"success": True, "message": success}
           
        


    def setNotif(self, timePick, email):
        if not self.assignment:
            return {"success": True, "message": f"You have no assignments to be notified about :)."}
        else:
            user_email = input("Please enter your email: ").strip()

            if self.check_email(user_email):
                print("Email is valid.")
            else: 
                print("Email not valid! Try again.")

        

            

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
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        self.catalog = {
            "headwear" : {
                "SR" : 190,
                "R" : 170,
                "N" : 150,
                },
           
            "face" : {
                "SR": 180,
                "R" : 160,
                "N" : 140
            },
            
            "body" : {
                "SR" : 200,
                "R" : 180,
                "N" : 160
            },
            
            "pants" : {
                "SR" : 200,
                "R" : 180,
                "N" : 160
            },
           
            "feet" : {
                "SR" : 160,
                "R" : 140,
                "N" : 120
            }
        }
        self.p_inventory = []

    def buy(self, item, rank):
        price = self.catalog[item][rank]
        if self.tracker.choin >= price:
            self.tracker.choin -= price
            self.p_inventory.append((item, rank))
            return{"success": True, "message": f"Yippeeee :D! You successfully purchased an clothing item for your avatar!"}
        else:
            return{"success": False, "message": f"Sorry... :( you don't have enough choins to buy this item. Complete more assginments to be able to purchase items.)"}



#code below creates object in backend for us to utilize fastapi and data model 

tracker = Assignment()
game = Game(tracker)

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

@app.post("/buy")
def buy(data: GameData):
    result = game.buy(data.item, data.rank)
    return result