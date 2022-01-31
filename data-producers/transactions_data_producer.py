import requests
import logging
import sys
import json as json_format
from faker import Faker
import random

def log_error(s):
    logging.error(s)
    print(s)
    exit(1)


def create_transaction(path, json, auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }
    logging.info("Creating transaction " + json_format.dumps(json))
    try:
        response = requests.post(path + ":8073/transactions", json=json, headers=headers)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        log_error("Error, failed to establish connection with server. Terminating process.")

    if response.status_code == 200:
        logging.info("Success, created transaction.")
        logging.info(response.text)
        return True
    elif response.status_code == 404:
        logging.warning("Warning, could not find associated account number. Failed to insert")
        logging.warning(response.text)
    elif response.status_code == 500:
        logging.warning("Warning, internal server error, potentially caused by attempting to register an already-"
                        "registered user. Failed to insert.")
        logging.warning(response.text)
    else:
        logging.warning("Warning, non-positive response received ({}).".format(response.status_code))
        logging.warning(response.text)
    return ""



def generate_transaction_json(i, fake, accounts):
    # Get an account number
    index = random.randint(0, len(accounts)-2)
    num = accounts[index].split(',')[0]
    # Determine transaction type
    if random.randint(1, 2) == 2:
        return {
            "type": fake.random_choices(elements=('PURCHASE', 'DEPOSIT', 'REFUND', 'PAYMENT', 'VOID'), length=1)[0],
            "method": fake.random_choices(elements=('ACH', 'ATM', 'APP'), length=1)[0],
            "amount": random.randint(0,10000),
            "merchantName": fake.bs(),
            "merchantCode": fake.numerify("#####"),
            "description": fake.sentence(nb_words=10)[:254],
            "accountNumber": num
        }
    else:
        return {
            "type": fake.random_choices(elements=('WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT'), length=1)[0],
            "method": fake.random_choices(elements=('ACH', 'ATM', 'APP'), length=1)[0],
            "amount": random.randint(0, 10000),
            "merchantName": "None",
            "description": fake.sentence(nb_words=10)[:254],
            "accountNumber": num
        }


if __name__ == '__main__':
    logging.basicConfig(filename='.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(message)s')

    # Validate command line arguments
    if len(sys.argv) != 3:
        print("Error, invalid arguments. Expecting \"hostname [# of transactions]\"")
        logging.info("Error, invalid arguments. Expecting \"hostname [# of transactions]\"")

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


    Faker.seed(0)
    fake = Faker()
    with open('accounts.csv', 'r') as accounts_file:
        accounts = accounts_file.read().split('\n')
        for i in range(0, iterations):
            bank_json = generate_transaction_json(i, fake, accounts)
            create_transaction(site_path, bank_json, token)
