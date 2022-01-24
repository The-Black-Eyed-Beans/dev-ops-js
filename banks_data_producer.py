import requests
import logging
import sys
import json as json_format
from faker import Faker

def log_error(s):
    logging.error(s)
    print(s)
    exit(1)


def create_bank(path, json, auth_token):
    logging.info("Registering bank " + json_format.dumps(json))

    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }

    try:
        response = requests.post(path + ":8083/banks", json=json, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")
    if response.status_code == 201:
        logging.info("Success, inserted bank.")
        logging.info(response.text)
        return response.json()['id']
    elif response.status_code == 400:
        logging.warning("Warning, bank information is incomplete. Failed to insert.")
    else:
        logging.warning("Warning, non-positive response received ({}).".format(response.status_code))
        logging.warning(response.text)
    return -1

def generate_bank_json(fake):
    return {
        "routingNumber": fake.aba(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.random_choices(elements=("AK", "AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","HI","IA","ID",
                                               "IL","IN","KS","KY", "LA","MA","MD","ME","MI","MN","MS","MO","MT","NC",
                                               "NE","NH","NJ","NM","NV","NY","ND","OH", "OK","OR","PA","RI","SC","SD",
                                               "TN","TX","UT","VT","VA","WA","WV","WI","WY"), length=1)[0],
        "zipcode": fake.postcode(),
    }


if __name__ == '__main__':
    logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')

    # Validate command line arguments
    if len(sys.argv) != 3:
        print("Error, invalid arguments. Expecting \"hostname [# of banks]\"")
        logging.info("Error, invalid arguments. Expecting \"hostname [# of banks]\"")

    # Parse number of inserts from command line args
    iterations = 0
    try:
        iterations = int(sys.argv[2])
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

    fake = Faker()
    with open('banks.csv', 'a') as bank_file:
        for i in range(0, iterations):
            bank_json = generate_bank_json(fake)
            id = create_bank(site_path, bank_json, token)
            if id != -1:
                bank_file.write(str(id) + ',')
