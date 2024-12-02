import random

def DetectEnemy():
    randomNum = random.random() # Random Number Between 0 and 1
    if randomNum > 0.5:
        return True
    else:
        return False

# While Loop
is_enemy_near = DetectEnemy()
while is_enemy_near:
    print("Taking cover!")
    is_enemy_near = DetectEnemy()