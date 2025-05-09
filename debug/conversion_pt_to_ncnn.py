#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 03:22:02 2025

@author: ubuntu
"""

from ultralytics import YOLO

model = YOLO('runs/detect/train14/weights/best.pt')

model.export(format="ncnn")