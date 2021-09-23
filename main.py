import codecs
import argparse
import html, json
import re, os, ast
from datetime import datetime


from caption_processing import metadata_from_caption, valid_caption
from create_report_csv import write_csv_report_metadata
from create_report import get_url_from_txt
'''
exports image array as a json file that can easily be re-imported into python and used again for other scripts. JSON is named
    'danam_metadata_<export date>_<export time>.json'
'''
def write_json(array, dir="json/"):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    #filename = "danam_metadata_{}.json".format(now)
    filename = "cleaned_metadata_{}.json".format(now)
    with open(dir+filename, 'w') as file:
        json.dump(array, file)

def one_line(text):
    return text.replace("\n", "").strip()

'''
exports pre-processed image metadata array into csv file for importing DANAM metadata into HeidIcon. csv file is named
    'danam_metadata_<export date>_<export time>.csv'
if optional parameter dir is not given, the csv will be written in the same folder as the python script
'''
def write_csv(metadata, logfile, dir="csv/", ids=[]):
    
    using_mon_ids = (len(ids)>0)
   
    csv_file_content = ""
    headers = "Filename; Title/caption;	Date inscription/object;	Date photo/drawing text;	Date photo/drawing Y-M-D;	Date photo/drawing to;	Agent 1;	Role of Agent 1;	Agent 2;	Role of Agent 2;	Owner;	References;   ;  Notes;   monument-id;	classification-id;	classification-text;	Agent 3;	Date scan/digitization;	image-licence;	image-right-url;	image-rights-text;	heiDATA-link;	heiDOK-link;\n"
   
   
    csv_file_content += headers
    for item in metadata:
        try:
            
            # if we are getting only a few monuments based on mon_ids.txt, and item's mon_id is not in mon_ids, skip
            if using_mon_ids and item['mon_id'] not in ids:
                logfile.write("Skipping this item because {} is not in mon_ids.txt.\n".format(item['mon_id']))
                continue
            
            csv_file_content += '\"'+item['filename']+'\"'+";" + '\"'+item['caption']+'\"'+";" + '\"'+item['date1']+'\"'+";" + '\"'+item['date2']+'\"'+";"
            csv_file_content += '\"'+item['date']+'\"'+";" + '\"'+item['date3']+'\"'+";" + '\"'+item['agent']+'\"'+";" + '\"'+item['role']+'\"'+";"
            csv_file_content += '\"'+item['agent2']+'\"'+";" + '\"'+item['role2']+'\"'+";" + '\"'+one_line(item['copyright'])+'\"'+";" + '\"'+one_line(item['source'])+'\"'+";"
            csv_file_content += '\"\"'+";" +'\"'+one_line(item['notes'])+'\"'+";" + '\"'+item['mon_id']+'\"'+";" + '\"'+item['class_code']+'\"'+";" + '\"'+item['classification']+'\"'+";"
            csv_file_content += '\"'+item['agent3']+'\"'+";" + '\"'+item['date_scan']+'\"'+";" + '\"'+item['license']+'\"'+";" + '\"'+item['url']+'\"'+";" + '\"'+item['rights_text']+'\"'+";"
            csv_file_content += '\"'+item['heidata']+'\"'+";" + '\"'+item['heidoc']+'\"'
            
        except Exception as e:
            logfile.write("Key Error! Image entry \'{}\' only has the following keys:\n{}".format( item['filename'],'\n'.join(item.keys())))
            pass

        csv_file_content += "\n"


    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    if using_mon_ids:
        filename = "danam_metadata_select_{}.csv".format(now)
    else:
        filename = "danam_metadata_all_{}.csv".format(now)
        
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
        editorials= [tile["data"]["66fd9c70-ce1b-11e9-b993-0242ac140002"] for tile in object['tiles'] if '66fd9c70-ce1b-11e9-b993-0242ac140002' in tile['data'].keys()]



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
                jsonrawdata['editorials'] = editorials
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
    keys.remove('editorials')
    if '4b84aa48-9eea-11e9-8b93-0242ac120006' in keys:
        keys.remove('4b84aa48-9eea-11e9-8b93-0242ac120006')

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

    #get editorial
    image_metadata['editorial'] = ""
    for editorial in image_json['editorials']:
        image_metadata['editorial'] = editorial.strip().replace("\n", "").replace(",,", ", ")

    #get reports
    image_metadata['report_url'] = image_json['danam_id']
    #image_metadata['report_url'] = image_json['notegroup_id']

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
output:

'''
def danam_to_csv(danam_export, dir="csv/", verbose=False, json=False, report=False, ids=[], fix=True):
    images = read_danam_export(danam_export)
    metadata = []
    metadata_report = []
        
    log = "log.txt"
    logfile = codecs.open(log, 'w', 'utf-8')

    prev_mon_id = "ABCDE"

    for image in images:

        caption = get_caption(image)
    
        if fix:
            caption = caption.replace(", photo by", "; photo by")
    
        
        parts = caption.split(';')

        if not valid_caption(caption) or len(parts) < 3:
            logfile.write("{}\"\n is not a valid caption!\n".format(caption))
            if verbose:
                print("\"{}\"\n is not a valid caption!\n".format(caption))
            
            image_metadata = {}
            metadata_from_json(image, image_metadata)
            
                
        else:
            logfile.write("Caption is correct and is being processed...\n")
            if verbose:
                print("Caption is correct and is being processed...\n")
      
            image_metadata = get_metadata(image, parts)
            mon_id = image_metadata['mon_id']
            metadata.append(image_metadata)
            if prev_mon_id != mon_id:
                prev_mon_id = mon_id
                metadata_report.append(image_metadata)

    if json:
        write_json(metadata)

    if len(ids) > 0:
        write_csv(metadata, logfile, dir, ids)
    else:
        write_csv(metadata, logfile, dir)
        
        
    if report:
        if len(ids) > 0:
            write_csv_report_metadata(metadata_report, dir)
        else:
            write_csv_report_metadata(metadata_report, dir)
    
    logfile.write("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(images), len(metadata)))
    print("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(images), len(metadata)))
    
    logfile.close()

if __name__ == "__main__":

    '''
    use argparser to create a command promt tool
    '''
    argparser = argparse.ArgumentParser(description="convert DANAM JSON export into HeidIcon CSV")

    argparser.add_argument("-f", "--file", required=True, help="DANAM json dump")
    argparser.add_argument("-v", "--verbose", dest='verbose', required=False, action="store_true", help="output logs in command line")
    argparser.add_argument("-json", "--json", dest='json', required=False, action="store_true", help="output cleaned metadata json")
    argparser.add_argument("-ids", required=False, type=str, help="export CSV only for monuments in a given txt file")
    argparser.add_argument("-report", "--report-meta", dest='reportmeta', required=False, action="store_true", help="export report metadata as well as image metadata")
    argparser.add_argument("-no-fix", required=False, dest='nofix', action="store_false", help="set to not fix possible mistakes in the caption")
    args = argparser.parse_args()
    
    ids = []
    if args.ids != None:
        print("Reading Monument IDs from "+args.ids)
        ids = get_url_from_txt(args.ids)
        print("Exporting CSV Metadata for the following monuments:\n")
        print(ids)
        
    else:
        print("Exporting CSV Metadata for all monuments in JSON")
        
    danam_to_csv(args.file, verbose=args.verbose, json=args.json, report=args.reportmeta, ids=ids, fix=args.nofix)
