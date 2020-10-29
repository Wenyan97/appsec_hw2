from shlex import quote

from django.test import TestCase, Client
import json
import os
from os import system
from LegacySite.models import User, Product, Card
from . import extras

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GiftcardSite.settings')
import django

django.setup()
CARD_PARSER = 'giftcardreader'


class MyTest(TestCase):
    def test_1(self):
        resp = self.client.get('/gift/', {'director': '<script>alert(this is a xss attack!)</script>'})
        string = bytes.decode(resp.content)
        # check whether "<" and ">" -> "&lt" and "&gt"
        if string.__contains__("&lt;script&gt"):
            print("XSS Test OK!")

    def test_2(self):
        resp = self.client.post('/gift/1', {'amount': '1', 'username': 'wenyan97'})
        if resp.status_code == 403:
            print("CRSF test passed!")

    def test_3(self):
        card_file_data = open('part1/sqlInjection_stealpassword.gftcrd')
        card_file_path = f'./tmp/SQLi_test_parser.gftcrd'
        card_data = extras.parse_card_data(card_file_data.read(), card_file_path)

        signature = json.loads(card_data)['records'][0]['signature']
        card_query = Card.objects.raw('select id from LegacySite_card where data = %s', params=[signature])
        if len(card_query) == 0:
            print('SQL injection test passed!!!')

    def test_4(self):
        card_path_name = open('part1/commandInjection.txt')
        # KG: Are you sure you want the user to control that input?
        command = f"./{CARD_PARSER} 2 {card_path_name} > tmp_file"
        safe_command = quote(command)
        ret_val = system(safe_command)
        if ret_val != 0:
            print('command injection passed!!!')
