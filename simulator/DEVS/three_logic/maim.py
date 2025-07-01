from Road import Road, RoadState
import DEVS_1
import DEVS_2
import DEVS_3   

import os
import platform

def clear_terminal():
    """Clears the terminal screen based on the user's operating system."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

clear_terminal()



road_generator = Road(car_generator = True)
#road_generator.push_vehicle(5, 10)  # Push a vehicle to the generator road
road_1 = Road()
road_2 = Road(car_deletion = False)


print(road_generator)
print(road_1)   
print(road_2)
NOF_iter = 20


for i in range(NOF_iter):
    print(f"-------------- ITER {i}----------------------------------------")
    # First DEVS 
    DEVS_1.step_3(road_generator, road_1)
    DEVS_1.step_3(road_1, road_2)
    DEVS_1.step_3(road_2, None)
    
    # print(road_generator)
    # print(road_1)   
    # print(road_2)

    # print("           DEVS 1.5-------------------------------------")
    DEVS_1.step_5(road_generator)
    DEVS_1.step_5(road_1)
    DEVS_1.step_5(road_2) 
    
    # print(road_generator)
    # print(road_1)   
    # print(road_2)

    DEVS_1.step_6(road_generator)
    DEVS_1.step_6(road_1)       
    DEVS_1.step_6(road_2)
    # print("           DEVS 1.6-------------------------------------")
    # print(road_generator)
    # print(road_1)   
    # print(road_2)


    # Second DEVS
    # print ("         DEVS 2. 3-------------------------------------")
    DEVS_2.step_3(road_generator, None)
    DEVS_2.step_3(road_1, road_generator)       
    DEVS_2.step_3(road_2, road_1)
    
    # print(road_generator)
    # print(road_1)   
    # print(road_2)

    # print("           DEVS 2.56-------------------------------------")
    DEVS_2.step_5_6(road_generator)
    DEVS_2.step_5_6(road_1) 
    DEVS_2.step_5_6(road_2)
    
    # print(road_generator)
    # print(road_1)   
    # print(road_2)


    # Third DEVS
    # print("           DEVS 3------------------------------------")
    DEVS_3.step_3_5_6(road_generator, road_1)
    DEVS_3.step_3_5_6(road_1, road_2)
    DEVS_3.step_3_5_6(road_2, None)
    
    print(road_generator)
    print(road_1)   
    print(road_2)


    
    print("--------------------------------------------------")
 