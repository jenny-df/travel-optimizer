"""
Standard Vehicle Routing Problem with Time Windows

If there is no solution involving every one of the nodes, the algorithm will return "No Solution"
"""

import sqlite3
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from data_scraper import * 

"""Vehicle Routing Problem (VRP) with Time Windows

   Distances in hours
"""

def router(required_locations, optional_locations, ranking_considered, transport_mode, days_traveled):

    """Convert inputs to correct format for VRP ---------------------------------------------------------------------------------------------------------------------"""
    all_locations = required_locations + optional_locations

    # used later to give drop option for these nodes
    num_optional = len(optional_locations)

    print(all_locations[-num_optional])
    
    locations_for_distance_matrix = []
    time_windows = []
    reference_dict = {}

    idx=0
    for location in all_locations:
        id_, name,lat,longi, open_time, close, visit_time = location
        locations_for_distance_matrix.append((lat,longi))
        time_windows.append((open_time,close))
        reference_dict[idx] = {'name':name, 'lat':lat, 'long':longi, 'visit_time':visit_time}
        idx+=1
        
    # print(reference_dict)

    def compute_distance_matrix(locations):
        """Creates callback to return Haversine distance between points."""
        R = 6371e3  # Earth's mean radius in meters
        distances = []

        for from_counter, from_node in enumerate(locations):
            individual_node_distance = []
            for to_counter, to_node in enumerate(locations):

                if from_counter == to_counter:
                    individual_node_distance.append(0)
                else:
                    # Use Haversine formula to compute the shortest distance over the earth’s surface between locations
                    lat1, lon1 = to_node
                    lat2, lon2 = from_node

                    phi1 = lat1 * math.pi / 180  # phi, lambda in radians
                    phi2 = lat2 * math.pi / 180
                    phi_diff = (lat2 - lat1) * math.pi / 180 # latitude diff
                    lambda_diff = (lon2 - lon1) * math.pi / 180 # longitude diff

                    a = math.sin(phi_diff / 2) * math.sin(phi_diff / 2) + math.cos(phi1) * math.cos(phi2) * math.sin(lambda_diff / 2) * math.sin(lambda_diff / 2)
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

                    distance = R * c  # distance in meters
                    individual_node_distance.append(int(distance))
            distances.append(individual_node_distance)
        return distances

    # Create distance matrix which for each node contains a list of the distances (in meters) from that node to all other nodes
    distance_matrix = compute_distance_matrix(locations_for_distance_matrix)

    # Multiply distances in meters by coefficient to obtain time it takes to traverse given distance depending on mode of transportation
    def compute_time_matrix(transport_mode, distance_matrix):
        if transport_mode == 'car':
            # going 20 mph
            return([[int(0.002*length) for length in distance] for distance in distance_matrix])
        if transport_mode == 'walking':
            # 5km/h
            return([[int(0.012*length) for length in distance] for distance in distance_matrix])
        if transport_mode == 'public transport':
            # 15 mph
            return([[int(0.0025*length) for length in distance] for distance in distance_matrix])
        if transport_mode == 'bike':
            # 12 mph
            return([[int(0.003*length) for length in distance] for distance in distance_matrix])

    # Create data model for Vehicle Routing Problem 
    def create_data_model():
        data = {}

        # square array with dimensions equal to the number of nodes, gives entry (i,j) is the time it takes to get from node i to node j
        data["time_matrix"] = compute_time_matrix(transport_mode, distance_matrix)

        # list of tuples where each tuple is (open time, closing time) in same order as each node appears in time_matrix
        data["time_windows"] = time_windows

        # number of travel days
        data["num_days"] = days_traveled

        # start and end point (hotel where traveler is staying, in our case) -> Start/end point is always first location in list
        data["depot"] = 0

        return data

    

    # Prints solution in Terminal
    # def print_solution(data, manager, routing, solution):
        print(f"Objective (distance/time travelled which we are minimizing): {solution.ObjectiveValue()}")
        time_dimension = routing.GetDimensionOrDie("Time")
        total_time = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            while not routing.IsEnd(index):
                time_var = time_dimension.CumulVar(index)
                plan_output += (
                    f"{manager.IndexToNode(index)}"
                    f" Time({solution.Min(time_var)},{solution.Max(time_var)})"
                    " -> "
                )
                index = solution.Value(routing.NextVar(index))
            time_var = time_dimension.CumulVar(index)
            plan_output += (
                f"{manager.IndexToNode(index)}"
                f" Time({solution.Min(time_var)},{solution.Max(time_var)})\n"
            )
            plan_output += f"Time of the route: {solution.Min(time_var)}min\n"
            print(plan_output)
            total_time += solution.Min(time_var)
        print(f"Total time of all routes: {total_time}min")

    # Prints solution in Terminal
    def return_solution(data, manager, routing, solution):
        # print(f"Objective (sum of the arcs/travel costs along the edges, which we are minimizing): {solution.ObjectiveValue()}")
        time_dimension = routing.GetDimensionOrDie("Time")
        total_time = 0

        print(data["time_matrix"])
        print(data["time_windows"])

        plan = []
        for day_id in range(data["num_days"]):
            day_plan = []

            index = routing.Start(day_id)
            
            while not routing.IsEnd(index):
                #Cumulative travel time when a vehicle arrives at the location with the given index
                time_var = time_dimension.CumulVar(index)
                day_plan.append({'node_number':manager.IndexToNode(index),
                                    'travel_time': solution.Min(time_var)})

                index = solution.Value(routing.NextVar(index))
            time_var = time_dimension.CumulVar(index)
            day_plan.append({'node_number':manager.IndexToNode(index),
                        'travel_time': solution.Min(time_var)})
            total_time += solution.Min(time_var)
            plan.append(day_plan)

        plan_output = []

        for day_plan in plan:
            day_plan_output = []

            for location in day_plan:
                
                node_number = location['node_number']

                name_lat_long_visit = reference_dict[node_number]

                # reference_dict[idx] = {'name':name, 'lat':lat, 'long':long, 'visit_time':visit_time}

                day_plan_output.append({'name': name_lat_long_visit['name'], 
                                        'lat': name_lat_long_visit['lat'], 
                                        'long': name_lat_long_visit['long'],
                                        'travel_time': location['travel_time']-name_lat_long_visit['visit_time'],
                                        'visit_time': name_lat_long_visit['visit_time']})
            plan_output.append(day_plan_output)

        
        # Adjust times by first travel time
        # For each day, get first time window of second location then subtract this time from all travel_times and travel_window starting from second location of the day
        
        # for day_plan in plan_output: 

        #     second_loc_tw1 = day_plan[1]['travel_time']

        #     for loc_idx in range(1,len(day_plan)):
        #         day_plan[loc_idx]['travel_time'] -= second_loc_tw1

        # Aggregate travel time and visit time
        total_travel_time = 0
        total_visit_time = 0
        sites = set()

        for day_plan in plan_output:
            # day_travel_time = 0
            day_visit_time = 0

            total_travel_time = day_plan[-1]['travel_time'] - day_plan[0]['travel_time']

            for location in day_plan:
                # print(location['name'], location['travel_time'])
                # day_travel_time += location['travel_time']
                day_visit_time += location['visit_time']
                sites.add(location['name'])
            
            # total_travel_time += day_travel_time
            total_visit_time += day_visit_time

        # return plan_output, total_travel_time, total_visit_time, num_sites_visited
        return plan_output, total_travel_time, total_visit_time, len(sites)-1

        # return plan_output, total_travel_time, total_visit_time
        # for day_plan in plan_output:
        #     for loc in day_plan:
        #         print(loc)
        # print(total_travel_time, total_visit_time)
        # print()



    """Solve the VRP with time windows."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["time_matrix"]), data["num_days"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes (set to minutes)."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        time = data["time_matrix"][from_node][to_node] 
        # + reference_dict[to_index]['visit_time']
        return time

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = "Time"
    routing.AddDimension(
        transit_callback_index,
        1440,  # allow waiting time
        1440,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time,
    )
    time_dimension = routing.GetDimensionOrDie(time)

    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data["time_windows"]):
        if location_idx == data["depot"]:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    depot_idx = data["depot"]
    for vehicle_id in range(data["num_days"]):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1]
        )

    # # Add visit time breaks
    node_visit_transit = [0] * routing.Size()
    for index in range(routing.Size()-1):
        node = manager.IndexToNode(index)
        node_visit_transit[index] = reference_dict[index]['visit_time']

    break_intervals = {}
    for v in range(manager.GetNumberOfVehicles()):
        break_intervals[v] = [
            routing.solver().FixedDurationIntervalVar(
                0,  # start min
                120,  # start max
                reference_dict[v]['visit_time'],  # duration: visit time of place
                False,  # optional: no
                f'Break for vehicle {v}')
        ]
        time_dimension.SetBreakIntervalsOfVehicle(
            break_intervals[v],  # breaks
            v,  # vehicle index
            node_visit_transit)
    
    total_travel_time_minus_depot = 0

    for node_idx in range(1,len(data["time_matrix"])):

        # don't count distance to hotel
        node_distances = data["time_matrix"][node_idx]
        individual_travel = sum(node_distances) - node_distances[0]
        total_travel_time_minus_depot += individual_travel

    total_travel_time_minus_depot = int(total_travel_time_minus_depot/2)

    # Allow node dropping for locations that are optional - works with penalty of any size
    penalty = total_travel_time_minus_depot
    for node_idx in range(num_optional-1, len(all_locations)):
        routing.AddDisjunction([manager.NodeToIndex(node_idx)], penalty)

    # Instantiate route start and end times to produce feasible times.
    for i in range(data["num_days"]):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i))
        )
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        return return_solution(data, manager, routing, solution)
    else:
        return [],0,0

locations = [('HOTEL', 'Marriott Hotel', 42.3629114, -71.0861978, 540, 1080, 0), ('ChIJpbiA_0J344kRmiVu-fjcbAA', 'Massachusetts Hall', 42.3744368, -71.118281, 540, 1020, 60), ('ChIJP7WqWapw44kRiTw1teyTNdM', 'BLUE COVE MANAGEMENT, INC.', 42.360091, -71.0941599, 540, 1020, 60)]

locations2 = [('ChIJa3g3jhBx44kRZPE5-nY3-gE', 'K-Curl Studio', 42.3548561, -71.0661193, 540, 1020, 60), ('ChIJbz8lP_Z544kRBFV6ZMsNgKI', 'Fenway Park', 42.3466764, -71.0972178, 540, 1020, 60), ('ChIJ7YKigxh644kR6D24lfwf8oA', 'Churchill Hall', 42.3387904, -71.088892, 420, 1140, 60), ('ChIJZRKlXXd644kRMqoHxDSSRD4', 'Chinatown', 42.3493259, -71.0621815, 540, 1020, 60)]

print(router(locations, locations2, False, 'car', 2))