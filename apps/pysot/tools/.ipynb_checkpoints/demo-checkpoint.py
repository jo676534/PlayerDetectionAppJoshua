from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from os.path import isfile, join
import argparse

import cv2
import torch
import numpy as np
from glob import glob

from pysot.core.config import cfg
from pysot.models.model_builder import ModelBuilder
from pysot.tracker.tracker_builder import build_tracker

torch.set_num_threads(1)

# parser = argparse.ArgumentParser(description='tracking demo')
# parser.add_argument('--config', type=str, help='config file')
# parser.add_argument('--snapshot', type=str, help='model name')
# parser.add_argument('--video_name', default='', type=str,
#                     help='videos or image files')
# args = parser.parse_args()


def get_frames(video_name):
    if not video_name:
        cap = cv2.VideoCapture(0)
        # warmup
        for i in range(5):
            cap.read()
        while True:
            ret, frame = cap.read()
            if ret:
                yield frame
            else:
                break
    elif video_name.endswith('avi') or \
        video_name.endswith('mp4'):
        cap = cv2.VideoCapture("demo/soc.mp4") # args.video_name
        while True:
            ret, frame = cap.read()
            if ret:
                yield frame
            else:
                break
    else:
        images = glob(os.path.join(video_name, '*.jp*'))
        #images = sorted(images,
        #                key=lambda x: int(x.split('/')[-1].split('.')[0]))
        images.sort(key=lambda x: int(x[13:-4]))
        for img in images:
            frame = cv2.imread(img)
            yield frame


def get_frames_new(first, final): 
    print("in new get frames")
    pathIn = './vid2img/'
    folder_name = 'vid2img'
    frames = glob(os.path.join(folder_name, '*.jp*'))
    frames.sort(key=lambda x: int(x[13:-4]))
    
    ctr = first
    while (ctr <= final):
        print("yielded frame #{}".format(ctr))
        yield cv2.imread(frames[ctr])
        ctr += 1
        
    

#def main(): #should end up taking in first_frame, final_frame, x0, y0, x1, y1

def rt_track(first_frame, final_frame, x0, y0, x1, y1):
    print("DEMO APP CALLED 1")
    print("DEMO APP CALLED 2")
    cfg.merge_from_file("apps/pysot/experiments/siamrpn_alex_dwxcorr_otb/config.yaml") # args.config # "experiments/siamrpn_alex_dwxcorr_otb/config.yaml"
    cfg.CUDA = torch.cuda.is_available() and cfg.CUDA
    device = torch.device('cuda' if cfg.CUDA else 'cpu')

    # create model
    model = ModelBuilder()
    
    # load model
    model.load_state_dict(torch.load("apps/pysot/experiments/siamrpn_alex_dwxcorr_otb/model.pth", # args.snapshot # "experiments/siamrpn_alex_dwxcorr_otb/model.pth"
        map_location=lambda storage, loc: storage.cpu()))
    model.eval().to(device)
    
    # build tracker
    tracker = build_tracker(model)
    
    # open file
    pos = open("apps/pysot/output/pos.txt", "w") 
    
    is_first_frame = True

    video_name = "soc"
    
    cv2.namedWindow(video_name, cv2.WND_PROP_FULLSCREEN) # This line fails to run on a second attempt (ALSO SEE LINE 150 + 157)
    
    frame_number = 0 
    
    for frame in get_frames_new(first_frame, final_frame): # for frame in get_frames("demo/soc.mp4"):
        print("At begining of for loop")
        if is_first_frame:
            x = x0
            y = y0
            w = x1 - x0
            h = y1 - y0 # x, y, w, h = (800, 400, 70, 100) # init_rect
            
            tracker.init(frame, (x, y, w, h)) # tracker.init(frame, init_rect)
            
            pos.write("{0} {1} {2} {3} {4}\n".format(frame_number, x, y, w, h))
            cv2.imwrite("apps/pysot/output/frames/frame%d.jpg" % frame_number, frame)
            is_first_frame = False
        else:
            outputs = tracker.track(frame)
            if 'polygon' in outputs:
                polygon = np.array(outputs['polygon']).astype(np.int32)
                cv2.polylines(frame, [polygon.reshape((-1, 1, 2))],
                              True, (0, 255, 0), 3)
                mask = ((outputs['mask'] > cfg.TRACK.MASK_THERSHOLD) * 255)
                mask = mask.astype(np.uint8)
                mask = np.stack([mask, mask*255, mask]).transpose(1, 2, 0)
                frame = cv2.addWeighted(frame, 0.77, mask, 0.23, -1)
            else: # Grab from two lines down the x,y,w,h
                bbox = list(map(int, outputs['bbox']))
                cv2.rectangle(frame, (bbox[0], bbox[1]),
                              (bbox[0]+bbox[2], bbox[1]+bbox[3]),
                              (0, 255, 0), 3)
                pos.write("{0} {1} {2} {3} {4}\n".format(frame_number, bbox[0], bbox[1], bbox[2], bbox[3]))
            cv2.imshow(video_name, frame) # CV IMAGE LINE (BREAKS ON SUBSEQUENT ATTEMPTS) ALSO SEE LINE 110
            cv2.imwrite("apps/pysot/output/frames/frame%d.jpg" % frame_number, frame)
            cv2.waitKey(10) # was ten for my testing
        frame_number += 1
    
    pos.close()
    cv2.destroyWindow(video_name) # comment linked to the cv window's creation on line 110
    
    print("End of demo app")
    # this will have to create and return a dataframe of frame locations

# if __name__ == '__main__':
#     main()
