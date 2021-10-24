import requests
import json
import jsonschema
import random
import ipaddress
from lxml import html


class GithubCrawler:

    def __init__(self, input_data):
        """
        :param input_data: Must be a json containing the following elements:
                    - "keywords": Keywords to be used as search terms.
                    - "proxies": List of proxies.
                        One of them is selected randomly
                        to perform all requests.
                    - "type": Type of object to search for.
                        SUPPORTED TYPES: "repositories", "issues", "wikis"
        """
        self.delay_between_queries = 5
        self._validate_input(input_data)
        self.url_root = 'https://github.com'
        self.url_search = \
            self.url_root + '/search?q=' + \
            '+'.join(input_data['keywords']) + \
            '&type=' + input_data['type']
        self.proxy = {
            'https': 'https://' + random.choice(input_data['proxies'])
        }
        self.type = input_data['type']
        self.search_urls = []
        self.output = []

    @staticmethod
    def _validate_input(input_data):
        input_schema = {
            "type": "object",
            "properties": {
                "keywords": {"type": "array"},
                "proxies": {"type": "array"},
                "type": {"type": "string"},
            },
            "required": ["keywords", "proxies", "type"]
        }
        # raises ValidationError if schema requirements are not met
        jsonschema.validate(input_data, input_schema)
        # raises ValueError if 'keywords is empty'
        if input_data['keywords'].__len__() == 0:
            raise ValueError('There must be at least one keyword')
        for proxy in input_data['proxies']:
            # expects 2 values, otherwise raises ValueError
            ip, port = proxy.split(":")
            # raises ValueError if 'ip' is not an IPv4/IPv6 address
            ipaddress.ip_address(ip)
            # check port
            if not port.isnumeric() or int(port) < 0 or int(port) > 65535:
                raise ValueError(str(port) + " is not a valid port")
        # raises ValueError if 'type' is not in scope
        if input_data['type'].lower() != 'repositories' \
                and input_data['type'].lower() != 'wikis' \
                and input_data['type'].lower() != 'issues':
            raise ValueError(input_data['type'] +
                             " is not a valid type. Valid types are: "
                             "'Repositories, 'Wikis', 'Issues'"
                             )

    def _make_request(self, url):
        return requests.get(url=url, proxies=self.proxy)

    @staticmethod
    def _get_data_html(response):
        return html.fromstring(response.content)

    def _parse_search_urls(self, data_html):
        """
        Fills 'self.search_urls' with the urls from 1st page of search results
        """
        data_list = data_html.xpath(
            "//ul[@class='repo-list']"
            "/li[@class='repo-list-item hx_hit-repo d-flex "
            "flex-justify-start py-4 public source']"
            "/div[@class='mt-n1 flex-auto']"
            "/div[@class='d-flex']"
            "/div[@class='f4 text-normal']"
            "/a[@class='v-align-middle']"
            "/@href"
        )
        for data in data_list:
            self.search_urls.append(self.url_root + data)

    @staticmethod
    def _parse_repo_languages(data_html):
        """
        :rtype: dictionary containing the languages
                and its % of usage from the given repository
        """
        data_list = data_html.xpath(
            "//a[@data-ga-click='Repository, language stats search click, "
            "location:repo overview']"
        )
        languages_dict = {}
        for data in data_list:
            language = data.text_content().strip().splitlines()
            languages_dict[language[0]] = language[1].strip()
        return languages_dict

    @staticmethod
    def _parse_repo_owner(data_html):
        """
        :rtype: string containing the owner name from the given repository
        """
        data_owner = data_html.xpath("//span[@itemprop='author']")
        return data_owner[0].text_content().strip()

    def _get_type_repo(self):
        """
        Makes a request for each url from 'self.search_urls'
        to retrieve the corresponding owner and languages list.
        Fills 'self.output' with the results.
        """
        for url in self.search_urls:
            response_repo = self._make_request(url)
            data_html_repo = self._get_data_html(response_repo)
            languages_dict = self._parse_repo_languages(data_html_repo)
            owner_repo = self._parse_repo_owner(data_html_repo)
            self.output.append(
                {'url': url,
                 'extra': {
                     'owner': owner_repo,
                     'language_stats': languages_dict
                 }
                 }
            )

    def _get_type_other(self):
        self.output = [{'url': url} for url in self.search_urls]

    def execute_search(self):
        """
        Executes the search with the given input data
        If 'self.type' = 'repositories', also retrieves
                         owner and language list for each url
        Else, returns only the urls from the search result
        """
        response_search = self._make_request(self.url_search)
        data_html_search = self._get_data_html(response_search)
        self._parse_search_urls(data_html_search)
        if self.type == 'repositories':
            self._get_type_repo()
        else:
            self._get_type_other()

    def results_to_file(self, filename):
        if self.output.__len__() > 0:
            out_file = open(filename, "w")
            json.dump(self.output, out_file, indent=2)
            out_file.close()
        else:
            print("--The output is empty--")


if __name__ == "__main__":
    inputs = {
         "keywords": [
             "python",
             "jwt"
         ],
         "proxies": [
             '140.227.211.47:8080',
             '140.227.69.170:6000'
         ],
         "type": "repositories"
    }

    c = GithubCrawler(inputs)
    c.execute_search()
    c.results_to_file("output.json")
    print(c.output)
