import subprocess
import numpy as np
import logging


def execute(command):
    return subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)


def imagestoremove(imageTagList, numOfContainersToKeep):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    narr = np.array(imageTagList)
    versions = narr[narr[:, 2].argsort()]  # oldest on top, newest on last
    logger.debug("Total images")
    logger.debug(versions)
    # Numbers of rows
    rowCount = versions.shape[0]
    # taking last 3 rows
    splitRowCount = rowCount - numOfContainersToKeep
    print "### Images List to remain"
    print np.matrix(versions[splitRowCount:rowCount])
    # In Python, array can be select as flowing
    # array[row1:row2, col1:col2]
    ImagesToRemove = versions[0:splitRowCount]
    print "### Images list to remove"
    print ImagesToRemove
    return ImagesToRemove