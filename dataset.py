from download import Download
import unicodecsv

class Dataset:


    def __init__(self, data, from_json):
        if from_json:
            self.init_from_json(data)
        else:
            self.init_from_result(data)

    def init_from_result(self, result):
        self.name = self.parse_name(result.get("display_name"))
        self.description = self.parse_name(result.get("description"))
        self.organization_name = self.parse_name(result.get("organization").get("display_name"))
        self.political_level = result.get("organization").get("political_level")
        self.tags = self.parse_tags(result.get("groups"))
        self.downloads = self.parse_downloads(result.get("resources"))
        self.id = result.get("name")
        self.visits = result.get('visits')

    def init_from_json(self, json):
        self.name = json.get('name')
        self.description = json.get('description')
        self.organization_name = json.get('organization').get('name')
        self.political_level = json.get('organization').get('political_level')
        self.tags = json.get('tags')
        self.downloads =  [Download(download, download.get('url'), self) for download in json['downloads']]
        self.id = json.get('id')
        self.visits = json.get('visits', 0)

    def parse_name(self, name):
        if(name == None):
            return "NULL"
        if name.get("de", "") != "":
            return name ["de"]
        elif name.get("en", "") != "":
            return name["en"]
        elif name.get("fr", "") != "":
            return name["fr"]
        else:
            return name.get("it", "")

    def parse_tags(self, tags):
        tagnames = []
        for tag in tags:
            tagnames.append(tag["name"])
        return tagnames


    def parse_downloads(self, downloads):
        downloads_data = []
        for download_json in downloads:
            url = ""
            url = download_json.get("download_url", "")
            if not url:
                url = download_json['url']


            downloads_data.append(Download(download_json, url, self))

        return downloads_data



    def merge_dl_number(self, path):
        self.visits = 0
        with open(path, 'r') as downloads:
            downloads = unicodecsv.reader(downloads, delimiter=";")
            for row in downloads:
                if(self.id in row[0]):
                    self.visits = self.visits + int(row[2])


    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "organization": {
                "name": self.organization_name,
                "political_level": self.political_level
            },
            "tags": self.tags,
            "downloads": ([download.serialize() for download in self.downloads]),
            "id": self.id,
            "visits": self.visits
        }
