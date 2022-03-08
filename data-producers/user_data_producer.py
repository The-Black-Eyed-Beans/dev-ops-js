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


def register_user(path, json, auth_token):
    logging.info("Registering user " + json_format.dumps(json))
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    try:
        response = requests.post(path + ":" + os.environ.get("USER_PORT") + "/users/registration", json=json, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")
    if response.status_code == 500:
        logging.info("Experienced internal server error, which occurs on a success.")
        logging.info(response.text)
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


def generate_user_registration_json(applicant_json, fake, membershipId):
    password = ''
    for i in range(0, random.randint(2,4)):
        password += fake.random_choices(elements=('@', '$', '!', '%', '*', '?', '&'), length=1)[0]
    for i in range(0, random.randint(2,4)):
        password += str(fake.random_digit())
    for i in range(0, random.randint(2,4)):
        password += fake.random_uppercase_letter()
    for i in range(0, random.randint(2,4)):
        password += fake.random_lowercase_letter()
    password = list(password)
    random.shuffle(password)
    password = ''.join(password)
    return {
        "role": "member",
        "username": fake.user_name(),
        "password": password,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": applicant_json['email'],
        "phone": applicant_json['phone'],
        "membershipId": membershipId,
        "lastFourOfSSN": applicant_json["socialSecurity"][-4:]
    }


if __name__ == '__main__':
    logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')

    load_dotenv()

    # Validate command line arguments
    if len(sys.argv) != 1:
        print("Error, invalid arguments. Expecting none")
        logging.info("Error, invalid arguments. Expecting none")

    # Parse site path from command line args
    site_path = os.environ.get("URL")

    token = ''
    with open('auth_token.txt', 'r') as auth_token_file:
        token = auth_token_file.read()

    fake = Faker()

    logging.info("Preparing to insert users...")
    with open('applicants.csv', 'r') as applicants_file, open('accounts.csv', 'r') as accounts_file:
        accounts = accounts_file.read().split("\n")[:-1]
        applicants = applicants_file.read().split("\n")[:-1]
        for i in range(0, len(accounts)):
            applicant_json = json_format.loads(applicants[i][applicants[i].index(',')+1:])
            json = generate_user_registration_json(applicant_json, fake, accounts[i].split(',')[1])
            register_user(site_path, json, token)
