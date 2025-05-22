import pandas as pd
from src.database.data import Database

if __name__ == "__main__":
    db = Database()  # Ensure class name is capitalized
    columns, data = db.fetch_data()

    # Convert to pandas DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Print the DataFrame
    print(df)


# use this snipit of code to insert every day data in database
# BULK INSERT Hyyzo
# FROM 'C:\Users\flips\Downloads\today.csv'
# WITH (
#     FIELDTERMINATOR = ',',
#     ROWTERMINATOR = '\n',
#     FIRSTROW = 2 -- Agar pehli row header hai toh 2, nahi toh 1
# );

# use this code to delete the data of specific date
# DELETE FROM Hyyzo
# WHERE CAST(action_date AS DATE) = '2025-05-20';

