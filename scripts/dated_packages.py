#!/usr/bin/python

import os
import os.path
import sys
import time

import piksemel


SUCCESS, FAIL = xrange(2)


def isExpired(date, days):
    diff = time.time() - time.mktime(time.strptime(date, '%Y-%m-%d'))
    secs = 60 * 60 * 24 * days
    return diff > secs


def getSpecs(folder):
    specs = []
    for root, dirs, files in os.walk(folder):
        if 'pspec.xml' in files:
            specs.append(root)
        if '.svn' in dirs:
            dirs.remove('.svn')
    return specs


def main():
    if len(sys.argv) != 3:
        print 'Usage: %s repo-path [-]days' % sys.argv[0]
        return FAIL

    if not os.path.isdir(sys.argv[1]):
        print 'Repo path is not valid.'
        return FAIL

    days = sys.argv[2]

    revert = days[0] == '-'
    if revert:
        days = days[1:]

    if not days.isdigit():
        print 'Days must be integer.'
        return FAIL

    repopath = sys.argv[1]
    days = int(days)

    errors = []
    for packagedir in getSpecs(repopath):
        shortpath = '%s/pspec.xml' % packagedir[len(repopath):]
        try:
            doc = piksemel.parse(os.path.join(packagedir, 'pspec.xml'))
            date = doc.getTag('History').getTag('Update').getTagData('Date')
        except:
            errors.append('Can\'t parse: %s' % shortpath)
            continue

        try:
            expired = isExpired(date, days)
        except ValueError:
            errors.append('Invalid date: %s (%s)' % (shortpath, date))
            continue

        if (not revert and expired) or (revert and not expired):
            print '%s %s' % (shortpath.ljust(70), date)

    if len(errors):
        print
        print 'Errors:'
        for e in errors:
            print ' ', e

    return SUCCESS


if __name__ == '__main__':
    sys.exit(main())
