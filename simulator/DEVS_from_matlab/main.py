from Road import Road


# Definition of roads

road_generator = Road(car_generator=True, )
road1 = Road()
road2 = Road()
roads = [road_generator, road1, road2]

nof_iter = 17
for i in range(nof_iter):
    print("------------------ITER " + str(i) + " ---------------------------------")
 
    for road in roads:
        road.min_time_to_complete()

    road_generator.comparison_times()
    road1.comparison_times(road_generator)
    road2.comparison_times(road1)


    print("Move in road")
    for road in roads:
        road.move_vehicles_in_road()


    
   
    roads[0].move_vehicle_next_road(roads[1])
    roads[1].move_vehicle_next_road(roads[2])
    #roads[2].move_vehicle_next_road()
 
   

    for road in roads:
        road.move_time()
        print(road)

    
    print("-------------------------------------------------------")

# print(roads[i])

# print("NEXT ITER")
# print("Calculate times")
# for road in roads:
#     road.min_time_to_complete()
#     print(road)

# print("Move in road")
# for road in roads:
#     road.move_vehicles_in_road()
#     print(road)

# print("Move next road")
# for i in range(len(roads)-1):
#     roads[i].move_vehicle_next_road(roads[i])
#     print(roads[i])

# roads[2].move_vehicle_next_road()

# print(roads[i])