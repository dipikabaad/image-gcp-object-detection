import psutil
import humanize
import os
import argparse
import logging
import GPUtil as GPU

from os.path import isfile, join
from os import listdir

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tensorflow as tf
import pandas as pd

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from netlight_utils import constants
from detection_library.netlight_object_detection import ObjectDetection

# from object_detection.utils import ops as utils_ops
# from object_detection.utils import label_map_util
# from object_detection.utils import visualization_utils as vis_util

#GPUs = GPU.getGPUs()
#gpu = GPUs[0]
#def printm():
# process = psutil.Process(os.getpid())
# print("Gen RAM Free: " + humanize.naturalsize( psutil.virtual_memory().available ), " | Proc size: " + humanize.naturalsize( process.memory_info().rss))
# print("GPU RAM Free: {0:.0f}MB | Used: {1:.0f}MB | Util {2:3.0f}% | Total {3:.0f}MB".format(gpu.memoryFree, gpu.memoryUsed, gpu.memoryUtil*100, gpu.memoryTotal))
#printm()

# This is needed to display the images.
# %matplotlib inline

if __name__ == "__main__":

	# Setting logging
	formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
	stream_logger = logging.getLogger('logger_stream')
	stream_logger.setLevel(constants.LOGGING_LEVEL)
	# Set handler
	streamHandler = logging.StreamHandler()
	streamHandler.setFormatter(formatter)
	stream_logger.addHandler(streamHandler)

	parser = argparse.ArgumentParser(description='Process some integers.')
	# Accept if local/vm env for running
	parser.add_argument('env', type=int, help='1: if running on VM on google cloud, 2: if running on local machine other than cloud')
	args = parser.parse_args()
        print(args.env)
	if args.env == 1:
		stream_logger.info('VM settings activated!')
		# Setting the constants
		PATH_TO_FROZEN_GRAPH = constants.PATH_TO_FROZEN_GRAPH
		# List of the strings that is used to add correct label for each box.
		PATH_TO_LABELS = constants.PATH_TO_LABELS
		MODELS_PATH = constants.MODELS_PATH
		# Detection
		OUTPUT_IMAGE_BASE_DIR = constants.OUTPUT_IMAGE_BASE_DIR
		OUTPUT_CSV_BASE_DIR = constants.OUTPUT_CSV_BASE_DIR
	else:
		stream_logger.info('LOCAL settings activated!')
		# Setting the constants
		PATH_TO_FROZEN_GRAPH = constants.PATH_TO_FROZEN_GRAPH_LOCAL
		# List of the strings that is used to add correct label for each box.
		PATH_TO_LABELS = constants.PATH_TO_LABELS_LOCAL
		MODELS_PATH = constants.MODELS_PATH_LOCAL
		# Detection
		OUTPUT_IMAGE_BASE_DIR = constants.OUTPUT_IMAGE_BASE_DIR_LOCAL
		OUTPUT_CSV_BASE_DIR = constants.OUTPUT_CSV_BASE_DIR_LOCAL

	PATH_TO_TEST_IMAGES_DIR = OUTPUT_IMAGE_BASE_DIR + '/Netlight_Test_Data'
	PATH_OUTPUT_DIR = OUTPUT_IMAGE_BASE_DIR + '/Netlight_Output_Data'
	CSV_OUTPUT_DIR = OUTPUT_CSV_BASE_DIR + '/Netlight_Object_Detection'

	# This is needed to give the path to the models research where object_detection resides.
	sys.path.append(MODELS_PATH + "research")
	sys.path.append(MODELS_PATH)
	sys.path.append(MODELS_PATH + 'slim')
	from object_detection.utils import visualization_utils as vis_util


	# Initialize object detection object
	object_detection_model = ObjectDetection(PATH_TO_FROZEN_GRAPH, PATH_TO_LABELS, args.env)

	# List all files
	TEST_IMAGE_PATHS = [join(PATH_TO_TEST_IMAGES_DIR, f) for f in listdir(PATH_TO_TEST_IMAGES_DIR) if isfile(join(PATH_TO_TEST_IMAGES_DIR, f))]
	OUTPUT_FILENAMES = [ join(PATH_OUTPUT_DIR, 'final_') + f for f in listdir(PATH_TO_TEST_IMAGES_DIR) if isfile(join(PATH_TO_TEST_IMAGES_DIR, f))]
	stream_logger.info(TEST_IMAGE_PATHS)
	# TEST_IMAGE_PATHS = [ join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 8) ]

	# Size, in inches, of the output images.
	IMAGE_SIZE = (12, 8)

	# def run_inference_for_single_image(image, graph):
	#  	with graph.as_default():
	#     		with tf.Session() as sess:
	#       			# Get handles to input and output tensors
	#       			ops = tf.get_default_graph().get_operations()
	#       			all_tensor_names = {output.name for op in ops for output in op.outputs}
	#       			tensor_dict = {}
	#       			for key in [ 'num_detections', 'detection_boxes', 'detection_scores', 'detection_classes', 'detection_masks' ]:
	#         			tensor_name = key + ':0'
	#        				if tensor_name in all_tensor_names:
	#           				tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
	#       			if 'detection_masks' in tensor_dict:
	#         			# The following processing is only for single image
	#         			detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
	#         			detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
	#         			# Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
	#         			real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
	#         			detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
	#         			detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
	#         			detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
	#             			detection_masks, detection_boxes, image.shape[1], image.shape[2])
	#         			detection_masks_reframed = tf.cast(
	#             				tf.greater(detection_masks_reframed, 0.5), tf.uint8)
	#         			# Follow the convention by adding back the batch dimension
	#         			tensor_dict['detection_masks'] = tf.expand_dims(
	#             				detection_masks_reframed, 0)
	#       			image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
	#
	#       			# Run inference
	#       			output_dict = sess.run(tensor_dict, feed_dict={image_tensor: image})
	#
	#       			# all outputs are float32 numpy arrays, so convert types as appropriate
	#       			output_dict['num_detections'] = int(output_dict['num_detections'][0])
	#       			output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.int64)
	#       			output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
	#       			output_dict['detection_scores'] = output_dict['detection_scores'][0]
	#       			if 'detection_masks' in output_dict:
	#         			output_dict['detection_masks'] = output_dict['detection_masks'][0]
	#  	return output_dict

	final_output = []
	image_index = 0
	for image_path in TEST_IMAGE_PATHS:
		image = Image.open(image_path)
		# the array based representation of the image will be used later in order to prepare the
		# result image with boxes and labels on it.
		image_np = object_detection_model.load_image_into_numpy_array(image)
	  	# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
		image_np_expanded = np.expand_dims(image_np, axis=0)
	  	# Actual detection.
		output_dict = object_detection_model.run_inference_for_single_image(image_np_expanded)
	  	# Visualization of the results of a detection.
		image_np = vis_util.visualize_boxes_and_labels_on_image_array(
			image_np,
			output_dict['detection_boxes'],
			output_dict['detection_classes'],
			output_dict['detection_scores'],
			object_detection_model.category_index,
			instance_masks=output_dict.get('detection_masks'),
			use_normalized_coordinates=True,
			line_thickness=8)
		output_dict_for_final = {}
		output_dict_for_final['detection_boxes'] = output_dict['detection_boxes']
		output_dict_for_final['detection_classes'] = output_dict['detection_classes']
		output_dict_for_final['detection_scores'] = output_dict['detection_scores']
		final_output.append(output_dict_for_final)
	  	# plt.figure(figsize=IMAGE_SIZE)
	  	# plt.imshow(image_np)
		new_im = Image.fromarray(image_np)
		new_im.save(OUTPUT_FILENAMES[image_index])
		image_index += 1

	print("Final Output")
	print(final_output)

	# Grouping the tags with some location when the threshold is greater 0.5
	output_for_file = []
	for image_output in final_output:
		existing_boxes = {}
		for i in range(len(image_output['detection_boxes'])):
			key_dict = tuple(image_output['detection_boxes'][i].tolist())
			if (image_output['detection_scores'][i] > 0.5) or (object_detection_model.category_index[image_output['detection_classes'][i]]['name'] in ['horse', 'wine glass']):
				# [class, score]
				horse_with_less_prob = False
				# Allowing only one horse
				if (image_output['detection_scores'][i] < 0.5):
					for key, value in existing_boxes.items():
						if 'horse' in value:
							horse_with_less_prob = True
							break
				if not(horse_with_less_prob):
					existing_boxes[key_dict] = [ object_detection_model.category_index[image_output['detection_classes'][i]]['name'], image_output['detection_scores'][i] ]
		output_for_file.append(existing_boxes)
	stream_logger.info(output_for_file)

	# Writing the output to a file
	img_objs = {'image_names': [], 'object_names': [], 'bounding_boxes': [], 'scores': [] }
	img_by_objs = {'image_names': [], 'objects': [], 'bounding_boxes': [], 'scores': []}

	# building the dictionaries for building the dataframe
	for i in range(len(output_for_file)):
		scores = []
		boxes = []
		objects = []
		image_name = TEST_IMAGE_PATHS[i]
		# Going through the dictionary to get the bounding box, object name, and score for an image
		for key, value in output_for_file[i].items():
			img_objs['image_names'].append(image_name)
			img_objs['object_names'].append(value[0])
			img_objs['scores'].append(value[1])
			img_objs['bounding_boxes'].append(key)
			objects.append(value[0])
			scores.append(value[1])
			boxes.append(key)

		# For building the dataframe with image name and objects in single row
		img_by_objs['image_names'].append(image_name)
		img_by_objs['objects'].append(objects)
		img_by_objs['bounding_boxes'].append(boxes)
		img_by_objs['scores'].append(scores)

	df2 = pd.DataFrame.from_dict(img_objs)
	df2.to_csv(CSV_OUTPUT_DIR + '/netlight_object_detection.csv')
	df3 = pd.DataFrame.from_dict(img_by_objs)
	df3.to_csv(CSV_OUTPUT_DIR + '/netlight_objects_identified.csv')
	print(df3)
