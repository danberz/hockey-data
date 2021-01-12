import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database for NHL info / stats without FKs """
    commands = (
        """
        CREATE TABLE Conferences (
            conference_key      INTEGER         PRIMARY KEY
        )
        """,
        """ 
        CREATE TABLE Divisions (
            division_key        INTEGER         PRIMARY KEY,
            name                varchar(255)    NOT NULL
                )
        """,
        """
        CREATE TABLE Teams (
            team_key            INTEGER         PRIMARY KEY,
            name                VARCHAR(80)     NOT NULL,
            abbreviation        VARCHAR(3)      NOT NULL,
            division            INTEGER         NOT NULL
        )
        """,
        """
        CREATE TABLE Players (
            player_key          INTEGER          PRIMARY KEY,
            first_name          VARCHAR(30)     NOT NULL,
            last_name           VARCHAR(30)     NOT NULL,
            number              INTEGER,
            team                INTEGER
        )
        """,
        """
        CREATE TABLE Games (
            game_key            INTEGER         PRIMARY KEY,
            home_team           INTEGER         NOT NULL,
            away_team           INTEGER         NOT NULL,
            home_team_score     INTEGER         NOT NULL,
            away_team_score     INTEGER         NOT NULL,
            puck_drop           DATE            NOT NULL
        )
        """,
        """
        CREATE TABLE Events (
            game_key            INTEGER         NOT NULL,
            event_key           VARCHAR(30)     NOT NULL,
            description         VARCHAR(255)    NOT NULL,
            primary_type        VARCHAR(50),
            secondary_type      VARCHAR(50),
            player_1            INTEGER,
            player_1_type       VARCHAR(50),
            player_2            INTEGER,
            player_2_type       VARCHAR(50),
            player_3            INTEGER,
            player_3_type       VARCHAR(50),
            player_4            INTEGER,
            player_4_type       VARCHAR(50),
            period              INTEGER,
            time_remaining      VARCHAR(5)
        )
        """)
    conn = None
    try:
        # Read the connection parameters
        params = config()
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # Create tables
        for command in commands:
            cur.execute(command)
        # Close communication with the PostgreSQL database server
        cur.close()
        # Commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
