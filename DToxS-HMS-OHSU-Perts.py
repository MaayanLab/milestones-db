__author__ = 'mmcdermott'

from pymongo import MongoClient

client = MongoClient('mongodb://mmcdermott:kroyweN@loretta/LINCS')
db = client['LINCS']
md = db["milestones"]

with open('DToxS-HMS-OHSU-Perts.txt', 'w+') as out:
    out.write('Center\tPerturbagen\n')
    uniquePerts = []
    for doc in md.find({'center': 'DTOXS'}):
        for pert in doc.get('perturbagens', {}):
            if pert not in uniquePerts:
                out.write(doc['center'] + '\t' + pert['name'] + '\n')
                uniquePerts.append(pert)
    uniquePerts = []
    for doc in md.find({'center': 'HMS LINCS'}):
        for pert in doc.get('perturbagens', {}):
            if pert not in uniquePerts:
                out.write(doc['center'] + '\t' + pert['name'] + '\n')
                uniquePerts.append(pert)
    uniquePerts = []
    for doc in md.find({'center': 'MEP LINCS'}):
        for pert in doc.get('perturbagens', {}):
            if pert not in uniquePerts:
                out.write(doc['center'] + '\t' + pert['name'] + '\n')
                uniquePerts.append(pert)
