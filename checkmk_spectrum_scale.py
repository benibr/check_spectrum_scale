#!/usr/bin/env python3
import argparse
import sys
import os
import subprocess
import re
import csv

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3


class CheckResult:
    """Simple storage class for return values of the script"""

    def __init__(self, returnCode=None, serviceName=None, returnMessage=None, metrics=None, longOutput=None):

        if returnCode is None:
            self.returnCode = STATE_UNKNOWN
        else:
            self.returnCode = returnCode

        if serviceName is None:
            self.serviceName = "UNKNOWN"
        else:
            self.serviceName = serviceName

        if returnMessage is None:
            self.returnMessage = "UNKNOWN"
        else:
            self.returnMessage = returnMessage

        if metrics is None:
            self.metrics = None
        else:
            self.metrics = metrics

        if longOutput is None:
            self.longOutput = None
        else:
            self.longOutput = longOutput

    def printMonitoringOutput(self):
        """
        Concatenate full message and print it, then exit with returnCode     

        Error:
            Prints unknown state if the all variables in the instance are default.
        """
        returnText = f"{self.returnCode} \"{self.serviceName}\""
        if self.metrics is not None:
            returnText = returnText + " " + self.metrics
        else:
            returnText = returnText + " - "
        returnText = returnText + " " + self.returnMessage
        if self.longOutput is not None:
            returnText = returnText + " " + self.longOutput

        print(returnText)
        sys.exit(self.returnCode)


def getRowByFields(table, criteria):
    for row in table:
        if set(criteria.items()).issubset(row.items()):
            return row


def executeBashCommand(command):
    """
    Args:
        command    -    command to execute in bash

    Return:
        Returned string from command
    """
    print(f"running command '{command}'", file=sys.stderr)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, universal_newlines=True)
    return str(process.communicate()[0])


def checkRequirements():
    """
    Check if following tools are installed on the system:
        -IBM Spectrum Scale
    """

    if not (os.path.isdir("/usr/lpp/mmfs/bin/") and os.path.isfile("/usr/lpp/mmfs/bin/mmhealth")):
        checkResult = CheckResult()
        checkResult.returnCode = STATE_CRITICAL
        checkResult.returnMessage = "CRITICAL - No IBM Spectrum Scale Installation detected."
        checkResult.printMonitoringOutput()


def checkHealth(args):
    checkResult = CheckResult()
    checkResult.serviceName = "Spectrum Scale Node Health"

    output = executeBashCommand("/usr/lpp/mmfs/bin/mmhealth node show -Y")
    stateOutput = (row for row in output.split("\n") if row.startswith("mmhealth:State:"))

    table = csv.DictReader(stateOutput, delimiter=":")
    criteria = {"component": "NODE", "entitytype": "NODE"}
    row = getRowByFields(table, criteria)

    state = row["status"]

    if not ((state == "HEALTHY") or (state == "TIPS")):
        checkResult.returnCode = STATE_CRITICAL
        checkResult.returnMessage = "CRITICAL: Node is in state 'str(state)'"
    else:
        checkResult.returnCode = STATE_OK
        checkResult.returnMessage = f"OK: Node is in state '{str(state)}'"
    checkResult.printMonitoringOutput()


def argumentParser():
    """
    Parse the arguments from the command line
    """
    parser = argparse.ArgumentParser(description='Check heath of the GPFS node')

    subParser = parser.add_subparsers()
    statusParser = subParser.add_parser('health', help='Check the health on a node')
    statusParser.add_argument('-w', '--warning', dest='warning', action='store',
                              help='Warning if online nodes below this value (default=5)', default=5)
    statusParser.add_argument('-c', '--critical', dest='critical', action='store',
                              help='Critical if online nodes below this value (default=3)', default=3)
    statusParser.add_argument('-L', '--Long', dest='longOutput', action='store_true',
                              help='Displaies additional informations in the long output', default=False)
    statusParser.add_argument('-n', '--node', dest='node', action='store_true',
                              help='Check state of the nodes', default=os.getenv('HOSTNAME'))
    return parser


if __name__ == '__main__':
    parser = argumentParser()
    args = parser.parse_args()
    checkRequirements()
    checkHealth(args)
