#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io,os
from google.cloud import vision
from google.cloud.vision import types
import base64 #pybase64
from PIL import Image,ImageDraw,ImageFont
import pyttsx3
import time
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='vision_api2.json'
#file_name='stair6.jpg'
speech=pyttsx3.init()
voices=speech.getProperty('voices')
speech.setProperty('voices',voices[0].id)
rate=speech.getProperty('rate')
speech.setProperty('rate',rate-30)
class Detection(object):
    def load(self,file_name):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']='vision_api2.json'
        self.client=vision.ImageAnnotatorClient()
        with open(file_name,'rb') as image_file:
            content=image_file.read()
        self.image=vision.types.Image(content=content)


    def localize_objects(self):
        objects=self.client.object_localization(
            image=self.image).localized_object_annotations


        print('Number of objects found: {}'.format(len(objects)))
        self.objs=objects
        for object in objects:
            print('\n{} (confidence: {})'.format(object.name, object.score))
            #print('Normalized bounding polygon vertices: ')
            #print(object.bounding_poly.normalized_vertices)


    def detect_labels(self):

        response = self.client.label_detection(image=self.image)

        labels = response.label_annotations
        print('')
        print(labels[0].description)
        speech.say(labels[0].description)
        speech.runAndWait()

    def draw(self,file_name):
        img=Image.open(file_name)
        img=img.resize((1000,750),Image.ANTIALIAS)
        width,height=img.size
        #print("width:",width," height:",height)
        colour=[(0,255,0),(255,0,0),(0,0,255),(255,255,0),(0,255,255),(0,125,120),(120,120,120),(120,120,120),(125,129,200),
                (200,200,200),(200,250,255),(255,120,120),(120,120,225)]
        x=0
        font=ImageFont.truetype('C:/Windows/Fonts/Arial.ttf',20)
        locs=0
        for obj in self.objs:
            draw=ImageDraw.Draw(img)
            loc=obj.bounding_poly.normalized_vertices
            draw.polygon([loc[0].x*width,loc[0].y*height,
                        loc[1].x*width,obj.bounding_poly.normalized_vertices[1].y*height,
                        loc[2].x*width,loc[2].y*height,
                        loc[3].x*width,loc[3].y*height],
                        outline=colour[x])
            
            if (abs(loc[0].y*height-locs)>30):
                draw.text((loc[0].x*width,loc[0].y*height),
                            text=obj.name,fill=(0,255,0),font=font)

                draw.text((loc[0].x*width,loc[0].y*height-25.0),
                            text="{0:.1f}%".format(obj.score*100),fill=(255,0,0),font=font)
            else:
                draw.text((loc[0].x*width,loc[0].y*height+20),
                            text=obj.name,fill=(0,255,0),font=font)

                draw.text((loc[0].x*width,loc[0].y*height+45),
                            text="{0:.1f}%".format(obj.score*100),fill=(255,0,0),font=font)
            locs=loc[0].y*height
            x+=1
            if (obj.score>0.67):
                if(loc[0].x*width!=loc[1].x*width):
                    center_x=(loc[0].x*width+loc[1].x*width)/2
                else:
                    center_x=(loc[0].x*width+loc[2].x*width)/2
                center_image=500
                if(center_image-center_x-50>0):
                    speech.say(obj.name + '  on the left')
                elif(center_x>center_image+50):
                    speech.say(obj.name + '  on the right')
                else:
                    speech.say(obj.name + '  in front')
                speech.runAndWait()
                time.sleep(0.3)
            else:
                pass

        img.show()

while True:
    print("\nHi! which one you choose?")
    file_name=input("1,2,3,4, or -1:")
    if (file_name=='-1'):
        print('Bye')
        break
    else:
        file_name=file_name+".jpg"
    detection=Detection()
    detection.load(file_name)
    detection.localize_objects()
    detection.detect_labels()
    detection.draw(file_name)
