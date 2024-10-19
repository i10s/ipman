# Configuration for Consul and environment variables
# File: /src/config.py

import os
import consul

class Config:
    def __init__(self):
        self.consul_client = consul.Consul(host=os.getenv('CONSUL_HOST', 'localhost'))

    def get_config(self, key):
        index, data = self.consul_client.kv.get(key)
        if data and 'Value' in data:
            return data['Value'].decode('utf-8')
        return None

    @property
    def DB_HOST(self):
        return self.get_config('ipman_db_host')

    @property
    def DB_PORT(self):
        return self.get_config('ipman_db_port')

    @property
    def DB_NAME(self):
        return self.get_config('ipman_db_name')

    @property
    def DB_USER(self):
        return self.get_config('ipman_db_user')

    @property
    def DB_PASSWORD(self):
        return self.get_config('ipman_db_password')

    def get_db_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
