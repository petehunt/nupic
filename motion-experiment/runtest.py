#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""A simple client to create a CLA model for hotgym."""

import csv
import datetime

from nupic.data.datasethelpers import findDataset
from nupic.frameworks.opf.modelfactory import ModelFactory

import model_params

DATA_PATH = "../../motion-experiment/test.csv"



def createModel():
  return ModelFactory.create(model_params.MODEL_PARAMS)



def runHotgym():
  model = createModel()
  model.disableLearning()
  # model.saveModel()
  model.enableInference({'predictionSteps': [1, 5],
                         'predictedField': 'activity',
                         'numRecords': 5397})
  print findDataset(DATA_PATH)
  with open (findDataset(DATA_PATH)) as fin:
    reader = csv.reader(fin)
    headers = reader.next()
    print headers
    print reader.next()
    print reader.next()
    for record in reader:
      print record
      record[1:-1] = [float(x) for x in record[1:-1]]
      modelInput = dict(zip(headers, record))
      #modelInput["ts"] = datetime.datetime.strptime(
      #    modelInput["ts"], "%Y-%m-%d %H:%M:%S.%f")
      result = model.run(modelInput)
      print result
  model.save('/vagrant/motion-experiment/model')


if __name__ == "__main__":
  runHotgym()
    
