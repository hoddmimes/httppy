#
# This program will scan HTTP server log files and try to identify brawler bot clients.
#  The program will update the file ./data/crawler-id-addresses.json with identified crawler / bot clients
import re
import json

crawler_json_patterns = []
crawler_json_addresses = []
crawler_addresses = []
prospects = []

http_server_log_dir = "/var/log/httpd/"
http_hosts = ["hoddmimes-access.log", "grimeton-access.log"]


def main():
    load_crawlers()  # load current identified crawlers
    scan_http_logs()  # scan http server logs
    analyze_prospects()
    save_ip_addresses()


def  save_ip_addresses():
    with open('data/crawler-ip-addresses.json', 'w') as outfile:
        json.dump(crawler_json_addresses, outfile)

def analyze_prospects():
    hosts_found =  []

    for i in range(len(prospects)):
        for j in range(len(prospects[i])):
            if not prospects[i][j] in hosts_found:
                count = count_occurencies( prospects[i][j])
                if count > 1:
                    hosts_found.append( prospects[i][j] )
                    print("found host: " + prospects[i][j])
                    toCrawlerAddresses( prospects[i][j], False)



def count_occurencies( ip_host : str ) -> int:
    count = 0
    for i in range(len(prospects)):
        if ip_host in prospects[i]:
            count = count + 1
    return count;

def test():
    m = re.search("PetalBot",
                  "Mozilla/5.0 (Linux; Android 7.0;) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 (compatible; PetalBot;+https://webmaster.petalsearch.com/site/petalbot)")
    print(m)


def scan_http_logs():
    for host in http_hosts:
        with open( http_server_log_dir + host) as f:
            ips = []
            contents = f.readlines()
            for logentry in contents:
                entry = parse_log_entry(logentry)
                if entry and (not local_client(entry)) and (not known_crawler(entry)):
                    if bot_pattern(entry["client"]):
                        toCrawlerAddresses(entry["ip"], True)
                    else:
                        if possibly_crawler(entry):
                            # print( entry["ip"] + "   " + entry["time"] + "  \"" + entry["request"] + "\"  " + entry["client"] );
                            ips.append(entry["ip"])
            prospects.append(ips)


def toCrawlerAddresses(ip_addr: str, isBot: bool) -> object:
    adr = dict()
    adr["ip"] = ip_addr;
    adr["bot"] = isBot;
    print("***** Added new crawler address " + ip_addr + " isbot: " + str(isBot))
    crawler_json_addresses.append(adr)
    crawler_addresses.append(ip_addr)


def local_client(entry: dict) -> bool:
    if entry["ip"].startswith('192.168.42'):
        return True
    else:
        return False


def known_crawler(entry: dict) -> bool:
    return entry["ip"] in crawler_addresses


def possibly_crawler(entry: dict):
    if (entry["status"] < str(400)):
        if entry["request"] == '/':
            return True
    return False


def bot_pattern(client: str) -> bool:
    for i in range(len(crawler_json_patterns)):
        m = re.search(crawler_json_patterns[i]["pattern"], client)
        if m:
            return True
    return False


def load_crawlers():
    with open('data/crawler-ip-addresses.json') as crawler_addr_file:
        file_contents = crawler_addr_file.read()
    global crawler_json_addresses
    crawler_json_addresses = json.loads(file_contents)

    with open('./data/crawler-agent-patterns.json') as crawler_pattern_file:
        file_contents = crawler_pattern_file.read()
    global crawler_json_patterns
    crawler_json_patterns = json.loads(file_contents)

    for i in range(len(crawler_json_addresses)):
        crawler_addresses.append(crawler_json_addresses[i]["ip"])


def parse_log_entry(logentry: str) -> dict:
    m = re.search(
        '^(\d+\.\d+\.\d+\.\d+).+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \"([^\"]*)\" (\d+) .+\"([^\"]*)\" \"([^\"]*)\"',
        logentry)
    if m:
        entry = {}
        entry["ip"] = m.group(1)
        entry["time"] = m.group(2)
        entry["request"] = m.group(3).split()[1]
        entry["status"] = m.group(4)
        entry["url"] = m.group(3).split()[1]
        entry["client"] = m.group(6)
        # print("url {" + entry["url"] + "}")
        return entry
    else:
        print("INV LOGENTRY: " + logentry)


# invalid


if __name__ == '__main__':
    main()
