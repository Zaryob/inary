#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import urllib2

import piksemel

first_revision = "27898"
accounts_url = "http://svn.pardus.org.tr/uludag/trunk/common/accounts"
authors = {}

def get_author_name_mail(author):
    if not authors:
        accounts = urllib2.urlopen(accounts_url)
        for line in accounts:
            if line.startswith("#"):
                continue
            elif line.count(":") != 3:
                continue

            account, name, mail, jabber = line.split(":")
            mail = mail.replace(" [at] ", "@")
            authors[account] = "%s <%s>" % (name, mail)

    return authors[author]

def cleanup_msg_lines(lines):
    result = []
    for line in lines:
        if line.startswith("BUG:FIXED:"):
            bug_number = line.split(":")[2]
            line = "Fixes the bug reported at http://bugs.pardus.org.tr/%s." % bug_number

        elif line.startswith("BUG:COMMENT:"):
            bug_number = line.split(":")[2]
            line = "See http://bugs.pardus.org.tr/%s." % bug_number

        elif line.startswith("Changes since "):
            return result[:-1]

        result.append(line)

    return result

def strip_empty_lines(msg):
    result = []
    for line in msg.splitlines():
        if not line.strip():
            line = ""

        result.append(line)

    return "\n".join(result)

def create_log_entry(author, date, msg):
    if author == "transifex":
        return None

    author = get_author_name_mail(author)
    date = date.split("T", 1)[0]

    lines = msg.splitlines()
    lines = cleanup_msg_lines(lines)
    lines[0] = "\t* %s" % lines[0]
    msg = "\n\t".join(lines)

    msg = strip_empty_lines(msg)
    entry = "%s %s\n%s" % (date, author, msg)

    return entry

if __name__ == "__main__":
    p = os.popen("svn log -r%s:HEAD --xml" % first_revision)
    doc = piksemel.parseString(p.read())

    entries = []
    for log_entry in doc.tags("logentry"):
        author = log_entry.getTagData("author")
        date = log_entry.getTagData("date")
        msg = log_entry.getTagData("msg")

        entry = create_log_entry(author, date, msg.strip())
        if entry:
            entries.append(entry)

    entries.reverse()
    open("ChangeLog", "w").write("\n\n".join(entries))
