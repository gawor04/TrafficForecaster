#!/usr/bin/python
#-*- coding: utf-8 -*-
import re
import datetime

from collections import namedtuple


LaneProperties = namedtuple('LaneProperties', 'name vehicles_quantity small_vehicles big_vehicles mean_speed max_speed')
SimpleLaneProporties = namedtuple('SimpleLaneProporties', 'name vehicles_quantity mean_speed')
Lane = namedtuple('Lane', 'name lane_proporites')
Directory = namedtuple('Directory', 'name lanes_list')
Classificator = namedtuple('Classificator', 'name directories_list')
Time = namedtuple('Time', 'year month day hour minute')

class TFZIKiTMapParser:

    def parse(self, HTML_string):

        self._HTML_string = HTML_string
        classificators = []

        if HTML_string.find('<title>ZIKiT Kraków - mapa</title') != -1:
            self.__classificators_strings = re.findall(r'markers\[\d+\]\s=\snew\sgoogle.maps.Marker.*?Klasyfikator\sruchu\spojazdów\s(.*?);', self._HTML_string)
            self.__classificators_names = re.findall(r'markers\[\d+\]\s=\snew\sgoogle.maps.Marker.*?Klasyfikator\sruchu\spojazdów\s.*nazwa:\'(.*?)\'.*\;', self._HTML_string)

            for idx in range(len(self.__classificators_names)):
                classificator = Classificator(self.__classificators_names[idx], self.__getDirectories(self.__classificators_strings[idx]))
                classificators.append(classificator)
        else:
            classificators = None

        return classificators

    def __getDirectories(self, classificator_string):

        directories_strings = re.findall(r'Kierunek\s(.*?)więcej', classificator_string)
        directories_names = re.findall(r'Kierunek\s\<b\>(.*?)\<', classificator_string)
        directories = []

        for idx in range(len(directories_names)):
            directory = Directory(directories_names[idx], self.__getLanes(directories_strings[idx]))
            directories.append(directory)

        return directories

    def __getLanes(self, lanes_string):

        lanes_names = self.__getLanesNames(lanes_string)
        lanes_vehicles_quantity = self.__getVehiclesQuantity(lanes_string, len(lanes_string))
        lanes_small_vehicles = self.__getSmallVehicles(lanes_string, len(lanes_string))
        lanes_big_vehicles = self.__getBigVehicles(lanes_string, len(lanes_string))
        lanes_mean_speeds = self.__getMeanSpeed(lanes_string, len(lanes_string))
        lanes_max_speeds = self.__getMaxSpeed(lanes_string, len(lanes_string))
        lanes = []
        complex_lanes = []

        for idx in range(len(lanes_names)):
            lanes.append(SimpleLaneProporties(lanes_names[idx], lanes_vehicles_quantity[idx], lanes_mean_speeds[idx]))

        return lanes

    def __getLanesNames(self, lanes_string):

        names_string = re.findall(r'(?:Parametr|Parametr/pas)\</th\>(.*?)\<tr\>\<td\sbgcolor=#CCCCCC>', lanes_string)
        names = re.findall(r'\<th\>(.*?)\</th\>', names_string[0])
        if(names[len(names)-1].find('pasy') != -1):
            del names[-1]

        return names

    def __getVehiclesQuantity(self, lanes_string, max_idx):

        vehicles_quantity_string = re.findall(r'(?:Ilość\spojazdów\s\[szt/10min\]|Iloć\spojazdów\s\[szt/10min\])\</td\>(.*?)\<tr\>\<td\sbgcolor=#CCCCCC>', lanes_string)
        vehicles_quantity = re.findall(r'(?:\<td\>|\<td\sbgcolor=yellow\>)(.*?)\</td\>', vehicles_quantity_string[0])
        self.__checkLen(vehicles_quantity, max_idx)

        return vehicles_quantity

    def __getSmallVehicles(self, lanes_string, max_idx):

        small_vehicles_string = re.findall(r'Pojazdy\s\<\s5m\s\[szt/10min\]\</td\>(.*?)\<tr\>\<td\sbgcolor=#CCCCCC>', lanes_string)
        small_vehicles = []

        if(len(small_vehicles_string) > 0):
            small_vehicles = re.findall(r'(?:\<td\>|\<td\sbgcolor=yellow\>)(.*?)\</td\>',small_vehicles_string[0])
            self.__checkLen(small_vehicles, max_idx)

        return small_vehicles

    def __getBigVehicles(self, lanes_string, max_idx):

        big_vehicles_string = re.findall(r'Pojazdy\s\>\s5m\s\[szt/10min\]\</td\>(.*?)\<tr\>\<td\sbgcolor=#CCCCCC>', lanes_string)
        big_vehicles = []

        if(len(big_vehicles_string) > 0):
            big_vehicles = re.findall(r'(?:\<td\>|\<td\sbgcolor=yellow\>)(.*?)\</td\>',big_vehicles_string[0])
            self.__checkLen(big_vehicles, max_idx)

        return big_vehicles

    def __getMeanSpeed(self, lanes_string, max_idx):

        mean_speeds_string = re.findall(r'Prędkosć\sśrednia\s\[km/h\]\</td\>(.*?)\<tr\>', lanes_string)
        mean_speeds = []

        if(len(mean_speeds_string) == 0):
            mean_speeds_string = re.findall(r'Prędkoć\srednia\s\[km/h\]\</td\>(.*?)\</table\>', lanes_string)

        if(len(mean_speeds_string) > 0):
            mean_speeds = re.findall(r'(?:\<td\>|\<td\sbgcolor=yellow\>)(.*?)\</td\>', mean_speeds_string[0])
            self.__checkLen(mean_speeds, max_idx)

        return mean_speeds

    def __getMaxSpeed(self, lanes_string, max_idx):

        max_speed_string = re.findall(r'\<tr\>\<td\sbgcolor=#CCCCCC\>Prędkosć\smaksymalna\s\[km/h\]\</td\>(.*?)\</tr\>', lanes_string)
        max_speeds = []


        if(len(max_speed_string) > 0):
            max_speeds = re.findall(r'(?:\<td\>|\<td\sbgcolor=yellow\>)(.*?)\</td\>', max_speed_string[0])
            self.__checkLen(max_speeds, max_idx)

        return max_speeds

    def getTime(self, HTML_string):

 #       time_string = (re.findall(r'\<a\stitle=\'Zaloguj\ssię,\saby\szmienić\sczas\si/lub\sokres\spomiaru\'\>Dane\sz:\s(.*?)-(.*?)-(.*?)\s(.*?):(.*?)\</a\>', HTML_string))
        time_string = list((re.findall(r'Dane\spojazdowe\sz\sgodz\s(.*?):(.*?)\s(.*?)-(.*?)-(.*?)</font>', HTML_string))[0])
        time = []
        if(len(time_string) > 0):
            time = Time(int(time_string[2]), int(time_string[3]), int(time_string[4]), int(time_string[0]), int(time_string[1]))
        else:
            print("parse time from html error")
            print(time_string)

        return datetime.datetime(*time[:5])

    def __checkLen(self, list, max_idx):

        if(len(list) > max_idx):
            del list[-1]

