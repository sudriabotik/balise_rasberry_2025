#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 03:22:02 2025

@author: ubuntu
"""

from ultralytics import YOLO

model = YOLO('/home/ubuntu/Documents/yolo/test/best_canette.pt')

model.export(format="ncnn")