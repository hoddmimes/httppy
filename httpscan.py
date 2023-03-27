import re
import json

crawler_addresses = []
http_server_log_dir = './'

def main():
    load_crawler_data()
    scan_http_log('grimeton')
    scan_http_log('hoddmimes')
    

def test():
    m = re.search("PetalBot", "Mozilla/5.0 (Linux; Android 7.0;) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 (compatible; PetalBot;+https://webmaster.petalsearch.com/site/petalbot)")
    print(m)


def scan_http_log(server: str ):
    with open( http_server_log_dir  + server + '-access.log') as f:
        contents = f.readlines()
    for logentry in contents:
        entry = parse_log_entry( logentry )
        if entry:
            if  (entry["status"] < str(400) ) and not local_client(entry) and not known_crawler(entry):
                print( "[" + server[0:1] + "] " + entry["ip"] + "   " + entry["time"] + "  \"" + entry["url"] + "\"  " + entry["client"] );
        else:
            print("INVLD LOGENTRY: " + logentry )


def known_crawler(entry: dict) -> bool:
    if entry["ip"] in crawler_addresses:
        # print(" bot filter ip: " + entry["ip"] )
        return True
    else:
        return False


def local_client(entry: dict) -> bool:
    if entry["ip"].startswith('192.168.42'):
        return True
    else:
        return False


def load_crawler_data():
    with open('data/crawler-ip-addresses.json') as user_file:
        file_contents = user_file.read()
    crawler_json_addresses = json.loads(file_contents)
    for i in range(len(crawler_json_addresses)):
        crawler_addresses.append(crawler_json_addresses[i]["ip"])


def parse_log_entry( logentry : str) -> dict:
    m = re.search('^(\d+\.\d+\.\d+\.\d+).+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \"([^\"]*)\" (\d+) .+\"([^\"]*)\" \"([^\"]*)\"', logentry )
    if m:
        entry = {}
        entry["ip"] = m.group(1)
        entry["time"]  = m.group(2)
        entry["request"] = m.group(3).split()[1]
        entry["status"] = m.group(4)
        entry["url"] =  m.group(3).split()[1]
        entry["client"] = m.group(6)
        #print(entry)
        return entry
    else:
        print("INV LOGENTRY: " + logentry )

# invalid



if __name__ == '__main__':
    main()
