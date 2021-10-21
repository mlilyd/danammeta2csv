'''
python module that includes all necessary caption processing functions
'''
import json
import re

########### dictionary definitions ###########
heidicon_id = json.load(open("json/dict/heidicon_id.json"))[0]

gnd_dict = {
            'architekturzeichnung': '4068827-6',
            'architekturfotografie': '4002855-0',
            'fotografie': '4045895-7',
            'skizze': '4181668-7',
            'grafik': '4021845-4',
            'gemälde': '4037220-0',
            'karte': '4029783-4',
            'inschrift': '4027107-9',
            'bericht': '4128022-2',
}

gnd_trans = {
            'architectural drawing':'Architekturzeichnung',
            'architectural photograph': 'Architekturfotografie',
            'photo':'Fotografie',
            'sketch':'Skizze',
            'graphic': 'Grafik',
            'painting': 'Gemälde',
            'location map': 'Karte',
            'inscription':'Inschrift',
            'report': 'Bericht',
}

licence_dict = {
            'CC BY-SA 4.0' : 'https://uni-heidelberg.de/nhdp',
            'Free access - no reuse': '',
}

##############################################
'''
read monument URL id from a simple txt file (one id per line). 
IDs can be commented as follows:

017a4a8f-b183-4e57-9ff9-54ae1145378f #LAL1870
60a8a8e0-e4e8-11e9-b125-0242ac130002 #LAL4250
cfc0099e-f15d-4c3e-8d8f-e048222f7956 #KIR0020

IDs can be commented python-wise with #

'''
def list_from_txt(textfile):
    ids = []

    with open(textfile, 'r', encoding="utf-8") as file:
        for line in file:
            if line[0] == "#" or line.strip() == "" : 
                continue
            id = line.split(" ")[0].strip()
            ids.append(id)

    return ids


#check date format, must follow DANAM guidelines
def isDate(date):

    date_formats = [
                "[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                "[0-9]{4}$",
                "[0-9]{4}-1[0-2]$|[0-9]{4}-0[1-9]$",
                "[0-9]{4}-[0-9]{4}$",
                "ca. [0-9]{4}$"
    ]

    for date_format in date_formats:
        search = re.search(date_format, date.strip())
        if search != None:
            if search.span(0)[0] == 0:
                	return True

    return False

#check caption for keywords
def valid_caption(caption):
    keywords = list_from_txt("log/keywords.txt")
    for keyword in keywords:
        pattern_search = re.search(keyword, caption)
        if pattern_search is not None:
            return True
    
    return False

#date processing
def get_date(textfield_part, image_metadata, shor_index):
    #date1
    image_metadata['date1'] = ""
    #date2
    image_metadata['date2'] = ""
    #date
    image_metadata['date'] = ""
    #date3
    image_metadata['date3'] = ""

    date = textfield_part.strip()
    date = date.split("\n")[0]

    if isDate(date):
        image_metadata['date'] = date
        short_index = 1

    regex_date = re.search('[0-9]{4}-[0-9]{4}', date)
    if regex_date != None:
        image_metadata['date']=date.split("-")[0]
        image_metadata['date3']=date.split("-")[1]

    if "ca." in image_metadata['date']:
         image_metadata['date2'] = image_metadata['date']
         image_metadata['date'] = ""

#agent, role, and classification processing
def get_agent_role_classification(textfield_part, image_metadata):
    
    
    image_metadata['agent'] = ""
    image_metadata['role'] = ""
    image_metadata['agent2'] = ""
    image_metadata['role2'] = ""
    #classification - auch von node-id
    classification = ""
    agents = []

    #falls foto
    if "photo by" in textfield_part or "photography by"  in textfield_part:
        classification_and_agent = textfield_part.split('by')
        agents = classification_and_agent[1:]
        #print(classification_and_agent)
        for item in classification_and_agent:
            item.replace(" ", "")
            item.lstrip(' ')
            item.lstrip()
            item.strip('&nbsp;')


        
        if len(agents) > 0 :
            try:
                image_metadata['agent'] = heidicon_id[agents[0]]
            except Exception as e:
                image_metadata['agent'] = agents[0]
                pass

        #role_agent1
        classification = classification_and_agent[0].strip().lower().lstrip(' ')
        if "photo" in classification:
            role = "photographer"
            classification = "architectural photograph"
        else:
            role = "draftsman"
        image_metadata['role'] = role

        if "inscription" in image_metadata['caption'].lower():
            classification = "inscription"

        #agent 2
        if len(agents) == 2:
            try:
                image_metadata['agent2'] = heidicon_id[agents[1]]
            except Exception as e:
                image_metadata['agent2'] = agents[1]
                pass

            #role_agent2
            image_metadata['role2'] = role

        else:
            image_metadata['agent2'] = ""

            #role_agent2
            image_metadata['role2'] = ""

    #falls nicht foto
    else:
        classification = 'architectural drawing'
        classification_and_agent = textfield_part.split('by')
        
        try:
            agents = classification_and_agent[1].split(',')
        except:
            agents = []
    
        
        try:
            image_metadata['agent'] = heidicon_id[agents[0]]
        except Exception as e:
            if len(agents)<0:
                image_metadata['agent'] = agents[0]
        

        role = "draftsman"
        image_metadata["role"] = role
        #agent 2
        if len(agents) == 2:
            try:
                image_metadata['agent2'] = heidicon_id[agents[1]]
            except Exception as e:
                image_metadata['agent2'] = agents[1]
                pass

            #role_agent2
            image_metadata['role2'] = role

        else:
            image_metadata['agent2'] = ''

            #role_agent2
            image_metadata['role2'] = ''

        caption_extra = classification_and_agent[0].strip()
        image_metadata["caption"] += ", "+caption_extra
        if "map" in image_metadata["caption"]:
            classification = "location map"
        if "sketch" in image_metadata["caption"]:
            classification = "sketch"

            
            
    if classification != "":
        image_metadata['classification'] = classification

#additional informations
def get_copyright_etc(textfield_parts, image_metadata, short_index, classification):
    #owner/copyright
    image_metadata['copyright'] = "Nepal Heritage Documentation Project"

    #references
    image_metadata['source'] = ""

    #license default
    license = "CC BY-SA 4.0"

    agent3 = ''
    update_date = ''
    #nochmal ueberpruefen..
    if len(textfield_parts) > (3 - short_index):
        for part in textfield_parts[(3 - short_index):]:
            if "courtesy of" in part.lower() or "no reuse" in part.lower():
                if image_metadata['copyright'] == "Nepal Heritage Documentation Project":
                    image_metadata['copyright'] = part.strip()
                license = "Free access - no reuse"
            elif "source" in part.lower():
                image_metadata['source'] = part.replace('Source:', '').replace('source:', '')
                image_metadata['source'] = image_metadata['source'].strip()
            elif "updated by" in part.lower():
                try:
                    agent3_and_update_date= part.split(",")
                    agent3=agent3_and_update_date[0].replace("updated by ", "")
                    update_date=agent3_and_update_date[1]
                except Exception as e:
                    pass
    if "free access" in image_metadata["copyright"]:
        image_metadata["copyright"] = ""
    #print(image_metadata['copyright'])
    #class_code
    if classification != "":
        class_code = gnd_dict[gnd_trans[classification].lower()]
    else:
        class_code = ""
    image_metadata['class_code'] = class_code

    #classification
    #
    image_metadata['classification'] = gnd_trans[classification]

    #agent3
    try:
        image_metadata['agent3'] = heidicon_id[agent3]
    except Exception as e:
        image_metadata['agent3'] = agent3
        pass


    #date_scan
    image_metadata['date_scan'] = update_date.split("\n")[0]

    #licence
    image_metadata['license'] = license

    #right_url
    if license != "":
        url = licence_dict[license]
    else:
        url = ""
    #print("url = ",url)
    image_metadata['url'] = url

    #rights_text
    if license=='CC BY-SA 4.0':
        rights_text="Nepal Heritage Documentation Project"
    else:
        rights_text=""
    image_metadata['rights_text'] = rights_text

'''
get metadata available through captions (most of the metadata)
input:
textfield_parts - the resulting array from splitting the caption by ";"
image_metadata - metadata dictionary
the function is divided into smaller functions
'''
def metadata_from_caption(textfield_parts, image_metadata):

    image_metadata['caption'] = textfield_parts[0].replace("\n","")
    #classification architectural drawing subcategories

    short_index=0
    get_date(textfield_parts[2], image_metadata, short_index)

   

    get_agent_role_classification(textfield_parts[1], image_metadata)
    '''
    if image_metadata['mon_id']=='BAL0009':
        agent_text = open("log/agent_bug.txt", 'a')
        agent_text.write(textfield_parts[1]+"\n")
        agent_text.write("{}, {}, {}, {}\n".format(image_metadata['agent'], image_metadata['role'], image_metadata['agent2'], image_metadata['role2']))
        agent_text.close()
    '''
    classification = image_metadata['classification']
    get_copyright_etc(textfield_parts, image_metadata, short_index, classification)

if __name__ == '__main__':

    captions = ["Kvātha Bāhāḥ, southern side of the Bāhaḥ with a statue of Padmapāṇi Lokeśvara, view from N; photo by Yogesh Budathoki; 2020-08-04", "Kvātha Bāhāḥ, view from NW; photo by Carl Pruscha; ca. 1974; courtesy of Carl Pruscha; free access – no reuse; source: Carl Pruscha, Kathmandu Valley, 1975, vol. II, p. 199 (P-256)"]

    for caption in captions:
        parts = caption.split(';')

        if  not valid_caption(caption) or len(parts) < 3:
            print("Caption\n\n{}\n\nis not valid!".format(caption))

        else:
            print("Caption is correct and is being processed...")
            image_metadata = {}
            metadata_from_caption(parts, image_metadata)
