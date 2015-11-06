# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 14:43:16 2015

@author: Michael
"""
import PIL
import os

# Set to 1 if you want to resize based on the height of the image
height = 0 

image_extension = ".jpeg"
desired_size_in_pixels = 100

for files in os.listdir("."):
    if files.endswith(image_extension):
        img = PIL.Image.open(files)
        current_size = img.size[height]
        scale = (desired_size_in_pixels/float(current_size))
        other_dimension_in_pixels = int((float(img.size[abs(height-1)])*float(scale)))
        if height == 0:
            img = img.resize((desired_size_in_pixels, other_dimension_in_pixels), PIL.Image.ANTIALIAS)
        else:
            img = img.resize((other_dimension_in_pixels, desired_size_in_pixels), PIL.Image.ANTIALIAS)
        thumbnail_name = files.replace(image_extension,' thumbnail'+image_extension)
        img.save(thumbnail_name)
