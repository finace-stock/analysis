#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from tushare_info import StockInfo
from algorithm import SecondOrder
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ts_token = "180785c0bbc0efcfbecccc82e1fb2deaed9ed7e3a5149368374bc02c"


if __name__ == "__main__":
    # stock_info = StockInfo(token=ts_token)
    # stocks = stock_info.list_all_stocks()
    # for item in stocks[:4]:
    #     print(item)

    # industries = stock_info.list_industries()
    # with open("./data/industry.json", "w") as output_json:
    #     json.dump(industries, output_json)
    # data = pro.stock_basic(exchange='', list_status='L',
    #                        fields='ts_code,symbol,name,area,industry,list_date')
    # data = data.values.tolist()
    # print(tabulate(data, headers=["Code", "Symbol", "Name", "Area", "Industry", "List Date"]))
    # with open("./stocks.json", "w") as out_file:
    #     json.dump(data, out_file)
    # result = ts.get_industry_classified()
    # industry_classified = list(set([item[2] for item in result.values.tolist()]))
    # print(industry_classified)
    with open("./data/stocks.json", "r") as in_file:
        data = json.load(in_file)

    code_list = [
        ["{}{}".format(stock[0].split(".")[-1].lower(), stock[1]), stock[2], stock[4]]
        for stock in data
    ]
    # code_list = code_list[:100]

    analyze_data = {}
    for code in code_list:
        second_order_algorithm = SecondOrder(symbol=code[0], name=code[1], industry=code[2])
        second_order_algorithm.analyze()
        analyze_data[code[0]] = {
            "overall": second_order_algorithm.result["overall"],
            "predict": second_order_algorithm.result["predict"],
        }

    with open("result.json", "w") as result_json:
        json.dump(analyze_data, result_json)
