import requests
import traceback
import json
import jellyfish
from bs4 import BeautifulSoup


class Marathon():
    '''
    '''

    def __init__(self):
        pass

    def get_marathon_data(self, date_range=None, type1=None, cities=None, month=None):

        base_url = "http://indiarunning.com/race-finder.html"
        # example :
        # http://indiarunning.com/race-finder.html?DateRange=all&type1=10k,5k&Cities=Mumbai&From=2018-10-07&To=2018-10-12

        # sanitizing the data
        city_map = {
            'JPR': "Jaipur",
            'MMB': "Mumbai",
            'BNKLR': "Bengaluru",
            'XN': "Chennai",
            'HTRBT': "Hyderabad",
            'KLKT': "Kolkata",
            'PN': "Pune",
            'TLH': "Delhi",
            'KMBTR': "Coimbatore",
            'AMTBT': "Ahmedabad"
        }

        race_type_map = {
            '5kae': "5k",
            'fivek': "5k",
            'five k': "5k",
            '5k': "5k",

            '2kae': "2k",
            'twok': "2k",
            'two k': "2k",
            '2k': "2k",

            '10kae': "10k",
            'tenk': "10k",
            '10 k': "10k",
            '10k': "10k",

            'half marathon': "Half",
            'half': "Half",
            '21k': "Half",
            'Half': "Half",
            'half run': "Half",

            'full marathon': "Full",
            'full': "Full",
            '42k': "Full",
            'Full': "Full",
            'full run': "Full"

        }

        date_range_map = {
            'NKSTWKNT': "week1",
            'NKST WKNT': "week1",
            'NKST MN0': "month1",
            'NKSTMN0': "month1"
        }

        month_map = {
            'JNR': "Jan",
            'FBRR': "Feb",
            'MRX': "Mar",
            'APRL': "Apr",
            'M': "May",
            'JN': "Jun",
            'JL': "Jul",
            'AKST': "Aug",
            'SPTMBR': "Sep",
            'OKTBR': "Oct",
            'NFMBR': "Nov",
            'TSMBR': "Dec"
        }

        if cities:
            try:
                city_approx = jellyfish.metaphone(str(cities))
                cities = city_map.get(str(city_approx))
            except Exception as e:
                city_approx = None
                pass

        if type1:
            type1 = race_type_map.get(str(type1))

        if date_range:
            date_range_approx = jellyfish.metaphone(str(date_range))

            if date_range_map.get(str(date_range_approx)):
                date_range = date_range_map.get(str(date_range_approx))

            if month_map.get(str(date_range_approx)):
                month = month_map.get(str(date_range_approx))
                date_range = None

        params = {
            'DateRange': date_range,
            'type1': type1,
            'Cities': cities,
            'Months': month
        }

        request_headers = {
        }

        if params:
            base_url = base_url + '?'
            tmp = True
            for key, val in params.items():
                if tmp:
                    base_url = base_url + str(key) + '=' + str(val) if val is not None else base_url
                else:
                    base_url = base_url + '&' + str(key) + '=' + \
                        str(val) if val is not None else base_url
                tmp = False

        try:
            print(base_url, "\n", "!!!")
            html_request = requests.get(base_url)
            html = BeautifulSoup(html_request.text, 'html.parser')
            res = []
            if html:
                nav = html.find('td', valign="top")
                data_list = nav.find_all('tr')
                data_list_size = len(data_list)
                if data_list:
                    # getting headers
                    header_list = []
                    header = data_list[0].find_all('td')
                    for i in header:
                        header_list.append(str(i.text))
                    # getting data
                    for item in data_list[1:]:
                        tmp_dict = {}
                        item_list = item.find_all('td')
                        for x, y in enumerate(item_list):
                            tmp_dict[header_list[x]] = str(y.text)
                        res.append(tmp_dict)
                else:
                    pass
            return False, res
        except Exception as e:
            traceback.print_exc()
            return True, e.__str__()
