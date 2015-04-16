__author__ = 'mmcdermott'

import re

from pymongo import MongoClient

client = MongoClient("mongodb://username:password@master/LINCS")
md = client["LINCS"]["milestonesCons"]

with open('phaseOneData.txt', 'w+') as pOneData:
    outputStr = ""
    for doc in md.find({"phase": "LP1"}):
        center = doc["center"]
        outputStr += center + "\t"

        assay = doc["assay"]
        outputStr += assay + "\t"

        assayInfo = doc["assay-info"]
        outputStr += assayInfo + "\t"

        try:
            cellLines = ""
            for line in doc["cell-lines"]:
                # name,type,class,tissue,hmsId
                # No class field in cell lines.
                # Add after generating excel file.
                try:
                    cellLines += line["name"] + "," + line["type"] + ",," + \
                            line["tissue"] + "," + line["hmsId"] + ";"
                except KeyError:
                    cellLines += line["name"] + "," + "" + ",," + \
                            line["tissue"] + "," + line["hmsId"] + ";"
            # Strip last ";"
            cellLines = cellLines[:-1]
            outputStr += cellLines + "\t"
        except KeyError:
            outputStr += "" + "\t"

        try:
            cellLinesMeta = ""
            for obj in doc["cell-lines-meta"]:
                # count\type
                cellLinesMeta += str(obj["count"]) + "\\" + obj["type"] + ";"
            # Strip last ";"
            cellLinesMeta = cellLinesMeta[:-1]
            outputStr += cellLinesMeta + "\t"
        except KeyError:
            outputStr += "" + "\t"

        try:
            perturbagens = ""
            for pert in doc["perturbagens"]:
                # name,type,hmsId,lincsId
                perturbagens += pert["name"] + "," + pert["type"] + "," + \
                        pert["hmsId"] + "," + str(pert["lincsId"]) + ";"
            # Strip last ";"
            perturbagens = perturbagens[:-1]
            outputStr += perturbagens + "\t"
        except KeyError:
            outputStr += "" + "\t"

        try:
            pertMeta = ""
            for ct in doc["perturbagens-meta"]["count-type"]:
                # pair\type1,count1
                pertMeta += "false" + "\\" + ct["type"] + "," + \
                        str(ct["count"]) + ";"
            # Strip last ";"
            pertMeta = pertMeta[:-1]
            outputStr += pertMeta + "\t"
        except KeyError:
            outputStr += "" + "\t"

        if doc["release-dates"]:
            date = doc["release-dates"][0]["date"].strftime('%m/%d/%y')
            outputStr += date + "\t" + "\t" + "\t"
        else:
            outputStr += "" + "\t" + "\t" + "\t"

        if doc["release-link"]:
            releaseLink = doc["release-link"]
            outputStr += releaseLink + "\t"
        else:
            outputStr += "" + "\t"

        outputStr += doc["phase"] + "\t"

        try:
            proteins = ""
            for prot in doc["proteins"]:
                # name,form,source,organism,hmsId;...
                proteins += prot["name"] + "," + prot["form"] + "," + \
                        prot["source"] + "," + prot["organism"] + "," + \
                    prot["hmsId"] + ";"
            # Strip last ";"
            proteins = proteins[:-1]
            outputStr += proteins + "\t"
        except KeyError:
            outputStr += "" + "\t"


        try:
            protMeta = ""
            for metaObj in doc["proteins-meta"]:
                # count,type
                protMeta += str(metaObj["count"]) + "\\" + metaObj["type"]
            outputStr += protMeta + "\t"
        except KeyError:
            outputStr += "" + "\t"

        try:
            hmsId = doc["hmsId"]
            outputStr += hmsId + "\t"
        except KeyError:
            outputStr += "" + "\t"

        outputStr += "\n"
        # Remove weird line breaks from some descriptions
        outputStr = re.sub(r"<br />\n", "", outputStr)
        pOneData.write(outputStr)
        outputStr = ""
