import requests
import ssl
import json
import time
from dataset import Dataset

# Data-Structure:
#
# name
# id
# description
# organization
#   name
#   political level
# tags[]
# downloads[]
#   format
#   url
#   created
#   issued
#   modified
#   rights
#   size



max_number = 10


def dump(datasets):
    with open('opendata.swiss.datasets.json', 'w') as fp:
        fp.write(
            json.dumps(
                [dataset.serialize() for dataset in datasets],
                indent=4, separators=(',', ': ')
            )
        )

# Get the list of Datasets
r = requests.get("https://opendata.swiss/api/3/action/package_list")
packages = r.json()

# packages = {
#     'result': [
#         'abfallgefasse',
#         'bazl-geocat-harvester',
#         'bodenubersichtskarte-wms-dienst',
#     ]
# }

datasets = []


for i, package in enumerate(packages['result']):
    dataset_name = package #packages['result'][i]
    time.sleep(0.2)

    if (i > max_number): print i; break

    try:
        dataset = requests.get("https://opendata.swiss/api/3/action/package_show?id=" + dataset_name)
    except (ssl.SSLError):
        continue


    if dataset.status_code == 200:
        result = dataset.json()['result']
        print dataset_name
        data = Dataset(result)
        datasets.append(data)
    else:
        print "Status code " + dataset.status_code

    dump(datasets)





