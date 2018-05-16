#!/usr/bin/env python
from __future__ import print_function

import sys
import argparse
import random
import time
import json
import logging
import codecs
import csv
from builtins import range, str

from webapollo import WAAuth, WebApolloInstance, AssertUser, AssertAdmin
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def isGroupAdmin(userName, groupName):
    groupAdmin = wa.groups.getGroupAdmin(groupName)
    for admin in groupAdmin:
        if admin['username'] == userName:
            return True
    return False

def pwgen(length):
    chars = list('qwrtpsdfghjklzxcvbnm')
    return ''.join(random.choice(chars) for _ in range(length))

def cleanInput(dict):
    cleanedDict = {k:v.strip() for k,v in dict.items()}
    return cleanedDict

def createApolloUser(user, out, gx_user):
    user = cleanInput(user)
    password = pwgen(12)
    time.sleep(1)
    users = wa.users.loadUsers()
    apollo_user = [u for u in users
            if u.username == user['useremail']]

    if len(apollo_user) == 1:
        userObj = apollo_user[0]
        # check if gx_user is admin or creator of the apollo_user
        creatorData = wa.users.getUserCreator(userObj.username)
        if gx_user.role != 'ADMIN' and creatorData['creator'] != str(gx_user.userId):
            sys.exit(gx_user.username + " is not authorized to update user: " + userObj.username)
        returnData = wa.users.updateUser(userObj, user['useremail'], user['firstname'], user['lastname'], password)
        out.writerow({'Operation':'Update User', 'First Name': user['firstname'], 'Last Name': user['lastname'],
                       'Email': user['useremail'], 'New Password': password})
        print("Update user %s" % user['useremail'])
    else:
        returnData = wa.users.createUser(user['useremail'], user['firstname'], user['lastname'],
                                         password, role='user', metadata={'creator': gx_user.userId})
        out.writerow({'Operation':'Create User', 'First Name': user['firstname'], 'Last Name': user['lastname'],
                      'Email': user['useremail'], 'New Password': password})
        print("Create user %s" % user['useremail'])
    print("Return data: " + str(returnData) + "\n")


def createApolloUsers(users_list, out, gx_user):
    if gx_user.role != 'INSTRUCTOR' and gx_user.role != 'ADMIN':
        sys.exit(gx_user.role + " is not authorized to create users")
    for user in users_list:
        if user['batch'] == "false":
            createApolloUser(user, out, gx_user)
        elif user['batch'] == "true":
            users = parseUserInfoFile(user['format'], user['false_path'])
            for u in users:
                if not 'useremail' in u:
                    logger.error("Cannot find useremail in the text file, make sure you use the correct header, see README file for examples.")
                if not 'firstname' in u:
                    logger.error("Cannot find firstname in the text file, make sure you use the correct header, see README file for examples.")
                if not 'lastname' in u:
                    logger.error("Cannot find lastname in the text file, make sure you use the correct header, see README file for examples.")
                createApolloUser(u, out, gx_user)


def deleteApolloUser(user, out, gx_user):
    user = cleanInput(user)
    apollo_user = wa.users.loadUsers(email=user['useremail'])
    if len(apollo_user) == 1:
        userObj = apollo_user[0]
        # check if gx_user is admin or creator of the apollo_user
        creatorData = wa.users.getUserCreator(userObj.username)
        if gx_user.role != 'ADMIN' and creatorData['creator'] != str(gx_user.userId):
            sys.exit(gx_user.username + " is not authorized to delete user: " + userObj.username)
        returnData = wa.users.deleteUser(userObj)
        out.writerow({'Operation':'Delete User', 'First Name': userObj.firstName, 'Last Name': userObj.lastName,
                      'Email': userObj.username})
        print("Delete user %s" % userObj.username)
        print("Return data: " + str(returnData) + "\n")
    else:
        logger.error("The user %s doesn't exist", user['useremail'])


def deleteApolloUsers(users_list, out, gx_user):
    if gx_user.role != 'INSTRUCTOR' and gx_user.role != 'ADMIN':
        sys.exit(gx_user.role + " is not authorized to delete users")
    for user in users_list:
        if user['batch'] == "false":
            deleteApolloUser(user, out, gx_user)
        elif user['batch'] == "true":
            users = parseUserInfoFile(user['format'], user['false_path'])
            for u in users:
                if not 'useremail' in u:
                    logger.error("Cannot find useremail in the text file, make sure you use the correct header, see README file for examples.")
                    exit(1)
                deleteApolloUser(u, out, gx_user)


def addApolloUserToGroup(user, out, gx_user):
    user = cleanInput(user)
    apollo_user = wa.users.loadUsers(email=user['useremail'])
    groups = wa.groups.loadGroups()
    group = [g for g in groups if g.name == user['group']]
    if not apollo_user:
        logger.error("the user %s doesn't exist", user['useremail'])
        exit(1)
    if not group:
        logger.error("the group %s doesn't exist", user['group'])
        exit(1)
    if len(group) > 1:
        logger.warn("There are more than one groups with the name %s", user['group'])
        exit(1)
    userObj = apollo_user[0]
    groupObj = group[0]
    creatorData = wa.groups.getGroupCreator(groupObj.name)
    # proceed if gx_user is global admin, group creator or group admin
    if gx_user.role != 'ADMIN' and not isGroupAdmin(gx_user.username, groupObj.name) and creatorData['creator'] != str(gx_user.userId):
        sys.exit(gx_user.username + " is not authorized to add user to group: " + groupObj.name)
    returnData = wa.users.addUserToGroup(groupObj, userObj)
    out.writerow({'Operation':'Add User to Group', 'First Name': userObj.firstName, 'Last Name': userObj.lastName,
                  'Email': userObj.username, 'Add to Group': groupObj.name})
    print("Add user %s to group %s" % (userObj.username, groupObj.name))
    print("Return data: " + str(returnData) + "\n")

def addApolloUsersToGroups(users_list, out, gx_user):
    for user in users_list:
        if user['batch'] == "false":
            addApolloUserToGroup(user, out, gx_user)
        elif user['batch'] == "true":
            users = parseUserInfoFile(user['format'], user['false_path'])
            for u in users:
                if not 'useremail' in u:
                    logger.error("Cannot find useremail in the text file, make sure you use the correct header, see README file for examples.")
                    exit(1)
                if not 'group' in u:
                    logger.error("Cannot find group in the text file, make sure you use the correct header, see README file for examples.")
                    exit(1)
                addApolloUserToGroup(u, out, gx_user)


def removeApolloUserFromGroup(user, out, gx_user):
    user = cleanInput(user)
    apollo_user = wa.users.loadUsers(email=user['useremail'])
    groups = wa.groups.loadGroups()
    group = [g for g in groups if g.name == user['group']]
    if not apollo_user:
        logger.error("the user %s doesn't exist", user['useremail'])
        exit(1)
    if not group:
        logger.error("the group %s doesn't exist", user['group'])
        exit(1)
    if len(group) > 1:
        logger.warn("There are more than one groups with the name %s", user['group'])
        exit(1)
    userObj = apollo_user[0]
    groupObj = group[0]
    creatorData = wa.groups.getGroupCreator(groupObj.name)
    # proceed if gx_user is global admin, group creator or group admin
    if gx_user.role != 'ADMIN' and not isGroupAdmin(gx_user.username, groupObj.name) and creatorData['creator'] != str(gx_user.userId):
        sys.exit(gx_user.username + " is not authorized to remove user from group: " + groupObj.name)
    returnData = wa.users.removeUserFromGroup(groupObj, userObj)
    out.writerow({'Operation':'Remove User from Group', 'First Name': userObj.firstName, 'Last Name': userObj.lastName,
                  'Email': userObj.username, 'Remove from Group': groupObj.name})
    print("Remove user %s from group: %s" % (userObj.username, groupObj.name))
    print("Return data: " + str(returnData) + "\n")

def removeApolloUsersFromGroups(users_list, out, gx_user):
    for user in users_list:
        if user['batch'] == "false":
            removeApolloUserFromGroup(user, out, gx_user)
        elif user['batch'] == "true":
            users = parseUserInfoFile(user['format'], user['false_path'])
            for u in users:
                if not 'useremail' in u:
                    logger.error("Cannot find useremail in the text file, make sure you use the correct header, see README file for examples.")
                    exit(1)
                if not 'group' in u:
                    logger.error("Cannot find group in the text file, make sure you use the correct header, see README file for examples.")
                    exit(1)
                removeApolloUserFromGroup(u, out, gx_user)


def parseUserInfoFile(file_format, filename):
    if file_format == "tab":
        delimiter = '\t'
    elif file_format == "csv":
        delimiter = ','
    else:
        logger.error("The %s format is not supported!", file_format)
    with open(filename, 'r') as f:
        lines = f.readlines()
    headers = lines[0].split(delimiter)
    users = []
    lines = lines[1:]
    for l in lines:
        l = l.split(delimiter)
        info = dict()
        fields = len(l)
        for i in range(fields):
            title = headers[i].strip()
            info[title] = l[i].strip()
        users.append(info)
    return users

def loadJson(jsonFile):
    try:
        data_file = codecs.open(jsonFile, 'r', 'utf-8')
        return json.load(data_file)
    except IOError:
        logger.error("Cannot find JSON file\n")
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Apollo user management via web services')
    WAAuth(parser)

    parser.add_argument('-j', '--data_json', help='JSON file containing the metadata of the inputs')
    parser.add_argument('-o', '--output', help='HTML output')

    args = parser.parse_args()
    jsonData = loadJson(args.data_json)
    outputFile = open(args.output, 'a')
    fieldnames = ['Operation', 'First Name', 'Last Name', 'Email', 'New Password', 'Add to Group', 'Remove from Group']
    csvWriter = csv.DictWriter(outputFile, fieldnames=fieldnames)
    csvWriter.writeheader()
    operations_dictionary = jsonData.get("operations")
    email = jsonData.get("email")
    wa = WebApolloInstance(args.apollo, args.username, args.password)
    gx_user = AssertUser(wa.users.loadUsers(email=email))
    for operation, users_list in operations_dictionary.items():
        if operation == "create":
            # proceed if the gx_user is global admin or instructor
            # if the apollo_user exists, check if gx_user is admin or creator of the apollo_user before updating the user
            createApolloUsers(users_list, csvWriter, gx_user)
        elif operation == "delete":
            # proceed if the gx_user is global admin, or user's creator
            deleteApolloUsers(users_list, csvWriter, gx_user)
        elif operation == "add":
            # proceed if the gx_user is global admin or group admin or group creator
            addApolloUsersToGroups(users_list, csvWriter, gx_user)
        elif operation == "remove":
            # proceed if the gx_user is global admin or group admin or group creator
            removeApolloUsersFromGroups(users_list, csvWriter, gx_user)

    outputFile.close()

