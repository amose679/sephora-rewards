#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import psycopg2
import requests

from bs4 import BeautifulSoup
from config.app_config import Sephora
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient


class SephoraScraper():
    def __init__(self, text):
        self.send_texts = text
        self.conn = psycopg2.connect(database=Sephora.DbConfig.NAME,
                                     user=Sephora.DbConfig.USER)

    def _send_text(self, body):
        # Don't send texts in testing
        if not self.send_texts:
            print body
            return

        client = TwilioRestClient(Sephora.TwilioConfig.SID,
                                  Sephora.TwilioConfig.AUTH)
        for num in Sephora.TwilioConfig.TO:
            try:
                client.messages.create(
                    body=body,
                    to=num,
                    from_=Sephora.TwilioConfig.FROM
                )
            except TwilioRestException as e:
                print e

    def _is_in_pts_range(self, rewards, low_bound=750, high_bound=4000):
        filtered = []
        for reward in rewards:
            pts = reward['bi_value']
            if pts >= low_bound and pts < high_bound:
                filtered.append(reward)
        return filtered

    def _is_in_stock(self, rewards):
        return [r for r in rewards if r.get('is_in_stock', True)]

    def _was_already_notified(self, rewards):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id FROM notified_rewards WHERE id = ANY(%(ids)s)",
            {'ids': list([r['id'] for r in rewards])}
        )
        res = set(r[0] for r in cur.fetchall())
        return [r for r in rewards if r['id'] not in res]

    def _filter_rewards(self, rewards):
        ''' Filters rewards for ones I want to be notified about

        Args:
            rewards (list): list of rewards at different levels

        Returns:
            list: filtered for rewards I want to be notified of
        '''
        rewards = self._is_in_pts_range(rewards)
        rewards = self._is_in_stock(rewards)
        return rewards

    def _find_rewards(self):
        '''Scrapes html to find rewards'''
        html_doc = requests.get(Sephora.Config.REWARDS_URL).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        scripts = soup.find_all('script')
        rewards = []
        for script in scripts:
            if script.attrs.get('seph-json-to-js') == 'allRewards':
                groups = json.loads(script.text)['bi_reward_groups']
                for level in groups:
                    rewards += level['skus']
        return rewards

    def _save_notified_rewards(self, rewards):
        cur = self.conn.cursor()
        for reward in rewards:
            cur.execute(
                "INSERT INTO notified_rewards (id, name) VALUES (%s, %s)",
                (reward['id'], reward['display_name'])
            )
        self.conn.commit()

    def main(self):
        rewards = self._find_rewards()
        rewards = self._filter_rewards(rewards)
        if not rewards:
            return
        body = ''
        for reward in rewards:
            body += '(%s) %s \n' % (reward['bi_value'], reward['display_name'])
        self._send_text(body)
        self._save_notified_rewards(rewards)


if __name__ == '__main__':
    Sephora.init_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--text', action='store_true', default=False)
    args = parser.parse_args()
    ss = SephoraScraper(args.text)
    ss.main()
