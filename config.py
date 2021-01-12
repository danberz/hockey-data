# For reading the database.ini file and formatting it for connection
from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    # Creating a parser
    parser = ConfigParser()
    # Reading database.ini
    parser.read(filename)

    # Get section
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
