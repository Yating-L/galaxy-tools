#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import sys
import shutil
import json
import os

from webapollo import AssertUser, CnOrGuess, GuessCn, GuessOrg, OrgOrGuess, WAAuth, WebApolloInstance
from export import export
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample script to completely delete an organism')
    WAAuth(parser)
    parser.add_argument('email', help='User Email')
    CnOrGuess(parser)
    parser.add_argument('--gff', type=argparse.FileType('w'))
    parser.add_argument('--fasta', type=argparse.FileType('w'))
    parser.add_argument('--json', type=argparse.FileType('w'))
    parser.add_argument('--remove_old_directory', action='store_true', help='Remove old directory')

    args = parser.parse_args()

    wa = WebApolloInstance(args.apollo, args.username, args.password)
    # User must have an account
    gx_user = AssertUser(wa.users.loadUsers(email=args.email))

    # Get organism commonName
    org_cn = GuessOrg(args, wa)
    if isinstance(org_cn, list):
        org_cn = org_cn[0]

    org = wa.organisms.findOrganismByCn(org_cn)

    if not org:
        sys.exit("Organism %s doesn't exist" % org_cn)

    # check if the gx_user is global admin or organism administrative
    has_perms = False
    for user_owned_organism in gx_user.organismPermissions:
        if user_owned_organism['organism'] == org['commonName'] and 'ADMINISTRATE' in user_owned_organism['permissions']:
            has_perms = True
            break
    if not has_perms and gx_user.role != 'ADMIN':
        sys.exit(gx_user.username + " is not authorized to delete this organism. You need to request administrative permission for this organism from the owner.")

    old_directory = org['directory']

    # Export annotation GFF file, genome FASTA file, and organism JSON file
    # First check if the data directory exist, if exist do export
    if os.path.exists(old_directory):
        org_cn_list, seqs = GuessCn(args, wa)
        org_data = []
        if args.gff:
            print("\tExport annotation data")
        if args.fasta:
            print("\tExport genome sequences")
        for org_cn in org_cn_list:
            indiv_org_data = export(wa, org_cn, seqs, gff=args.gff, fasta=args.fasta)
            org_data.append(indiv_org_data)
        if args.json:
            args.json.write(json.dumps(org_data, indent=2))
            print("\tExport organism data")

        # If user wants to delete data directory, do so
        if args.remove_old_directory:
            shutil.rmtree(old_directory)
            print("\tRemoved old data directory")
    else:
        print("\tData directory doesn't exist. Skip exporting.")
    # Delete organims from the database
    returnData = wa.organisms.deleteOrganism(org['id'])
    print("\tDeleted organism %s" % org_cn)


