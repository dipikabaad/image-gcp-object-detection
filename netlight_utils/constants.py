import logging

vm_config = {
    # GCP VM Settings
    'PATH_TO_FROZEN_GRAPH' : '/opt/graph_def/faster_rcnn_resnet101_coco_11_06_2017/frozen_inference_graph.pb',
    'PATH_TO_LABELS' : '/opt/models/research/object_detection/data/mscoco_label_map.pbtxt',
    'MODELS_PATH' : '/opt/models/',
    'OUTPUT_IMAGE_BASE_DIR' : "/data",
    'OUTPUT_CSV_BASE_DIR' : '/data'
}

local_config = {
    # LOCAL MAC LOCATIONS
    'PATH_TO_FROZEN_GRAPH' : '../graph_def/faster_rcnn_resnet101_coco_11_06_2017/frozen_inference_graph.pb',
    'PATH_TO_LABELS' : '../models/research/object_detection/data/mscoco_label_map.pbtxt',
    'MODELS_PATH' : '../models/',
    'OUTPUT_IMAGE_BASE_DIR' : "../Image_Data",
    'OUTPUT_CSV_BASE_DIR' : '../CSV_Data'
}

cloud_config = {
    'PROJECT_ID' : 'myobjectdetection-248112',
    'STORAGE_BUCKET' : 'netlight-all-images',
    'OUTPUT_IMAGE_DIR' : 'Test_Output_Data'
}

app_config = {
    'ALLOWED_EXTENSIONS' : ['jpg', 'jpeg', 'png', 'gif'],
    'LOGGING_LEVEL' : logging.DEBUG
}
