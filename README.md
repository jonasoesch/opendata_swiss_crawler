# opendata.swiss Crawler

This is a crawler for the Open Data-Plattform of the Swiss Confederation. [opendata.swiss](http://opendata.swiss) collects open datasets from the national, cantonal and communal administration which is published for free use. The crawler attempts to download each dataset and analyze it.

The result is an interactive viusalization that allows the exploriation of the data on the platform by different criteria.

## Usage

First of all you should set all the options in `config.py` to your preference.

The dependecies are:

* Python 2.7 and everything in `requirements.txt`
* Node.js

And that is basically it. You can now run:

    python main.py

in your console.

One complete run takes about 3 hours in order to analyze 2500 datasets.
