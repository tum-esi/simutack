# import useful libraries
import os
import numpy as np
import cv2
from yolo_utils import *
import time

from StreamServer import StreamServer
from traffic_sign import Sign
from ImageInput import ImageInput


# ==============================================================================
# -- constants -----------------------------------------------------------------
# ==============================================================================
BB_COLOR = (248, 64, 24)

# ==============================================================================
# -- class -------------------------------------------------------------------
# ==============================================================================
class TrafficSignDetector:
    def __init__(self):
        """
        Constructor. 
        """
        self.running = True

        # I/O
        #time.sleep(10)  # Wait 10s to ensure simutack has properly booted up
        simutack_url = "simutack:3000"
        self.handler = None
        self.image_input = ImageInput(simutack_url)
        self.image_input.start_listening()
        self.stream_server = StreamServer(self)

        # Load class names
        img_file = './data/classes.names'
        self.classNames = read_classes(img_file)
        print("Classes' names :\n", self.classNames)

        # Load the model config and weights
        modelConfig_path = './cfg/yolov4-rds.cfg'
        modelWeights_path = './weights/yolov4-rds_best_2000.weights'

        # Read the model cfg and weights with the cv2 DNN module
        neural_net = cv2.dnn.readNetFromDarknet(modelConfig_path, modelWeights_path)

        # Set the preferable Backend to GPU
        neural_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        neural_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        # Defining the input frame resolution for the neural network to process
        self.network = neural_net
        self.height, self.width = 416,416

        # Confidence and non-max suppression threshold for this YoloV3 version
        self.confidenceThreshold = 0.5
        self.nmsThreshold = 0.2

        # Traffic Sign
        self.sign = Sign(self.classNames)

    def process_frame(self, frame):
        detected_sign = ""
        processed_frame = None
        try:
            # Check for valid frame
            if frame is None:
                return processed_frame, detected_sign

            # Convert frame
            frame = np.frombuffer(frame, dtype=np.uint8)
            frame = cv2.imdecode(frame, flags=1)
            frame = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB)
            frame_size = frame.shape[:2]


            # using convert_to_blob function : 
            outputs = convert_to_blob(frame, self.network, self.height, self.width)    
            # apply object detection on the video file
            bounding_boxes, class_objects, confidence_probs = object_detection(outputs, frame, self.confidenceThreshold)   
            # perform non-max suppression
            indices = nms_bbox(bounding_boxes, confidence_probs, self.confidenceThreshold, self.nmsThreshold)

            # pred_bbox = np.concatenate([np.reshape(pred_sbbox, (-1, 5 + self.num_classes)),
            #                             np.reshape(
            #                                 pred_mbbox, (-1, 5 + self.num_classes)),
            #                             np.reshape(pred_lbbox, (-1, 5 + self.num_classes))], axis=0)
            # bboxes = utils.postprocess_boxes(
            #     pred_bbox, frame_size, self.input_size, 0.3)
            # bboxes = utils.nms(bboxes, 0.45, method='nms')
            # print(f"TF Pro took: {time.perf_counter()-ts}s")
            # ts = time.perf_counter()

            # Filter for traffic signs
            # bboxes = self.sign.filter_traffic_sign(bboxes)

            # descriptive string (e.g., '30', '50', 'stop')
            # print(f"Sign D took: {time.perf_counter()-ts}s")

            # ts = time.perf_counter()
            # detected_sign = str(
            #     self.sign.process_traffic_sign(frame, bboxes))
            
            detected_sign = str(
               self.sign.process_traffic_sign(frame, bounding_boxes))

            # Draw bounding boxes into image
            box_drawing(frame, indices, bounding_boxes, class_objects, confidence_probs, self.classNames, color=(255,102,0), thickness=3)
            processed_frame = frame

            # processed_frame = utils.draw_bounding_boxes_image(
            #     frame, bboxes)
            # print(f"Sign P took: {time.perf_counter()-ts}s")

        except Exception as e:
            print(e)

        return processed_frame, detected_sign

    def attach_handler(self, handler):
        self.handler = handler

    def game_loop(self):
        """
        Main program loop.
        """
        while self.running:
            # Start time measurement
            t_start = time.perf_counter()

            # Get data (if available)
            image = self.image_input.get_image()

            # Process received image frame (returns the frame with bounding boxes around detected signs as well as the value of the sign)
            processed_frame, detected_sign = self.process_frame(image)

            # Stream results
            if (self.handler is not None) and (processed_frame is not None):
                self.handler.stream_update(processed_frame, detected_sign)

            # Stop time measurement
            t_elapsed = time.perf_counter() - t_start
            print("Elapsed time: {:.3f}".format(t_elapsed))

# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================
if __name__ == '__main__':
    t = TrafficSignDetector()
    t.game_loop()

