import csv
from urllib.request import urlopen
import io
import json
from pymongo import MongoClient
from dateutil.parser import parse

# Connect to MongoDB collection milestones
# Make sure that mongoDB is running
client = MongoClient("mongodb://username:password@localhost/LINCS")
db = client["LINCS"]
md = db["milestones"]
md.drop()

# All Ids of LINCS Phase One data from LIFE
phaseOneIds = ["20000","20001","20002","20003","20004","20020","20021",
"20022","20023","20024","20025","20026","20027","20028","20029","20030",
"20031","20032","20033","20034","20035","20036","20037","20038","20039",
"20040","20041","20042","20043","20044","20045","20046","20047","20048",
"20049","20050","20051","20052","20053","20054","20055","20056","20057",
"20058","20059","20060","20061","20062","20063","20064","20065","20066",
"20067","20068","20069","20070","20071","20072","20073","20074","20075",
"20076","20077","20078","20079","20080","20081","20082","20083","20084",
"20085","20086","20087","20088","20089","20090","20091","20092","20093",
"20094","20095","20096","20097","20098","20099","20100","20101","20102",
"20103","20104","20105","20106","20107","20108","20109","20110","20111",
"20112","20113","20114","20115","20116","20117","20118","20119","20120",
"20121","20122","20123","20124","20125","20126","20127","20128","20129",
"20130","20131","20132","20133","20134","20135","20136","20137","20138",
"20139","20140","20146","20147","20148","20149","20150","20151","20152",
"20153","20154","20155","20156","20157","20158","20159","20160","20161",
"20162","20163","20164","20165","20166","20167","20168","20169","20170",
"20171","20172","20173","20174","20175","20176","20177","20178","20179",
"20180","20181","20182","20183","20184","20185","20186","20187","20188",
"20189","20190","20191","20192","20193","20194","20195","20196","20197",
"20198","20199","20200","20201","20202","20203","20204","20205","20206",
"20207","20209","20210","20211","20212","20213","20214","20215","20216",
"20217","20218","20219","20220","20221","20222","20223","20224","20225",
"20227","20228","20229","20230","20231","20232","20233","20234","20235",
"20236","20237","20238","20239","20240","20241","20242","20243","20244",
"20245","20246","20247","20248","20249","20250","20251","20252","20253",
"20254","20255","20256","20257","20258","20259","20260","20261","20262",
"20263","20264"]

# Dictionaries for caching lines, sms, and ps
lineCache = {}
smCache = {}
pCache = {}

for ID in phaseOneIds:
    print(ID)
    emptyDict = {}

    # outD will be the final dict/JSON for the mongoDB database
    outD = emptyDict.copy()

    # Load JSON of Dataset using Harvard"s API
    datasetUrl = "http://lincs.hms.harvard.edu/db/api/v1/dataset/" + \
            ID + "/?format=json"
    reply = urlopen(datasetUrl).read().decode("utf8")
    dataset = json.loads(reply)

    outD["center"] = "HMS-LINCS"
    outD["assay"] = dataset["assayTitle"]
    outD["assay-info"] = dataset["assayDescription"]
    outD["phase"] = "LP1"
    outD["hmsId"] = ID
    outD["release-link"] = "http://lincs.hms.harvard.edu/db/datasets/"+ID+"/"

    # Change from YYYY-MM-DD to MM/DD/YYYY TZ because I know this works.
    # Parses and gives the proper time zone --> -400 = middle of the U.S
    dateArr = []
    date = dataset["mostRecentUpdate"]
    dateSplit = date.split("-")
    rawDate = dateSplit[1] + "/" + dateSplit[2] + "/" + dateSplit[0]
    cleanDate = parse(rawDate + " -0400")
    releaseDate = {
            "date": cleanDate,
            "releaseLevel": 1
        }
    dateArr.append(releaseDate)

    if dateArr:
        outD["release-dates"] = dateArr

    # Download csv and parse to get associated small molecules, cell lines,
    # and/or proteins
    # Get names of small molecules and IDs of cell lines/proteins
    csvUri = dataset["datapointFile"]["uri"]
    csvResponse = urlopen(csvUri)
    csvI = csvResponse.read().decode("utf-8")
    csvIO = io.StringIO(csvI, newline="")
    cr = csv.reader(csvIO)

    smIds = []
    lineIds = []
    pIds = []

    smArr = []
    cLineArr = []
    pArr = []

    for row in cr:
        if row[0] == "datarecordID":
            continue
        if row[2] and row[3]:
            # Build small molecule ID and check if in cache. If not,
            # get meta-data from Harvard API
            smId = str(row[2]) + "-" + str(row[3])
            if smId not in smIds:
                smIds.append(smId)
                smDict = emptyDict.copy()
                smUrl = "http://lincs.hms.harvard.edu/db/api/v1/" + \
                        "smallmolecule/" + smId + "/?format=json"
                if smId not in smCache:
                    smReply = urlopen(smUrl).read().decode("utf8")
                    respDict = json.loads(smReply)
                    smCache[smId] = respDict
                else:
                    respDict = smCache[smId]
                smDict["hmsId"] = smId
                smDict["lincsId"] = respDict["smLincsID"]
                smDict["name"] = respDict["smName"]
                smDict["type"] = "small molecule"
                smArr.append(smDict)

        if row[9]:
            # Get cell line ID and check if in cache. If not,
            # get meta-data from Harvard API
            cLineId = str(row[9])
            if cLineId not in lineIds:
                lineIds.append(cLineId)
                cLineDict = emptyDict.copy()
                lineUrl = "http://lincs.hms.harvard.edu/db/api/v1/" + \
                        "cell/" + cLineId + "/?format=json"
                if cLineId not in lineCache:
                    lineReply = urlopen(lineUrl).read().decode("utf8")
                    respDict = json.loads(lineReply)
                    lineCache[cLineId] = respDict
                else:
                    respDict = lineCache[cLineId]
                cLineDict["hmsId"] = cLineId
                cLineDict["name"] = respDict["clName"]
                if respDict["clCellType"]:
                    cLineDict["type"] = respDict["clCellType"] # Cancer lines?
                if respDict["clOrgan"]:
                    cLineDict["tissue"] = respDict["clOrgan"]
                if respDict["clOrganism"]:
                    cLineDict["organism"] = respDict["clOrganism"]
                cLineArr.append(cLineDict)

        if row[11]:
            # Get protein ID and check if in cache. If not,
            # get meta-data from Harvard API
            pId = str(row[11])
            if pId not in pIds:
                pIds.append(pId)
                pDict = emptyDict.copy()
                pUrl = "http://lincs.hms.harvard.edu/db/api/v1/protein/" + \
                        pId + "/?format=json"
                if pId not in pCache:
                    pReply = urlopen(pUrl).read().decode("utf8")
                    respDict = json.loads(pReply)
                    pCache[pId] = respDict
                else:
                    respDict = pCache[pId]
                pDict["hmsId"] = pId
                pDict["name"] = respDict["ppName"]
                if respDict["ppProteinType"]:
                    pDict["type"] = respDict["ppProteinType"]
                if respDict["ppProteinSource"]:
                    pDict["source"] = respDict["ppProteinSource"]
                if respDict["ppProteinForm"]:
                    pDict["form"] = respDict["ppProteinForm"]
                if respDict["ppSourceOrganism"]:
                    pDict["organism"] = respDict["ppSourceOrganism"]
                pArr.append(pDict)

    # Enter small molecules and count as perturbagens
    smLength = len(smIds)
    if not smLength == 0:
        outD["perturbagens"] = smArr
        pertMeta = emptyDict.copy()
        pertCountArr = []
        countType = {
                "count": smLength,
                "type": "small molecules"
                }
        pertCountArr.append(countType)
        pertMeta["count-type"] = pertCountArr
        if pertMeta:
            outD["perturbagens-meta"] = pertMeta

    # Enter cell lines and count
    lineLength = len(lineIds)
    if not lineLength == 0:
        outD["cell-lines"] = cLineArr
        cLineMetaArr = []
        cLineMeta = {
                "count": lineLength,
                "type": "cell lines" # Is this right?
                }                    # Are any iPSC differentiated?
        cLineMetaArr.append(cLineMeta)
        outD["cell-lines-meta"] = cLineMetaArr

    # Enter proteins and count
    pLength = len(pIds)
    if not pLength == 0:
        outD["proteins"] = pArr
        pMetaArr = []
        pMeta = {
                "count": pLength,
                "type": "proteins" # Right? Are any iPSC differentiated?
                }
        pMetaArr.append(pMeta)
        outD["proteins-meta"] = pMetaArr

    md.insert(outD)
