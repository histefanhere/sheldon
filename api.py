from dataclasses import dataclass
import requests
import os

from dotenv import load_dotenv

load_dotenv()

url = "https://minecraft-mp.com/api/?object=servers&element=voters&key={key}&month={month}&format=json"


@dataclass
class Voter:
    username: str
    votes: int


class Response:
    def __init__(self, resp):
        self.resp = resp
        self.month = resp['month']
        self.voters = []
        for voter in resp['voters']:
            username, votes = voter['nickname'], int(voter['votes'])
            self.voters.append(Voter(username, votes))


def get_current_month() -> Response:
    return __call('current')


def get_previous_month() -> Response:
    return __call('previous')


def __call(month) -> Response:
    full_url = url.format(key=os.getenv('API_KEY'), month=month)
    res = requests.get(full_url)
    return Response(res.json())
