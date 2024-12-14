import autoit
import time

def main_loop():
    # Loop until broken
    while True:
        try:     
            # Move Left
            autoit.control_send("Fortnite", "", "{a down}", mode=0)
            time.sleep(1)
            autoit.control_send("Fortnite", "", "{a up}", mode=0)
            
            # Move Right
            autoit.control_send("Fortnite", "", "{d down}", mode=0)
            time.sleep(1)
            autoit.control_send("Fortnite", "", "{d up}", mode=0)

            time.sleep(60)  # Wait before repeating the loop

        except Exception as e:
            print(e)  # Print any errors that occur
            break

if __name__ == "__main__":
    main_loop()  # Start the main program loop