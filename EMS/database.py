import sqlite3

# 'sqlite3 var/ems.db'

def create_table():
    """Create the databbase table."""
    try:
        connection = sqlite3.connect('sqlite/ems.db')
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data(
            totalCarbonEmission VARCHAR(256) NOT NULL, 
            solarCarbonEmission VARCHAR(256) NOT NULL,
            evCarbonEmission VARCHAR(256) NOT NULL,
            emsCarbonEmission VARCHAR(256) NOT NULL,
            postid INTEGER PRIMARY KEY AUTOINCREMENT,
            created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chart(
            baselineEmission VARCHAR(256) NOT NULL,
            noEMSEmission VARCHAR(256) NOT NULL,
            withEMSEmission VARCHAR(256) NOT NULL,
            postid INTEGER PRIMARY KEY AUTOINCREMENT,
            created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        connection.close()
    except sqlite3.Error as error:
        print(f"Error while creating table: {error}")


def upload_data(data):
    """Upload generated data to database."""
    try:
        connection = sqlite3.connect('sqlite/ems.db')
        cursor = connection.cursor()

        # Update data
        cursor.execute(
            "INSERT INTO data(totalCarbonEmission, solarCarbonEmission, evCarbonEmission, emsCarbonEmission) "
            "VALUES (?,?,?,?,?,?,?) ",
            (data['totalCarbonEmission'], data['solarCarbonEmission'], data['evCarbonEmission'], data['emsCarbonEmission'])
        )
        connection.commit()

        cursor.execute(
            "INSERT INTO chart(baselineEmission, noEMSEmission, withEMSEmission) "
            "VALUES (?,?,?) ",
            (data['baselineEmission'], data['noEMSEmission'], data['withEMSEmission'])
        )
        connection.commit()

        # close the connection
        connection.close()
    except sqlite3.Error as error:
        print(f"Error while inserting data: {error}")


if __name__ == "__main__":
    create_table()