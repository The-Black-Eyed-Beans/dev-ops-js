import requests
import mysql.connector
import logging
import sys
import os
from dotenv import load_dotenv


def log_error(s):
    logging.error(s)
    print(s)
    exit(1)


def initialize_account_sequence():
    logging.info("Initializing account sequence.")
    try:
        db = mysql.connector.connect(host=os.environ.get("DB_HOST"), port=os.environ.get("DB_PORT"),
                                     user=os.environ.get("DB_USERNAME"), password=os.environ.get("DB_PASSWORD"))
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.DatabaseError):
        log_error("Error, cannot connect to database on '{}:{}', terminating process."
                  .format(os.environ.get("DB_HOST"), os.environ.get("DB_PORT")))
    except mysql.connector.errors.ProgrammingError:
        log_error("Error, access denied for given username and password, terminating process.")
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM alinedb.account_sequence")
    except mysql.connector.errors.ProgrammingError:
        log_error("Error, database name or tables did not match. Make sure you are using the most recent version of"
                  "the Aline database. Terminating process.")
    num_values = cursor.fetchall()
    if len(num_values) == 0:
        cursor.execute("INSERT INTO alinedb.account_sequence (next_val) VALUES (1)")
    else:
        logging.warning("Warning, attempted to initialize a database that already contains values for an admin user.")
    db.commit()
    logging.info("Success, account sequence initialized.")


def initialize_none_merchant():
    logging.info("Initializing 'None' merchant.")
    try:
        db = mysql.connector.connect(host=os.environ.get("DB_HOST"), port=os.environ.get("DB_PORT"),
                                     user=os.environ.get("DB_USERNAME"), password=os.environ.get("DB_PASSWORD"))
    except (mysql.connector.errors.InterfaceError, mysql.connector.errors.DatabaseError):
        log_error("Error, cannot connect to database on '{}:{}', terminating process."
                  .format(os.environ.get("DB_HOST"), os.environ.get("DB_PORT")))
        exit(1)
    except mysql.connector.errors.ProgrammingError:
        log_error("Error, access denied for given username and password, terminating process.")
        exit(1)
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM alinedb.merchant")
    except mysql.connector.errors.ProgrammingError:
        log_error("Error, database name or tables did not match. Make sure you are using the most recent version of"
                  "the Aline database. Terminating process.")
    num_values = cursor.fetchall()
    if len(num_values) == 0:
        cursor.execute("INSERT INTO alinedb.merchant (code, name) VALUE ('NONE', 'No Merchant')")
    else:
        logging.warning("Warning, attempted to initialize a database that already contains values for None merchant.")
    db.commit()
    logging.info("Success, 'None' merchant inserted.")


def create_user_and_login(path, json):
    headers = {
        "Content-Type": "application/json"
    }
    requests.post(path + ":8070/users/registration", json=json, headers=headers)

    login_request_json = {
        "username": json["username"],
        "password": json["password"]
    }
    response = requests.post(path + ":8071/login", json=login_request_json, headers=headers)

    return response.headers['Authorization']


def validate_variables():
    # Validate necessary environment variables
    required_variables = ('DB_USERNAME', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME')
    logging.info("Validating environment variables.")
    for var in required_variables:
        if os.environ.get(var) is None:
            logging.info("Error, missing environment variable for " + var)
            exit(1)
    logging.info("Success, validated environment variables.")


if __name__ == '__main__':
    logging.basicConfig(filename='.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')

    # Load environment
    load_dotenv()

    # Validate command line arguments
    if len(sys.argv) != 2:
        print("Error, invalid arguments. Expecting hostname")
        logging.info("Error, invalid arguments. Expecting hostname")

    validate_variables()
    initialize_account_sequence()
    initialize_none_merchant()
    with open('applicants.csv', 'w') as applicants_file:
        applicants_file.write('')
    with open('accounts.csv', 'w') as accounts_file:
        accounts_file.write('')
    with open('banks.csv', 'w') as banks_file:
        banks_file.write('')
    # Create admin to acquire token
    user_json = {
        "role": "admin",
        "username": "username",
        "password": "Password1!",
        "firstName": "firstName",
        "lastName": "lastName",
        "email": "email@email.email",
        "phone": "410-404-1120"
    }
    # Parse site path from command line args
    site_path = sys.argv[1]
    with open('auth_token.txt', 'w') as auth_token_file:
        auth_token_file.write(create_user_and_login(site_path, user_json))
    exit(0)
