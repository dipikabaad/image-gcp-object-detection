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
import tarfile
import tensorflow as tf
import zipfile
import pandas as pd

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from utils import constants

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
	raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')

# Setting the logging level
logging.basicConfig(level=constants.LOGGING_LEVEL)

# Importing the object_detection model based on model path for env
env_type = 2
if env_type == 1:
	MODELS_PATH = constants.MODELS_PATH
else:
	MODELS_PATH = constants.MODELS_PATH_LOCAL
sys.path.append(MODELS_PATH + "research")
sys.path.append(MODELS_PATH)
sys.path.append(MODELS_PATH + 'slim')

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

#GPUs = GPU.getGPUs()
#gpu = GPUs[0]
#def printm():
# process = psutil.Process(os.getpid())
# print("Gen RAM Free: " + humanize.naturalsize( psutil.virtual_memory().available ), " | Proc size: " + humanize.naturalsize( process.memory_info().rss))
# print("GPU RAM Free: {0:.0f}MB | Used: {1:.0f}MB | Util {2:3.0f}% | Total {3:.0f}MB".format(gpu.memoryFree, gpu.memoryUsed, gpu.memoryUtil*100, gpu.memoryTotal))
#printm()

# This is needed to display the images.
# %matplotlib inline
class ObjectDetection:
	# Class for detection the objects in the
	def __init__(self, frozen_graph_path, labels_path, env_type=1):
		self.detection_graph = tf.Graph()
		self.env_type = env_type
		self.frozen_graph_path = frozen_graph_path
		self.labels_path = labels_path
		self.category_index = ""
		self.setup()

	# Setting up initial parameters for object detection
	def setup(self):
		with self.detection_graph.as_default():
			od_graph_def = tf.GraphDef()
			with tf.gfile.GFile(self.frozen_graph_path, 'rb') as fid:
		    		serialized_graph = fid.read()
		    		od_graph_def.ParseFromString(serialized_graph)
		    		tf.import_graph_def(od_graph_def, name='')

		# Loading Label Map
		self.category_index = label_map_util.create_category_index_from_labelmap(self.labels_path, use_display_name=True)

	def check_fun(self):
		print("Nothing")
	# Helper Image Loader
	def load_image_into_numpy_array(self, image):
		(im_width, im_height) = image.size
		return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

	# Run inference for a single image
	def run_inference_for_single_image(self, image):

	 	with self.detection_graph.as_default():
	    		with tf.Session() as sess:
	      			# Get handles to input and output tensors
	      			ops = tf.get_default_graph().get_operations()
	      			all_tensor_names = {output.name for op in ops for output in op.outputs}
	      			tensor_dict = {}
	      			for key in [ 'num_detections', 'detection_boxes', 'detection_scores', 'detection_classes', 'detection_masks' ]:
	        			tensor_name = key + ':0'
	       				if tensor_name in all_tensor_names:
	          				tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
	      			if 'detection_masks' in tensor_dict:
	        			# The following processing is only for single image
	        			detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
	        			detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
	        			# Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
	        			real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
	        			detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
	        			detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
	        			detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
	            			detection_masks, detection_boxes, image.shape[1], image.shape[2])
	        			detection_masks_reframed = tf.cast(
	            				tf.greater(detection_masks_reframed, 0.5), tf.uint8)
	        			# Follow the convention by adding back the batch dimension
	        			tensor_dict['detection_masks'] = tf.expand_dims(
	            				detection_masks_reframed, 0)
	      			image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

	      			# Run inference
	      			output_dict = sess.run(tensor_dict, feed_dict={image_tensor: image})

	      			# all outputs are float32 numpy arrays, so convert types as appropriate
	      			output_dict['num_detections'] = int(output_dict['num_detections'][0])
	      			output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.int64)
	      			output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
	      			output_dict['detection_scores'] = output_dict['detection_scores'][0]
	      			if 'detection_masks' in output_dict:
	        			output_dict['detection_masks'] = output_dict['detection_masks'][0]
	 	return output_dict
