#############################
# Full Imports
import sys
import os
import csv
import itertools
import nupic.support

#############################
# Partial Imports
from nupic.frameworks.opf.experiment_runner import initExperimentPrng
from nupic.frameworks.opf import opfbasicenvironment, opfhelpers
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.opftaskdriver import OPFTaskDriver
from nupic.frameworks.opf.opfutils import InferenceElement

def main():
    # Start Logging
    nupic.support.initLogging(verbose=True)
    
    # Initialize random number generators
    initExperimentPrng()
        
    # Pull the experiment directory from the command line
    experimentDir = sys.argv[1]
    
    # Get an interface to our experiment in that directory
    expIface = getExperimentInterface(experimentDir)

    # Create a 'default task' for the experiment to run.    
    expIface.convertGrokEnvToOPF()
    experimentTasks = expIface.getModelControl().get('tasks', [])
    
    # Pull out the model description from the interface object
    modelDescription = expIface.getModelDescription()
    
    # Instantiate our CLA model
    model = ModelFactory.create(modelDescription)
    
    # Create a task driver to manage our experiment
    task = experimentTasks[0]
    taskControl = task['taskControl']
    taskDriver = OPFTaskDriver(taskControl = taskControl, model = model)

    # Get our iteration count so we know when to stop
    numIters = task['iterationCount']
    
    if numIters >= 0:
        # If we have an iteration limit, use that
        iterTracker = iter(xrange(numIters))
    else:
        # Otherwise just continue to return the next number forever
        iterTracker = iter(itertools.count())
        
    # Reset the model, just in case
    model.resetSequenceStates()
    
    # Do setup - preparing to star the experiment!
    taskDriver.setup()
    
    # Prepare to store the predictions as they are made
    fh = open('tbPredictions.csv','w')
    writer = csv.writer(fh)

    streamDef = task['dataset']
    datasetReader = opfbasicenvironment.BasicDatasetReader(streamDef)

    # Run through all the records!
    while True:
        # Check controlling iterator first
        try:
            count = next(iterTracker)
            print count
        except StopIteration:
            break
    
        # Read next input record
        try:
            inputRecord = datasetReader.next()
            print inputRecord
        except StopIteration:
            break
        
        # Process input record
        result = taskDriver.handleInputRecord(inputRecord=inputRecord)
        
        # NOTE: Direction with value of 0 may not be encoded properly
        #print 'All inferences:'
        #print result.inferences
        
        #print "Result Row:"
        row = [count, result.inferences['multiStepBestPredictions'][1], result.inferences['multiStepBestPredictions'][5]]
        #print row
        writer.writerow(row)
    
        if InferenceElement.encodings in result.inferences:
            result.inferences.pop(InferenceElement.encodings)
    
        #print ".",
        #sys.stdout.flush()

    # Reset the model, just in case
    model.resetSequenceStates()

    # Save the model to disk
    saveModel(model = model,
               experimentDir = experimentDir,
               checkpointLabel=task['taskLabel'])

def saveModel(model, experimentDir, checkpointLabel):
    """Save model"""
    checkpointDir = getModelCheckpointDir(experimentDir, checkpointLabel)
    model.save(saveModelDir=checkpointDir)


def getModelCheckpointDir(experimentDir, checkpointLabel):
    """Creates directory for serialization of the model
  
    checkpointLabel:
        Checkpoint label (string)
  
    Returns:
      absolute path to the serialization directory
    """
    checkpointDir = os.path.join(getCheckpointParentDir(experimentDir),
                                 checkpointLabel + '.nta')
    checkpointDir = os.path.abspath(checkpointDir)
  
    return checkpointDir

def getCheckpointParentDir(experimentDir):
    """Get checkpoint parent dir.
  
    Returns: absolute path to the base serialization directory within which
        model checkpoints for this experiment are created
    """
    baseDir = os.path.join(experimentDir, "savedmodels")
    baseDir = os.path.abspath(baseDir)
  
    return baseDir

def getExperimentInterface(experimentDir):
    '''
    Returns an interface to an experiment configured by a description.py
    file.
    
    experimentDir - Full path to directory containing the experiments
                    description.py file
    '''

    descriptionPyModule = opfhelpers.loadExperimentDescriptionScriptFromDir(
        experimentDir)
      
    # Wrap the dicts in that file in an interface
    expIface = opfhelpers.getExperimentDescriptionInterfaceFromModule(
        descriptionPyModule)
    
    return expIface

if __name__ == "__main__":
    main()
