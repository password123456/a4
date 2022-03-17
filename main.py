__author__ = 'https://github.com/password123456/'

import os
import sys
import importlib
import json
import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from netaddr import valid_ipv4

importlib.reload(sys)

_today_ = datetime.today().strftime('%Y-%m-%d')
_ctime_ = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

_home_path_ = 'F:/code/pythonProject/collect_cloud_ips'
_db_ = '%s/db/%s-cloud_ipinfo.csv' % (_home_path_, _today_)

_headers_ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) \
             Chrome/49.0.2623.112 Safari/537.36', 'Content-Type': 'application/json; charset=utf-8'}


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def collect_azure_cloud_ips():

    _url = 'https://www.microsoft.com/en-eg/download/confirmation.aspx?id=56519'
    _azure_file = '%s/azure.json' % _home_path_
    _name_ = 'AZURE'

    if os.path.exists(_azure_file):
        create_time = os.stat(_azure_file).st_ctime
        azure_file_datetime = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d')
        today = datetime.now().date()

        if str(azure_file_datetime) == str(today):
            get_azure_cloud = True
        else:
            get_azure_cloud = False
    else:
        print('%s[+] Download New %s Cloud File%s' % (Bcolors.OKGREEN, _name_, Bcolors.ENDC))
        r = requests.get(_url, headers=_headers_, verify=True)
        if r.status_code == 200:
            body = r.text
            soup = BeautifulSoup(body, 'html.parser')
            result = soup.find('div', {'class': 'start-download'})
            if result:
                download_url = result.find('a').get('href')
                r = requests.get(download_url, headers=_headers_, verify=True)
                if r.status_code == 200:
                    body = r.text
                    with open(_azure_file, 'w') as f:
                        f.write(body)
                    f.close()
                    get_azure_cloud = True
                else:
                    res_status = r.status_code
                    message = '** %s_Cloud Collector **\n▶ Connection Error: http %s\n' % (_name_, res_status)
                    print(message)
                    sys.exit(1)
            else:
                message = '** %s_Cloud Collector **\n▶ Fail to Parse Download page\n %s\n' % (_name_, _url)
                print(message)
                sys.exit(1)

        else:
            res_status = r.status_code
            message = '** %s_Cloud Collector **\n▶ Connection Error: http %s\n' % (_name_, res_status)
            print(message)
            sys.exit(1)
        r.close()

    if not get_azure_cloud:
        print('%s[+] Downloaded %s Cloud File Found.%s' % (Bcolors.OKGREEN, _name_, Bcolors.ENDC))
        r = requests.get(_url, headers=_headers_, verify=True)
        if r.status_code == 200:
            body = r.text
            soup = BeautifulSoup(body, 'html.parser')
            result = soup.find('div', {'class': 'start-download'})
            if result:
                download_url = result.find('a').get('href')
                r = requests.get(download_url, headers=_headers_, verify=True)
                if r.status_code == 200:
                    body = r.text
                    with open(_azure_file, 'w') as f:
                        f.write(body)
                    f.close()
                else:
                    res_status = r.status_code
                    message = '** %s_Cloud Collector **\n▶ Connection Error: http %s\n' % (_name_, res_status)
                    print(message)
                    sys.exit(1)
            else:
                message = '** %s_Cloud Collector **\n▶ Fail to Parse Download page\n %s\n' % (_name_, _url)
                print(message)
                sys.exit(1)

        else:
            res_status = r.status_code
            message = '** %s_Cloud Collector **\n▶ Connection Error: http %s\n' % (_name_, res_status)
            print(message)
            sys.exit(1)

    with open(_azure_file, 'r') as azure_file:
        if os.path.exists(_db_):
            mode = 'a'
            header = True
        else:
            mode = 'w'
            header = False
        fa = open(_db_, mode)
        writer = csv.writer(fa, delimiter=',', lineterminator='\n')

        if not header:
            writer.writerow(['datetime', 'platform', 'create_time', 'region', 'ip_prefix', 'service'])

        azure_ip_dictionary = json.load(azure_file)
        n = 0
        print('%s[+] Collect %s Cloud IP Prefixes.%s' % (Bcolors.OKGREEN, _name_, Bcolors.ENDC))

        for ip_group in azure_ip_dictionary['values']:
            if ip_group['name'].startswith('AzureCloud.'):
                service = ip_group['name']
                region = ip_group['properties']['region']
                platform = ip_group['properties']['platform']
                iplist = ip_group['properties']['addressPrefixes']
                length = len(iplist)

                for ip_prefix in range(length):
                    ip_prefix = iplist[ip_prefix]

                    check_ipv4 = ip_prefix.split('/')[0]
                    ip_valid = valid_ipv4(check_ipv4)
                    if ip_valid:
                        try:
                            n = n + 1
                            writer.writerow([_ctime_, platform, _ctime_, region, ip_prefix, service])
                            sys.stdout.write('\r ----> Processing... %d lines' % n)
                            sys.stdout.flush()
                        except KeyboardInterrupt:
                            sys.exit(0)
                        except Exception as e:
                            print('%s- Exception::%s%s' % (Bcolors.WARNING, e, Bcolors.ENDC))
        fa.close()
    azure_file.close()
    

def main():
    collect_azure_cloud_ips()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print('%s- Exception::%s%s' % (Bcolors.WARNING, e, Bcolors.ENDC))
