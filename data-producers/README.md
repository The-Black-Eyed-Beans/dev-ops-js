# data-producers

Scripts for populating the application with dummy data. Requires an .env file with the following fields populated:

`DB_USERNAME`
`DB_PASSWORD`
`DB_HOST`
`DB_PORT`
`DB_NAME`
`ENCRYPT_SECRET_KEY`
`JWT_SECRET_KEY`

`USER_PORT`
`UNDERWRITER_PORT`
`TRANSACTION_PORT`
`BANK_PORT`
`URL`

Population begins using `data_producer_initializer.py`, which will populate the database with necessary fields (such as account_sequence and the None merchant) if not present, and obtain credentials and save them to a file.

`applicant_data_producer.py` takes an argument for the number of applicants to produce, and saves their information to an output file

`user_data_producer.py` attempts to register all applicants created this session as users

`banks_data_producer.py [count]` crates a given number of banks

`branches_data_producer.py [count]` creates a given number of branches, assigned to random banks created this session

`transactions_data_producer.py [count]` creates a given number of transactions, assigned to random users created this session.
