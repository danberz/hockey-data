import datetime
import get_funcs as gf
import psycopg2
from config import config

# Checking log file for last run date YYYY-MM-DD.
log = open('last_update.txt', 'r', newline='')
last_run = log.read()
log.close()

# Updating log file with tomorrows date for future runs.
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
log = open('last_update.txt', 'w', newline='')
log.write(tomorrow.strftime('%Y-%m-%d'))
log.close()


def insert_divisions():
    """ Getting Division data using NHL API and inserting it into the Divisions table """
    divisions = gf.get_divisions()
    # SQL Statement for inserting data into Divisions table
    sql = """ INSERT INTO divisions VALUES(%s, %s)"""
    # For each Division in the NHL API JSON
    for division in divisions.values():
        # Insert it into the Division table
        cur.execute(sql, (
            division['division_key'],
            division['name']
        ))


def insert_teams():
    """ Getting Team data using NHL API and inserting it into the Teams table """
    teams = gf.get_teams()
    # SQL Statement for inserting data into Teams table
    sql = """ INSERT INTO Teams VALUES(%s, %s, %s, %s)"""
    for team in teams.values():
        # Executing the INSERT statement.
        cur.execute(sql, (
            team['id'],
            team['name'],
            team['abbreviation'],
            team['division']
        ))


def insert_players():
    """ Getting Player data using NHL API and inserting it into the Players table """
    players = gf.get_players(gf.get_team_ids())
    # SQL Statement for inserting data into the Players table.
    sql = """ INSERT INTO Players VALUES(%s, %s, %s, %s, %s)"""
    # Going through each Player.
    for player in players.values():
        # Executing the INSERT statement.
        cur.execute(sql, (
            player['player_id'],
            player['first_name'],
            player['last_name'],
            player['number'],
            player['team']
        ))


def insert_games():
    """ Getting Game data using NHL API and inserting it into the Games table """
    # Getting Game data since last run up to, and including, today.
    games = gf.get_games(gf.get_team_ids(), last_run, str(tomorrow))
    # SQL Statement for inserting data into the Games table.
    sql = """ INSERT INTO Games VALUES(%s, %s, %s, %s, %s, %s)"""
    # Going through each Game
    for game in games.values():
        # Executing the INSERT statement.
        cur.execute(sql, (
            game['game_id'],
            game['home_team'],
            game['away_team'],
            game['home_team_score'],
            game['away_team_score'],
            game['puck_drop']
        ))


def insert_events():
    """ Getting Event data using NHL API and inserting it into the Events table """
    # Getting Game_ids since last run up to, and including, today.
    events = gf.get_events(gf.get_game_ids(gf.get_team_ids(), last_run, str(tomorrow)))
    # SQL Statement for inserting data into the Events table.
    sql = """ INSERT INTO Events VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    # Going through each event
    for event in events.values():
        # Executing the INSERT statement
        cur.execute(sql, (
            event['game'],
            event['event_id'],
            event['description'],
            event['primary_type'],
            event['secondary_type'],
            event['player_1'],
            event['player_1_type'],
            event['player_2'],
            event['player_2_type'],
            event['player_3'],
            event['player_3_type'],
            event['player_4'],
            event['player_4_type'],
            event['period'],
            event['time_remaining']
        ))


if __name__ == '__main__':
    # Connecting to Postgres.
    conn = None
    try:
        # Reading database configuration.
        params = config()
        # Connecting to the Postgres database.
        conn = psycopg2.connect(**params)
        # Creating a new cursor.
        cur = conn.cursor()
        # Getting Divisions info from the NHL API and inserting into the Divisions table.
        insert_divisions()
        # Getting Teams info from the NHL API and inserting into the Teams table.
        insert_teams()
        # Getting Players info from the NHL API and inserting into the Players table.
        insert_players()
        # Getting Events info from the NHL API and inserting into the Events table
        insert_events()
        # Committing changes to the database.
        conn.commit()
        # Closing communication with the database.
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
