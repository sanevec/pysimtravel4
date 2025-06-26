from Road import Road, RoadState

road_generator = Road(car_generator=True)
road_1 = Road()
road_2 = Road()

print(road_generator)
print(road_1)
print(road_2)
print("------------------------DEVS 3--------------------------")
road_generator.DEVS_send_event(None, road_1)
road_1.DEVS_send_event(road_generator, road_2)
road_2.DEVS_send_event(road_1, None)


print(road_generator)
print(road_1)
print(road_2)
print("------------------------DEVS 5---------------------------")

road_generator.DEVS_process_event()
road_1.DEVS_process_event()     
road_2.DEVS_process_event()

print(road_generator)
print(road_1)
print(road_2)
print("----------------------DEVS 6----------------------------")
road_generator.DEVS_modify_state()
road_1.DEVS_modify_state()
road_2.DEVS_modify_state()
print(road_generator)
print(road_1)
print(road_2)
print("--------------------------------------------------")

print("------------------------DEVS 3--------------------------")
road_generator.DEVS_send_event(None, road_1)
road_1.DEVS_send_event(road_generator, road_2)
road_2.DEVS_send_event(road_1, None)


print(road_generator)
print(road_1)
print(road_2)
print("------------------------DEVS 5---------------------------")

road_generator.DEVS_process_event()
road_1.DEVS_process_event()     
road_2.DEVS_process_event()

print(road_generator)
print(road_1)
print(road_2)
print("----------------------DEVS 6----------------------------")
road_generator.DEVS_modify_state()
road_1.DEVS_modify_state()
road_2.DEVS_modify_state()
print(road_generator)
print(road_1)
print(road_2)
print("--------------------------------------------------")