#!/usr/bin/env python
from __future__ import division
import numpy as np
import cv2
import argparse

NAME = 'Colorspaces'


def viz_colorspaces(rgb_image, viz_scale, disp_size=None):

    '''
    Returns image that shows the channels of the BGR, HSV, and LAB colorspace
    representations of a given image
    '''

    # Create grid of reduced size image panels
    w, h = (int(rgb_image.shape[1] * viz_scale), int(rgb_image.shape[0] * viz_scale)) if disp_size is None \
        else (int(disp_size[0] / 4), int(disp_size[1] / 3))
    viz = np.zeros((h * 3, w * 4, 3), dtype=np.uint8)

    def flatten_channels(img, labels):
        ''' Return horizontal stacking of single channels with a label overlayed '''
        assert len(labels) == img.shape[2]
        flat = np.hstack(cv2.split(img))
        for i, label in enumerate(labels):
            cv2.putText(flat, label, (i * w, int(h * 0.15)), cv2.FONT_HERSHEY_PLAIN, viz_scale * 5, 255, 2)
        return flat

    # Display small version of original image to the left of the grid
    rgb_small = cv2.resize(rgb_image, dsize=(w, h))
    viz[h:h * 2, :w] = rgb_small

    # Create small versions of image converted to HSV and LAB colorspaces
    images_and_labels = \
        zip([rgb_small, cv2.cvtColor(rgb_small, cv2.COLOR_BGR2HSV), cv2.cvtColor(rgb_small, cv2.COLOR_BGR2LAB)],
            [['B', 'G', 'R'], ['H', 'S', 'V'], ['L', 'A', 'B']])

    # Set 3x3 grid of single channel images from 3 3-channel images
    make_3deep = lambda x: np.repeat(x[:, :, np.newaxis], 3, axis=2)  # Needed for displaying in color
    viz[:, w:] = np.vstack(map(make_3deep, map(lambda x: flatten_channels(*x), images_and_labels)))
    return viz

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--use_cam', help='Use webcam (number)', type=int)
    parser.add_argument('-v', '--use_video', help='Use video', type=str)
    parser.add_argument('-r', '--use_ros_topic', help='Use ROS topic', type=str)
    parser.add_argument('-s', '--scale', help='Scale for image processing', type=float, default=0.5)
    args = parser.parse_args()

    if args.use_cam is not None or args.use_video:
        if args.use_cam is not None:
            cap = cv2.VideoCapture(args.use_cam)
        else:
            cap = cv2.VideoCapture(args.use_video)

        while(True):
            success, rgb_orig = cap.read()

            if not success:
                break

            cv2.imshow(NAME, viz_colorspaces(rgb_orig, args.scale, disp_size=(500, 500)))
            cv2.waitKey(5)

        cap.release()

    elif args.use_ros_topic is not None:
        key = None

        def disp_image(img):
            cv2.imshow(NAME, viz_colorspaces(img, args.scale))
            cv2.waitKey(10)

        import rospy
        import mil_ros_tools
        rospy.init_node(NAME)
        mil_ros_tools.Image_Subscriber(topic=args.use_ros_topic, callback=disp_image)
        rospy.spin()

    cv2.destroyAllWindows()
