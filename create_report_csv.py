import codecs
from datetime import datetime


# A collection of function to create CSV metadata for DANAM Reports

'''
create a dictionary based on the editorial text in a DANAM report.
input: editorial text as string (e.g. '')
output: 
'''
def get_editors(text):
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
    return "Editor?"

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
def write_csv_report_metadata(metadata, dir=".\\"):
    csv_file_content = ""
    headers = "Dateiname;   Name (Title/Object);	Klassifikation;	Klassifikationsname;	Lokale Systematik;	Rechteinhaber"
    
    t_o = 0
    #csv_file_content += headers
    for item in metadata:
        try:
            
            editorial_text, t_n = editors_to_csv(item['editorial'])
            if t_n > t_o:
                t_o = t_n
            
            csv_file_content += '\"'+"DANAM - {}.pdf".format(item['mon_id'])+'\"'+";" + '\"'+"Report {}".format(item['mon_id'])+'\"'+";" + '\"'+"4177815-7"+'\"'+";" + '\"'+"Report"+'\"'+";"
            csv_file_content += '\"'+item['mon_id']+'\"'+";" + '\"'+"Nepal Heritage Documentation Project"+'\"'+";" + editorial_text + "\n" 
            
        except:
            #csv_file_content += '\n'
            print("Key Error! This image entry only has the following keys:\n{}".format('\n'.join(item.keys())))
            pass
    
    for i in range(0, t_o+1):
        headers += ";   Künstler/Urheber/Hersteller (normiert);   Rolle"
        
    headers += "\n"   
    csv_file_content = headers + csv_file_content
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = "danam_report_metadata_{}.csv".format(now)
    file = codecs.open(dir+filename, 'w', 'utf-8')
    file.write(csv_file_content)
    file.close()

    filename = "danam_report_metadata_latest.csv"
    file = codecs.open(dir+filename, 'w', 'utf-8')
    file.write(csv_file_content)
    file.close()