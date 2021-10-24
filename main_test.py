import pytest
from jsonschema.exceptions import ValidationError
from os.path import exists
from os import remove
from main import GithubCrawler

proxies = ['140.227.211.47:8080', '140.227.69.170:6000']
input_ok_repositories = {
    "keywords": [
        "python",
        "django-rest-framework",
        "jwt"
    ],
    "proxies": proxies,
    "type": "repositories"
}
input_ok_wikis = {
    "keywords": [
        "python",
        "django-rest-framework",
        "jwt"
    ],
    "proxies": proxies,
    "type": "wikis"
}
input_ok_issues = {
    "keywords": [
        "python",
        "django-rest-framework",
        "jwt"
    ],
    "proxies": proxies,
    "type": "issues"
}
input_ok_no_results = {
    "keywords": [
        "asd",
        "123",
        "bnm"
    ],
    "proxies": proxies,
    "type": "repositories"
}
input_fail_schema = {
    "keywords": [
        "python",
        "django-rest-framework",
        "jwt"
    ],
    "proxies": proxies
}
input_fail_keywords_empty = {
    "keywords": [],
    "proxies": proxies,
    "type": "repositories"
}
input_fail_proxy_ip = {
    "keywords": [
        "python",
        "django-rest-framework",
        "jwt"
    ],
    "proxies": [
        '140.227.69.1700:6000'
    ],
    "type": "repositories"
}
input_fail_proxy_port = {
    "keywords": [
        "python",
        "django-rest-framework",
        "jwt"
    ],
    "proxies": [
        '140.227.69.170:x'
    ],
    "type": "repositories"
}
input_fail_type_invalid = {
    "keywords": [
        "python",
        "django-rest-framework",
        "jwt"
    ],
    "proxies": proxies,
    "type": "x"
}


def create_instance(input_data):
    return GithubCrawler(input_data)


def execute(instance: GithubCrawler):
    instance.execute_search()
    return instance.output


def output_results(instance: GithubCrawler, filename):
    instance.results_to_file(filename)


@pytest.mark.parametrize("input_data", [
    input_ok_repositories,
    input_ok_wikis,
    input_ok_issues
])
def test_input_valid_data(input_data):
    create_instance(input_data)


@pytest.mark.parametrize("input_data", [
    input_fail_schema,
    input_fail_keywords_empty,
    input_fail_proxy_ip,
    input_fail_proxy_port,
    input_fail_type_invalid
])
def test_input_invalid_data(input_data):
    with pytest.raises((ValueError, ValidationError)):
        create_instance(input_data)


@pytest.mark.parametrize("input_data", [
    input_ok_repositories,
    input_ok_wikis,
    input_ok_issues
])
def test_execute(input_data):
    instance = create_instance(input_data)
    execute(instance)


@pytest.mark.parametrize("input_data", [
    input_ok_repositories,
    input_ok_no_results
])
def test_output_results(input_data, filename='test_output.json'):
    if exists(filename) is True:
        remove(filename)
    instance = create_instance(input_data)
    execute(instance)
    output_results(instance, filename)
    if instance.output.__len__() == 0:
        assert exists(filename) is False
    else:
        assert exists(filename) is True
