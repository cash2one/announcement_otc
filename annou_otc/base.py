# -*- coding: utf-8 -*-

import sys
import time
import linecache
from random import sample
from datetime import datetime
from string import digits, letters

from eggs.dbs import Mongodb
from config.config_otc import PORT
from config.config_otc import STOCK_DB, STOCK_HOST, STOCK_TABLE
from annou_parser import TypFieldIdentification, CatFiledIdentification

coll_stock = Mongodb(STOCK_HOST, PORT, STOCK_DB, STOCK_TABLE)


def error_info():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('Exception in:({}, LINE {} "{}") \n\tError: {}'.format(filename, lineno, line.strip(), exc_obj))


class DataPopulation(TypFieldIdentification, CatFiledIdentification):
    def __init__(self, code, file_path, pub, title, file_ext, pdt):
        self.__code = code
        self.__pub = pub
        self.__pdt = pdt
        self.__src = file_path
        super(DataPopulation, self).__init__(title, file_path, file_ext)

    @property
    def pdt(self):
        return datetime.strptime(self.__pub, '%Y-%m-%d')

    @classmethod
    def other_secu(cls, code):
        query = {'tick': code}
        fields = {'code': 1, 'org.id': 1, 'mkt.code': 1}

        if code == '000000':
            raise ValueError('Code: <%s> 券商' % code)

        # secu限定如果不是券商公告(code：000000)的全部加 _QS_EQ
        secu = [{'cd': code + '_QS_EQ', 'mkt': '', 'org': ''}]

        try:
            stock_dict = coll_stock.get(query, fields)
            secu[0]['mkt'] = stock_dict['mkt']['code']
            secu[0]['org'] = stock_dict['org']['id']
        except (KeyError, TypeError, IndexError):
            pass
        return secu

    @property
    def other_pub(self):
        return self.__pub

    @property
    def other_src(self):
        return self.__src

    @property
    def other_sid(self):
        return self.__src

    @property
    def random_characters(self):
        characters = sample(letters, 8) + sample(digits, 5) + sample(letters, 5)
        return ''.join(characters)

    @property
    def other_pid(self):
        timestamp_rand = str(time.time()) + self.random_characters
        return self.encrypt_md5(timestamp_rand)

    def _others_field(self):
        others = {
            'title': self.file_title, 'pid': self.other_pid, 'upt': datetime.now(), 'crt': datetime.now(),
            'src': self.other_src, 'sid': self.other_sid, 'pdt': self.pdt, 'secu': self.other_secu(self.__code),
            'cru': '000000', 'upu': '000000',  'valid': '1', 'effect': None, 'check': False, 'audit': False,
            'pub': self.other_pub
        }

        if others['secu'][0]['org']:
            others['stat'] = 2
        else:
            others['stat'] = 1
        return others

    def populate_data(self):
        try:
            data = {}
            data.update(typ=self.get_typ())
            data.update(cat=self.get_cat())
            data.update(file=self.file_data())
            data.update(self._others_field())
            return data
        except Exception as e:
            error_info()
            print('Data Error: [{0}]'.format(e))

        return {}

    @staticmethod
    def close():
        coll_stock.disconnect()
        TypFieldIdentification.close()

