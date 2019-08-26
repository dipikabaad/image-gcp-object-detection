import logging

# GCP VM Settings
PATH_TO_FROZEN_GRAPH='/opt/graph_def/faster_rcnn_resnet101_coco_11_06_2017/frozen_inference_graph.pb'
PATH_TO_LABELS ='/opt/models/research/object_detection/data/mscoco_label_map.pbtxt'
MODELS_PATH='/opt/models/'
PATH_TO_TEST_IMAGES_DIR = "/data/Netlight_Test_Data"
PATH_OUTPUT_DIR = "/data/Netlight_Output_Data"
PATH_CSV_OUTPUT_DIR = '/data/Netlight_Object_Detection'
OUTPUT_IMAGE_BASE_DIR = "/data"
OUTPUT_CSV_BASE_DIR = '/data'

# LOCAL MAC LOCATIONS
PATH_TO_FROZEN_GRAPH_LOCAL='../graph_def/faster_rcnn_resnet101_coco_11_06_2017/frozen_inference_graph.pb'
PATH_TO_LABELS_LOCAL='../models/research/object_detection/data/mscoco_label_map.pbtxt'
MODELS_PATH_LOCAL='../models/'
OUTPUT_IMAGE_BASE_DIR_LOCAL = "../Image_Data/"
OUTPUT_CSV_BASE_DIR_LOCAL = '../CSV_Data'

LOGGING_LEVEL = logging.DEBUG
