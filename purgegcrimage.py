#!/usr/bin/env python
import argparse
from purgegcrfunctions import execute, imagestoremove

parser = argparse.ArgumentParser()
parser.add_argument('--Environment', help="Environment i.e. dev, uat or live", default='local')
parser.add_argument('--Keep', help="Number of containers to keep per service", default=3)
parser.add_argument('--WhatIf', help="Will not remove containers, would just notify what it would be deleting", default=False)
args = parser.parse_args()

rootrepolist = []
repolist = []
numOfContainersToKeep = int(args.Keep)
whatif = bool(args.WhatIf)
env = args.Environment
env = str(env).lower()

# Get List of repository
cmdRepoList = "gcloud container images list --repository=asia.gcr.io/cexdev-office-dev"
output = execute(cmdRepoList)
output = output.split('\n')

print "### Processing root repo...."
for line in output:
    if (line.startswith('asia.gcr.io')
    and env in line):
        rootrepolist.append(line)

countofrootrepo=len(rootrepolist)
if countofrootrepo < 1:
    print "### No root repo found for '" + env + "' environment"
    exit()

print "### Processing child repo within root repo...."
# loop in each repo for more image
for rootrepo in rootrepolist:
    print "### Processing child repo [" + rootrepo + "] ...."
    cmdInternalRepoList = "gcloud container images list --repository=" + rootrepo
    output = execute(cmdInternalRepoList)
    output = output.split('\n')
    
    for line in output:
        if line.startswith('asia.gcr.io'):
            repolist.append(line)    
    break

# List all images
for repo in repolist:
    repoListTags = []
    print "### Processing tag list [" + repo + "] ...."
    cmdListTag = "gcloud container images list-tags " + repo
    output = execute(cmdListTag)
    output = output.split('\n')    
    countOfTag = len(output) - 2 # One for header, and last line

    if countOfTag > numOfContainersToKeep:
        print '### Image, count'
        print repo, countOfTag
        for line in output:
            if ('DIGEST' not in line 
                    and line.strip() != ""): #line is not header and empty line
                items = line.split()
                repoListTags.append((repo, items[1], items[2]))
        imgstodelete = imagestoremove(repoListTags, numOfContainersToKeep)

        # Delete imaages
        if whatif != True:
            for img in imgstodelete:
                imgname = img[0]
                imgtag = img[1]
                fullimagename = imgname + ":" + imgtag
                print "### Deleting image [" + fullimagename + "] ...."
                removetagcmd = "gcloud container images delete " + fullimagename + " --quiet"
                print removetagcmd
                output = execute(removetagcmd)
                print output
    else:
        print "### Repo contains '" + str(countOfTag) + "' images, which is less than number of images to keep: " + str(numOfContainersToKeep)

    print "\n\n"
    # move to next repo in the list
