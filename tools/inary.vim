" File: inary.vim
" Author: Suleyman Poyraz
" Version: 0.1
" Description: Lots of useful functions for inary packagers
" License: GPLv3
"
"
"
""""""""" USAGE
" You can change the keybindings for your personal use
nmap <F2>h :call FixHash()<CR>
nmap <F2>a :call PackageTakeover()<CR>
nmap <F2>c :call AddComment()<CR>
nmap <F2>o :call OpenHomePage()<CR>
nmap <F2>p :call AddPatches()<CR>
nmap <F2>w :call ShowOther()<CR>
nmap <F2>d :call ShowDiff()<CR>
nmap <F2>t :call CreateCommit()<CR>
nmap <F2>s :call SvnCommit()<CR>




"""""""" FUNCTIONS
""""""""""""""""""

function! FixHash()
python3 << EOF
import os
import vim
import hashlib
import ciksemel

buf = vim.current.buffer

correct_syntax = False
for row, line in enumerate(buf[:]):
    if "<Archive sha1sum=" in line:
        correct_syntax = True
        tag = ciksemel.parseString(line)
        hash = tag.getAttribute("sha1sum")
        uri = tag.firstChild().data()
        file_name = os.path.basename(uri)
        file_path = os.path.join("/var/cache/inary/archives", file_name)

        if not os.path.exists(file_path):
            if os.path.exists("tmp.xml"):
                os.unlink("tmp.xml")
            vim.command("w tmp.xml")
            # dont call sudo if invoked as root
            if os.geteuid():
                vim.command("!sudo inary -d bi --fetch tmp.xml; rm -f tmp.xml")
            else:
                vim.command("!inary -d bi --fetch tmp.xml; rm -f tmp.xml")

        new_hash = hashlib.sha1(open(file_path, "r").read().encode('utf-8')).hexdigest()
        tag.setAttribute("sha1sum", new_hash)
        buf[row] = " " * 8 + tag.toString()

if not correct_syntax:
    print ("Error: The Archive attribute 'sha1sum' must come first.")
EOF
endfunction

function! PackageTakeover()
python3 << EOF
import os
import vim

buf = vim.current.buffer

conf_file = os.path.expanduser("~/.packagerinfo")
if os.path.exists(conf_file):
    # Read from it
    name, email = open(conf_file, "r").read().strip().split(",")

else:
    name = vim.eval('input("Please enter your full name as seen in pspec files: ")')
    email = vim.eval('input("Please enter your full email as seen in pspec files: ")')
    open(conf_file, "w").write("%s,%s" % (name, email))

pkgr_name = "            <Name>%s</Name>\n" % name
pkgr_email = "            <Email>%s</Email>\n" % email

for row, line in enumerate(buf[:]):
    if "            <Name>" in line:
        buf[row] = pkgr_name
    elif "            <Email>" in line:
        buf[row] = pkgr_email
        break

EOF
endfunction


function! AddComment()
python << EOF
import vim
import time
import inary
import os

conf_file = os.path.expanduser("~/.packagerinfo")
if os.path.exists(conf_file):
    # Read from it
    name, email = open(conf_file, "r").read().strip().split(",")

else:
    name = vim.eval('input("Please enter your full name as seen in pspec files: ")')
    email = vim.eval('input("Please enter your full email as seen in pspec files: ")')
    open(conf_file, "w").write("%s,%s" % (name, email))

CONSTANTS = inary.constants.Constants()
pspec = inary.specfile.SpecFile(CONSTANTS.pspec_file)

release = '        <Update release="%d">' % (int(pspec.history[0].release) + 1)
date =    '            <Date>%s</Date>' % time.strftime("%Y-%m-%d")
version = '            <Version>%s</Version>' % pspec.history[0].version
comment = '            <Comment></Comment>'
name =    '            <Name>%s</Name>' % name
email =   '            <Email>%s</Email>'% email
update=   '        </Update>'

buf = vim.current.buffer
win = vim.current.window

for row, line in enumerate(buf[:]):
    if "<History>" in line:
        #NOTE: do not use double quotes, it can fail
        comment_row = row + 5
        vim.command("call append(%s, ['%s','%s','%s','%s','%s','%s','%s'])" % (row + 1,
                                                                                    release,
                                                                                    date,
                                                                                    version,
                                                                                    comment,
                                                                                    name,
                                                                                    email,
                                                                                    update))
win.cursor = (comment_row, 21)

def normal(str):
    vim.command("normal "+str)

normal("i")
EOF
endfunction


function! OpenHomePage()
python << EOF
import vim
import webbrowser
import ciksemel

buf = vim.current.buffer

for row, line in enumerate(buf[:]):
    if "<Homepage>" in line:
        tag = ciksemel.parseString(line)
        url = tag.firstChild().data()
try:
    xdg_browser = webbrowser.GenericBrowser('xdg-open')
    xdg_browser.open(url)
except:
    print('ERROR: could not open url')

EOF
endfunction


function! AddPatches()
python3 << EOF
import vim
import os
import subprocess

buf = vim.current.buffer

if os.path.exists(".svn"):
    cmd = ["svn", "st", "files/"]
else:
    cmd = ["git", "status", "-s", "files/"]

output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split("\n")

patches = []
for patch in output:
    if patch[0] == "?" or patch[0] == "A":
        if patch.endswith("patch") or patch.endswith("diff"):
            patch = patch.split("/", 1)[1]
            frmt_patch = '            <Patch level="1">%s</Patch>' % patch
            patches.append(frmt_patch)

for row, line in enumerate(buf[:]):
    if "</Source>" in line:
        if "</Patches>" in buf[row - 1]:
            for patch in patches:
                vim.command("call append(%s, '%s')" % (row - 1, patch))
        else:
            vim.command("call append(%s, ['        <Patches>', '        </Patches>'])" % row)
            for patch in patches:
                vim.command("call append(%s, '%s')" % (row + 1, patch))

EOF
endfunction


function! ShowDiff()
python << EOF
import vim

cur_filename = vim.eval('@%')
old_filename = ".svn/text-base/%s.svn-base" % cur_filename

vim.command(":vert diffsplit %s" % old_filename)

EOF
endfunction


function! ShowOther()
python << EOF

import vim
cur_filename = vim.eval('@%')

if cur_filename == "pspec.xml":
    vim.command(":vs actions.py")
elif cur_filename == "actions.py":
    vim.command(":vs pspec.xml")

EOF
endfunction


function! CreateCommit()
python << EOF
import re
import os
import vim
import ciksemel

def normal(str):
    vim.command("normal "+str)

pspec = ciksemel.parse("pspec.xml")
comment_data = pspec.getTag("History").getTag("Update").getTagData("Comment")

file_name = "commit-msg.tmp"
if os.path.exists(file_name):
    os.unlink(file_name)

commit_file  = open(file_name, "w")
commit_file.write(comment_data)

# \D matches any non-digit chars. we need the bug numbers. so...
bug_comments = [re.sub("\D", "", i) for i in comment_data.split() if "pb#" in i]
if bug_comments:
    for i in bug_comments:
        commit_file.write("\nBUG:COMMENT:%s" % i)
commit_file.close()

vim.command(":vs commit-msg.tmp")
normal("ggVG=")

EOF
endfunction

function! SvnCommit()
python << EOF
import vim

vim.command(":!svn ci --file commit-msg.tmp")
os.system("rm commit-msg.tmp")
EOF
endfunction

