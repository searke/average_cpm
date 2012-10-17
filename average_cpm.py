""" An example program of how data may read in from a CSV file.
Computations are done on the data and and a CSV file is returned
with the results.
"""

import csv, sys
import argparse
from numpy import *
from itertools import groupby

class FileReader:
    """ For reading CSV files with text headers """

    def __init__(self, filepath, delimiter=','):        
        # Create reader and read in the header for the csv file
        try:      
            self.reader = csv.reader(open(filepath,'r'), delimiter=delimiter)
            self.header = self.reader.next()
        except csv.Error:
            sys.exit(filepath + ' could not be read appropiately')

    def ValidateFields(self, requiredFields):
	
        """Ensures that the file read in is valid: checks that all strings
        in the input list are in the header"""

        validFile = all([x in self.header for x in requiredFields]) \
        and 'data' in self.header

        #TODO validate can be improved to check more than the header
        if not validFile:
            sys.exit('The required header elements are not present')

    def MakeGroupedList(self, groupingFields):

        """Returns a list of pairs. The keys of this dictionary are 
           the different elements under the groupField. Each key is
           associated with a numpy array filled with corresponding 
           entries from the data field"""

        # The indices of the group fields and data fields
        groupingIndexes = [self.header.index(x) for x in groupingFields]
        dataIndex = self.header.index('data')

        # Reduce the file to pairs of group fields and data elements 
        def groupsOnLine(line):
            return [line[x] for x in groupingIndexes]       
    
        groupDataPairs = [(groupsOnLine(line),float(line[dataIndex])) \
        for line in self.reader]

        # Bring data with same groupIDs together
        # TODO gotta be a better way in itertools for this. 

        # Sort by the first element
        sortedPairs = sorted(groupDataPairs, key = lambda x:x[0])

        # Group by the first element        
        groupedPairs = groupby(sortedPairs, lambda x:x[0])
     
        # Each last pair should simply be a list of numbers
        cleanedPairs = [(group,map(lambda x:x[-1],list(data))) \
        for (group,data) in groupedPairs]

        # Convert the data part of the pairs into a Numpy array
        return map(lambda x:(x[0],array(x[1])), cleanedPairs)
      
    def __iter__(self):
        return self

    def next(self):
        return self.reader.next()

def parseArguments():

    """Returns a map from options to arguments and handles 
    the commandline input"""

    parser = argparse.ArgumentParser(description='Process data in CSV file.')

    parser.add_argument('--data_file', \
    help='The full directory to the input file', type=str, required=True)

    parser.add_argument('--group_by', help='The grouping dimension', type=str,\
    required=True, nargs='+')

    parser.add_argument('--delimiter', \
    help='The seperator used in the CSV file.' ,\
    default=",", type=str, required=False)

    return vars(parser.parse_args())    


if __name__ == '__main__':
    # Gives map from option names to given arguments
    args = parseArguments()
    # Create the file reader
    filereader = FileReader(args['data_file'],args['delimiter'])
    # Ensure that header has at least the data and group_by fields
    filereader.ValidateFields(args['group_by'])
    # Extract data from file in a usable format
    groupedData = filereader.MakeGroupedList(args['group_by'])
    # Calculate the mean of each of each list for every group
    meanedData = map(lambda x: (x[0],mean(x[1])), groupedData)

    # Output the results
    for group in meanedData:
	print ",".join(group[0])+ "," + str(group[1])+"\n"
