import sqlite3

# connecting to the database
connection = sqlite3.connect("map.db")

# cursor
cursor = connection.cursor()

# print statement will execute if there
# are no errors
print("Connected to the database")

# SQL command to create a table in the database
sql_command = """CREATE TABLE IF NOT EXISTS map (
    LocationID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Latitude DECIMAL(10, 6) NOT NULL,
    Longitude DECIMAL(10, 6) NOT NULL,
    OpenTime TIME,
    CloseTime TIME
);"""

# execute the statement
cursor.execute(sql_command)

# SQL command to insert data into the database
sql_command ="""INSERT INTO map (LocationID, Name, Latitude, Longitude, OpenTime, CloseTime)
VALUES
    (1, 'Coffee House', 40.7128, -74.0060, '07:00:00', '19:00:00'),
    (2, 'Park', 34.0522, -118.2437, '06:00:00', '22:00:00'),
    (3, 'Library', 51.5074, -0.1278, '09:00:00', '18:00:00'),
    (4, 'Gym', -33.8688, 151.2093, '06:30:00', '21:00:00'),
    (5, 'Restaurant', 48.8566, 2.3522, '11:30:00', '22:30:00'),
    (6, 'Museum', 55.7558, 37.6176, '10:00:00', '17:00:00'),
    (7, 'Grocery Store', 42.3601, -71.0589, '08:00:00', '20:00:00'),
    (8, 'Movie Theater', 34.0522, -118.2437, '12:00:00', '23:00:00'),
    (9, 'Convenience Store', 37.7749, -122.4194, '06:00:00', '00:00:00'),
    (10, 'Bookstore', 40.7128, -74.0060, '10:00:00', '21:00:00');"""

# execute the statement
# cursor.execute(sql_command)

# To save the changes in the files. Never skip this.
# If we skip this, nothing will be saved in the database.
connection.commit()

# execute the command to fetch all the data from the table emp
cursor.execute("SELECT * FROM map")
 
# store all the fetched data in the ans variable
ans = cursor.fetchall()

# SQL command to create a table in the database
sql_command = """CREATE TABLE IF NOT EXISTS distance (
    LocationID INT PRIMARY KEY,
    Location1 FLOAT,
    Location2 FLOAT,
    Location3 FLOAT,
    Location4 FLOAT,
    Location5 FLOAT,
    Location6 FLOAT,
    Location7 FLOAT,
    Location8 FLOAT,
    Location9 FLOAT,
    Location10 FLOAT
);"""

# execute the statement
cursor.execute(sql_command)

# SQL command to insert data into the database
sql_command ="""
INSERT INTO distance (LocationID, Location1, Location2, Location3, Location4, Location5, Location6, Location7, Location8, Location9, Location10)
VALUES
    (1, 0, 548, 776, 696, 582, 274, 502, 194, 308, 194),
    (2, 548, 0, 684, 308, 194, 502, 730, 354, 696, 742),
    (3, 776, 684, 0, 992, 878, 502, 274, 810, 468, 742),
    (4, 696, 308, 992, 0, 114, 650, 878, 502, 844, 890),
    (5, 582, 194, 878, 114, 0, 536, 764, 388, 730, 776),
    (6, 274, 502, 502, 650, 536, 0, 228, 308, 194, 240),
    (7, 502, 730, 274, 878, 764, 228, 0, 536, 194, 468),
    (8, 194, 354, 810, 502, 388, 308, 536, 0, 342, 388),
    (9, 308, 696, 468, 844, 730, 194, 194, 342, 0, 274),
    (10, 194, 742, 742, 890, 776, 240, 468, 388, 274, 0);
"""
 
# execute the statement
cursor.execute(sql_command)

# execute the command to fetch all the data from the table distance
cursor.execute("""
               SELECT Location1, Location2, Location4, Location7, Location9
               FROM distance
               WHERE LocationID IN (1,2,4,7,9);
               """)

# store all the fetched data in the ans variable
ans = cursor.fetchall()

# Create distance matrix which is a list of lists of ints
distance_matrix = [[int(distance) for distance in individual_distances] for individual_distances in ans]

# close the connection
connection.close()

"""Simple Vehicles Routing Problem (VRP)

   Distances are in meters.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Create data model for VRP 
def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = 1
    data["depot"] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")
    max_route_distance = 0
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += f" {manager.IndexToNode(index)} -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        plan_output += f"{manager.IndexToNode(index)}\n"
        plan_output += f"Distance of the route: {route_distance}m\n"
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print(f"Maximum of the route distances: {max_route_distance}m")


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = "Distance"
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

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