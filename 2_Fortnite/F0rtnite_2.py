import autoit
import time

def main_loop():
    start_time = time.time() # Record the start time
    max_duration = 150 * 60  # 150 minutes = 150 * 60 seconds
    
    # Loop until broken
    while (time.time() - start_time) < max_duration:
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

    autoit.win_close("Fortnite")

if __name__ == "__main__":
    main_loop()  # Start the main program loop