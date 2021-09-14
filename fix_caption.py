#from danam_to_csv import *
from main import *
#logfile = codecs.open("fix_log.txt", 'a', 'utf-8')


verbose = False;
report = False;
dir = ".//"

danam_export = read_danam_export("new.json")
to_fix = "BAL0006"

fixed_images = []

for image in danam_export:
    if to_fix in image['mon_ids']:
        fixed_images.append(image)


metadata = []
metadata_report = []

for image in fixed_images:
    caption = get_caption(image)
    
    
    caption = caption.replace(", photo by", "; photo by")
    #image['fixed_caption'] = caption
    
    parts = caption.split(';')
    
    prev_mon_id = "ABCDE"

    if not valid_caption(caption) or len(parts) < 3:
        #logfile.write("Caption\n\"{}\"\nis not valid!".format(caption))
        if verbose:
            print("Caption\n\"{}\"\nis not valid!".format(caption))
        
        image_metadata = {}
        metadata_from_json(image, image_metadata)
            
                
    else:
        #logfile.write("Caption is correct and is being processed...\n")
        if verbose:
            print("Caption is correct and is being processed...\n")
    
        image_metadata = get_metadata(image, parts)
    
    mon_id = image_metadata['mon_id']
    #if (len(ids) > 0 and mon_id in ids) or (len(ids)<=0):        
    metadata.append(image_metadata)
    #'''
    if prev_mon_id != mon_id:
        prev_mon_id = mon_id
        metadata_report.append(image_metadata)
    #'''

    if json:
        write_json(metadata, dir)
        
    write_csv(metadata, dir)
    if report:
        write_csv_report_metadata(metadata_report, dir)
    
    #logfile.write("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(fixed_images), len(metadata)))
    print("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(fixed_images), len(metadata)))
    
    #logfile.close()
