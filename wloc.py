# -*- coding: utf-8 -*-
#!/usr/bin/python

# Mostly taken from paper by François-Xavier Aguessy and Côme Demoustier
# http://fxaguessy.fr/rapport-pfe-interception-ssl-analyse-donnees-localisation-smartphones/

import code
import sys

import BSSIDApple_pb2
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# python3
unicode = str

def padBSSID(bssid):
	result = ''
	for e in bssid.split(':'):
		if len(e) == 1:
			e='0%s'%e
		result += e+':'
	return result.strip(':')

def ListWifiLocsApple(wifi_list):
	apdict = {}
	for wifi in wifi_list.wifi:
		if wifi.HasField('location'):
			lat=wifi.location.latitude*pow(10,-8)
			lon=wifi.location.longitude*pow(10,-8)

			mac=padBSSID(wifi.bssid)
			apdict[mac] = (lat,lon)
	return apdict

def QueryBSSID(query, more_results=True):
	list_wifi = BSSIDApple_pb2.BlockBSSIDApple()
	if type(query) in (str,unicode):
		bssid_list = [query]
	elif type(query) == list:
		bssid_list = query
	else:
		raise TypeError('Provide 1 BSSID as string or multiple BSSIDs as list of strings')
	for bssid in bssid_list:
		wifi = list_wifi.wifi.add()
		wifi.bssid = bssid
	if more_results:
		list_wifi.return_single_result = 0 # last byte in request == 0 means return ~400 results, 1 means only return results for BSSIDs queried
	else:
		list_wifi.return_single_result = 1
	ser_list_wifi = list_wifi.SerializeToString()
	length_ser_list_wifi = len(ser_list_wifi)
	headers = {'Content-Type':'application/x-www-form-urlencoded', 'Accept':'*/*', "Accept-Charset": "utf-8","Accept-Encoding": "gzip, deflate",\
			"Accept-Language":"en-us", 'User-Agent':'locationd/1753.17 CFNetwork/711.1.12 Darwin/14.0.0'}
	data = "\x00\x01\x00\x05"+"en_US"+"\x00\x13"+"com.apple.locationd"+"\x00\x0a"+"8.1.12B411"+"\x00\x00\x00\x01\x00\x00\x00" + chr(length_ser_list_wifi) + ser_list_wifi.decode();
	r = requests.post('https://gs-loc.apple.com/clls/wloc',headers=headers,data=data,verify=False) # CN of cert on this hostname is sometimes *.ls.apple.com / ls.apple.com, so have to disable SSL verify
	list_wifi = BSSIDApple_pb2.BlockBSSIDApple() 
	list_wifi.ParseFromString(r.content[10:])
	return ListWifiLocsApple(list_wifi)
