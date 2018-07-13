#!/usr/bin/env python
from __future__ import print_function

import argparse
import json
import sys

from BCBio import GFF

from Bio import SeqIO

from future import standard_library

from webapollo import CnOrGuess, GuessCn, WAAuth, WebApolloInstance

standard_library.install_aliases()
try:
    import StringIO as io
except ImportError:
    import io


def export(wa, org_cn, seqs, gff=False, fasta=False):
    org_data = wa.organisms.findOrganismByCn(org_cn)

    data = io.StringIO()

    kwargs = dict(
        exportType='GFF3',
        seqType='genomic',
        exportGff3Fasta=True,
        output="text",
        exportFormat="text",
        organism=org_cn,
    )

    if len(seqs) > 0:
        data.write(wa.io.write(
            exportAllSequences=False,
            sequences=seqs,
            **kwargs
        ).encode('utf-8'))
    else:
        data.write(wa.io.write(
            exportAllSequences=True,
            sequences=[],
            **kwargs
        ).encode('utf-8'))

    # Seek back to start
    data.seek(0)

    records = list(GFF.parse(data))
    if len(records) == 0:
        print("Could not find any sequences or annotations for this organism + reference sequence")
        sys.exit(2)
    else:
        for record in records:
            record.annotations = {}
            record.features = sorted(record.features, key=lambda x: x.location.start)
            if gff:
                GFF.write([record], gff)
            record.description = ""
            if fasta:
                SeqIO.write([record], fasta, 'fasta')

    return org_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample script to add an attribute to a feature via web services')
    WAAuth(parser)
    CnOrGuess(parser)
    parser.add_argument('--gff', type=argparse.FileType('w'))
    parser.add_argument('--fasta', type=argparse.FileType('w'))
    parser.add_argument('--json', type=argparse.FileType('w'))

    args = parser.parse_args()

    wa = WebApolloInstance(args.apollo, args.username, args.password)

    org_cn_list, seqs = GuessCn(args, wa)

    org_data = []
    for org_cn in org_cn_list:
        indiv_org_data = export(wa, org_cn, seqs, gff=args.gff, fasta=args.fasta)
        org_data.append(indiv_org_data)
    args.json.write(json.dumps(org_data, indent=2))
