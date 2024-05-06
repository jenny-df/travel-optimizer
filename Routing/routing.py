import sqlite3

# connecting to the database
connection = sqlite3.connect("map.db")

# cursor
cursor = connection.cursor()

# print statement to make sure there are no errors
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
    (1, 'Coffee House', 40.7128, -74.0060, 7, 19),
    (2, 'Park', 34.0522, -118.2437, 6, 22),
    (3, 'Library', 51.5074, -0.1278, 9, 18),
    (4, 'Gym', -33.8688, 151.2093, 6, 21),
    (5, 'Restaurant', 48.8566, 2.3522, 11, 22),
    (6, 'Museum', 55.7558, 37.6176, 10, 17),
    (7, 'Grocery Store', 42.3601, -71.0589, 8, 20),
    (8, 'Movie Theater', 34.0522, -118.2437, 12, 23),
    (9, 'Convenience Store', 37.7749, -122.4194, 6, 12),
    (10, 'Bookstore', 40.7128, -74.0060, 10, 21);"""

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
    (1, 0, 6, 9, 8, 7, 3, 6, 2, 3, 2),
    (2, 6, 0, 8, 3, 2, 6, 8, 4, 8, 8),
    (3, 9, 8, 0, 11, 10, 6, 3, 9, 5, 3),
    (4, 8, 3, 11, 0, 1, 7, 10, 6, 10, 10),
    (5, 7, 2, 10, 1, 0, 6, 9, 4, 8, 9),
    (6, 3, 6, 6, 7, 6, 0, 2, 3, 2, 2),
    (7, 6, 8, 3, 10, 9, 2, 0, 6, 2, 5),
    (8, 2, 4, 9, 6, 4, 3, 6, 0, 4, 4),
    (9, 3, 8, 5, 10, 8, 2, 2, 4, 0, 3),
    (10, 2, 8, 8, 10, 9, 2, 5, 4, 3, 0);
"""
 
# execute the statement
cursor.execute(sql_command)

# execute the command to fetch some location data from the table distance
cursor.execute("""
               SELECT Location1, Location2, Location4, Location7, Location9
               FROM distance
               WHERE LocationID IN (1,2,4,7,9);
               """)

# store all the fetched data in the ans variable
ans = cursor.fetchall()

# Create distance matrix which is a list of lists of ints
distance_matrix = [[int(distance) for distance in individual_distances] for individual_distances in ans]

# execute the command to fetch open and closing times data from the table map
cursor.execute("""
               SELECT OpenTime, CloseTime
               FROM map
               WHERE LocationID IN (1,2,4,7,9);
               """)

# store all the fetched data in the ans variable
time_windows = cursor.fetchall()

# close the connection
connection.close()

"""Vehicle Routing Problem (VRP) with Time Windows

   Distances in hours
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Create data model for VRP 
def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["time_matrix"] = distance_matrix
    data["time_windows"] = time_windows
    data["num_vehicles"] = 2
    data["depot"] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
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
        """Returns the travel time between the two nodes."""
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
        30,  # allow waiting time
        30,  # maximum time per vehicle
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