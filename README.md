# GithubCrawler
This is a simple github crawler that retrieves search results from the 1st page of results from a github search.

The GithubCrawler object needs a JSON input with the following structure: 
  - keywords: list of keywords to search
  - proxies: list of proxies to use to make the requests. One of them is selected randomly to perform all requests.
  - type: string to indicate the type of object to search. Allowed types are: repositories, wikis, issues.

The following methods are available to the user:
 - execute_search: Executes the search according to the given input data.
 - results_to_file: If the search produced results, it generates an output JSON file with the given filename.

The output will be a JSON containing the urls from the 1st page of results. If 'type' is repositories, it will also contain for each url the owner of the repository and the languages stats. The output structure is the following:
 - url: url of the repository
 - extra:
      - owner: name of the repository owner
      - languages: list of languages used and its % of usage 

To execute, run main.py
