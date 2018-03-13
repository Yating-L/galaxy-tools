#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import json

from webapollo import AssertUser, GuessOrg, OrgOrGuess, WAAuth, WebApolloInstance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def checkPermission(gx_user, org_cn):
    org_permissions = wa.users.getOrganismPermissionsForUser(gx_user)
    for organism in org_permissions:
        if org_cn == organism['organism'] and "ADMINISTRATE" in organism['permissions']:
            return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample script to completely delete an organism')
    WAAuth(parser)
    parser.add_argument('email', help='User Email')
    OrgOrGuess(parser)

    args = parser.parse_args()

    wa = WebApolloInstance(args.apollo, args.username, args.password)
    # User must have an account
    gx_user = AssertUser(wa.users.loadUsers(email=args.email))

    # Get organism
    org_cn = GuessOrg(args, wa)
    if org_cn:
        # Check user perms on org.
        org_cn = org_cn[0]
        org = wa.organisms.findOrganismByCn(org_cn)
        if checkPermission(gx_user, org_cn):
            returnData = wa.organisms.deleteOrganism(org['id'])
            print("Delete organism %s" % org_cn)
            print("returnData = " + str(returnData) + "\n")
        else:
            logger.error("Not authorized! You do not have permissions to delete this organism. You need to request administrative permission for this organism from the owner.")
            exit(1)
    else:
        logger.error("Organism %s doesn't exist" % org_cn)


