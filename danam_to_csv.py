import codecs
import argparse
import html, json
import re, os, ast
from datetime import datetime
from pprint import pprint

from caption_processing import metadata_from_caption, valid_caption
'''
exports image array as a json file that can easily be re-imported into python and used again for other scripts. JSON is named
    'danam_metadata_<export date>_<export time>.json'
'''
def write_json(array, dir=".\\"):
    #now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    #filename = "danam_metadata_{}.json".format(now)
    filename = "cleaned_metadata.json"
    with open(dir+filename, 'w') as file:
        json.dump(array, file)

'''
made sure every text(caption, notes, etc) is in one line
'''
def one_line(text):
    return text.replace("\n", "").strip()

'''
exports pre-processed image metadata array into csv file for importing DANAM metadata into HeidIcon. csv file is named
    'danam_metadata_<export date>_<export time>.csv'
if optional parameter dir is not given, the csv will be written in the same folder as the python script
'''
def write_csv(metadata, dir=".\\"):
    csv_file_content = ""
    headers = "Filename; Title/caption;	Date inscription/object;	Date photo/drawing text;	Date photo/drawing Y-M-D;	Date photo/drawing to;	Agent 1;	Role of Agent 1;	Agent 2;	Role of Agent 2;	Owner;	References;   ;  Notes;   monument-id;	classification-id;	classification-text;	Agent 3;	Date scan/digitization;	image-licence;	image-right-url;	image-rights-text;	heiDATA-link;	heiDOK-link\n"

    csv_file_content += headers
    for item in metadata:
        try:
            csv_file_content += '\"'+item['filename'].replace('__','_')+'\"'+";" + '\"'+item['caption']+'\"'+";" + '\"'+item['date1']+'\"'+";" + '\"'+item['date2']+'\"'+";"
            csv_file_content += '\"'+item['date']+'\"'+";" + '\"'+item['date3']+'\"'+";" + '\"'+item['agent'].lstrip(' ')+'\"'+";" + '\"'+item['role']+'\"'+";"
            csv_file_content += '\"'+item['agent2'].lstrip(' ')+'\"'+";" + '\"'+item['role2']+'\"'+";" + '\"'+one_line(item['copyright'])+'\"'+";" + '\"'+one_line(item['source'])+'\"'+";"
            csv_file_content += '\"\"'+";" +'\"'+one_line(item['notes'])+'\"'+";" + '\"'+item['mon_id']+'\"'+";" + '\"'+item['class_code']+'\"'+";" + '\"'+item['classification']+'\"'+";"
            csv_file_content += '\"'+item['agent3']+'\"'+";" + '\"'+item['date_scan']+'\"'+";" + '\"'+item['license']+'\"'+";" + '\"'+item['url']+'\"'+";" + '\"'+item['rights_text']+'\"'+";"
            csv_file_content += '\"'+item['heidata']+'\"'+";" + '\"'+item['heidoc']+'\"'+";"

            csv_file_content += "\n"

        except:
            csv_file_content += '\n'
            print("Key Error! This image entry only has the following keys:\n{}".format('\n'.join(item.keys())))
            pass

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = "danam_metadata_{}.csv".format(now)
    file = codecs.open(dir+filename, 'w', 'utf-8')
    file.write(csv_file_content)
    file.close()

'''
reads danam json export and extract only the images
input: danam json export file
output: array of dictionaries of all images in danam
'''
def read_danam_export(danam_export):
    source_json = json.load(codecs.open(danam_export, 'r', 'utf-8'))

    res = []
    for object in source_json["business_data"]["resources"]:
        danam_id = object['resourceinstance']['resourceinstanceid']
        mon_ids = [tile["data"]["28294784-9323-11e9-bf23-0242ac120006"] for tile in object['tiles'] if '28294784-9323-11e9-bf23-0242ac120006' in tile['data'].keys()]

        for tiles in object['tiles']:
            if "'type': 'image/" in str(tiles.get('data')) or "'type': 'application/pdf" in str(tiles.get('data')):

                #clean string from html tags
                jsonstr = str(tiles.get('data'))
                jsonstr = jsonstr.replace("</p>", "")
                jsonstr = jsonstr.replace("<p>", "")
                jsonstr = jsonstr.replace("&nbsp;", " ")

                pos = jsonstr.find("[{")
                reptext =jsonstr[pos-39:pos-3].strip()
                jsonstr = jsonstr.replace(reptext, "imagedata")

                TAG_RE = re.compile('<[^>]+>')
                jsonstr = TAG_RE.sub('', jsonstr)

                jsonrawdata = ast.literal_eval(jsonstr)
                jsonrawdata['danam_id'] = danam_id
                jsonrawdata['mon_ids'] = mon_ids
                res.append(jsonrawdata)

    return res

'''
captions are stored as various nodes (e.g "fa9e551a-b100-11e9-b84d-0242ac120006")
these should just be combined together into one string. Moreover, unecessary texts, such as the standard copyright text on primary images, also need to be removed
input: an image dictionary
output: caption as one string variable, textfield
'''
def get_caption(image):
    keys = list(image.keys())
    keys.remove('imagedata')
    keys.remove('danam_id')
    keys.remove('mon_ids')
    if '4b84aa48-9eea-11e9-8b93-0242ac120006' in keys:
        keys.remove('4b84aa48-9eea-11e9-8b93-0242ac120006')
    if '4a7e2146-b8f9-11e9-8ef3-0242ac120007' in keys:
        keys.remove('4a7e2146-b8f9-11e9-8ef3-0242ac120007')

    textfield = ""
    for key in keys:
        if image[key] is not None:
            textfield += image[key] + "\n"

    textfield.replace("&nbsp;", " ")
    textfield = html.unescape(textfield)

    #'''
    #check if copyright text is included, this need to be removed
    copyright_text = "The latest report will always be available in DANAM (this page).\n\n"
    if copyright_text in textfield:
        textfield_paragraph = textfield.split(copyright_text)
        text_index = 0
        for index in range(len(textfield_paragraph)):
            if "If not otherwise stated" not in textfield_paragraph[index]:
                text_index = index
        textfield = textfield_paragraph[text_index]
    #'''

    if "(CC BY-SA 4.0)." in textfield:
        textfield = textfield.split('(CC BY-SA 4.0).')[1].strip()

    return textfield

'''
get metadata only available through danam exporrt, such as image filename, mon_id, classification(?), and notes
input:
image_json - image dictionary from danam
image_metadata - metadata dictionary
'''
def metadata_from_json(image_json, image_metadata):


    image_metadata['danam_id'] = image_json['danam_id']
    #get filename
    #separates name and file extension, but file extension remains.
    image_metadata['filename_danam'] = os.path.splitext(image_json['imagedata'][0]['name'])[0].replace(' ', '_')
    image_metadata['filetype'] = os.path.splitext(image_json['imagedata'][0]['name'])[1].replace('.','')
    #delete weird filename ending from DANAM
    filename_ending = re.compile('\_(?!section)(?!Section)[a-zA-Z0-9]{7}\\b')
    if filename_ending.search(image_metadata['filename_danam']) == '_section'== True:
        image_metadata['filename'] = image_metadata['filename_danam']
    else:
        image_metadata['filename'] = filename_ending.sub('', image_metadata['filename_danam'])

    #get mon_id
    image_metadata['mon_id'] = ""
    for mon_id in image_json['mon_ids']:
        regex_search = re.search('[A-Z]{3}[0-9]{3,4}', mon_id)
        if regex_search != None:
            image_metadata['mon_id'] = mon_id
    if image_metadata['mon_id'] == "":
        fname = image_metadata['filename']
        #print(fname)
        regex_search = re.search('[A-Z]{3}[0-9]{3,4}', fname)
        if regex_search == None:
            mon_id = ""
        else:
            mon_id = regex_search.group(0)
        image_metadata['mon_id'] = mon_id


    #try to get image classification - will be overwritten later, not sure if still needed? maybe for social/historical photograph???
    classification="architectural photograph"
    if "fb0a532e-b8f7-11e9-b8a9-0242ac120007" in image_json.keys():
        classification = "photo"
    elif "1aed634a-c332-11e9-af2c-0242ac140003" in image_json.keys():
        classification = "inscription"
    elif "0266d2a6-9ee9-11e9-98a0-0242ac120006" in image_json.keys():
        classification = "architectural drawing"
    image_metadata['classification'] = classification

    #try to get extra notes about image from danam
    notes= ""
    try:
        notes= image_json['e02c2194-b100-11e9-87e2-0242ac120006'].strip().replace('&nbsp;', ' ')
    except Exception as e:
        pass
    image_metadata['notes'] = notes

    image_metadata['heidoc']=''
    image_metadata['heidata']=''

'''
get DANAM metadata, both from caption and DANAM json export
input:
    image - partial json from DANAM
    caption_parts - caption split by ";"
output:
    dictionary image_metadata
'''
def get_metadata(image, caption_parts):
    image_metadata = {}
    metadata_from_json(image, image_metadata)
    metadata_from_caption(caption_parts, image_metadata)
    return image_metadata

'''
creates a HeidIcon compatible CSV file out of DANAM json export file
input:
    danam_export - DANAM json export
    json_export - if True, will also write a json output in addition to a csv output.
output: csv file of the images' metadata

'''
def danam_to_csv(danam_export, dir=".\\", verbose=False, json=False):
    images = read_danam_export(danam_export)
    metadata = []
    log = "log.txt"
    logfile = codecs.open(dir+log, 'a', 'utf-8')



    for image in images:

        caption = get_caption(image)
        parts = caption.split(';')

        if not valid_caption(caption) or len(parts) < 3:
            logfile.write("Caption\n\"{}\"\nis not valid!".format(caption))
            if verbose:
                print("Caption\n\"{}\"\nis not valid!".format(caption))
        else:
            logfile.write("Caption is correct and is being processed...\n")
            if verbose:
                print("Caption is correct and is being processed...\n")

            image_metadata = get_metadata(image, parts)
            metadata.append(image_metadata)

    if json:
        write_json(metadata, dir)
    write_csv(metadata, dir)
    logfile.write("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(images), len(metadata)))
    print("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(images), len(metadata)))
    logfile.close()

if __name__ == "__main__":

    '''
    use argparser to create a command promt tool
    '''
    argparser = argparse.ArgumentParser(description="convert DANAM JSON export into HeidIcon CSV")

    argparser.add_argument("-f", "--file", required=True, help="DANAM json export")
    argparser.add_argument("-v", "--verbose", dest='verbose', required=False, action="store_true")
    argparser.add_argument("-json", "--json", dest='json', required=False, action="store_true")
    args = argparser.parse_args()

    danam_to_csv(args.file, verbose=args.verbose, json=args.json)
