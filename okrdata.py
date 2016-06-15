import pandas as pd
import re
import requests

data = requests.get('https://openknowledge.worldbank.org/'\
    'oai/request?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:'\
    'openknowledge.worldbank.org:10986/17584')
    
captions = []
if data.status_code == requests.codes.ok:
        #Get caption
        contents = data.text
        p = re.compile(r'<dc:description>(.*?)</dc:description>',re.DOTALL)
        q = re.compile(r'<dc:coverage>(.*?)</dc:coverage>',re.DOTALL)        
        r = re.compile(r'<dc:date>(.*?)</dc:date>',re.DOTALL)        
        captions += p.findall(contents)
        captions += q.findall(contents)
        captions += r.findall(contents)        
        print len(captions)
    