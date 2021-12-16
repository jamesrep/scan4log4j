# James - 2021-12-16
import socket
import fileinput
import signal

def handler(signum, frame):
    pass

signal.signal(signal.SIGINT, handler)

lstAll = []

for line in fileinput.input():
    try:
        lstAll.append(line)
    except KeyboardInterrupt:
        pass

print("[+] Resolving list of hostnames ....")

for line in lstAll:    
    try:
        ip = socket.gethostbyname(line.strip())
        print(ip)
    except:
        print("{0} - could not be resolved".format(line.strip()))

