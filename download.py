import uuid
import os
import requests
from analyzer import Analyzer
from lxml import etree
import StringIO
import config as cfg

# Status
# 0. Untouched
# 1. Metadata
# 2. Downloaded
# 3. Analyzed

class Download:

    def __init__(self):
        self.format = ''
        self.real_format = ''
        self.url = ''
        self.created = ''
        self.issued = ''
        self.modified = ''
        self.rights = ''
        self.size = ''
        self.id = str(uuid.uuid4())
        self.dataset = None
        self.status = 'Untouched'
        self.filepath = cfg.data_dir 

    def __init__(self, json, url, dataset):
        self.format = json.get("format")
        self.real_format = json.get("real_format")
        self.url = url
        self.created = json.get("created")
        self.issued = json.get("issued")
        self.modified = json.get("modified")
        self.rights = json.get("rights")
        self.size =  json.get("byte_size")
        self.id = str(uuid.uuid4())
        self.dataset = dataset
        self.dl_error = json.get('dl_error')
        self.status = json.get('status')
        self.path = json.get('path', '')
        self.status_code = json.get('status_code', '')
        self.content_type = json.get('content_type', '')
        self.total = json.get('total', '')
        self.dimensions = json.get('dimensions', '')
        self.file_size = json.get('file_size', '')
        self.filepath = cfg.data_dir




    def download(self):

        self.set_dir()
        path = self.filepath = self.filepath + '/' + self.id


        if(self.format == 'MULTIFORMAT'):
            self.sitg_case()

        # Trying to catch all the possibilities for failure
        try:
            r = requests.get(self.url, stream=True)
            r.raise_for_status()
        except requests.exceptions.ConnectionError:
            return self.update_with_dl_information(error='connection')
        except requests.exceptions.Timeout:
            return self.update_with_dl_information(error='timeout')
        except requests.exceptions.TooManyRedirects:
            return self.update_with_dl_information(error='too many redirects')
        except requests.exceptions.HTTPError:
            return self.update_with_dl_information(status_code=r.status_code, error='http')
        except requests.exceptions.MissingSchema:
            if not("http://" in self.url):
                self.url = "http://"+self.url
                return self.download()

        try:
            # Write to file
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
        except requests.exceptions.ChunkedEncodingError:
            print "Chunk encoding error"

        self.update_with_dl_information(path=path, status_code=r.status_code, content_type=r.headers['Content-Type'])

        if not(self.dl_error) and cfg.keep_data:
            self.status = 'Downloaded'


    def update_with_dl_information(self, path=None, status_code=None, content_type = None, error=None):
        self.path = path
        self.status_code = status_code
        self.content_type = content_type
        self.dl_error = error



    def sitg_case(self):

        try:

            old_url = self.url

            base_url = 'http://ge.ch'

            landing = requests.get(self.url).text


            parser = etree.HTMLParser()
            landing_tree = etree.parse(StringIO.StringIO(landing), parser)
            conditions_path = base_url + landing_tree.xpath('//div[@class="opendata-download-file-SHP"]/parent::a/@href')[0]


            conditions = requests.get(conditions_path).text

            conditions_tree = etree.parse(StringIO.StringIO(conditions), parser)
            real_url = conditions_tree.xpath('//input[contains(@value, "URL de")]/@onclick')[0].split("'")[1]

            self.url = real_url

        except IndexError:
            self.url = old_url



    def set_dir(self):

        try:
            if not os.path.exists(self.filepath):
                os.makedirs(self.filepath)
        except Exception as e:
            print "Couldn't find nor create the target directory for the data"
            raise e

        # Creating the directory structure -> organization/dataset
        try:
            self.filepath = self.filepath + "/" + self.dataset.organization_name.encode("ascii", "ignore")
            if not os.path.exists(self.filepath):
                os.makedirs(self.filepath)
        except Exception as e:
            print self.dataset.name + ": Orga dir: " + str(e)

        try:
            self.filepath = self.filepath + '/' + self.dataset.id
            if not os.path.exists(self.filepath):
                os.makedirs(self.filepath)
        except Exception as e:
            print self.dataset.name + ": Dataset dir: " + str(e)


    def get_dir(self):
        return self.filepath


    def analyze(self):
        Analyzer().analyze(self)

    def delete_file(self):
        try:
            os.unlink(self.filepath)
            print "Deleted"
        except OSError as e:
            False
            
    def serialize(self):
        return {
            "format": self.format,
            "real_format": self.real_format,
            "url": self.url,
            "created": self.created,
            "issued": self.issued,
            "modified": self.modified,
            "rights": self.rights,
            "size": self.size,
            "status": self.status,
            "dl_error": self.dl_error,
            "path": self.path,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "total": self.total,
            "dimensions": self.dimensions,
            "file_size": self.file_size,
            "filepath": self.filepath
        }


