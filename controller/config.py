import os
from configparser import ConfigParser


class Config(ConfigParser):
    def __init__(self, path='system.ini'):
        super().__init__()
        self.path = path
        self.read(self.path)

    def save(self):
        with open(self.path, 'w') as f:
            self.write(f)

    def load(self, path):
        try:
            self.read(path)
        except IOError:
            print('File not existed')


if __name__ == '__main__':
    conf = Config()
    print(conf.items('controller'))
