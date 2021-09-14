'''
python module that includes all necessary caption processing functions
'''
import json
import re

########### dictionary definitions ###########
'''
heidicon_id = {
            ' Thomas Schrom': '1248182',
            ' Yogesh Budathoki': '1173885',
            ' Rishi Amatya': '1248177',
            ' Niels Gutschow': '1248173',
            ' Bijay Basukala': '1156661',
            ' Anil Basukala'	:	'1173868'	,
            ' David C. Andolfatto'	:  '1248176'	,
            ' Christiane Brosius'	:  '1182530'	,
            ' Nashib Kafle'	: '1173869'	,
            ' Ashma Adhikari'	: '1238508'	,
            ' Axel Michaels'	: '1257090'	,
            ' Alina Tamrakar'	: '1208660'	,
            ' Bibek Basukala'	: '1238506'	,
            ' Bharat Maharjan'	: '1208644'	,
            ' Bishnu Bahadur Shresta'	: '1174961'	,
            ' Bruce Owens'	: '1243391'	,
            ' Carl Pruscha'	:'1173886'	,
            ' Charlotte von Waitz'	:'1173870'	,
            ' Clarence Comyn Taylor'	:'1243395'	,
            ' Danish Architect Group'	: '1208651'	,
            ' Dirgha Man Chitrakar'	:'1243397'	,
            ' Gustave Le Bon'	: '1178307'	,
            ' Gyanendra Joshi'	:'1173887'	,
            ' Hagmüller and Associates'	:'1274094'	,
            ' Hemaraja Sakya'	:'1243392'	,
            ' Hrijata Dahal'	:'1212955'	,
            ' Hugh R. Downs'	:'1182507'	,
            ' KVPT'	: '1264430'	,
            ' Krishna Ram Chitrakar'	: '1258159'	,
            ' Mani Lama'	: '1178312'	,
            ' Mary Slusser'	: '1258156'	,
            ' Matthias Arnold'	: '1156663'	,
            ' Nutan Sharma'	:'1156665'	,
            ' Padma Sundar Maharjan'	: '1156662'	,
            ' Phil Chase'	: '1248378'	,
            ' Rajendra Shakya'	:'1174964'	,
            ' Ravi Shakya'	: '1232286'	,
            ' Rajan Maharjan'	:'1232284'	,
            ' Reinhard Herdick'	:'1249903'	,
            ' Rohit Ranjitkar'	: '1238521'	,
            ' Sabina Tandukar'	: '1208668'	,
            ' Shekhar Dongol'	: '1182505'	,
            ' Stanislaw Klimek'	: '1248206'	,
            ' Suresh Shrestha'	:'1174959'	,
            ' Sushil Rajbhandari'	:'1174710'	,
            ' Thomas L. Kelly'	:  '1238520'	,
            ' Sabrina Dangol': '1257081',
            ' Alina Maharjan': '1258150',
            ' Sameer Tamrakar' : '1205338',
            ' Thomas Laird': '1268069',
            ' Chiniya Tamrakar': '1268070',
            ' Rajan Maharjan': '1232284',
            ' Hugh R. Downs': '1182507',
            ' Charlotte von Waitz': '1173870',
            ' Marc Gaborieau': '1264428',
            ' Nahib Kafle': '1173869',
            ' Stanislav Klimek': '1248206',
            ' Shailendra Shrestha': '1283532',
            ' Hugh R. Downs': '1182507',
            ' S. Klimek': '1248206',
            ' Manik Bajracharya': '1257091',
            ' Pankaj Nakarmi': '1300339',
}
'''
heidicon_id = json.load(open("json/heidicon_id.json"))[0]


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
    keywords = ["; photo by",
                ";photo by",
                "; location map by",
                "; site plan by",
                ";location map by",
                ";site plan by",
                "drawing by",
                "; floor plan",
                "; view from",
                "; photography by",
                ";floor plan",
                "; first floor plan",
                "; elevation drawing",
                ";view from",
                ";photography by",
                "; photograph by",
                ";sketch by",
                "; sketch by",
                "; section",
                "; existing ground floor plan",
                "; existing first floor plan",
                "; existing second floor plan",
                "; restored ground floor plan",
                "; restored first floor plan",
                "; restored second floor plan",
                "; existing elevation",
                "; restored elevation",
                "; existing section",
                "; restored section",
                "; southern elevation",
                "; eastern elevation",
                "; east elevation",
                "; top view",
                "; elevation"]

    for key in keywords:
        if key in caption:
            return True
    #print("No keywords found...")
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
        #print(classification_and_agent)
        agents = classification_and_agent[1].split(',')
        for item in agents:
            item.replace(" ", "")
            item.lstrip(' ')
            item.lstrip()
            item.strip('&nbsp;')


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
            image_metadata['agent'] = heidicon_id[agents[0]]
        except Exception as e:
            pass

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

            #print("Processing completed! The following information was extracted:\n{}".format("\n".join(image_metadata.keys())))
