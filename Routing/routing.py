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
               SELECT LocationID, Location1, Location2, Location4, Location7, Location9
               FROM distance
               WHERE LocationID IN (1,2,4,7,9);
               """)

# store all the fetched data in the ans variable
ans = cursor.fetchall()

# Since we have already selected all the data entries
# using the "SELECT *" SQL command and stored them in
# the ans variable, all we need to do now is to print
# out the ans variable
for i in ans:
    print(i)

# close the connection
connection.close()




