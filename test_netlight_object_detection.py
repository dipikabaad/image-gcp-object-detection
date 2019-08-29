# Basic libraries
import psutil
import humanize
import os
import argparse
import logging
import GPUtil as GPU
from os.path import isfile, join
from os import listdir

# Data related libraries
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tensorflow as tf
import pandas as pd
import csv
import requests
from requests.exceptions import Timeout

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from netlight_utils import constants
from detection_library.netlight_object_detection import ObjectDetection
from detection_library.cloud_utils import check_extension, get_safe_filename
# Google cloud libraries
from google.cloud import storage

if __name__ == "__main__":

	# Setting logging
	formatter = logging.Formatter('%(asctime)s : %(message)s')
	stream_logger = logging.getLogger('logger_stream')
	stream_logger.setLevel(constants.app_config['LOGGING_LEVEL'])
	# Set handler
	# streamHandler = logging.StreamHandler()
	# streamHandler.setFormatter(formatter)
	# stream_logger.addHandler(streamHandler)

	# Accept the command line arguments
	parser = argparse.ArgumentParser(description='Process some integers.')
	# param for finding if local/vm env for running
	parser.add_argument('env', type=int, help='1: if running on VM on google cloud, 2: if running on local machine other than cloud')
	args = parser.parse_args()
	if args.env == 1:
		stream_logger.info('VM settings activated!')
		machine_config = constants.vm_config
	else:
		stream_logger.info('LOCAL settings activated!')
		machine_config = constants.local_config

	# Setting the constants
	# Path to frozen graph
	PATH_TO_FROZEN_GRAPH = machine_config['PATH_TO_FROZEN_GRAPH']
	# List of the strings that is used to add correct label for each box.
	PATH_TO_LABELS = machine_config['PATH_TO_LABELS']
	# Model directory
	MODELS_PATH = machine_config['MODELS_PATH']
	# Output files directory
	OUTPUT_IMAGE_BASE_DIR = machine_config['OUTPUT_IMAGE_BASE_DIR']
	OUTPUT_CSV_BASE_DIR = machine_config['OUTPUT_CSV_BASE_DIR']

	PATH_TO_TEST_IMAGES_DIR = OUTPUT_IMAGE_BASE_DIR + '/Netlight_Test_Data'
	PATH_OUTPUT_DIR = OUTPUT_IMAGE_BASE_DIR + '/Netlight_Output_Data'
	CSV_OUTPUT_DIR = OUTPUT_CSV_BASE_DIR + '/Netlight_Object_Detection'

	API_ENDPOINT = "http://127.0.0.1:5000/"

	# This is needed to give the path to the models research where object_detection resides.
	sys.path.append(MODELS_PATH + "research")
	sys.path.append(MODELS_PATH)
	sys.path.append(MODELS_PATH + 'slim')
	from object_detection.utils import visualization_utils as vis_util

	# Initialize object detection object
	object_detection_model = ObjectDetection(PATH_TO_FROZEN_GRAPH, PATH_TO_LABELS, args.env)

	# Generate input files' paths
	client = storage.Client(project=constants.cloud_config['PROJECT_ID'])
	bucket = client.bucket(constants.cloud_config['STORAGE_BUCKET'])
	TEST_IMAGE_PATHS = []
	for blob in bucket.list_blobs():
		try:
			check_extension(blob.name, constants.app_config['ALLOWED_EXTENSIONS'])
		except:
			stream_logger.warning('{} file is not an image.'.format(blob.name))
			continue
		if (blob.name.startswith('Netlight Helsink') and ('/' in blob.name)):
			TEST_IMAGE_PATHS.append(blob.name)
	stream_logger.debug(TEST_IMAGE_PATHS[:10])

	# List all files
	# stream_logger.info(TEST_IMAGE_PATHS)
	# TEST_IMAGE_PATHS = [ join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 8) ]

	# Size, in inches, of the output images.
	IMAGE_SIZE = (12, 8)
	final_output = []
	OUTPUT_FILENAMES_temp = []
	total_images = len(TEST_IMAGE_PATHS)
	print(object_detection_model.category_index)
	# Write the output line by line to csv
	with open( CSV_OUTPUT_DIR + '/' + 'obj_detection_output.csv', mode='a') as csv_file:
		fieldnames = ['input_file_path', 'location', 'detected_objects', 'detected_scores', 'detected_boxes', 'output_file_path']
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='\t')
		writer.writeheader()
		count = 0
		for image_path in TEST_IMAGE_PATHS:
			if count % 20 == 0:
				stream_logger.info("Completed docs {}: {}".format((float(count)/total_images)*100, count))
			count += 1
			blob = bucket.get_blob(image_path)
			blob.download_to_filename(PATH_TO_TEST_IMAGES_DIR + '/' + 'sample.jpg')
			filename = image_path[image_path.rfind('/')+1:]
			temp_new_outputfile = get_safe_filename(filename)
			storage_output_filepath = constants.cloud_config['OUTPUT_IMAGE_DIR'] + '/' + temp_new_outputfile
			OUTPUT_FILENAMES_temp.append(storage_output_filepath)

			# image = Image.open(image_path)
			image = Image.open(PATH_TO_TEST_IMAGES_DIR + '/' + 'sample.jpg')
			# the array based representation of the image will be used later in order to prepare the
			# result image with boxes and labels on it.

			# TODO: Fix the reshape issue for some of the images
			try:
				image_np = object_detection_model.load_image_into_numpy_array(image)
			except:
				continue
		  	# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
			image_np_expanded = np.expand_dims(image_np, axis=0)
		  	# Actual detection.
			output_dict = object_detection_model.run_inference_for_single_image(image_np_expanded)
		  	# Visualization of the results of a detection.
			vis_util.visualize_boxes_and_labels_on_image_array(
				image_np,
				output_dict['detection_boxes'],
				output_dict['detection_classes'],
				output_dict['detection_scores'],
				object_detection_model.category_index,
				instance_masks=output_dict.get('detection_masks'),
				use_normalized_coordinates=True,
				line_thickness=8)
			output_dict_for_final = {}
			#output_dict_for_final['detection_boxes'] = output_dict['detection_boxes']
			#output_dict_for_final['detection_classes'] = output_dict['detection_classes']
			#output_dict_for_final['detection_scores'] = output_dict['detection_scores']
			output_dict_for_final['input_file_path'] = image_path
			output_dict_for_final['output_file_path'] = storage_output_filepath
			output_dict_for_final['location'] = image_path[image_path.find(' ') + 1:image_path.rfind('/')]
			# Create a dictionary with key as the bounding box dimension and value as array of [ object classname, detection_score]
			existing_boxes = {}
			for i in range(len(output_dict['detection_boxes'])):
				key_dict = tuple(output_dict['detection_boxes'][i].tolist())
				if (output_dict['detection_scores'][i] > 0.5) or (object_detection_model.category_index[output_dict['detection_classes'][i]]['name'] in ['horse', 'wine glass']):
					# [class, score]
					horse_with_less_prob = False
					# Allowing only one horse
					if (output_dict['detection_scores'][i] < 0.5):
						for key, value in existing_boxes.items():
							if 'horse' in value:
								horse_with_less_prob = True
								break
					if not(horse_with_less_prob):
						existing_boxes[key_dict] = [ object_detection_model.category_index[output_dict['detection_classes'][i]]['name'], output_dict['detection_scores'][i] ]
			scores = []
			boxes = []
			objects = []
			# Going through the dictionary to get the bounding box, object name, and score for an image
			for key, value in existing_boxes.items():
				objects.append(value[0])
				scores.append(value[1])
				boxes.append(key)
			output_dict_for_final['detected_objects'] = objects
			output_dict_for_final['detected_scores'] = scores
			output_dict_for_final['detected_boxes'] = boxes
			# try:
			# 	r = requests.post(url = API_ENDPOINT + 'insert_data', json = output_dict_for_final, timeout=3)
            #     # r = requests.get(url = API_ENDPOINT, timeout=1)
			# 	print(r.text)
			# 	if r['status'] != 200:
			# 		stream_logger.error("Insertion failed for record {}".format(output_dict_for_final['input_file_path']))
			# except Timeout as e:
			# 	stream_logger.exception("Timeout occured during insert_data")

			writer.writerow(output_dict_for_final)
			# final_output.append(output_dict_for_final)
		  	# plt.figure(figsize=IMAGE_SIZE)
		  	# plt.imshow(image_np)
			new_im = Image.fromarray(image_np)
			local_image_path = PATH_OUTPUT_DIR + '/' + 'sample_output.jpg'
			new_im.save(local_image_path)
			blob_dest = bucket.blob(storage_output_filepath)
			blob_dest.upload_from_filename(local_image_path)
