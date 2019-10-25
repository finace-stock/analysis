import plotly as py
import plotly.graph_objs as go
import time
import warnings
import pandas as pd
import requests
import ast
import numpy as np
import datetime
from scipy.signal import argrelextrema
import json
import math
from scipy.optimize import leastsq
import plotly.io as pio

buy_upper_limit = 30000
overall_data_json = {"result": {}, "result_short": {}, "overall": {"result": []}, "predict": {}}
contract_details = {
    "ZC": {
        "name": "动力煤",
        "market": "郑",
        "quantity": 100,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "黑色",
    },
    "CY": {
        "name": "棉纱",
        "market": "郑",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "OI": {
        "name": "菜籽油",
        "market": "郑",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "RI": {
        "name": "早籼稻",
        "market": "郑",
        "quantity": 20,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "WH": {
        "name": "强麦",
        "market": "郑",
        "quantity": 20,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "FG": {
        "name": "玻璃",
        "market": "郑",
        "quantity": 20,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "化工",
    },
    "RS": {
        "name": "油菜籽",
        "market": "郑",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "RM": {
        "name": "菜籽粕",
        "market": "郑",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "JR": {
        "name": "粳稻",
        "market": "郑",
        "quantity": 20,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "LR": {
        "name": "晚籼稻",
        "market": "郑",
        "quantity": 20,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "SF": {
        "name": "硅铁",
        "market": "郑",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "黑色",
    },
    "SM": {
        "name": "锰硅",
        "market": "郑",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "黑色",
    },
    "CF": {
        "name": "棉花",
        "market": "郑",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "SR": {
        "name": "白糖",
        "market": "郑",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "TA": {
        "name": "PTA",
        "market": "郑",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "化工",
    },
    "AP": {
        "name": "苹果",
        "market": "郑",
        "quantity": 10,
        "contract": 0.07,
        "cycle_num": 8,
        "category": "农产品",
    },
    "PM": {
        "name": "普麦",
        "market": "郑",
        "quantity": 50,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "MA": {
        "name": "甲醇",
        "market": "郑",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "化工",
    },
    "CS": {
        "name": "玉米淀粉",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "M": {
        "name": "豆粕",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "A": {
        "name": "豆一",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "JM": {
        "name": "焦煤",
        "market": "连",
        "quantity": 60,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "黑色",
    },
    "JD": {
        "name": "鸡蛋",
        "market": "连",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "I": {
        "name": "铁矿石",
        "market": "连",
        "quantity": 100,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "黑色",
    },
    "FB": {
        "name": "纤维板",
        "market": "连",
        "quantity": 500,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "BB": {
        "name": "胶合板",
        "market": "连",
        "quantity": 500,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "PP": {
        "name": "聚丙烯",
        "market": "连",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "化工",
    },
    "C": {
        "name": "玉米",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "农产品",
    },
    "B": {
        "name": "豆二",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "Y": {
        "name": "豆油",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "L": {
        "name": "塑料",
        "market": "连",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "化工",
    },
    "P": {
        "name": "棕榈油",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "农产品",
    },
    "V": {
        "name": "PVC",
        "market": "连",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 8,
        "category": "化工",
    },
    "J": {
        "name": "焦炭",
        "market": "连",
        "quantity": 100,
        "contract": 0.05,
        "cycle_num": 13,
        "category": "黑色",
    },
    "HC": {
        "name": "热轧卷板",
        "market": "沪",
        "quantity": 10,
        "contract": 0.04,
        "cycle_num": 12,
        "category": "黑色",
    },
    "CU": {
        "name": "铜",
        "market": "沪",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 16,
        "category": "贵金属",
    },
    "AL": {
        "name": "铝",
        "market": "沪",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 16,
        "category": "有色",
    },
    "RU": {
        "name": "橡胶",
        "market": "沪",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 12,
        "category": "化工",
    },
    "NI": {
        "name": "镍",
        "market": "沪",
        "quantity": 1,
        "contract": 0.05,
        "cycle_num": 16,
        "category": "有色",
    },
    "SN": {
        "name": "锡",
        "market": "沪",
        "quantity": 1,
        "contract": 0.05,
        "cycle_num": 16,
        "category": "有色",
    },
    "AG": {
        "name": "白银",
        "market": "沪",
        "quantity": 15,
        "contract": 0.04,
        "cycle_num": 19,
        "category": "贵金属",
    },
    "BU": {
        "name": "沥青",
        "market": "沪",
        "quantity": 10,
        "contract": 0.04,
        "cycle_num": 12,
        "category": "化工",
    },
    "FU": {
        "name": "燃料油",
        "market": "沪",
        "quantity": 10,
        "contract": 0.08,
        "cycle_num": 8,
        "category": "能源",
    },
    "ZN": {
        "name": "锌",
        "market": "沪",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 16,
        "category": "有色",
    },
    "AU": {
        "name": "黄金",
        "market": "沪",
        "quantity": 1000,
        "contract": 0.04,
        "cycle_num": 19,
        "category": "贵金属",
    },
    "RB": {
        "name": "螺纹钢",
        "market": "沪",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 12,
        "category": "黑色",
    },
    "WR": {
        "name": "线材",
        "market": "沪",
        "quantity": 10,
        "contract": 0.07,
        "cycle_num": 12,
        "category": "黑色",
    },
    "PB": {
        "name": "铅",
        "market": "沪",
        "quantity": 5,
        "contract": 0.05,
        "cycle_num": 16,
        "category": "有色",
    },
    "SC": {
        "name": "原油",
        "market": "沪",
        "quantity": 1000,
        "contract": 0.05,
        "cycle_num": 19,
        "category": "能源",
    },
    "SH51": {
        "name": "50ETF",
        "market": "沪",
        "quantity": 1000,
        "contract": 0.05,
        "cycle_num": 19,
        "category": "能源",
    },
    "SH60": {
        "name": "浦发银行",
        "market": "沪",
        "quantity": 1000,
        "contract": 0.05,
        "cycle_num": 19,
        "category": "能源",
    },
    "CJ": {
        "name": "红枣",
        "market": "郑",
        "quantity": 5,
        "contract": 0.07,
        "cycle_num": 19,
        "category": "能源",
    },
    "EG": {
        "name": "乙二醇",
        "market": "连",
        "quantity": 10,
        "contract": 0.05,
        "cycle_num": 19,
        "category": "能源",
    },
    "SP": {
        "name": "纸浆",
        "market": "沪",
        "quantity": 10,
        "contract": 0.04,
        "cycle_num": 19,
        "category": "能源",
    },
}

file_base_dir = "E:\\nginx\\html\\highstock\\"


def get_qihuo_ohlc(pinzhong_id, time_scale=240):
    if time_scale == 240:
        dayline_prefix = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol="
    if time_scale < 240:
        dayline_prefix = (
            "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine"
            + str(time_scale)
            + "m?symbol="
        )
    #
    qh_url = dayline_prefix + pinzhong_id
    print(qh_url)
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


def get_stock_ohlc(pinzhong_id, time_scale):
    qh_url = (
        "https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol="
        + pinzhong_id
        + "&scale="
        + str(time_scale)
        + "&ma=no&datalen=200"
    )
    r = requests.get(qh_url)
    print(qh_url)
    response_string = r.text
    response_code = r.status_code
    if response_code != 200:
        print("remote server responses wrongly")
        return
    raw_array = json.loads(response_string)
    response_array = []
    for raw_item in raw_array:
        tmp_item = []
        tmp_item.append(raw_item["day"])
        tmp_item.append(raw_item["open"])
        tmp_item.append(raw_item["high"])
        tmp_item.append(raw_item["low"])
        tmp_item.append(raw_item["close"])
        response_array.append(tmp_item)
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
    print(response_array)
    return response_array


def get_output_idx(time_scale):
    json_idx = "result"
    if time_scale <= 60:
        json_idx = "result_short"
    return json_idx


def get_ohlc(pinzhong_id, time_scale):
    global file_base_dir
    if str(pinzhong_id).lower().startswith("sh") or str(pinzhong_id).lower().startswith("sz"):
        result_json = get_stock_ohlc(pinzhong_id, time_scale)

    else:
        result_json = get_qihuo_ohlc(pinzhong_id, time_scale)
        # result_json.append(get_last_qh_ohlc(pinzhong_id))
    result_json = result_json[-300:]

    overall_data_json[get_output_idx(time_scale)][pinzhong_id] = {}
    overall_data_json[get_output_idx(time_scale)][pinzhong_id]["ohlc"] = result_json
    cn_name = contract_details[pinzhong_id[:-4].upper()]["name"]
    overall_data_json[get_output_idx(time_scale)][pinzhong_id]["name"] = cn_name

    return result_json


def refine_min_max_list(min_list, max_list, raw_list):
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


def get_extreme_points(response_array, n=10):
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

    min_list, max_list = refine_min_max_list(min_list, max_list, raw_list)

    overall_max_posi = int(df.idxmax()["close"] - array_length)
    overall_min_posi = int(df.idxmin()["close"] - array_length)

    if overall_max_posi not in max_list:
        max_list.append(int(overall_max_posi))

    if overall_min_posi not in min_list:
        min_list.append(int(overall_min_posi))

    return sorted(min_list), sorted(max_list)


def get_value_list_from_indexes(response_array, index_list):
    result_list = []
    for idx in index_list:
        date_time = response_array[idx][0]
        close_value = response_array[idx][4]
        result_list.append([date_time, close_value])
    return result_list


def get_index_from_datetime(response_array, timenumber):
    for idx, value in enumerate(response_array):
        if value == timenumber:
            return idx
    return -1


def get_extreme_series(pinzhong_id, response_array, time_scale):
    min_list, max_list = get_extreme_points(response_array, 20)

    overall_data_json[get_output_idx(time_scale)][pinzhong_id]["min"] = get_value_list_from_indexes(
        response_array, min_list
    )
    overall_data_json[get_output_idx(time_scale)][pinzhong_id]["max"] = get_value_list_from_indexes(
        response_array, max_list
    )

    overall_min_list, overall_max_list = get_extreme_points(response_array, 60)
    overall_data_json[get_output_idx(time_scale)][pinzhong_id][
        "overall_min"
    ] = get_value_list_from_indexes(response_array, overall_min_list)
    overall_data_json[get_output_idx(time_scale)][pinzhong_id][
        "overall_max"
    ] = get_value_list_from_indexes(response_array, overall_max_list)

    return min_list, max_list, overall_min_list, overall_max_list


def get_polycurv_start_index(response_array, min_indexes, max_indexes, depth):
    if depth == 2:
        depth = 5
    if len(min_indexes) >= depth and len(max_indexes) >= depth:
        start_idx = min(max_indexes[-depth], min_indexes[-depth])
        start_idx = start_idx + len(response_array)
    else:
        start_idx = 1
    # start_idx = 1 #####################################
    return start_idx


def index_p2curv(df, start_index, depth=4):
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


def get_updown_start_index(response_array, min_indexes, max_indexes):
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


def get_line_list(response_array, start_index, point_list):
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


def get_line_from_point_list(response_array, start_index, point_list):
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

    result_slope = round((result_list[-1][1] - result_list[-2][1]) * 1000 / result_list[-1][1]) / 10

    return result_slope, result_list


def index_uplowline(
    pinzhong_id,
    response_array,
    overall_max_indexes,
    overall_min_indexes,
    max_list,
    min_list,
    time_scale,
):
    start_index = get_updown_start_index(response_array, overall_min_indexes, overall_max_indexes)
    max_point_list = get_line_list(response_array, start_index, max_list)
    min_point_list = get_line_list(response_array, start_index, min_list)
    max_line_slope, max_line_series = get_line_from_point_list(
        response_array, start_index, max_point_list
    )
    min_line_slope, min_line_series = get_line_from_point_list(
        response_array, start_index, min_point_list
    )

    overall_data_json[get_output_idx(time_scale)][pinzhong_id]["upperline"] = max_line_series
    overall_data_json[get_output_idx(time_scale)][pinzhong_id]["downline"] = min_line_series
    return max_line_slope, max_line_series, min_line_slope, min_line_series


def get_poly_fitting_series(
    pinzhong_id, response_array, min_indexes, max_indexes, depth, time_scale
):
    start_idx = get_polycurv_start_index(
        response_array, min_indexes, max_indexes, math.ceil(depth / 2)
    )
    df = pd.DataFrame(response_array, columns=["date", "open", "high", "low", "close"])
    fitting_series, predict_rate = index_p2curv(df, start_idx, depth)
    # updown_rate = round((fitting_series[-1][1] - fitting_series[-min(40, len(fitting_series))][1])*1000/fitting_series[-1][1])/10
    updown_rate = (
        round((fitting_series[-1][1] - fitting_series[-2][1]) * 1000000 / fitting_series[-1][1])
        / 10
    )

    overall_data_json[get_output_idx(time_scale)][pinzhong_id][
        "fitting" + str(depth)
    ] = fitting_series
    return predict_rate, fitting_series


def get_contract_size(pinzhong_id, last_price):
    pinzhong_id = pinzhong_id[:-4]
    if pinzhong_id.upper() not in contract_details:
        return 1
    detailed_item = contract_details[str(pinzhong_id).upper()]

    return round(
        buy_upper_limit
        / (detailed_item["quantity"] * (detailed_item["contract"] + 0.03) * last_price * 2)
    )


def generate_one_piece(pinzhong_id, time_scale, length, is_curv_overall=False):
    response_array = get_ohlc(pinzhong_id, time_scale)
    min_list, max_list, overall_min_list, overall_max_list = get_extreme_series(
        pinzhong_id, response_array, time_scale
    )
    if is_curv_overall:
        predict_rate, _ = get_poly_fitting_series(
            pinzhong_id, response_array, overall_min_list, overall_max_list, length, time_scale
        )
    else:
        predict_rate, _ = get_poly_fitting_series(
            pinzhong_id, response_array, min_list, max_list, length, time_scale
        )

    max_line_slope, max_line_series, min_line_slope, min_line_series = index_uplowline(
        pinzhong_id,
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


def generate_one(pinzhong_id):
    print(pinzhong_id)

    predict_short_5, short_overall_slope, short_last_price = generate_one_piece(
        pinzhong_id, 60, 2, False
    )
    predict_long_5, long_overall_slope, long_last_price = generate_one_piece(
        pinzhong_id, 240, 2, False
    )
    print(predict_long_5, predict_short_5)
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

    can_buy_size = get_contract_size(pinzhong_id, short_last_price)

    overall_data_json["overall"]["result"].append(
        {
            "name": pinzhong_id,
            "cname": contract_details[pinzhong_id.upper()[:-4]]["name"],
            "score": score,
            "buysize": can_buy_size,
            "bgcolor": bgcolor,
            "price": short_last_price,
        }
    )
    overall_data_json["predict"][pinzhong_id] = {}
    overall_data_json["predict"][pinzhong_id]["long"] = round(
        long_last_price * (predict_long_5 / 100 + 1), 3
    )
    overall_data_json["predict"][pinzhong_id]["short"] = round(
        short_last_price * (predict_short_5 / 100 + 1), 3
    )


"""
     ['j2001', '焦炭2001'],
     ['i2001', '铁矿2001'],
     ['rb2001', '螺纹钢2001'],
     ['ta2001', 'PTA2001'],
     ['ma2001', '甲醇2001'],

     ['p2001', '棕榈油2001'],
     ['ap2001', '苹果2001'],
     ['cf2001', '棉花2001'],
     ['eg2001', '乙二醇2001'],
     """

if __name__ == "__main__":
    code_list = [
        ["sh600000", "浦发银行"],
        ["sh510050", "50ETF"],
        ["m2001", "豆粕2001"],
        ["c2001", "玉米2001"],
    ]

    # while True:
    overall_data_json = {"result": {}, "result_short": {}, "overall": {"result": []}, "predict": {}}
    for code in code_list:
        generate_one(code[0])
    result_json_filename = file_base_dir + "overall.json"
    overall_data_json["overall"]["result"].sort(key=lambda x: abs(x["score"]), reverse=True)
    with open(result_json_filename, "w") as fp:
        json.dump(overall_data_json, fp)
    print(datetime.datetime.now())
    #    time.sleep(300)
