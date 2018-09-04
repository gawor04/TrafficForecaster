# -*- coding: utf-8 -*-
from datetime import datetime
from TFCarsGetter.TFZIKiTMapParser import TFZIKiTMapParser
import requests
import csv
from pathlib import Path
import io
import pandas
import logging


class TFCarsGetter:
    __logger = logging.getLogger(__name__)

    def __init__(self, out_files_path, csv_10min_name):

        self.__out_files_path = out_files_path
#        self.__html_name = html_name
        self.__csv_10min_name = csv_10min_name
        self.__get_request_result = True
        self.__last_day = datetime.now().day

    def task(self):

        r = self.__HTTPGetRequest()

        if self.__get_request_result:

            # ISO-8859-2 -> polish characters
            html_content = str(r.content, 'ISO-8859-2', errors='replace')

            map_parser = TFZIKiTMapParser()
            classificators = map_parser.parse(html_content)

            # write vehicles quantity every 10min, task should be called every 10 min
            self.__write10MinCSV(classificators)
            # save webpage
            #self.__writeHTML(html_content)
            if(self.__last_day != datetime.now().day):
                print("new day")

            self.__last_day = datetime.now().day

        else:
            self.__logger.warninig("HTTP request problem")

    def __HTTPGetRequest(self):

        self.__get_request_result = True

        try:
            # Zikit Kraków mapa
            r = requests.get('http://83.14.235.178/?B1=1440&H1=900')
        except requests.exceptions.RequestException as e:
            self.__logger.warning("__HTTPGetRequest error: " + str(e))
            self.__get_request_result = False

        return r

    def __write10MinCSV(self, classificators):

        row_val = []
        row_val.append(datetime.now().strftime("%Y-%m-%d %H:%M"))
        row_val += self.__getVehicles(classificators)

        field_names = []
        field_names.append('date')
        field_names += self.__getFieldNames(classificators)

        self.__writeCSV(self.__csv_10min_name, field_names, row_val)

    def __writeDayCSV(self, classificators, last_day):

        ten_min_csv = pandas.read_csv(self.__out_files_path + self.__csv_10min_name + '.csv', encoding='ISO-8859-2')
        times = ten_min_csv['date']
        day_string = last_day.strftime("%Y-%m-%d")

        day_idxs = [i for i, s in enumerate(times) if day_string in s]
        field_names = self.__getFieldNames(classificators)

        ten_min_csv = ten_min_csv.astype('str')
        veh_sum_list = []
        veh_sum_list.append(last_day.strftime("%Y-%m-%d"))

        for field_name in field_names:
            veh_sum = 0
            rep_list = [v.replace('-', '0') for v in ten_min_csv.iloc[day_idxs[0]:day_idxs[-1]][field_name]]

            for v in rep_list:
                veh_sum = str(int(v) + int(veh_sum))

            veh_sum_list.append(veh_sum)

        field_names = []
        field_names.append('date')
        field_names += self.__getFieldNames(classificators)

        self.__writeCSV(self.__csv_day_name, field_names, veh_sum_list)

    def __writeHTML(self, html_content):
        pass
        # save webpage, name template: self.__html_name_Year_Month_Day_Hour_Minute.html
        # try:
        #     with io.open(
        #             self.__out_files_path + self.__html_name + datetime.now().strftime("_%Y_%m_%d_%H_%M") + ".html",
        #             'w', encoding='ISO-8859-2') as f:
        #         f.write(html_content)
        #         f.close()
        #
        # except ValueError:
        #     self.__logger.fault("Write HTML error: " + str(ValueError))

    def __writeCSV(self, name, header, row_to_add):

        try:
            file_exists = True
            path = self.__out_files_path + name + '.csv'

            if not Path(path).is_file():
                file_exists = False

            with io.open(path, 'a', encoding='ISO-8859-2') as csv_file:

                writer = csv.DictWriter(csv_file, header)

                if not file_exists:
                    self.__logger.debug("Create" + path)
                    writer.writeheader()

                row = {}

                if len(header) == len(row_to_add):
                    for cell_idx in range(len(header)):
                        row[header[cell_idx]] = row_to_add[cell_idx]

                    writer.writerow(row)

                else:
                    self.__logger.warning('Header and row dimensions are not equal')
                    self.__logger.warning('Header: ')
                    self.__logger.warning(len(header))
                    self.__logger.warning('Row: ')
                    self.__logger.warning(len(row_to_add))

                csv_file.close()

        except ValueError:
            self.__logger.error("Write CSV error: " + str(ValueError))

    def __getFieldNames(self, classificators):

        field_names = []

        for classificator in classificators:
            for directory in classificator.directories_list:
                for lane in directory.lanes_list:
                    field_names.append(classificator.name + ":" + directory.name + ":" + lane.name)

        return field_names

    def __getVehicles(selfself, classificators):

        vehicles = []

        for classificator in classificators:
            for directory in classificator.directories_list:
                for lane in directory.lanes_list:
                    vehicles.append(lane.vehicles_quantity)

        return vehicles
