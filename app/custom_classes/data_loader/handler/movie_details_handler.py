import re
from typing import Any, List, Optional
from typing import Dict

import requests as requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import request

from app.custom_classes.data_loader.handler.abstract_handler import AbstractHandler


class MovieDetailsHandler(AbstractHandler):
    def execute(self, request_data: Dict[Any, Any]) -> List[Dict[Any, Any]]:
        movies_details_list: List[Dict[Any, Any]] = []
        for movie_data in request_data[1:10]:
            movies_details_list.append(self.get_film_details(movie_data['Wiki Link']))
        return movies_details_list

    @staticmethod
    def get_film_details(url: str) -> Dict[Any, Any]:
        if url == "":
            return {}
        request_handler: request = requests.get(url)
        movie_details: Dict[Any, Any] = {}
        html_table = MovieDetailsHandler.get_table_data_from_html(request_handler)
        if html_table is None:
            return {}

        if html_table.find_all('tr') is not None:
            for tr in html_table.find_all('tr')[1:]:
                property_name: Optional[str, None] = None
                if tr.find('th'):
                    property_name = tr.find('th').text
                elif tr.find('div'):
                    property_name = MovieDetailsHandler.clean_unicode_text(tr.div)
                if property_name is not None:
                    property_value_list: List[Dict[str, str]] = []
                    for td in tr.find_all('td'):
                        if td.findAll('li'):
                            property_value_list = MovieDetailsHandler.parse_listed_html(property_value_list, td)
                        else:
                            property_value_list = MovieDetailsHandler.parse_non_listed_html(property_value_list, td)
                    movie_details[property_name] = property_value_list
        # print(movie_details)
        return movie_details

    @staticmethod
    def clean_unicode_text(obj_: Any):
        return obj_.text.replace(u'\xa0', u' ')

    @staticmethod
    def parse_non_listed_html(property_value_list: List[Dict[str, str]], td: Any) -> List[Dict[str, str]]:
        if td.findAll("sup"):
            for sup in td.findAll("sup"):
                sup.decompose()
        value: str = MovieDetailsHandler.clean_unicode_text(td)
        link: Optional[str, None] = None
        if td.find('a', href=re.compile(r'^(?!.*?#cite).*')):
            link = td.find('a')["href"]
            if link[0:5] == "/wiki":
                link = r"https://en.wikipedia.org/" + link
        property_value_list.append({"value": value,
                                    "url": link})
        return property_value_list

    @staticmethod
    def parse_listed_html(property_value_list: List[Dict[str, str]], td: Any) -> List[Dict[str, str]]:
        for li in td.findAll('li'):
            link: Optional[str, None] = None
            if li.find('a', href=re.compile(r'^(?!.*?#cite).*')):
                link = li.find('a', href=re.compile(r'^(?!.*?#cite).*'))["href"]
                if link[0:5] == "/wiki":
                    link = r"https://en.wikipedia.org/" + link
            value: str = MovieDetailsHandler.clean_unicode_text(li)
            property_value_list.append({"value": value,
                                        "url": link})
            return property_value_list

    @staticmethod
    def get_table_data_from_html(request_handler):
        html_table: Tag = BeautifulSoup(features="lxml", markup=request_handler.text). \
            find("table",
                 {"class": "infobox vevent"})
        if html_table is None:
            html_table: Tag = BeautifulSoup(features="lxml", markup=request_handler.text). \
                find("table",
                     {"class": "infobox vcard"})
        return html_table

    def handle(self, request_data: Any):
        return super().handle(request_data)
