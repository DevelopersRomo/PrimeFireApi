import pyodbc
print("Drivers detected:")
for d in pyodbc.drivers():
    print(d)
