#!/usr/bin/env python

import requests
import json


class JsonClient(object):
    def __init__(self, url="http://localhost:5000"):
        self.url = url

    def request(self, path, **params):
        url = "%s/%s" % (self.url, path)
        r = requests.post(url, params)
        return r.json()

    def auth(self, user, password):
        response = self.request('auth', user=user, password=password)
        if response['status'] == 'error':
            return None
        return response['data']

    def logout(self, cookie):
        response = self.request('logout', cookie=cookie)

    def register(self, user, password):
        response = self.request('register', user=user, password=password)

    def unregister(self, cookie):
        response = self.request('unregister', cookie=cookie)

    def change_password(self, cookie, new_password):
        self.request('change_password', cookie=cookie, new_password=new_password)

    def change_attr(self, cookie, name, args):
        args = json.dumps(args)
        self.request('change_attr', cookie=cookie, name=name, args=args)

    def check_user_name(self, name):
        self.request('check_user_name', name=name)

    def set_password(self, cookie, name, password, args):
        args = json.dumps(args)
        self.request('set_password', cookie=cookie, name=name, password=password, args=args)

    def del_password(self, cookie, name):
        self.request('del_password', cookie=cookie, name=name)

    def get_password(self, cookie, name):
        response = self.request('get_password', cookie=cookie, name=name)
        if response['status'] == 'error':
            return None
        return response['data']

    def get_passwords(self, cookie, args):
        args = json.dumps(args)
        response = self.request('get_passwords_by', cookie=cookie, args=args)
        if response['status'] == 'error':
            return None
        return response['data']

    def get_all_passwords(self, cookie):
        response = self.request('get_all_passwords', cookie=cookie)
        if response['status'] == 'error':
            return None
        return response['data']

    def export(self, cookie):
        response = self.request('export', cookie=cookie)
        if response['status'] == 'error':
            return None
        return response['data']

    def restore(self, cookie, data):
        response = self.request('restore', cookie=cookie, data=data)
