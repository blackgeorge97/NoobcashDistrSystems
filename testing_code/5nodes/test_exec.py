from concurrent.futures import ThreadPoolExecutor
import requests
import json

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def post_function(url, message):
	requests.post(url, data = message, headers = headers)

id_url = {}
id_url[0] = 'http://127.0.0.1:5000'
id_url[1] = 'http://127.0.0.1:5001'
id_url[2] = 'http://127.0.0.1:5002'
id_url[3] = 'http://127.0.0.1:5003'
id_url[4] = 'http://127.0.0.1:5004'


#post_function(url1, message1)


def transaction_maker(id):
    filename = 'transactions' + str(id) + '.txt'
    f = open(filename,'r')
    lines = f.readlines()
    url = id_url[id] + '/transaction/create'
    for line in lines:
        data = line.split()
        receiver_id = data[0][2]
        amount = data[1]
        message = {'receiver_id' : int(receiver_id), 'amount' : int(amount)}
        m = json.dumps(message)
        post_function(url, m)
    f.close


with ThreadPoolExecutor(5) as executor:
    executor.submit(transaction_maker, 0)
    executor.submit(transaction_maker, 1)
    executor.submit(transaction_maker, 2)
    executor.submit(transaction_maker, 3)
    executor.submit(transaction_maker, 4)

throughput = 0
block_time = 0

for i in range(5):
    response = requests.get(id_url[i] + '/test/results').json()
    throughput += response['throughput']
    block_time += response['block_time']

throughput = throughput / 5
block_time = block_time / 5

f = open("res_c1_dif_4.txt", "x")
f.write(str(throughput) + ' ' + str(block_time))
f.close()