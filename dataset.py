from download import Download

class Dataset:
    def __init__(self, result):
        self.name = self.parse_name(result.get("display_name"))
        self.description = self.parse_name(result.get("description"))
        self.organization_name = self.parse_name(result.get("organization").get("display_name"))
        self.political_level = result.get("organization").get("political_level")
        self.tags = self.parse_tags(result.get("groups"))
        self.downloads = self.parse_downloads(result.get("resources"))
        self.id = result.get("name")


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

            print url

            downloads_data.append(Download(download_json, url))

        return downloads_data



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
        }
