#!/usr/bin/env python3
'''
Usage:
    $ cli.py [127.0.0.1] [5000] [--coordinator]
'''


import requests
import json
from argparse import ArgumentParser


headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

bootstrap_ip = '127.0.0.1'
bootstrap_port = '5000'

# parse arguments

parser = ArgumentParser()
parser.add_argument('-ip', '--ip', default='127.0.0.1', type=str, help='Hosting ip')
parser.add_argument('-p', '--port', default='5000', type=str, help='port to listen on')

args = parser.parse_args()

ip = args.ip
port = args.port

HOST = 'http://' + ip + ':' + port


################################################################################

help_message = '''
Usage:
$ python cli.py -p PORT           Start as participant
Available commands:
* `t [recepient_id] [amount]`   Send `amount` NBC to `recepient`
* `view`                        View transactions of the latest block
* `balance`                     View balance of each wallet (as of last validated block)
* `help`                        Print this help message
* `exit`                        Exit client (will not stop server)
Extra commands:
* `source [fname]`              Read and send transactions from `fname`
* `balance_all`                 View balance of each wallet (as of last received transaction)
'''


# Enter main loop
while True:
    cmd = input("> ")
    print(cmd)

    if cmd == 'balance':
        balance = requests.get(HOST+'/wallet/balance').json()
       
        print(balance)
        
    
    elif cmd == 'balance_all':
        # print list of participants with their balance as of the last validated block
        
        ring = requests.get('http://' + ip + ':' + bootstrap_port +'/ring').json()['ring']

        for r in ring:
            port = r["address"][10:14]
            ID = r["id"]
            balance = requests.get('http://' + ip + ':' + port +'/wallet/balance').json()
            print(ID)
            print(balance)


    elif cmd == 'view':
        # print list of transactions from last validated block
        API = HOST + '/transaction/get'
        transactions = requests.get(API).json()['transactions']

        for tx in transactions:
            print(f'id:\t{tx["id"]}\nsender:\t{tx["sender"]}\t->\nreceiver:\t{tx["receiver"]}\namount:\t{tx["amount"]}\tNBC\n')

    elif cmd.startswith('t'):
        # create a new transaction
        parts = cmd.split()
        message = json.dumps({'receiver_id' : int(parts[1]), 'amount' : int(parts[2])})
        
        API = HOST + '/transaction/create'
        response = requests.post(API, data = message, headers = headers)

        if response.status_code == 200:
            print('OK.')
        else:
            print(f'Error: {response.text}')
    
    elif cmd.startswith('source'):
        # read file of transactions
        parts = cmd.split()
        participants = requests.get(HOST + '/wallet/balance').json()

        try:
            fname = parts[1]
            with open(fname, 'r') as fin:
                for line in fin:
                    lol = line.split()
                                  
                    message = json.dumps({'receiver_id' : int(lol[1]), 'amount' : int(lol[2])})
                    API = HOST+'/transaction/create'
                    response = requests.post(API, data = message, headers = headers)

                    if response.status_code == 200:
                        print('OK.')
                    else:
                        print(f'Error: {response.text}')
        except Exception as e:
            print(f'error: {e.__class__.__name__}: {e}')
    
    elif cmd == 'help':
        print(help_message)

    elif cmd == 'exit':
        exit(-1)

    else:
        print(f'{cmd}: Unknown command. See `help`')