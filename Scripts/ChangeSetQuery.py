#!/usr/bin/env python
#---------------------------------------------------------------------------
# Copyright 2013 The Open Source Electronic Health Record Agent
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#---------------------------------------------------------------------------

from __future__ import with_statement
import os # to get gtm environment variables
import sys
import subprocess
import re
import argparse
import json

class GerritChangeSetQuery(object):

  GERRIT_JSON_HEADER = ")]}'"

  def __init__(self, gerritUrl, projName):
    self._projName = projName
    self._gerritUrl = gerritUrl

  def queryChangeSet(self, age="1w", limit="10", 
                     status="open", branch='master'):
    httpUrl = (
      "%s/changes/?format=JSON&q=project:%s+status:%s+-age:%s+branch:%s&n=%s" %
      (self._gerritUrl, self._projName, status, age, branch, limit)
    )
    print httpUrl
    outputJson = self.__execQueryByCurl__(httpUrl)
    if outputJson is None:
      return
    for commit in outputJson:
      print commit["_number"]
      self.getCommitDetail(commit["_number"])
    # handle the case that might have nore change set

  def getCommitDetail(self, gerritId):
    outputDetail = "o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES"
    httpUrl = ("%s/changes/?format=JSON&q=%s&%s" %
                (self._gerritUrl, gerritId, outputDetail))
    print httpUrl
    outputJson = self.__execQueryByCurl__(httpUrl)
    for changeSet in outputJson:
      # print out the files change
      curRev = changeSet['current_revision']
      commitDetail = changeSet['revisions'][curRev]
      import pprint
      pprint.pprint(commitDetail['files'])

  def __execQueryByCurl__(self, queryUrl):
    cmdList = ['curl', "-s" , queryUrl]
    outputJson = None
    try:
      output = subprocess.Popen(cmdList, stdout=subprocess.PIPE).communicate()[0]
      output = output.strip(' \r\n')
      print output
      """ get rid of the header """
      if output.find(self.GERRIT_JSON_HEADER) == 0:
        output = output[len(self.GERRIT_JSON_HEADER):]
      outputJson = json.loads(output)
    except OSError as ex:
      print ex
    return outputJson

GERRIT_URL = "http://review.code.osehra.org"
GERRIT_PROJECT_NAME = "VistA-Patches"

def main():
  changeQuery = GerritChangeSetQuery(GERRIT_URL,
                                     GERRIT_PROJECT_NAME)
  changeQuery.queryChangeSet()

if __name__ == '__main__':
  main()
