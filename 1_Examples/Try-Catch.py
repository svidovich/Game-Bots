import random

def RiskyAction():
    randomNum = random.random() # Random Number Between 0 and 1
    if randomNum > 0.5:
        print(Error) # Will throw an error because we forgot the "'s
    else:
        return

# Try/Catch Statements
try:
    # Simulating an action that might cause an error
    RiskyAction()
except Exception as e:
    print(f"An error occurred: {e}")