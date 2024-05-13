"""
Standard Vehicle Routing Problem with Time Windows

If there is no solution involving every one of the nodes, the algorithm will return "No Solution"
"""

import sqlite3
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
# from data_scraper import *

"""Necessary inputs for the VRP: locations, """

# list of tuples (ID, latitude, longitude, open time, close time) for every location
# locations = get_routes_simple()
locations = [('ChIJ20bVJYdZwokRhI7esP3mYM0', 40.71881799999999, -73.9900876, 60, 1200), 
             ('ChIJ2RFUePdYwokRd5R6XF6xFD0', 40.7651258, -73.97992359999999, 240, 1309), 
             ('ChIJ8VOfr1RYwokRhil9_pcMKuc', 40.7564269, -73.9888338, 320, 1200), 
             ('ChIJ9U1mz_5YwokRosza1aAk0jM', 40.7587402, -73.9786736, 180, 1054), 
             ('ChIJCXoPsPRYwokRsV1MYnKBfaI', 40.78132409999999, -73.9739882, 0, 1440), 
             ('ChIJEdN5k4lYwokRuNPGGOZUwOQ', 40.7805136, -73.9810847, 139, 1089), 
             ('ChIJHfPuClZYwokRP2wzLQjhuEI', 40.7601775, -73.9843631, 389, 1300), 
             ('ChIJK3vOQyNawokRXEa9errdJiU', 40.7060855, -73.9968643, 0, 1440), 
             ('ChIJKxDbe_lYwokRVf__s8CPn-o', 40.7614327, -73.97762159999999, 0, 700), 
             ('ChIJMf7Re8dZwokRJ0Nyj2IixlM', 40.745866, -74.006985, 701, 1300), 
             ('ChIJN3MJ6pRYwokRiXg91flSP8Y', 40.73958770000001, -74.0088629, 567, 987),
             ('ChIJN6W-X_VYwokRTqwcBnTw1Uk', 40.7724641, -73.9834889, 4, 1434)]

locations_for_distance_matrix = []
time_windows = []
# [(lat, long) for (id,lat,long, open, close) in locations]

for location in locations:
    id,lat,long, open, close = location
    locations_for_distance_matrix.append((lat,long))
    time_windows.append((open,close))

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
                lat1 = to_node[0]
                lat2 = from_node[0]
                lon1 = to_node[1]
                lon2 = from_node[1]

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

# Coefficient to multiply distances in meters to obtain time it takes to traverse given distance depending on mode of transportation

# print([[0.001*length for length in distance] for distance in distance_matrix])

transport_mode = 'car'

def compute_time_matrix(transport_mode, distance_matrix):
    if transport_mode == 'car':
        # going 20 mph
        return([[int(0.002*length) for length in distance] for distance in distance_matrix])
    if transport_mode == 'walk':
        # 5km/h
        return([[int(0.012*length) for length in distance] for distance in distance_matrix])
    if transport_mode == 'public transportation':
        # 15 mph
        return([[int(0.0025*length) for length in distance] for distance in distance_matrix])
    if transport_mode == 'biking':
        # 12 mph
        return([[int(0.003*length) for length in distance] for distance in distance_matrix])
    
print(compute_time_matrix(transport_mode, distance_matrix))
print(time_windows)


# Round latitute and longitude to 6 decimal places (conserves within 11cm accuracy) and convert to int
# locations = [(int(round(lat,6)*(1e+6)), int(round(long,6)*(1e+6))) for (id,lat,long) in locations]

# Create time window matrix, a list of tuples where each tuple is (open time, closing time) in same order as each node appears in time_matrix
# time_windows = [(133, 831), (1071, 1374), (290, 827), (313, 1032), (12, 382), (1045, 1440), (72, 604), (348, 1086), (755, 1302), (434, 1012), (43, 659), (0,1440)]
# time_windows = [(start // 60, end // 60) for start, end in time_windows]

print(time_windows)



"""Vehicle Routing Problem (VRP) with Time Windows

   Distances in hours
"""

# Create data model for Vehicle Routing Problem 
def create_data_model():
    data = {}

    # square array with dimensions equal to the number of nodes, gives entry (i,j) is the time it takes to get from node i to node j
    data["time_matrix"] = compute_time_matrix(transport_mode, distance_matrix)

    # list of tuples where each tuple is (open time, closing time) in same order as each node appears in time_matrix
    data["time_windows"] = time_windows

    # number of vehicles (days of travel, in our case)
    data["num_vehicles"] = 5

    # start and end point of each vehicle (hotel where traveller is staying, in our case)
    data["depot"] = 0

    return data

# Prints solution in Terminal
def print_solution(data, manager, routing, solution):
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


def main():
    """Solve the VRP with time windows."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["time_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes (set to hours)."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["time_matrix"][from_node][to_node]

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
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1]
        )

    # Instantiate route start and end times to produce feasible times.
    for i in range(data["num_vehicles"]):
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
        print_solution(data, manager, routing, solution)
    else:
        print("No solution found !")


if __name__ == "__main__":
    main()


# return format [{'name': name, 'lat': lat, 'long' : long}, {}]