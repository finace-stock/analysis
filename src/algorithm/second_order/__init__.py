#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import datetime
import json
import logging
import math
import time

import numpy as np
import pandas as pd
import requests
from scipy.signal import argrelextrema

from algorithm.base import Algorithm
from .config import STOCK_QUERY_URL, BuyType, FUTURES_DAILY_KLINE_URL, FUTURES_INNER_KLINE_URL

logger = logging.getLogger(__name__)
buy_upper_limit = 30000
overall_data_json = {"result": {}, "result_short": {}, "overall": {"result": []}, "predict": {}}


#
#
# def get_contract_size(pinzhong_id, last_price):
#     pinzhong_id = pinzhong_id[:-4]
#     if pinzhong_id.upper() not in contract_details:
#         return 1
#     detailed_item = contract_details[str(pinzhong_id).upper()]
#
#     return round(
#         buy_upper_limit
#         / (detailed_item["quantity"] * (detailed_item["contract"] + 0.03) * last_price * 2)
#     )


class SecondOrder(Algorithm):
    def __init__(self, symbol=None, name=None, industry=None, target_type=BuyType.Stock.value):
        self._id = symbol
        self._name = name
        self._industry = industry
        self._type = target_type

    @staticmethod
    def _get_index_from_datetime(response_array, time_number):
        for idx, value in enumerate(response_array):
            if value == time_number:
                return idx
        return -1

    @staticmethod
    def _get_output_idx(time_scale):
        json_idx = "result"
        if time_scale <= 60:
            json_idx = "result_short"
        return json_idx

    def _refine_min_max_list(self, min_list, max_list, raw_list):
        min_length = len(min_list) - 1

        for idx, item in enumerate(min_list):
            if idx < min_length:
                tmp_min_idx = item
                tmp_max_idx = min_list[idx + 1]
                already_in = False
                for tmp_item in max_list:
                    if tmp_min_idx < tmp_item < tmp_max_idx:
                        already_in = True
                        break
                if already_in is False:
                    tmp_list = raw_list[tmp_min_idx:tmp_max_idx]
                    tmp_idx = tmp_list.index(max(tmp_list))
                    tmp_idx = tmp_idx + tmp_min_idx

                    max_list.append(tmp_idx)
        max_list = sorted(max_list)
        max_length = len(max_list) - 1
        for idx, item in enumerate(max_list):
            if idx < max_length:
                tmp_min_idx = item
                tmp_max_idx = max_list[idx + 1]
                already_in = False
                for tmp_item in min_list:
                    if tmp_min_idx < tmp_item < tmp_max_idx:
                        already_in = True
                        break
                if already_in is False:
                    tmp_list = raw_list[tmp_min_idx:tmp_max_idx]
                    tmp_idx = tmp_list.index(min(tmp_list))
                    tmp_idx = tmp_idx + tmp_min_idx

                    min_list.append(tmp_idx)
        min_list = sorted(min_list)
        return min_list, max_list

    def _get_extreme_points(self, response_array, n=10):
        array_length = len(response_array)
        df = pd.DataFrame(response_array, columns=["date", "open", "high", "low", "close"])

        df["min"] = df.iloc[argrelextrema(df.close.values, np.less, order=n)[0]]["close"]
        df["max"] = df.iloc[argrelextrema(df.close.values, np.greater, order=n)[0]]["close"]
        final_min = df["min"].notna()
        min_list = df.index[final_min].tolist()
        min_list = [x - array_length for x in min_list]
        final_max = df["max"].notna()
        max_list = df.index[final_max].tolist()
        max_list = [x - array_length for x in max_list]
        raw_list = df["close"].tolist()

        min_list, max_list = self._refine_min_max_list(min_list, max_list, raw_list)

        overall_max_posi = int(df.idxmax()["close"] - array_length)
        overall_min_posi = int(df.idxmin()["close"] - array_length)

        if overall_max_posi not in max_list:
            max_list.append(int(overall_max_posi))

        if overall_min_posi not in min_list:
            min_list.append(int(overall_min_posi))

        return sorted(min_list), sorted(max_list)

    def _get_value_list_from_indexes(self, response_array, index_list):
        result_list = []
        for idx in index_list:
            date_time = response_array[idx][0]
            close_value = response_array[idx][4]
            result_list.append([date_time, close_value])
        return result_list

    def _get_extreme_series(self, symbol, response_array, time_scale):
        min_list, max_list = self._get_extreme_points(response_array, 20)

        overall_data_json[self._get_output_idx(time_scale)][symbol][
            "min"
        ] = self._get_value_list_from_indexes(response_array, min_list)
        overall_data_json[self._get_output_idx(time_scale)][symbol][
            "max"
        ] = self._get_value_list_from_indexes(response_array, max_list)

        overall_min_list, overall_max_list = self._get_extreme_points(response_array, 60)
        overall_data_json[self._get_output_idx(time_scale)][symbol][
            "overall_min"
        ] = self._get_value_list_from_indexes(response_array, overall_min_list)
        overall_data_json[self._get_output_idx(time_scale)][symbol][
            "overall_max"
        ] = self._get_value_list_from_indexes(response_array, overall_max_list)

        return min_list, max_list, overall_min_list, overall_max_list

    def _get_polycurv_start_index(self, response_array, min_indexes, max_indexes, depth):
        if depth == 2:
            depth = 5
        if len(min_indexes) >= depth and len(max_indexes) >= depth:
            start_idx = min(max_indexes[-depth], min_indexes[-depth])
            start_idx = start_idx + len(response_array)
        else:
            start_idx = 1
        # start_idx = 1 #####################################
        return start_idx

    def _index_p2curv(self, df, start_index, depth=4):
        result_array = []
        y = df["close"].astype(np.float)[start_index:]
        date_array = df["date"].astype(np.float)[start_index:]
        x = list(range(0, len(y)))
        z = np.polyfit(x, y, depth)
        p = np.poly1d(z)
        for x_value in x:
            result_y = p(x_value)
            result_array.append([date_array[start_index + x_value], result_y])
        predict_rate = round(p(max(x) + 10) * 100 / y.tolist()[-1] - 100, 2)
        return result_array, predict_rate

    def _get_updown_start_index(self, response_array, min_indexes, max_indexes):
        start_idx = -len(response_array)
        if len(min_indexes) > 0 and len(max_indexes) > 0:
            start_idx = min(max_indexes[-1], min_indexes[-1])
        if len(min_indexes) > 0 and len(max_indexes) == 0:
            start_idx = min_indexes[-1]
        if len(min_indexes) == 0 and len(max_indexes) > 0:
            start_idx = max_indexes[-1]
        if start_idx > -30:
            start_idx = -100
        start_idx = start_idx + len(response_array)
        return max(start_idx - 10, 0)

    def _get_line_list(self, response_array, start_index, point_list):
        start_index = start_index - len(response_array)
        result_list = []
        for idx in point_list:
            if idx > start_index:
                result_list.append([idx, response_array[idx][1]])
        if len(result_list) < 2 and len(point_list) >= 2:
            result_list = []
            result_list.append([point_list[-2], response_array[point_list[-2]][1]])
            result_list.append([point_list[-1], response_array[point_list[-1]][1]])
        return result_list

    def _get_line_from_point_list(self, response_array, start_index, point_list):
        # point_list = get_line_list(response_array, start_index, point_list)
        result_list = []
        x = []
        y = []
        for point in point_list:
            # x.append(point + len(response_array))
            # y.append(response_array[point][1])
            x.append(point[0] + len(response_array))
            y.append(point[1])
        if len(x) == 1:
            x.append(x[0] + 1)
            y.append(y[0])
        z = np.polyfit(x, y, 1)

        p = np.poly1d(z)
        x = np.array(range(start_index, len(response_array)))
        for idx in x:
            result_list.append([response_array[idx][0], p(idx)])

        result_slope = (
            round((result_list[-1][1] - result_list[-2][1]) * 1000 / result_list[-1][1]) / 10
        )

        return result_slope, result_list

    def _index_uplowline(
        self,
        symbol,
        response_array,
        overall_max_indexes,
        overall_min_indexes,
        max_list,
        min_list,
        time_scale,
    ):
        start_index = self._get_updown_start_index(
            response_array, overall_min_indexes, overall_max_indexes
        )
        max_point_list = self._get_line_list(response_array, start_index, max_list)
        min_point_list = self._get_line_list(response_array, start_index, min_list)
        max_line_slope, max_line_series = self._get_line_from_point_list(
            response_array, start_index, max_point_list
        )
        min_line_slope, min_line_series = self._get_line_from_point_list(
            response_array, start_index, min_point_list
        )

        overall_data_json[self._get_output_idx(time_scale)][symbol]["upperline"] = max_line_series
        overall_data_json[self._get_output_idx(time_scale)][symbol]["downline"] = min_line_series
        return max_line_slope, max_line_series, min_line_slope, min_line_series

    def _get_poly_fitting_series(
        self, symbol, response_array, min_indexes, max_indexes, depth, time_scale
    ):
        start_idx = self._get_polycurv_start_index(
            response_array, min_indexes, max_indexes, math.ceil(depth / 2)
        )
        df = pd.DataFrame(response_array, columns=["date", "open", "high", "low", "close"])
        fitting_series, predict_rate = self._index_p2curv(df, start_idx, depth)
        # updown_rate = round((fitting_series[-1][1] - fitting_series[-min(40, len(fitting_series))][1])*1000/fitting_series[-1][1])/10
        updown_rate = (
            round((fitting_series[-1][1] - fitting_series[-2][1]) * 1000000 / fitting_series[-1][1])
            / 10
        )

        overall_data_json[self._get_output_idx(time_scale)][symbol][
            "fitting" + str(depth)
        ] = fitting_series
        return predict_rate, fitting_series

    def _get_qihuo_ohlc(self, symbol, time_scale=240):
        qh_url = ""
        if time_scale == 240:
            qh_url = FUTURES_DAILY_KLINE_URL.format(symbol=symbol)
        if time_scale < 240:
            qh_url = FUTURES_INNER_KLINE_URL.format(scale=time_scale, symbol=symbol)
        #
        logger.debug("Qi huo url %s", qh_url)
        r = requests.get(qh_url)
        response_string = r.text
        response_code = r.status_code
        if response_code != 200:
            print("remote server responses wrongly")
            return
        else:
            response_array = ast.literal_eval(response_string)
            if len(response_array[-1][0].split(" ")) > 1:
                response_array = response_array[::-1]
        for item in response_array:
            if len(item[0].split(" ")) == 1:
                item[0] = item[0] + " 00:00:00"
            # item[0] = 1000*int(time.mktime(datetime.datetime.strptime(item[0], "%Y-%m-%d %H:%M:%S").timetuple()))
            raw_datetime = datetime.datetime.strptime(
                item[0], "%Y-%m-%d %H:%M:%S"
            ) + datetime.timedelta(hours=8)
            item[0] = 1000 * int(time.mktime(raw_datetime.timetuple()))
            item[1] = float(item[1])
            item[2] = float(item[2])
            item[3] = float(item[3])
            item[4] = float(item[4])
            del item[5]
        return response_array

    def _get_stock_ohlc(self, symbol, time_scale):
        qh_url = STOCK_QUERY_URL.format(symbol=symbol, scale=time_scale, len=200)
        r = requests.get(qh_url)
        logger.debug("stock query url %s", qh_url)
        response_string = r.text
        response_code = r.status_code
        if response_code != 200:
            print("remote server responses wrongly")
            return
        raw_array = json.loads(response_string)
        response_array = []
        for raw_item in raw_array:
            tmp_item = [
                raw_item["day"],
                raw_item["open"],
                raw_item["high"],
                raw_item["low"],
                raw_item["close"],
            ]
            response_array.append(tmp_item)
        # TODO: separate into single function
        for item in response_array:
            if len(item[0].split(" ")) == 1:
                item[0] = item[0] + " 00:00:00"
            # item[0] = 1000*int(time.mktime(datetime.datetime.strptime(item[0], "%Y-%m-%d %H:%M:%S").timetuple()))
            raw_datetime = datetime.datetime.strptime(
                item[0], "%Y-%m-%d %H:%M:%S"
            ) + datetime.timedelta(hours=8)
            item[0] = 1000 * int(time.mktime(raw_datetime.timetuple()))
            item[1] = float(item[1])
            item[2] = float(item[2])
            item[3] = float(item[3])
            item[4] = float(item[4])
        # print(response_array)
        return response_array

    def _get_ohlc(self, symbol, time_scale):
        result_json = []
        if self._type == BuyType.Stock.value:
            result_json = self._get_stock_ohlc(symbol, time_scale)
        elif self._type == BuyType.QiHuo.value:
            result_json = self._get_qihuo_ohlc(symbol, time_scale)
        result_json = result_json[-300:]

        overall_data_json[self._get_output_idx(time_scale)][symbol] = {}
        overall_data_json[self._get_output_idx(time_scale)][symbol]["ohlc"] = result_json
        overall_data_json[self._get_output_idx(time_scale)][symbol]["name"] = self._name

        return result_json

    def _generate_one_piece(self, symbol, time_scale, length, is_curv_overall=False):
        response_array = self._get_ohlc(symbol, time_scale)
        min_list, max_list, overall_min_list, overall_max_list = self._get_extreme_series(
            symbol, response_array, time_scale
        )
        if is_curv_overall:
            predict_rate, _ = self._get_poly_fitting_series(
                symbol, response_array, overall_min_list, overall_max_list, length, time_scale
            )
        else:
            predict_rate, _ = self._get_poly_fitting_series(
                symbol, response_array, min_list, max_list, length, time_scale
            )

        max_line_slope, max_line_series, min_line_slope, min_line_series = self._index_uplowline(
            symbol,
            response_array,
            overall_max_list,
            overall_min_list,
            max_list,
            min_list,
            time_scale,
        )
        overall_slope = max_line_slope + min_line_slope
        last_price = response_array[-1][4]
        return predict_rate, overall_slope, last_price

    def analyze(self):
        logger.info("analyze stock %s", self._id)

        predict_short_5, short_overall_slope, short_last_price = self._generate_one_piece(
            self._id, 60, 2, False
        )
        predict_long_5, long_overall_slope, long_last_price = self._generate_one_piece(
            self._id, 240, 2, False
        )
        logger.info("%s: predict long_5 %s short_5 %s", self._name, predict_long_5, predict_short_5)

        score = 0
        bgcolor = "btn-warning"
        # if long_overall_slope > 0 and short_5 > 0 :
        if predict_long_5 > 0 and predict_short_5 > 0:
            bgcolor = "btn-danger"
            score = 100
        if predict_long_5 < 0 and predict_short_5 < 0:
            bgcolor = "btn-success"
            score = 100
        score = score + abs(predict_long_5 / 10 + predict_short_5 / 10)

        # can_buy_size = get_contract_size(self._id, short_last_price)
        data = {
            "result": {
                "name": self._id,
                "cname": self._name,
                "score": score,
                # "buysize": can_buy_size,
                "bgcolor": bgcolor,
                "price": short_last_price,
            },
            "predict": {
                "long": round(long_last_price * (predict_long_5 / 100 + 1), 3),
                "short": round(short_last_price * (predict_short_5 / 100 + 1), 3),
            },
        }

        return data
