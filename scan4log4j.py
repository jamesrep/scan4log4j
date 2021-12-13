#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# James - rewrote the code a bit to give some more options.
import requests
import concurrent.futures
import argparse
import os

MAX_POOL = 50

default_headers = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
   "Cache-Control": "max-age=0",
   "Upgrade-Insecure-Requests": "1",
   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
   "Accept-Language": "en-GB,en-US;q=0.9,en"
}

def scan(url, payloads, headers, split_headers, bPayloadInURL):
    print("[+] Testing url ", url)

    for payload in payloads:
        
        if split_headers:
            for header in headers:
                send_request(url, payload, [header])
        else:
            send_request(url, payload, headers)

        if(bPayloadInURL):
            strURL = url + "/" + payload
            send_request(strURL, payload, headers)


def send_request(url, payload, all_headers):
    all_headers = default_headers.copy()
    for header in all_headers:
        all_headers[header] = payload

    # Make it easier to create lists...
    if(url.find("http") != 0):
        if(url.find(":443") > 0):
            url = "https://{0}/".format(url)
        else:
            url = "http://{0}/".format(url)

    print('[+] Request send to {0} with payload {1}'.format(url , payload))

    try:
        resp = requests.get(url, headers=all_headers, allow_redirects=True, timeout=4, verify=False)
    except Exception as e:
        print("[-] Exception on request", str(e))

    if(resp == None):
        print("[-] No response from ", url)
    #else:
    #    print(resp.status_code, " - ", resp.text[:30].replace('\r', ' ').replace('\n', ' '))
    

def getPath(strFile):
    if(strFile.find(os.path.sep) >= 0):
        return strFile

    strScriptPath = os.path.dirname( os.path.abspath(__file__))
    return strScriptPath + os.path.sep + strFile

def main():    
    parser = argparse.ArgumentParser(description="Execute simple log4shell-scan")
    parser.add_argument("--urllist", help="Comma separated list of urls", type=str, required=False)
    parser.add_argument("--urls", help="File with a list of urls ", type=str, required=False, default='urls.txt')
    parser.add_argument("--directpayload", help="Specify the payload instead of reading it from a file ", type=str, required=False)
    parser.add_argument("--headers", help="List of headers ", type=str, required=False, default='headers.txt')
    parser.add_argument("--poolcount", help="Nr of tasks in pool ", type=int, required=False, default=60)
    parser.add_argument("--payloads", help="List of payloads ", type=str, required=False, default='payloads.txt')
    parser.add_argument("--splitheaders", help="If added then use for headers.", action="store_true", default=False)
    parser.add_argument("--payloadinurl", help="If added then payload in url.", action="store_true", default=True)

    args = parser.parse_args()     

    urls = []
    payloads = []
    headers = []

    if(args.urllist != None):
        get_urls = args.urllist.split(',')
    else:
        strUrls = getPath(args.urls)
        get_urls = open(strUrls, 'r').readlines()


    if(args.directpayload != None):
        payloads.append(args.directpayload )
    else:    
        strPayloads = getPath(args.payloads)
        get_payloads = open(strPayloads, 'r').readlines()
        for payload in get_payloads:
            payloads.append(payload.strip())

    strHeaders = getPath(args.headers)    
    get_headers = open(strHeaders, 'r').readlines()

    for url in get_urls:
        strUrl = url.strip()
        if(strUrl.find('#') == 0 or len(strUrl) < 1):
            continue
        urls.append(strUrl)

    for header in get_headers:
        headers.append(header.strip())
    
    executor = concurrent.futures.ProcessPoolExecutor(min(len(urls),min(MAX_POOL, args.poolcount)))
    futures = [executor.submit(scan, url, payloads, headers, args.splitheaders, args.payloadinurl) for url in urls]
    concurrent.futures.wait(futures)

if __name__ == "__main__":    
    main()