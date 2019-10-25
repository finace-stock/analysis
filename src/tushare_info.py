#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tushare as ts


class StockInfo(object):
    def __init__(self, token=None):
        self._token = token
        self._ts_pro = ts.pro_api(token)

    def list_all_stocks(self):
        data = self._ts_pro.stock_basic(
            exchange="", list_status="L", fields="ts_code,symbol,name,area,industry,list_date"
        )
        data = data.values.tolist()

        return data

    @staticmethod
    def list_industries():
        result = ts.get_industry_classified()
        industry_classified = list(set([item[2] for item in result.values.tolist()]))

        return industry_classified
