#!/usr/bin/env python
import numpy as np
import argparse
import dockerhelper
import logging

parser = argparse.ArgumentParser()
parser.add_argument('--Environment', help="Environment i.e. dev, uat or live", default='local')
parser.add_argument('--Keep', help="Number of containers to keep per service", default=3)
parser.add_argument('--WhatIf', help="Will not remove containers, would just notify what it would be deleting", default=False)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

numOfContainersToKeep = int(args.Keep)
whatif = args.WhatIf
env = args.Environment

print "### Args received, Keep: ", numOfContainersToKeep, ", WhatIf: ", whatif

objdockerhelper = dockerhelper.DockerHelper(env)
conImageList = objdockerhelper.GetListOfImages()

# Slice multi dimension list to extract just imageName
npArr  = np.array(conImageList)
imgNames  = npArr[:, 0]
print "### Total images found: ", len(imgNames)
uniqueImgNames, counts = np.unique(imgNames, return_counts=True)
print "### Unique images with count: ", len(uniqueImgNames)
uarr = np.column_stack((uniqueImgNames, counts))
logger.debug("Images with count")
logger.debug(np.matrix(uarr))
imagesWithMoreThanNthVersion = uarr[uarr[:, 1] > numOfContainersToKeep]
logger.debug("Images with greater that %s", numOfContainersToKeep)
logger.debug(np.matrix(imagesWithMoreThanNthVersion))
print "### Images with more than ", numOfContainersToKeep, " version"

for img in imagesWithMoreThanNthVersion:
    imageName = img[0]
    print "\n### Image"
    print imageName
    # Gets all the images for this imageName
    versions = npArr[npArr[:, 0] == imageName]
    # Sorting of the date, older first newer later
    versions = versions[versions[:, 3].argsort()]
    # Numbers of rows
    rowCount = versions.shape[0]
    print "### Images List to remain"
    print np.matrix(versions[(numOfContainersToKeep-1):rowCount])
    # Skipping last 3 rows
    newRowCount = rowCount - numOfContainersToKeep
    # In Python, array can be select as flowing
    # array[row1:row2, col1:col2]
    ImagesToRemove = versions[0:newRowCount]
    print "### Image to remove"
    print ImagesToRemove
    # Getting images ID's
    ImageIds = ImagesToRemove[:, 2]
    if not whatif == "True":
        # Removing Images
        for imgId in ImageIds:
            objdockerhelper.RemoveContainerImage(imgId)
    else:
        print "### WHATIF flag found, won't be deleting the container "

