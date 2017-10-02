import requests
import ssl
import json
import time
from dataset import Dataset
import os
import config as cfg

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



def dump(datasets):
    with open(cfg.output_file, 'w') as fp:
        fp.write(
            json.dumps(
                [dataset.serialize() for dataset in datasets],
                indent=4, separators=(',', ': ')
            )
        )



def resume():
    try:
        with open(cfg.output_file, 'r') as file:
            datasets = []
            for dataset in json.load(file):
                dataset_object = Dataset(dataset, True)
                datasets.append(dataset_object)

            return datasets
    except Exception:
        return []



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

datasets = resume()


for i, package in enumerate(packages['result']):

    dataset_name = package #packages['result'][i]
    dataset = None

    if (i > cfg.finish_at): break
    if (i < cfg.start_from): continue

    exists = False
    for ds in datasets:
        if (ds.id == dataset_name):
            print "Reading from cache: " + str(i) + ". "+ ds.id
            dataset = ds
            break


    if not(dataset):
        time.sleep(0.2)


        try:
            print "https://opendata.swiss/api/3/action/package_show?id=" + dataset_name
            ds = requests.get("https://opendata.swiss/api/3/action/package_show?id=" + dataset_name)
        except (ssl.SSLError):
            continue


        if ds.status_code == 200:
            print "Adding: " + str(i) + ". " + dataset_name
            result = ds.json()['result']
            dataset = Dataset(result, False)
            datasets.append(dataset)

        else:
            print "Status code " + ds.status_code

    for dl in dataset.downloads:
        if not(dl.status == 'Downloaded' or dl.status == "Analyzed"):
            print "Downloading..."
            dl.download()
        if not(dl.status == 'Analyzed'):
            print "Analyzing..."
            dl.analyze()

        if(not(cfg.keep_data)):
            dl.delete_file()

    dump(datasets)





