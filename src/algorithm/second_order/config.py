from enum import Enum, unique, EnumMeta

STOCK_QUERY_URL = (
    "https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={symbol}"
    "&scale={scale}&ma=no&datalen={len}"
)

FUTURES_DAILY_KLINE_URL = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol={symbol}"
FUTURES_INNER_KLINE_URL = (
    "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine{scale}"
    "m?symbol={symbol}"
)


class ExtraEnum(Enum):
    @classmethod
    def get_info(cls, title="", list_str=False):
        str_info = """
        """
        str_info += title
        if list_str:
            for name, member in cls.__members__.items():
                str_info += """
            %s
            """ % (
                    name.lower().replace("_", "."),
                )
        else:
            for name, member in cls.__members__.items():
                str_info += """
            %s: %s
            """ % (
                    member.value,
                    name,
                )
        return str_info

    @classmethod
    def to_choices(cls, string_as_value=False):
        if string_as_value:
            choices = [
                (name.lower().replace("_", "."), name) for name, member in cls.__members__.items()
            ]
        else:
            choices = [(member.value, name) for name, member in cls.__members__.items()]

        return choices

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls.__members__.values()))

    @classmethod
    def names(cls):
        return [name.lower() for name, _ in cls.__members__.items()]


@unique
class BuyType(ExtraEnum):
    Stock = "stock"
    QiHuo = "qi_huo"
    QiQuan = "qi_quan"
