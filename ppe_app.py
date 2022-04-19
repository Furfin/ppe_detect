import io
from PIL import Image
import os
import torch
import pandas as pd
import requests
from flask import Flask, render_template, request, make_response



def get_xyxy(img,dictOfModels):
   
    result = dictOfModels['best'](img)
    return result.xyxy[0]
