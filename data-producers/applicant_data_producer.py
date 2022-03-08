import requests
import logging
import sys
import json as json_format
from faker import Faker
import random
import os
from dotenv import load_dotenv


def log_error(s):
    logging.error(s)
    print(s)
    exit(1)


def create_application(path, id, auth_token, fake):
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    body = {
        "applicationType": fake.random_choices(elements=('CHECKING', 'SAVINGS', 'CHECKING_AND_SAVINGS'),
                                               length=1)[0],
        "noApplicants": "true",
        "applicantIds": [id]
    }
    logging.info("Registering applicant " + json_format.dumps(body))
    try:
        response = requests.post(path + ":" + os.environ.get("UNDERWRITER_PORT") + "/applications", json=body, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")

    if response.status_code == 201 and response.json()["accountsCreated"] == True:
        logging.info("Success, registered applicant.")
        logging.info(response.text)
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
        response = requests.post(path + ":" + os.environ.get("UNDERWRITER_PORT") + "/applicants", json=json, headers=headers)
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


def generate_applicant_json(fake):
    return {
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "dateOfBirth": fake.date(),
            "gender": fake.random_choices(elements=('MALE', 'FEMALE', 'OTHER', 'UNSPECIFIED'), length=1)[0],
            "email": fake.ascii_email(),
            "phone": fake.numerify("###-###-####"),
            "socialSecurity": fake.numerify("###-##-####"),
            "driversLicense": fake.random_choices(elements=("AK","AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA",
                                                            "HI","IA","ID","IL","IN","KS","KY","LA","MA","MD","ME",
                                                            "MI","MN","MS","MO","MT","NC","NE","NH","NJ","NM","NV",
                                                            "NY","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX",
                                                            "UT","VT","VA","WA","WV","WI","WY"), length=1)[0] +
                                                            fake.numerify("##########"),
            "income": random.randint(10000, 100000000),
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.random_choices(elements=("AK", "AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","HI","IA","ID",
                                               "IL","IN","KS","KY", "LA","MA","MD","ME","MI","MN","MS","MO","MT","NC",
                                               "NE","NH","NJ","NM","NV","NY","ND","OH", "OK","OR","PA","RI","SC","SD",
                                               "TN","TX","UT","VT","VA","WA","WV","WI","WY"), length=1)[0],
            "zipcode": fake.postalcode(),
            "mailingAddress": fake.street_address(),
            "mailingCity": fake.city(),
            "mailingState": fake.random_choices(elements=("AK", "AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","HI","IA","ID",
                                               "IL","IN","KS","KY", "LA","MA","MD","ME","MI","MN","MS","MO","MT","NC",
                                               "NE","NH","NJ","NM","NV","NY","ND","OH", "OK","OR","PA","RI","SC","SD",
                                               "TN","TX","UT","VT","VA","WA","WV","WI","WY"), length=1)[0],
            "mailingZipcode": fake.postalcode()
        }


if __name__ == '__main__':
    logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')

    load_dotenv()

    # Validate command line arguments
    if len(sys.argv) != 2:
        print("Error, invalid arguments. Expecting \"[# of applicants]\"")
        logging.info("Error, invalid arguments. Expecting \"[# of applicants]\"")

    # Parse number of inserts from command line args
    iterations = 0
    try:
        iterations = int(sys.argv[1])
        assert iterations > 0
    except IndexError:
        pass
    except (ValueError, AssertionError):
        log_error("Error, second argument must be a positive integer.")

    # Parse site path from env
    site_path = os.environ.get("URL")

    token = ''
    with open('auth_token.txt', 'r') as auth_token_file:
        token = auth_token_file.read()

    fake = Faker()

    logging.info("Preparing to insert {} applicants...".format(iterations))
    with open('applicants.csv', 'w') as applicants_file:
        for i in range(0, iterations):
            json = generate_applicant_json(fake)
            id = create_applicant(site_path, json, token)
            if id != -1:
                applicants_file.write(str(id) + "," + json_format.dumps(json) + '\n')

    logging.info("Preparing to insert {} applications...".format(iterations))
    with open('applicants.csv', 'r') as applicants_file, open('accounts.csv', 'w') as accounts_file:
        applicants = applicants_file.read().split("\n")[:-1]
        for i in range(0, len(applicants)):
            print(applicants[i])
            account_member_pair = create_application(site_path, applicants[i][:applicants[i].index(',')], token, fake)
            if account_member_pair != "":
                accounts_file.write(account_member_pair + "\n")

    exit(0)
