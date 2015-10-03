# coding=utf-8

import csv
from pymongo import MongoClient
from datetime import datetime
from dateutil.parser import parse

client = MongoClient('mongodb://username:passwordloretta/LINCS')
db = client['LINCS']
md = db['milestones']

ldrClient = MongoClient('mongodb://username:password@loretta/Milestones')
ldrDb = ldrClient['Milestones']
mdAssays = ldrDb['assays']
mdCellLines = ldrDb['cellLines']
mdPerturbagens = ldrDb['perturbagens']
mdReadouts = ldrDb['readouts']

mdAssays.drop()
mdCellLines.drop()
mdPerturbagens.drop()
mdReadouts.drop()

dInit = {}
mongoArr = []

with open('milestones-consolidated.txt', 'rU') as data:
    reader = csv.reader(data, skipinitialspace=False, delimiter="\t")
    mcArr = []
    for row in reader:
        if any(row):
            mcArr.append(row)
for inp in mcArr:
    if inp[0] and not (inp[0] == 'center'):
        # print(inp)
        dictTot = dInit.copy()
        assayDict = {}
        assayDict['name'] = inp[1]
        assayDict['info'] = inp[2]

        mdAssays.insert(assayDict)

        # cell-lines
        allCellLines = []
        clDictInit = {}

        # Format of cell line cell (from Excel):
        # name1,type1(cell line or iPSC differentiated),
        # class1(normal,cancer line,…)\control-or-disease,
        # tissue1;...
        # Split by ; then , to build arr of objs

        cellLineArr = inp[3].split(";")
        for cLine in cellLineArr:
            clDict = clDictInit.copy()
            cLineData = cLine.split(",")
            if cLineData[0]:
                clDict['name'] = cLineData[0]
            if len(cLineData) > 1:
                if cLineData[1]:
                    clDict['type'] = cLineData[1]
                if cLineData[2]:
                    # Check if \ in class
                    #            --->   For diseased (not cancer) cell lines
                    if "\\" in cLineData[2]:
                        classArr = cLineData[2].split("\\")
                        clDict['class'] = classArr[0]
                        clDict['controlOrDisease'] = classArr[1]
                    else:
                        clDict['class'] = cLineData[2]
                if cLineData[3]:
                    clDict['tissue'] = cLineData[3]
            if clDict:
                mdCellLines.insert(clDict)

        # perturbagens: name1,type1(,perturbagens1);name2,type2(,purturbagens2)
        # Split by ; then , to build arr of objs
        pertArr = []
        pertDictInit = {}

        pertsAll = inp[5].split(";")
        for perts in pertsAll:
            pertDict = pertDictInit.copy()
            pertData = perts.split(",")
            if pertData[0]:
                pertDict['name'] = pertData[0]
            if len(pertData) > 1:
                pertDict['type'] = pertData[1]
            # Check if has perturbagens value
            if len(pertData) == 3:
                pertDict['perturbagens'] = pertData[2]
            if pertDict:
                mdPerturbagens.insert(pertDict)

        # readouts -> name1\datatype1;name2\datatype2
        readoutsArr = []
        readoutsDictInit = {}

        allReadouts = inp[11].split(";")
        for readout in allReadouts:
            readoutDict = readoutsDictInit.copy()
            readoutData = readout.split("\\")
            if readoutData[0]:
                readoutDict['name'] = readoutData[0]
            if len(readoutData) == 2:
                readoutDict['datatype'] = readoutData[1]
            if readoutDict:
                mdReadouts.insert(readoutDict)
