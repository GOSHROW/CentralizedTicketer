from flask import jsonify
import pymongo

def getStatus(dbclient, user):
    issuesList = []
    for issues in dbclient["TicketedIssues"]["Issues"].find():
        if issues["clientname"] == user:
            issuesList.append(issues)
    return jsonify(issuesList(issuesList))

def verify(dbclient, request):
    username = request.args.get('user', '')
    key = request.args.get('key', '')
    users = dbclient["TicketedIssues"]["Users"]
    print([x for x in users.find()])
    for user in users.find():
        if user["username"] == username and user["auth"] == key:
            return True
    return False

def putRequest(dbclient, request):
    contact = request.args.get('email', '')
    username = request.args.get('user', '')
    message = request.args.get('message', '')
    deadline = request.args.get('deadline', '')
    issueno = request.args.get('issue', '')
    newissue = {"contact": contact, "message": message, "deadline": deadline}
    dbclient.update({"issueno": issueno, "user": username}, {"$set": newissue})

# modify as per scheme
# TODO: Make basic unique random
def getNO():
    return str(42)

def addIssue(dbclient, request):
    contact = request.args.get('email', '')
    username = request.args.get('user', '')
    message = request.args.get('message', '')
    deadline = request.args.get('deadline', '')
    issueno = request.args.get('issue', '')
    newissue = {"user": username, "issueno": getNO(), "contact": contact, "message": message, "deadline": deadline, "allotted": "None"}
    dbclient.insert_one(newissue)

def delIssues(dbclient, request):
    username = request.args.get('user', '')
    issueno = request.args.get('issue', '')
    todel = { "user": username, "issueno": issueno}
    dbclient.delete_one(todel)