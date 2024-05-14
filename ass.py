plan_output = [[{'name': 'Marriott Hotel', 'lat': 42.3629114, 'long': -71.0861978, 'travel_time': 0, 'visit_time': 0, 'time_windows': (0, 0)}, 
                {'name': 'Marriott Hotel', 'lat': 42.3629114, 'long': -71.0861978, 'travel_time': 0, 'visit_time': 0, 'time_windows': (0, 0)}], 
                [{'name': 'Marriott Hotel', 'lat': 42.3629114, 'long': -71.0861978, 'travel_time': 0, 'visit_time': 0, 'time_windows': (0, 0)}, 
                 {'name': 'BLUE COVE MANAGEMENT, INC.', 'lat': 42.360091, 'long': -71.0941599, 'travel_time': 480, 'visit_time': 60, 'time_windows': (540, 540)}, 
                 {'name': 'Massachusetts Hall', 'lat': 42.3744368, 'long': -71.118281, 'travel_time': 510, 'visit_time': 60, 'time_windows': (570, 570)}, 
                 {'name': 'Fenway Park', 'lat': 42.3466764, 'long': -71.0972178, 'travel_time': 552, 'visit_time': 60, 'time_windows': (612, 612)}, 
                 {'name': 'Churchill Hall', 'lat': 42.3387904, 'long': -71.088892, 'travel_time': 565, 'visit_time': 60, 'time_windows': (625, 625)}, 
                 {'name': 'Chinatown', 'lat': 42.3493259, 'long': -71.0621815, 'travel_time': 594, 'visit_time': 60, 'time_windows': (654, 654)}, 
                 {'name': 'K-Curl Studio', 'lat': 42.3548561, 'long': -71.0661193, 'travel_time': 602, 'visit_time': 60, 'time_windows': (662, 662)}, 
                 {'name': 'Marriott Hotel', 'lat': 42.3629114, 'long': -71.0861978, 'travel_time': 684, 'visit_time': 0, 'time_windows': (684, 684)}]]

# For each day, get first time window of second location then subtract this time from all travel_times and travel_window starting from second location of the day

for day_plan in plan_output: 

    second_loc_tw1 = day_plan[1]['travel_time']

    for loc_idx in range(1,len(day_plan)):
        day_plan[loc_idx]['travel_time'] -= second_loc_tw1

# Aggregate travel time and visit time
total_travel_time = 0
total_visit_time = 0

for day_plan in plan_output:
    day_travel_time = 0
    day_visit_time = 0

    for location in day_plan:
        print(location['name'], location['travel_time'])
        day_travel_time += location['travel_time']
        day_visit_time += location['visit_time']
    
    total_travel_time += day_travel_time
    total_visit_time += day_visit_time



print(plan_output, total_travel_time, total_visit_time)
    # for location in day_plan:

