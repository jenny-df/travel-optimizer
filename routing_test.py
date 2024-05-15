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
        # print(location['name'], location['travel_time'])
        day_travel_time += location['travel_time']
        day_visit_time += location['visit_time']
    
    total_travel_time += day_travel_time
    total_visit_time += day_visit_time




# print(plan_output, total_travel_time, total_visit_time)
    # for location in day_plan:



locations = [('HOTEL', 'Marriott Hotel', 42.3629114, -71.0861978, 540, 1080, 0), 
             ('ChIJpbiA_0J344kRmiVu-fjcbAA', 'Massachusetts Hall', 42.3744368, -71.118281, 540, 1020, 60), 
             ('ChIJP7WqWapw44kRiTw1teyTNdM', 'BLUE COVE MANAGEMENT, INC.', 42.360091, -71.0941599, 540, 1020, 60)]

locations2 = [('ChIJa3g3jhBx44kRZPE5-nY3-gE', 'K-Curl Studio', 42.3548561, -71.0661193, 540, 1020, 60), 
              ('ChIJbz8lP_Z544kRBFV6ZMsNgKI', 'Fenway Park', 42.3466764, -71.0972178, 540, 1020, 60), 
              ('ChIJ7YKigxh644kR6D24lfwf8oA', 'Churchill Hall', 42.3387904, -71.088892, 420, 1140, 60), 
              ('ChIJZRKlXXd644kRMqoHxDSSRD4', 'Chinatown', 42.3493259, -71.0621815, 540, 1020, 60)]

all_locations = locations + locations2

num_optional = len(locations2)

# print(num_optional, len(all_locations))

# # for i in range(num_optional-1, len(all_locations)):
# #     print(i)

# for node_idx in range(num_optional-1, len(all_locations)):
#     print(node_idx)

time_matrix = [[0, 5, 1, 3, 4, 5, 4], [5, 0, 5, 9, 7, 9, 10], [1, 5, 0, 4, 3, 4, 5], [3, 9, 4, 0, 5, 5, 1], [4, 7, 3, 5, 0, 2, 5], [5, 9, 4, 5, 2, 0, 4], [4, 10, 5, 1, 5, 4, 0]]

total_travel_time_minus_depot = 0

for node_idx in range(1,len(time_matrix)):

     # don't count distance to hotel
    node_distances = time_matrix[node_idx]
    individual_travel = sum(node_distances) - node_distances[0]
    total_travel_time_minus_depot += individual_travel

    total_travel_time_minus_depot = total_travel_time_minus_depot/2

# print(int(total_travel_time_minus_depot))
