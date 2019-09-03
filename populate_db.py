import csv
from netlight_utils import constants
import requests
from requests.exceptions import Timeout
import logging

formatter = logging.Formatter('%(asctime)s : %(message)s')
stream_logger = logging.getLogger('logger_stream')
stream_logger.setLevel(constants.app_config['LOGGING_LEVEL'])
API_ENDPOINT = "http://127.0.0.1:5000/"

def insert_models_results():
    """
    Insert the data from final results csv to mongodb
    """
    CSV_OUTPUT_PATH = constants.vm_config['OUTPUT_CSV_BASE_DIR'] + '/Netlight_Object_Detection/' + 'obj_detection_output.csv'

    with open(CSV_OUTPUT_PATH, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                row_obj_for_insertion = {}
                row_obj_for_insertion['input_file_path'] = row[0]
                row_obj_for_insertion['location'] = row[1]
                row_obj_for_insertion['detected_objects'] = row[2]
                row_obj_for_insertion['detected_scores'] = row[3]
                row_obj_for_insertion['detected_boxes'] = row[4]
                row_obj_for_insertion['output_file_path'] = row[5]
                # Call the API

                try:
                    r= requests.post(url = API_ENDPOINT + 'insert_data', json = row_obj_for_insertion, timeout=5)
                    # r = requests.get(url = API_ENDPOINT, timeout=1)
                    print(r.text)
                    # if r["status"] != 200:
                    #     stream_logger.error("Insertion failed for record {}".format(row_obj_for_insertion['input_file_path']))
                except Timeout as e:
                    stream_logger.exception("Timeout occured during insert_Ddata")
                line_count += 1
            # if line_count == 10:
            #     break
        #stream_logger.info(f'Processed {line_count} lines.')

insert_models_results()
