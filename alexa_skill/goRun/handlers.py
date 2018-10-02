import requests
import traceback
import json
from bs4 import BeautifulSoup


class Marathon():
    '''
    '''

    def __init__(self):
        pass

    def get_marathon_data(self, date_range=None, type1=None, cities=None, start_date=None, end_date=None):

        base_url = "http://indiarunning.com/race-finder.html"
        # example :
        # http://indiarunning.com/race-finder.html?DateRange=all&type1=10k,5k&Cities=Mumbai&From=2018-10-07&To=2018-10-12

        params = {
            'DateRange': date_range,
            'type1': type1,
            'Cities': cities,
            'From': start_date,
            'To': end_date
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

            print(base_url)

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
