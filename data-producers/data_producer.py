import requests
import mysql.connector
import logging
import sys
import os
import json as json_format
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


def create_application(path, id, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    body = {
        "applicationType": "CHECKING",
        "noApplicants": "true",
        "applicantIds": [id]
    }
    logging.info("Registering applicant " + json_format.dumps(body))
    try:
        response = requests.post(path + ":8071/applications", json=body, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")

    if response.status_code == 201:
        logging.info("Success, registered applicant.")
        return "{},{}".format(response.json()["createdAccounts"][0]["accountNumber"],
                              response.json()["createdMembers"][0]["membershipId"])
    elif response.status_code == 404:
        logging.warning("Warning, applicant id did not match anything in the table. Failed to insert")
        logging.warning(response.text)
    elif response.status_code == 500:
        logging.warning("Warning, internal server error, potentially caused by attempting to register an already-"
                        "registered user. Failed to insert.")
        logging.warning(response.text)
    else:
        logging.warning("Warning, non-positive response received ({}).".format(response.status_code))
        logging.warning(response.text)
    return ""


def create_applicant(path, json, auth_token):
    logging.info("Adding applicant " + json_format.dumps(json))
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    try:
        response = requests.post(path + ":8071/applicants", json=json, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")
    if response.status_code == 201:
        logging.info("Success, added applicant")
        return response.json()["id"]
    elif response.status_code == 409:
        logging.warning("Warning, applicant information is duplicated. Failed to insert")
        logging.warning(response.text)
    elif response.status_code == 400:
        logging.warning("Warning, applicant information is incomplete. Failed to insert.")
        logging.warning(response.text)
    else:
        logging.warning("Warning, non-positive response received ({}).".format(response.status_code))
        logging.warning(response.text)
    return -1


def register_user(path, json, auth_token):
    logging.info("Registering user " + json_format.dumps(json))
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    try:
        response = requests.post(path + ":8070/users/registration", json=json, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")
    if response.status_code == 500:
        logging.info("Experienced internal server error, which occurs on a success.")
        return True
    elif response.status_code == 409:
        logging.warning("Warning, user information is duplicated. Failed to insert")
        logging.warning(response.text)
    elif response.status_code == 400:
        logging.warning("Warning, user information is incomplete. Failed to insert.")
        logging.warning(response.text)
    else:
        logging.warning("Warning, non-positive response received ({}).".format(response.status_code))
        logging.warning(response.text)
    return False


def create_bank(path, json, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    requests.post(path + ":8083/banks", json=json, headers=headers)


def create_branch(path, json, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    requests.post(path + ":8083/branches", json=json, headers=headers)


def create_transaction(path, json, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    requests.post(path + ":8073/transactions", json=json, headers=headers)


def validate_variables():
    # Validate necessary environment variables
    required_variables = ('DB_USERNAME', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME')
    logging.info("Validating environment variables.")
    for var in required_variables:
        if os.environ.get(var) is None:
            logging.info("Error, missing environment variable for " + var)
            exit(1)
    logging.info("Success, validated environment variables.")


def generate_applicant_json(n):
    return {
            "firstName": "firstName",
            "lastName": "lastName",
            "dateOfBirth": "1990-10-10",
            "gender": "OTHER",
            "email": str(n) + "mail@email.email",
            "phone": str(n) + "23-456-7892",
            "socialSecurity": str(n) + "23-45-6782",
            "driversLicense": "DL123456789" + str(n),
            "income": 10000000,
            "address": "100 Street Name",
            "city": "city",
            "state": "AZ",
            "zipcode": "12345",
            "mailingAddress": "100 Street Name",
            "mailingCity": "city",
            "mailingState": "AZ",
            "mailingZipcode": "12345"
        }


def generate_user_registration_json(applicant_json, i, membershipId):
    return {
        "role": "member",
        "username": "username" + str(i),
        "password": str(i) + "Password1!",
        "firstName": "firstnamey",
        "lastName": "lastnamey",
        "email": applicant_json['email'],
        "phone": applicant_json['phone'],
        "membershipId": membershipId,
        "lastFourOfSSN": applicant_json["socialSecurity"][-4:]
    }


if __name__ == '__main__':

    # Load environment
    load_dotenv()

    # Validate command line arguments
    if len(sys.argv) == 3:
        if sys.argv[2] == "init":
            # Overwrite if init
            logging.basicConfig(filename='.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')
            validate_variables()
            initialize_account_sequence()
            initialize_none_merchant()
            with open('applicants.csv', 'w') as applicants_file:
                applicants_file.write('')
            with open('accounts.csv', 'w') as accounts_file:
                accounts_file.write('')
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
        elif sys.argv[2] != "register" and sys.argv[2] != "user":
            logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')
            print("Error, invalid arguments. Expecting \"hostname "
                  "[applicant|bank|branch|transaction] amount\", \"hostname [register|user]\" or \"hostname init\".")
            logging.info("Error, invalid arguments. Expecting \"hostname [applicant|bank|branch|transaction] "
                         "amount\", \"hostname [register|user]\" or \"hostname init\". Received: {}".format(sys.argv[1:]))
            exit(1)
    elif len(sys.argv) != 4:
        logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')
        print("Error, invalid arguments. Expecting \"hostname "
              "[applicant|bank|branch|transaction] amount\", \"hostname [register|user]\" or \"hostname init\".")
        logging.info("Error, invalid arguments. Expecting \"hostname [applicant|bank|branch|transaction] "
                     "amount\", \"hostname [register|user]\" or \"hostname init\". Received: {}".format(sys.argv[1:]))
        exit(1)

    # Set logging to append
    logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')

    # Check environment setup
    validate_variables()

    # Parse number of inserts from command line args
    iterations = 0
    try:
        iterations = int(sys.argv[3])
        assert iterations > 0
    except IndexError:
        pass
    except (ValueError, AssertionError):
        log_error("Error, second argument must be a positive integer.")

    # Parse site path from command line args
    site_path = sys.argv[1]

    token = ''
    with open('auth_token.txt', 'r') as auth_token_file:
        token = auth_token_file.read()

    # users_file = open('applicants.csv', 'r')
    # applicants = users_file.read().split(',')

    if sys.argv[2] == 'applicant':
        logging.info("Preparing to insert {} applicants...".format(iterations))
        with open('applicants.csv', 'w') as applicants_file:
            for i in range(0, iterations):
                json = generate_applicant_json(i)
                id = create_applicant(site_path, json, token)
                if id != -1:
                    applicants_file.write(str(id) + "," + json_format.dumps(json) + '\n')
        exit(0)

    elif sys.argv[2] == 'register':
        logging.info("Preparing to insert applications...")
        with open('applicants.csv', 'r') as applicants_file, open('accounts.csv', 'w') as accounts_file:
            applicants = applicants_file.read().split("\n")[:-1]
            for i in range(0, len(applicants)):
                account_member_pair = create_application(site_path, applicants[i][0], token)
                if account_member_pair != "":
                    accounts_file.write(account_member_pair + "\n")
        exit(0)

    elif sys.argv[2] == 'user':
        logging.info("Preparing to insert users...")
        with open('applicants.csv', 'r') as applicants_file, open('accounts.csv', 'r') as accounts_file:
            accounts = accounts_file.read().split("\n")[:-1]
            applicants = applicants_file.read().split("\n")[:-1]
            for i in range(0, len(accounts)):
                applicant_json = json_format.loads(applicants[i][applicants[i].index(',')+1:])
                json = generate_user_registration_json(applicant_json, i, accounts[i].split(',')[1])
                register_user(site_path, json, token)
        exit(0)

    bank_json = {
        "routingNumber": "123456789",
        "address": "1234 Address St.",
        "city": "city",
        "state": "state",
        "zipcode": "12345"
    }

    create_bank(site_path, bank_json, token)

    branch_json = {
        "name": "branchName",
        "address": "1234 Address St.",
        "city": "city",
        "state": "state",
        "zipcode": "12345",
        "phone": "180-180-1800",
        "bankID": 2
    }

    create_branch(site_path, branch_json, token)

    transaction_json = {
        "type": "DEPOSIT",
        "method": "ATM",
        "amount": 5858494,
        "merchantName": "Example Merchant",
        "merchantCode": "123456",
        "accountNumber": "0011011714"
    }

    create_transaction(site_path, transaction_json, token)
