import random

def loot_location(location):
    items = ["health pack", "ammo", "shield", "none"]
    return random.choice(items) # Random choice of items at this location

# List of locations to loot
locations = ["Warehouse", "House", "Cave", "Bridge"]

# Nested Loops
for location in locations:  # Outer loop iterates over locations
    print(f"Checking location: {location}")
    for attempt in range(2):  # Inner loop attempts to loot each location twice
        loot_result = loot(location)
        if loot_result != "none":
            print(f"Looted a {loot_result} on attempt {attempt + 1}")
        else:
            print(f"No loot found on attempt {attempt + 1}.")
    print(f"Finished checking {location}.\n")  # Ready for the next location