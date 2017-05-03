#!/usr/bin/python

__all__ = ['ApplicationDescriptionParser']

import tarfile
from tempfile import mkdtemp
import json
from os import rmdir
from shutil import rmtree


class ApplicationDescriptionParser:
    def __init__(self, file_path):
        workdir = file_path
        try:
            is_tar = tarfile.is_tarfile(file_path)
        except IOError:
            is_tar=False
        if is_tar:
            self.__tar = tarfile.open(file_path)
            workdir = mkdtemp()
            self.__tar.extractall(path=workdir)

        self.__content = json.load(open(workdir+"/description.json"))
        for m in self.__content['modules']:
            for s in m['scripts']:
                t = open(workdir+"/"+s['file'])
                s['file-content'] = t.read()
        if is_tar:
            rmtree(workdir)

    def get_description(self):
        return self.__content

