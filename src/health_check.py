
import requests

class healthCheck:
    def __init__(self, url):
        self.url = url

    def check(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False
