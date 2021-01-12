# hockey-data
Python Scripts for getting hockey stats and loading them into a Postgres database

database.ini needs to have address / login info for a postgres server formatted as such:
[postgresql]
host=
database=
user=
password=

create_tables.py creates the necessary tables and constraints for the tables

create_tables_no_fks.py creates the tables without keys (this is needed until data validation is introduced)

insert_data.py gets data from the nhl api and inserts it into the database

config.py parses database.ini

get_funcs.py has all the functionality required to get the data and reformat it

last_update.txt holds the date of last run + 1
