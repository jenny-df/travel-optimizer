"""
Standard Vehicle Routing Problem with Time Windows

If there is no solution involving every one of the nodes, the algorithm will return "No Solution"
"""

import sqlite3
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from data_scraper import * 

EARTH_R_METERS = 6371e3 
TRANSPORT_SPEEDS = {
    "car": 0.002, # 20 mph
    "walking": 0.012, # 5km/h
    'public transport' : 0.0025, # 15 mph
    'bike' : 0.003, # 12 mph
}

TRANSPORT_DAILY_LOC_LIMITS = {
    "car": 15, 
    "walking": 11,
    'public transport' : 14,
    'bike' : 15,
}

def compute_distance_matrix(locations):
    """
    Creates a distance matrix using Haversine distance between longitudes
    and latitudes.
    """
    
    distance_matrix = []

    for from_i, from_node in enumerate(locations):
        individual_node_distances = []
        for to_i, to_node in enumerate(locations):
            if from_i == to_i:
                individual_node_distances.append(0)
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

                distance = int(EARTH_R_METERS * c)  # distance in meters
                individual_node_distances.append(distance)
        distance_matrix.append(individual_node_distances)
    return distance_matrix

def compute_time_matrix(transport_mode, distance_matrix):
    """
    Creates a time matrix using the distance matrix found previously and 
    the average times for different modes of transports we support.

    Returns square list of lists with dimensions equal to the number of nodes,
    such that entry (i,j) is the time it takes to get from node i to node j
    """
    assert(transport_mode in TRANSPORT_SPEEDS, f"You are providing an invalid transport method {transport_mode}")
    return [[int(TRANSPORT_SPEEDS[transport_mode]*length) for length in distance] for distance in distance_matrix]

def print_solution(data, manager, routing, solution):
    '''
    Prints the solution that was found by the routing algorithm
    '''
    print(f"Objective (distance/time travelled which we are minimizing): {solution.ObjectiveValue()}")

    time_dimension = routing.GetDimensionOrDie("Time")
    total_time = 0
    for vehicle_id in range(data["num_days"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        time_var = time_dimension.CumulVar(index)
        while not routing.IsEnd(index):
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

def return_solution(data, manager, routing, solution, reference_list):
    '''
    Finds the final output of the problem
    '''
    time_dimension = routing.GetDimensionOrDie("Time")
    total_travel_time = 0
    total_visit_time = 0
    sites = set()
    plan = []

    for day_i in range(data["num_days"]):
        day_plan = []
        i = routing.Start(day_i)
        ending = False

        while True:
            if routing.IsEnd(i):
                ending = True

            #Cumulative travel time when a vehicle arrives at the location with the given index
            time_var = time_dimension.CumulVar(i)
            node_number = manager.IndexToNode(i)
            ref = reference_list[node_number]
 
            day_plan.append({'name': ref['name'], 
                            'lat': ref['lat'], 
                            'long': ref['long'],
                            'travel_time': solution.Min(time_var) - ref['visit_time'],
                            'visit_time': ref['visit_time']})
        
            total_visit_time += ref['visit_time']
            
            sites.add(ref['name'])

            if ending:
                break

            i = solution.Value(routing.NextVar(i))
   
        total_travel_time += day_plan[-1]['travel_time'] - day_plan[0]['travel_time']
        plan.append(day_plan)

    return plan, total_travel_time, total_visit_time, len(sites)-1

# Prints solution in Terminal
def return_solution(data, manager, routing, solution):
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


def create_time_callback(manager, time_matrix):
    def time_callback(from_i, to_i):
        """Returns the travel time between the two nodes (set to minutes)."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_i)
        to_node = manager.IndexToNode(to_i)
        return time_matrix[from_node][to_node] 
    return time_callback

def router(required, optional, ranking_considered, transport_mode, days_traveled):
    """
    Finds the optimal route between the given required and optional locations given a ranking,
    transportation mode, and number of days (number of vehicles)
    """

    locations_for_distance_matrix = []
    time_windows = []
    reference_list = []
    
    locations = required + optional # all locations
    total_num_locations = len(locations)
    num_loc_per_day = total_num_locations / days_traveled

    # Truncates locations if it seems excessive per day
    if num_loc_per_day > TRANSPORT_DAILY_LOC_LIMITS[transport_mode]:
        dif = num_loc_per_day - TRANSPORT_DAILY_LOC_LIMITS[transport_mode]
        num_locs_dif = round(dif * days_traveled)
        total_num_locations -= num_locs_dif
        locations = locations[:total_num_locations]

    if len(locations) < len(required):
        locations = required

    for _, name, latitude, longitude, open_time, close_time, visit_time in locations:
        locations_for_distance_matrix.append((latitude, longitude))
        time_windows.append((open_time, close_time))
        reference_list.append({'name':name, 'lat':latitude, 'long':longitude, 'visit_time':visit_time})

    distance_matrix = compute_distance_matrix(locations_for_distance_matrix)

    """Solve the VRP with time windows."""
    data = {
        "time_matrix": compute_time_matrix(transport_mode, distance_matrix),
        "time_windows": time_windows,
        "num_days": days_traveled,
        "depot": 0, # start and end point's index (hotel)
    }

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data["time_matrix"]), data["num_days"], data["depot"]
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    time_callback = create_time_callback(manager, data["time_matrix"])
    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint
    routing.AddDimension(
        transit_callback_index,
        1440,  # allow waiting time (1 Day)
        1440,  # maximum time per vehicle (1 Day)
        False,  # Don't force start cumul to zero.
        "Time",
    )
    time_dimension = routing.GetDimensionOrDie("Time")

    # Add time window constraints for each location except depot
    for location_i, time_window in enumerate(data["time_windows"]):
        if location_i != data["depot"]:
            index = manager.NodeToIndex(location_i)
            time_dimension.CumulVar(index).SetRange(*time_window)

    # Add time window constraints for each vehicle start node
    depot_window = data["time_windows"][data["depot"]]
    for vehicle_id in range(data["num_days"]):
        i = routing.Start(vehicle_id)
        time_dimension.CumulVar(i).SetRange(*depot_window)

    # Add visit time breaks (ASK)
    node_visit_transit = [0] * routing.Size()
    for i, ref in enumerate(reference_list):
        node_visit_transit[i] = ref['visit_time']

    for v in range(min(len(reference_list), manager.GetNumberOfVehicles())):
        time_dimension.SetBreakIntervalsOfVehicle(
            [routing.solver().FixedDurationIntervalVar(
                0,  # start min
                120,  # start max
                reference_list[v]['visit_time'],  # duration: visit time of place
                False,  # optional: no
                f'Break for vehicle {v}')
            ],  # breaks
            v,  # vehicle index
            node_visit_transit)

    if optional:
        total_travel_time_minus_depot = 0
        for node_distances in data["time_matrix"][1:]: # skips hotel
            total_travel_time_minus_depot += (sum(node_distances) - node_distances[0]) # skips hotel

        total_travel_time_minus_depot = int(total_travel_time_minus_depot/2)

        penalty = total_travel_time_minus_depot

        if ranking_considered:
            percent_penalty = 0
            for node_idx in range(len(locations),0,-1):
                # add penalty that is 5% larger for each higher ranking
                penalty = penalty*(1+percent_penalty)
                routing.AddDisjunction([manager.NodeToIndex(node_idx)], penalty)
                percent_penalty += 0.05

        else:
            # Allow node dropping for locations that are optional - set penalty to be greater than sum of all distances not going to depot
            for node_idx in range(len(optional)-1, len(locations)):
                routing.AddDisjunction([manager.NodeToIndex(node_idx)], penalty)

    # Instantiate route start and end times to produce feasible times
    for i in range(data["num_days"]):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i))
        )
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = 20
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
    
    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
        return return_solution(data, manager, routing, solution, reference_list)
    return [], 0, 0, 0

if __name__ == '__main__':


    locations = [('HOTEL', 'Marriott Hotel', 42.3629114, -71.0861978, 540, 1080, 0), ('ChIJpbiA_0J344kRmiVu-fjcbAA', 'Massachusetts Hall', 42.3744368, -71.118281, 540, 1020, 60), ('ChIJP7WqWapw44kRiTw1teyTNdM', 'BLUE COVE MANAGEMENT, INC.', 42.360091, -71.0941599, 540, 1020, 60), ('ChIJa3g3jhBx44kRZPE5-nY3-gE', 'K-Curl Studio', 42.3548561, -71.0661193, 540, 1020, 60), ('ChIJbz8lP_Z544kRBFV6ZMsNgKI', 'Fenway Park', 42.3466764, -71.0972178, 540, 1020, 60), ('ChIJ7YKigxh644kR6D24lfwf8oA', 'Churchill Hall', 42.3387904, -71.088892, 420, 1140, 60), ('ChIJZRKlXXd644kRMqoHxDSSRD4', 'Chinatown', 42.3493259, -71.0621815, 540, 1020, 60)]

    locations2 = [('ChIJpbiA_0J344kRmiVu-fjcbAA', 'Massachusetts Hall', 42.3744368, -71.118281, 540, 1020, 60), ('ChIJP7WqWapw44kRiTw1teyTNdM', 'BLUE COVE MANAGEMENT, INC.', 42.360091, -71.0941599, 540, 1020, 60), ('ChIJa3g3jhBx44kRZPE5-nY3-gE', 'K-Curl Studio', 42.3548561, -71.0661193, 540, 1020, 60), ('ChIJbz8lP_Z544kRBFV6ZMsNgKI', 'Fenway Park', 42.3466764, -71.0972178, 540, 1020, 60), ('ChIJ7YKigxh644kR6D24lfwf8oA', 'Churchill Hall', 42.3387904, -71.088892, 420, 1140, 60)]

    #42.3744368

    print(router(locations2, [], True, 'car', 2))
