# New: 

Clean DANAM JSON:
python clean_json.py -f json\DANAM\<JSON dump>

Create CSV file:
python write_csv.py -f json/cleaned-metadata/image_<TIME>.json -report -ids id_monument.txt

Download missing images from DANAM:
python download_danam.py -f <list of missing images>


# Old:

creating CSV metadata: python main.py 
usage: main.py [-h] -f FILE [-v] [-json] [-ids IDS] [-report] [-no-fix]

convert DANAM JSON export into HeidIcon CSV

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  DANAM json dump
  -v, --verbose         output logs in command line
  -json, --json         output cleaned metadata json
  -ids IDS              export CSV only for monuments in a given txt file
  -report, --report-meta
                        export report metadata as well as image metadata
  -no-fix               set to not fix possible mistakes in the caption


python create_report.py -csv danam_metadata_2021-04-14_18-18.csv
python create_report.py -txt id_report.txt
