#Purpose: designed to navigate blind people to walk away obstacles (a simple demo)
#         request google cloud vision API for object recognization.

#Return: 1.the object name,score            
#        2.read object name and its relative location to you(front, right, left)   
#        3.return an image that annotate the object with an rectangular with name and score on it.

import io,os
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image,ImageDraw,ImageFont
import pyttsx3
import time
import matplotlib.pyplot as plt


file_name='2.jpg' #the location of your image
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='vision_api2.json' #load your credentials json file(google)
font_path='C:/Windows/Fonts/Arial.ttf' #load your font file into draw()

speech=pyttsx3.init()
voices=speech.getProperty('voices')
speech.setProperty('voices',voices[0].id)
rate=speech.getProperty('rate')
speech.setProperty('rate',rate-15)

class Detection(object):
    def __init__(self,file_name,font_path):
        self.file_name=file_name
        self.client=vision.ImageAnnotatorClient()
        with open(file_name,'rb') as image_file:
            content=image_file.read()
        self.image=vision.types.Image(content=content)
        self.font_path=font_path

    def localize_objects(self):
        objects=self.client.object_localization(
            image=self.image).localized_object_annotations

        print('Number of objects found: {}'.format(len(objects)))
        self.objs=objects

    def detect_labels(self):
        response = self.client.label_detection(image=self.image)

        labels = response.label_annotations
        print('')
        print(labels[0].description)
        print('')
        speech.say(labels[0].description)
        speech.runAndWait()

    def draw(self):
        img=Image.open(self.file_name)
        img=img.resize((1000,750),Image.ANTIALIAS)
        width,height=img.size
        print("width:",width," height:",height)
        color=[(0,255,0),(255,0,0),(0,0,255),(255,255,0),(0,255,255),(0,125,120),(120,120,120),(120,120,120),(125,129,200),
                (200,200,200),(200,250,255),(255,120,120),(120,120,225)]
        x=0
        font=ImageFont.truetype(self.font_path,20)
        locs=0

        plt.ion()
        plt.imshow(img)
        plt.axis('off')
        plt.pause(0.2)
        
        draw=ImageDraw.Draw(img)
        
        for obj in self.objs:
            loc=obj.bounding_poly.normalized_vertices
            draw.polygon([(loc[0].x*width,loc[0].y*height),
                      (loc[1].x*width,loc[1].y*height),
                      (loc[2].x*width,loc[2].y*height),
                      (loc[3].x*width,loc[3].y*height)],
                      outline=color[x])


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
                center_x=(loc[0].x*width+loc[1].x*width)/2
                center_image=500
                if(center_image-center_x-50>0):
                    print(obj.name+' on the left\n')
                    speech.say(obj.name + '  on the left')
                elif(center_x>center_image+50):
                    print(obj.name+' on the right\n')
                    speech.say(obj.name + '  on the right')
                else:
                    print(obj.name+' in front\n')
                    speech.say(obj.name + '  in front')

                speech.runAndWait()

            else:
                pass

        img.show()


detection=Detection(file_name,font_path)
detection.localize_objects()
detection.detect_labels()
detection.draw()
