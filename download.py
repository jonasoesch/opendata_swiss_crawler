import uuid


class Download:

    def __init__(self):
        self.format = ''
        self.url = ''
        self.created = ''
        self.issued = ''
        self.modified = ''
        self.rights = ''
        self.size = ''
        self.id = str(uuid.uuid4())


    def __init__(self, json, url):
        self.format = json.get("format"),
        self.url = url,
        self.created = json.get("created"),
        self.issued = json.get("issued"),
        self.modified = json.get("modified"),
        self.rights = json.get("rights"),
        self.size =  json.get("byte_size")


    def serialize(self):
        return {
            "format": self.format,
            "url": self.url,
            "created": self.created,
            "issued": self.issued,
            "modified": self.modified,
            "rights": self.rights,
            "size": self.size
        }


