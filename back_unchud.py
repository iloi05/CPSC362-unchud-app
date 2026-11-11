# This file holds the back-end code for Unchud

from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from win11toast import toast
import random
import schedule
import threading
import time
import json # for game aspect
# pip install email-validator
from email_validator import validate_email, EmailNotValidError
import os
from pathlib import Path



#this creates the fast api application
app = FastAPI()
BASE_DIR = Path(__file__).parent


#create folder for Unchud in users AppData Directory
DATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "Unchud"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "assignments.json"

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
        self.load_data()    #auto loads saved assignment data whenever Assignment object created


    #json functions

    def save_data(self):
        data = {
            "assignments": self.assignment,
            "choin": self.choin
        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


    def load_data(self):
        if not DATA_FILE.exists():
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.assignment = data.get("assignments", {})
            self.choin = data.get("choin", 0)

        except (OSError, json.JSONDecodeError) as error:
            print(f"Error loading data: {error}")
    


    # helper functions
    def check_date(self, date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    def check_time(self, time):
        try:
            datetime.strptime(time, "%I:%M %p")
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
                    "message": "Invalid date format. Please use YYYY-MM-DD."}
        
        

        if not self.check_time(due_time):
            return {"success": False, 
                    "message": "Invalid time format. Please use HH:MM AM/PM."}
        


        if class_name not in self.assignment:
            self.assignment[class_name] = {}

        if due_date not in self.assignment[class_name]:
            self.assignment[class_name][due_date] = {}

        if due_time not in self.assignment[class_name][due_date]:
            self.assignment[class_name][due_date][due_time] = []

        assignments = self.assignment[class_name][due_date][due_time]

        if assignment_name not in assignments:
            assignments.append(assignment_name)

            self.save_data()

            return {
            "success": True,
            "message": f"You added {assignment_name} to your assignments!"
        }
        else:
            return {
            "success": False,
            "message": "Assignment already exists."
            }



    def mark_assignment(self, due_date, due_time, class_name, assignment_name):
        if class_name not in self.assignment:
            return {"success": False, "message": "Class not found."}

        if not self.check_date(due_date):
                    return {"success": False, 
                            "message": "Invalid date format. Please use YYYY-MM-DD."}  
        
        if not self.check_time(due_time):
                    return {"success": False, 
                        "message": "Invalid time format. Please use HH:MM AM/PM."}
        
        assignments = self.assignment[class_name].get(due_date, {}).get(due_time, [])
        if assignment_name not in assignments:
            return {"success": False, "message": "Assignment not found."}

        now = datetime.now().replace(second=0, microsecond=0)
        due = datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %I:%M %p")
        late_by = now - due

        success = (f"Congrats! You completed {assignment_name} for {class_name}! "
                   f"You get money for not being a chud! :D")

        if now < due:
            change = 50
            success += f" You've gained ${change:.2f} for completing this assignment early!"
        elif now == due:
            change = 25
            success += f" You've gained ${change:.2f} for completing this assignment on time!"
        elif late_by <= timedelta(minutes=30):
            change = -0.10
            success += (f" You've lost $0.10 for completing this assignment a few "
                        f"minutes late.")
        else:
            change = -5
            success += f" You've lost $5.00 for completing this assignment late."

        self.choin = round(self.choin + change, 2)
        success += f" Your balance is now ${self.choin:.2f}."

        if self.choin <= 0 and change < 0:
            success += (" Better start completing assignemnts on time so you "
                        "don't go into debt and become a chud! :)")

        self.assignment[class_name][due_date][due_time].remove(assignment_name)

        if not self.assignment[class_name][due_date][due_time]:
            del self.assignment[class_name][due_date][due_time]
            if not self.assignment[class_name][due_date]:
                del self.assignment[class_name][due_date]

        self.save_data()
        return {"success": True, "message": success}
           
        


    def all_assignments(self):
        # yields (class_name, due_date, due_time, assignment_name) for every pending assignment
        for class_name, dates in self.assignment.items():
            for due_date, times in dates.items():
                for due_time, names in times.items():
                    for name in names:
                        yield class_name, due_date, due_time, name

    def notif_weight(self, due_date, due_time):
        # how likely an assignment is to be picked for a notification (higher = more likely)
        PAST_DUE_WEIGHT = 1
        DUE_WITHIN_DAY_WEIGHT = 6
        DUE_WITHIN_3_DAYS_WEIGHT = 3
        LATER_WEIGHT = 1

        try:
            due = datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %I:%M %p")
        except ValueError:
            # unreadable date/time: still pickable, never crashes the scheduler
            return LATER_WEIGHT

        hours_left = (due - datetime.now()).total_seconds() / 3600
        if hours_left < 0:
            return PAST_DUE_WEIGHT
        if hours_left <= 24:
            return DUE_WITHIN_DAY_WEIGHT
        if hours_left <= 72:
            return DUE_WITHIN_3_DAYS_WEIGHT
        return LATER_WEIGHT

    def random_notif(self):
        # pick from a flat list of real assignments so empty classes/dates/times are never chosen
        pending = list(self.all_assignments())
        if not pending:
            return {"success": True, "message": "You have no assignments to be notified about :)."}

        # still random, but assignments due soon are more likely to be picked
        weights = [self.notif_weight(d, t) for _, d, t, _ in pending]
        class_name, due_date, due_time, assignment_name = random.choices(pending, weights=weights)[0]

        toast("Heads up Chud!", f"{assignment_name} for {class_name} is due {due_date} at {due_time}!")

        return {"success": True, "message": "Notification has been sent!"}

            
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
        item = item.lower()
        rank = rank.upper()
        if item not in self.catalog or rank not in self.catalog[item]:
            return {"success": False, "message": "That item doesn't exist."}
        price = self.catalog[item][rank]
        if self.tracker.choin >= price:
            self.tracker.choin = round(self.tracker.choin - price, 2)
            self.p_inventory.append((item, rank))
            self.tracker.save_data()
            return {"success": True, "message": f"Yippeeee :D! You purchased an {rank} {item} for your avatar!"}
        return {"success": False, "message": "Sorry... :( you don't have enough choins. Complete more assignments to buy items."}



#code below creates object in backend for us to utilize fastapi and data model 

tracker = Assignment()
game = Game(tracker)

#let's schedule know we should be doing this every 10 sec
schedule.every(10).seconds.do(tracker.random_notif)

#wraps the schedule execution for seperate thread
def run_scheduler():
    while True:
        # catch errors so one failed notification doesn't kill the thread for good
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(1)

#creates seperate thread so our program doesn't get stuck in infinite loop just giving notifications
schedule_thread = threading.Thread(target=run_scheduler, daemon= True)
schedule_thread.start()


#below is our API endpoint, this is how we interact with our backend functions through the API 

@app.post("/add_assignment")
def add_assignment(data: AssignmentData):
    result = tracker.add_assignment(data.due_date, data.due_time, data.class_name, data.assignment_name)
    return result

@app.post("/mark_assignment")
def mark_assignment(data: AssignmentData):
    result = tracker.mark_assignment(data.due_date, data.due_time, data.class_name, data.assignment_name)
    return result

@app.get("/assignments")
def get_assignments():
    return tracker.assignment

@app.post("/buy")
def buy(data: GameData):
    result = game.buy(data.item, data.rank)
    return result

@app.get("/home")
def home():
    return FileResponse(BASE_DIR / "Front_end_files" / "home.html")

@app.get("/shop")
def shop():
    return FileResponse(BASE_DIR / "Front_end_files" / "shop.html")

@app.get("/catalog")
def get_catalog():
    return game.catalog

@app.get("/choin")
def get_choin():
    return {"choin": tracker.choin}

@app.get("/front-unchud.js")
def front_js():
    return FileResponse(BASE_DIR / "Front_end_files" / "front-unchud.js")

app.mount("/", StaticFiles(directory=BASE_DIR / "Front_end_files"), name="frontend")