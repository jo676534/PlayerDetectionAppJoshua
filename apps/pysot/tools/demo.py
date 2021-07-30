from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from os.path import isfile, join
import argparse
from typing import final

import cv2
import torch
import numpy as np
from glob import glob
import pandas as pd

from pysot.core.config import cfg
from pysot.models.model_builder import ModelBuilder
from pysot.tracker.tracker_builder import build_tracker

torch.set_num_threads(1)


def get_frame(current_frame):
    resolution = (1280, 720)
    filename = "./Videos/game_0.mp4"
    
    vidcap = cv2.VideoCapture(filename)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    hasFrames, image = vidcap.read()
    if not hasFrames: return None 
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image  = cv2.resize(image, dsize=(resolution))
    vidcap.release()
    return image 


def rt_track(first_frame, final_frame, x0, y0, x1, y1):
    # cuda setup
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
    
    # initalize some variables
    is_first_frame = True
    frame_number = 0 
    rows = [] # categories are: (id_num, x0, y0, x1, y1)
    track_id = -1 # eventually need to set this to be a unique id

    # Need to check if we need to swap the variables
    if x0 > x1: x0, x1 = x1, x0
    if y0 > y1: y0, y1 = y1, y0
    
    for i in range(first_frame, final_frame+1):
        frame = get_frame(i-1) # video is zero indexed, but our frames are one indexed

        if is_first_frame:
            x = x0
            y = y0
            w = x1 - x0
            h = y1 - y0 
            
            tracker.init(frame, (x, y, w, h)) # tracker.init(frame, init_rect)
            
            rows.append([track_id, x0, y0, x1, y1])

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
                rows.append([track_id, bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3]])
            cv2.waitKey(1)
        frame_number += 1

    df = pd.DataFrame(rows, columns=["track_id", "x0", "y0", "x1", "y1"])
    return(df)
