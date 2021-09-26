import io
import codecs
import os, os.path
import requests
import argparse

from PIL import Image, UnidentifiedImageError
from write_csv import list_from_txt

URL = "https://danam.cats.uni-heidelberg.de/files/uploadedfiles/"
DIR = "uploads/"

'''
'''
def get_image(image_url, filename):
    req = requests.get(image_url)
    img_file = Image.open(io.BytesIO(req.content))
    img_file.save(filename)
    
'''
'''
def download_images(images): 
    log = "log/downloads.log"
    logfile = codecs.open(log, 'w', 'utf-8')
    
    for image in images:
        mon_id = image.split("_")[0].split("-")[0]+"/"
        
        if not os.path.isdir(DIR+mon_id):
            os.mkdir(DIR+mon_id)
        
        exts = [".png", ".jpg", ".jpeg", ".PNG", ".JPEG", ".JPG"]
        for ext in exts:
            response = requests.get(URL+image+ext)
            if response.status_code == 200:
                img_file = Image.open(io.BytesIO(response.content))
                img_file.save(DIR+mon_id+image+ext)
                logfile.write("Image {} saved to {}.\n".format(image, DIR+mon_id+image+ext))
                break
            logfile.write("Image {} cannot be found in DANAM.\n".format(image))
            
    return 0


if __name__ == "__main__":

    '''
    use argparser to create a command promt tool
    '''
    argparser = argparse.ArgumentParser(description="download missing images from DANAM")

    argparser.add_argument("-f", "--file", required=True, help="textfile with all images that need to be downloaded")
    args = argparser.parse_args()
    
    images = list_from_txt(args.file)
    download_images(images)