import requests
import json as j
import random

BASE_URL = "https://www.ambushdesign.com"

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US',
    'content-type': 'application/json',
    'ff-country': 'GB',
    'ff-currency': 'GBP',
    'origin': "https://www.ambushdesign.com",
    'referer': "https://www.ambushdesign.com/",
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'x-newrelic-id': 'VQUCV1ZUGwIFVlBRDgcA',
}

# load in info
with open('settings.json') as file:
    data = j.load(file)
file.close()

with open('proxies.txt') as file:
    content = file.readlines()
file.close()

proxies = []

for proxy in content:
    proxies.append({"http": proxy})

amountOfAccounts = int(input("Enter the number of accounts you wish to gen: "))
emails = []
randomcharacters = list("1234567890+_")

while len(emails) < amountOfAccounts:
    session = requests.Session()
    proxyToUser = random.choice(proxies)

    # Gen random string for email.
    unique = [random.choice(randomcharacters) for i in range(3)]
    email = "{}{}{}@{}".format(data["firstName"], data["lastName"], "".join(unique), data["catchAll"]).lower()

    print("Making account for email {}".format(email))
    # Create Account
    createData = {
        "email": email,
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "name": data["firstName"] + " " + data["lastName"],
        "password": data["password"],
        "username": email
    }

    create = session.post(url="{}/api/legacy/v1/account/register".format(BASE_URL), json=createData, headers=HEADERS, proxies=proxyToUser)
    
    if create.status_code != 200:
        print("Failed to gen account. Retrying!")
        continue

    print("Successfully created account - adding address!")

    # Add address
    addressData = {
        "addressLine1": data["addressLine1"],
        "addressLine2": data["addressLine2"],
        "addressLine3": data["addressLine3"],
        "city": {
            "name": data["city"],
        },
        "country": {
            "id": data["country"]
        },
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "phone": data["phone"],
        "state": {
            "name": data["state"]
        },
        "zipCode": data["zipCode"]
    }    
    
    
    address = session.post(url="{}/api/legacy/v1/addressbook".format(BASE_URL), json=addressData, headers=HEADERS, proxies=proxyToUser)
    
    if address.status_code != 200:
        print("Failed to add address. Retrying!")
        continue

    # Set as default shipping and billing address
    addressResponseData = j.loads(address.text)
    session.put(url="{}/api/legacy/v1/addressbook/shipping/{}".format(BASE_URL, addressResponseData["id"]), json={}, headers=HEADERS, proxies=proxyToUser)
    session.put(url="{}/api/legacy/v1/addressbook/shipping/{}".format(BASE_URL, addressResponseData["id"]), json={}, headers=HEADERS, proxies=proxyToUser)
    
    print("Successfully genned account + added address + set as default billing and shipping for {}".format(email))
    emails.append(email)

with open('out.txt', 'w') as file:
    for email in emails:
        file.write("{}:{}\n".format(email, data["password"]))

file.close()