import requests
import logging
import sys
import json as json_format
import random
from dotenv import load_dotenv
from faker import Faker
import os

def log_error(s):
    logging.error(s)
    print(s)
    exit(1)


def create_branch(path, json, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }

    logging.info("Registering branch " + json_format.dumps(json))

    try:
        response = requests.post(path + ":8083/branches", json=json, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")
    if response.status_code == 201:
        logging.info("Success, inserted branch.")
        logging.info(response.text)
    elif response.status_code == 400:
        logging.warning("Warning, branch information is incomplete. Failed to insert.")
    else:
        logging.warning("Warning, non-positive response received ({}).".format(response.status_code))
        logging.warning(response.text)


def generate_branch_json(faker, bank_id):
    return {
        "name": faker.bs(),
        "address": faker.street_address(),
        "city": faker.city(),
        "state": fake.random_choices(elements=("AK", "AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","HI","IA","ID",
                                               "IL","IN","KS","KY", "LA","MA","MD","ME","MI","MN","MS","MO","MT","NC",
                                               "NE","NH","NJ","NM","NV","NY","ND","OH", "OK","OR","PA","RI","SC","SD",
                                               "TN","TX","UT","VT","VA","WA","WV","WI","WY"), length=1)[0],
        "zipcode": fake.postcode(),
        "phone": fake.numerify("###-###-####"),
        "bankID": bank_id
    }


if __name__ == '__main__':
    logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')

    # Load environment
    load_dotenv()

    # Validate command line arguments
    if len(sys.argv) != 2:
        print("Error, invalid arguments. Expecting \"[# of branches]\"")
        logging.info("Error, invalid arguments. Expecting \"[# of branches]\"")

    # Parse number of inserts from command line args
    iterations = 0
    try:
        iterations = int(sys.argv[1])
        assert iterations > 0
    except IndexError:
        pass
    except (ValueError, AssertionError):
        log_error("Error, second argument must be a positive integer.")

    # Parse site path from command line args
    site_path = os.environ.get("URL")

    token = ''
    with open('auth_token.txt', 'r') as auth_token_file:
        token = auth_token_file.read()

    Faker.seed(0)
    fake = Faker()

    with open('banks.csv', 'r') as banks_file:
        fake = Faker()
        bank_id_list = [1] + banks_file.read().split(',')

        for i in range(0, iterations):
            bank_id = bank_id_list[random.randint(0, len(bank_id_list)-2)]
            branch_json = generate_branch_json(fake, bank_id)
            create_branch(site_path, branch_json, token)
