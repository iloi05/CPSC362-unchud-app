from back_unchud import *

options = [1, 2, 3, 4, 5]
unchud = Assignment()

while True:
    print("Welcome to Unchud! What would you like to do?")
    print("1. Add an assignment")
    print("2. Check assignments")
    print("3. Set a notification for an assignment")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if not choice.isdigit() or int(choice) not in options:
        print("Invalid choice. Please enter a number between 1 and 4.")
        continue

    choice = int(choice)

    if choice == 1:
        unchud.add_assignment()
    elif choice == 2:
        unchud.showAssignments()
    elif choice == 3:
        unchud.setNotif()
    elif choice == 4:
        print("Exiting Unchud. Goodbye!")
        break