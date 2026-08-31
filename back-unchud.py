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

    def notification(self, current_time, current_date):
        