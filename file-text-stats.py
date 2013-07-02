import csv
import json
import chardet
import StringIO
import pprint
import nltk

def unicode_csv_reader(unicode_csv_data, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_string):
    for line in StringIO.StringIO(unicode_csv_string):
        yield line.encode('utf-8')

def get_labels_dict(csvreader):
    rsingleregion = False
    rlabels = {}
    rheader = None
    for r in csvreader:
        if not rheader:
            rheader = r
            if "aocr:regiontype" not in rheader:
                rsingleregion = True
            for i in range(len(rheader)):
                rheader[i] = rheader[i].strip()
            continue
        rdict = dict(zip(rheader,r))
        for f in rdict.keys():
            v = rdict[f].strip()
            if len(v) == 0:
                del rdict[f]
            else:
                rdict[f] = v
        if (len(rdict.keys()) > 0):
            if rsingleregion:
                rlabels["primary"] = rdict
            else:
                if "aocr:regiontype" in rdict:
                    lr = rdict["aocr:regiontype"]
                    if lr not in rlabels:
                        del rdict["aocr:regiontype"]
                        rlabels[lr] = rdict
                    else:
                        print "Error, duplicate label region"
    return rlabels

datasets = { "1": "ent", "2": "lichens", "3": "herb" }

ignorefields = ["aocr:regionType","dwc:decimalLatitude","dwc:decimalLongitude","dwc:eventDate"]

with open("files-django.csv","rb") as csvfile:
    r = csv.reader(csvfile)
    header = None
    fields = {}
    badtokens = {}
    for row in r:
        if not header:
            header = row
            continue
        rdict = dict(zip(header, row))
        gold = ""
        silver = ""
        with open("{0}/gold/ocr/{1}.txt".format(datasets[rdict["dataset"]],rdict["name"])) as go:
            rawdata = go.read()
            cdresult = chardet.detect(rawdata)
            charenc = cdresult['encoding']
            gold = rawdata.decode(charenc).lower()
        #with open("{0}/silver/ocr/{1}.txt".format(datasets[rdict["dataset"]],rdict["name"])) as sp:
            #rawdata = sp.read()
            #cdresult = chardet.detect(rawdata)
            #charenc = cdresult['encoding']
            #silver = rawdata.decode(charenc).lower()            
        with open("{0}/gold/parsed/{1}.csv".format(datasets[rdict["dataset"]],rdict["name"])) as gp:
            rawdata = gp.read()
            cdresult = chardet.detect(rawdata)
            charenc = cdresult['encoding']
            txt = rawdata.decode(charenc)
            r = get_labels_dict(unicode_csv_reader(txt))
            for l in r:
                #print gold
                for f in r[l]:
                    if f in ignorefields:
                        continue                    
                    if r[l][f].strip().lower() not in gold:
                        a = nltk.word_tokenize(r[l][f].strip().lower())
                        tokens = True
                        alen = len(a)
                        twc = 0
                        for t in a:
                            if t not in gold:
                                if t in badtokens:
                                    badtokens[t] += 1
                                else:
                                    badtokens[t] = 1
                                twc += 1
                                tokens = False
                        if not tokens:
                            if f in fields:
                                fields[f]["wrong_tokens"] += twc
                                fields[f]["right_tokens"] += alen - twc
                                fields[f]["wrong"] += 1
                            else:
                                fields[f] = { "right":0, "wrong_tokens": twc, "right_tokens": alen - twc, "wrong": 1 }                        
                    else:
                        if f in fields:
                            fields[f]["right"] += 1
                        else:
                            fields[f] = { "right":1, "right_tokens": 0, "wrong": 0, "wrong_tokens": 0 }               
        #with open("{0}/silver/parsed/{1}.csv".format(datasets[rdict["dataset"]],rdict["name"])) as sp:
            #rawdata = sp.read()
            #cdresult = chardet.detect(rawdata)
            #charenc = cdresult['encoding']
            #txt = rawdata.decode(charenc)
            #r = get_labels_dict(unicode_csv_reader(txt))
            #for l in r:
                #for f in r[l]:
                    #if r[l][f] not in silver:
                        #print r[l][f]
                        #if f in fields:
                            #fields[f]["wrong"] += 1
                        #else:
                            #fields[f] = { "right":0, "wrong": 1 }                        
                    #else:
                        #if f in fields:
                            #fields[f]["right"] += 1
                        #else:
                            #fields[f] = { "right":1, "wrong": 0 }
                                                        
    for f in fields.keys():
       if fields[f]["wrong"] == 0:
           del fields[f]
    pprint.pprint(fields)
    
    btii = badtokens.iteritems()
    btii = sorted(btii, key=lambda tup: tup[1])
    pprint.pprint(btii)
