#!/usr/bin/env python

import docker
from datetime import datetime


class DockerHelper(object):
    """Docker helper class for docker related method"""

    def __init__(self, env='local'):
        tls_config = docker.tls.TLSConfig(
            ca_cert='certs/ca.pem',
            client_cert=('certs/cert.pem', 'certs/key.pem'),
            verify=True
        )
        if env == "local":
            self.client = docker.from_env()
        elif env == "dev":
            self.client = docker.DockerClient(base_url='tcp://10.4.1.233:2376',
                                                tls=tls_config)
        elif env == "uat":
            self.client = docker.DockerClient(base_url='tcp://10.204.2.29:2376',
                                                tls=tls_config)
        else:
            self.client = docker.from_env()

    def GetListOfImages(self):

        client = self.client
        conimages = client.images.list()
        #ImageName, Version, imageshortId, ImageDate
        shabsImageList = []
        for img in conimages:
            imgID = img.short_id
            imgTags  = img.tags
            timeelapse = img.attrs["Created"]
            imgDt = datetime.fromtimestamp(timeelapse)
            if imgTags == []:
                print "Tag empty for ", imgID, ", removing non tag Container"
                client.images.remove(imgID)
            for tag in imgTags:
                imgtag = tag.split(":")
                imageName = imgtag[0]
                imageVersion = imgtag[1]
                shabsImageList.append([imageName, imageVersion, imgID, imgDt])

        return shabsImageList


    def RemoveContainerImage(self, short_image_ID):
        client = docker.from_env()
        conimages = client.images.list()
        # ImageName, Version, imageshortId, ImageDate
        for img in conimages:
            if img.short_id == short_image_ID:
                print "Removing Container " + img.short_id
                try:
                    client.images.remove(img.id)
                except Exception as e:
                    print e.__doc__
                    print e.message
