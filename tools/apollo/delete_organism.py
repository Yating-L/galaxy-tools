#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import sys


from webapollo import AssertUser, GuessOrg, OrgOrGuess, WAAuth, WebApolloInstance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample script to completely delete an organism')
    WAAuth(parser)
    parser.add_argument('email', help='User Email')
    OrgOrGuess(parser)

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

    returnData = wa.organisms.deleteOrganism(org['id'])
    print("Delete organism %s" % org_cn)
    print("returnData = " + str(returnData) + "\n")

