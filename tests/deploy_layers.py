''' Mock AWS lambda layer deployment by moving layers from /lambda directory into the various lambda subdirectories '''
import os
import sys

LAYER_BASE = "./lambda/%s/python"
class DeployLambdaLayers:
    ''' Class for handling both setup and teardown of Lambda layers to simulate production environment.
    
    Moves lambda layer files to the root folder. Test files has been configured such that the lambda function imports directly from the root folder.'''
    
    def __init__(self, layers):
        self.layers = [layer for layer in layers]
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)
        self.__get_layer_files()
        sys.path = sys.path + self.paths
        
    def __get_layer_files(self):
        currentdir = os.path.dirname(os.path.realpath(__file__))
        parentdir = os.path.dirname(currentdir)
        self.paths = list(map(lambda x: '%s/lambda/%s/python'%(parentdir, x), self.layers))