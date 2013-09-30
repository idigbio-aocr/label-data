import csv
import json
import chardet

fixtures = []

datasets = { "1": "ent", "2": "lichens", "3": "herb" }

dcount = 1
for d in datasets:
    fixtures.append({
        "pk": d,
        "model": "scoring.Dataset",
        "fields": {
            "name": datasets[d]
        }
    })
    dcount += 1

rcount = 1
with open("files-django.csv","rb") as csvfile:
    r = csv.reader(csvfile)
    header = None
    for row in r:
        if not header:
            header = row
            continue
        rdict = dict(zip(header, row))
        with open("{0}/gold/ocr/{1}.txt".format(datasets[rdict["dataset"]],rdict["name"])) as go:
            rawdata = go.read()
            cdresult = chardet.detect(rawdata)
            charenc = cdresult['encoding']
            rdict["humantext"] = rawdata.decode(charenc).encode('utf-8')
        with open("{0}/gold/parsed/{1}.csv".format(datasets[rdict["dataset"]],rdict["name"])) as gp:
            rawdata = gp.read()
            cdresult = chardet.detect(rawdata)
            charenc = cdresult['encoding']
            rdict["goldparse"] = rawdata.decode(charenc).encode('utf-8')
        with open("{0}/silver/parsed/{1}.csv".format(datasets[rdict["dataset"]],rdict["name"])) as sp:
            rawdata = sp.read()
            cdresult = chardet.detect(rawdata)
            charenc = cdresult['encoding']
            rdict["silverparse"] = rawdata.decode(charenc).encode('utf-8')
            
        fixtures.append({
            "pk": rcount,
            "model": "scoring.Image",
            "fields": rdict
        })
        rcount += 1
        
with open("files-fixture.json","wb") as of:
    json.dump(fixtures,of,indent=2)