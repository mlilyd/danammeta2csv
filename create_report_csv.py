import json
import codecs
from datetime import datetime

from clean_json import replace_w_json

# A collection of function to create CSV metadata for DANAM Reports
heidicon_id = json.load(open("json/dict/heidicon_id.json"))[0]

'''
create a dictionary based on the editorial text in a DANAM report.
input: editorial text as string (e.g. '')
output: 
'''
def get_editors(text):
    text = replace_w_json(text, heidicon_id, strip=True)
    split = [i.replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ")  for i in text.split("</p><p>")]
    editors = {}
    for item in split:
        t = item.split(": ")
        field = t[0]
        names = t[1]
        editors[field] = names
    return editors

'''
a dictionary to translate editor roles into HeidIcon roles
'''
roles = {
    "Editor": "Editor",
    "Descriptions, iconography, social and religious activities": "Autor",
    "Photography": "Fotograf",
    "Drawings": "Zeichner",
    "Historical events, inscriptions": "Autor"
}

'''
use roles dictionary to translate editorial roles in HeidIcon roles
'''
def get_role(key):
    for role_key in roles.keys():
        if role_key in key:
            return roles[role_key]
    return "Editor"

'''
reformat editorial text for CSV output
'''
def editors_to_csv(text):
    editors = get_editors(text)
    csv_text = ""
    n = 0
    for key in editors.keys():
        persons = editors[key].split(',')
        for person in persons:
            n += 1
            csv_text += "\"{}\"; \"{}\"; ".format(person.strip(), get_role(key))
    
    return csv_text, n

'''
exports pre-processed image metadata array into csv file for importing DANAM Report metadata into HeidIcon. csv file is named
    'danam_report_metadata_<export date>_<export time>.csv'
if optional parameter dir is not given, the csv will be written in the same folder as the python script
'''
def write_csv_report_metadata(metadata, logfile, dir=".\\", ids=[]):
    
    using_mon_ids = (len(ids)>0)
    
    csv_file_content = ""
    headers = "filename;   title;	klassifikation_gnd; ; systematik;	res_rechteinhaber_text;	res_lizenz"
    
    t_o = 0
    #csv_file_content += headers
    for item in metadata:
        try:
            
            if using_mon_ids and item['mon_id'] not in ids:
                logfile.write("Skipping this item because {} is not in mon_ids.txt.\n".format(item['mon_id']))
                continue
        
            editorial_text, t_n = editors_to_csv(item['editorial'])
            if t_n > t_o:
                t_o = t_n
            
            csv_file_content += '\"'+"DANAM - {}.pdf".format(item['mon_id'])+'\"'+";" + '\"'+"Report {}".format(item['mon_id'])+'\"'+";" + "\"4177815-7\"; \"\"; "

            csv_file_content += '\"'+item['mon_id']+'\"'+";" + '\"'+"Nepal Heritage Documentation Project"+'\"'+";" + '\"'+"CC BY-SA 4.0"+'\"'+";" 
            
            csv_file_content += editorial_text + "\n" 
            
        except:
            logfile.write("Key Error! Image entry \'{}\' only has the following keys:\n{}".format( item['filename'],'\n'.join(item.keys())))
            pass
    
    
    for i in range(0, t_o+1):
        headers += ";   Künstler/Urheber/Hersteller (normiert);   Rolle"
        
    headers += "\n"   
    csv_file_content = headers + csv_file_content
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    if using_mon_ids:
        filename = "report_metadata_select_{}.csv".format(now)
    else:
        filename = "report_metadata_all_{}.csv".format(now)
    file = codecs.open(dir+filename, 'w', 'utf-8')
    file.write(csv_file_content)
    file.close()
