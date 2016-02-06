#!/usr/bin/python

# sanity tests
import api.tbed
import api.tutils
import time
import sys
import api.objmodel
import testcases.tcBasic
import testcases.tcPolicy
import testcases.tcNetwork
import testcases.tcTrigger
import testcases.tcAci
import argparse
import os
import exceptions
import traceback

# Create the parser and sub parser
parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='1.0.0')
parser.add_argument("-nodes", required=True, help="list of nodes(comma seperated)")
parser.add_argument("-iteration", default="3", help="Number of iterations")
parser.add_argument("-user", default='vagrant', help="User id for ssh")
parser.add_argument("-password", default='vagrant', help="password for ssh")
parser.add_argument("-binpath", default='/opt/gopath/bin', help="netplugin/netmaster binary path")
parser.add_argument("-containers", default='0', help="number of containers")
parser.add_argument("-short", default='false', help="do a quick run of the tests for quick validation")

# Parse the args
args = parser.parse_args()
addrList = args.nodes.split(",")

shortRun = args.short.lower()

numCntr = len(addrList) * 2
numIteration = int(args.iteration)
numTriggerTests = 6

if args.containers != '0':
    numCntr = int(args.containers)

if shortRun == "true":
    print "doing a short run"
    numCntr = len(addrList) * 2
    numIteration = 1
    numTriggerTests = 1

api.tutils.info("Running " + str(numIteration) + " iterations with " + str(numCntr) + " containers on " + str(len(addrList)) + " nodes")

try:
    # Time when test started
    startTime = time.time()

    # Setup testbed
    testbed = api.tbed.Testbed(addrList, args.user, args.password, args.binpath)

    time.sleep(15)

    testbed.chekForNetpluginErrors()

    # Run vlan tests
    testcases.tcNetwork.testAddDeleteTenant(testbed, numCntr, numIteration, encap="vlan")
    testcases.tcNetwork.testAddDeleteNetwork(testbed, (numCntr * 3), numIteration, encap="vlan")
    testcases.tcBasic.startRemoveContainer(testbed, numCntr, numIteration, encap="vlan")
    testcases.tcBasic.startStopContainer(testbed, numCntr, numIteration, encap="vlan")

    # Run policy tests. in vlan mode
    testcases.tcPolicy.testBasicPolicy(testbed, numCntr, numIteration, encap="vlan")
    testcases.tcPolicy.testPolicyAddDeleteRule(testbed, numCntr, numIteration, encap="vlan")
    testcases.tcPolicy.testPolicyFromEpg(testbed, numCntr, numIteration, encap="vlan")

    # Run vxlan tests
    testcases.tcNetwork.testAddDeleteTenant(testbed, numCntr, numIteration, encap="vxlan")
    testcases.tcNetwork.testAddDeleteNetwork(testbed, (numCntr * 3), numIteration, encap="vxlan")
    testcases.tcBasic.startRemoveContainer(testbed, numCntr, numIteration, encap="vxlan")
    testcases.tcBasic.startStopContainer(testbed, numCntr, numIteration, encap="vxlan")

    # Run policy tests. in vxlan mode
    testcases.tcPolicy.testBasicPolicy(testbed, numCntr, numIteration, encap="vxlan")
    testcases.tcPolicy.testPolicyAddDeleteRule(testbed, numCntr, numIteration, encap="vxlan")
    testcases.tcPolicy.testPolicyFromEpg(testbed, numCntr, numIteration, encap="vxlan")

    # Run multiple triggers on the Testbed
    testcases.tcTrigger.testMultiTrigger(testbed, (numIteration * numTriggerTests))

    # Run ACI mode sanity
    testcases.tcAci.testACIMode(testbed)

    # Cleanup testbed
    testbed.cleanup()

    # Calculate how long it took
    doneTime = time.time()
    elapsedTime = doneTime - startTime
    api.tutils.log("Test started at " + time.asctime(time.localtime(startTime)))
    api.tutils.log("Test ended at " + time.asctime(time.localtime(doneTime)))
    if elapsedTime > 120.0:
        api.tutils.log("Tests took " + str(elapsedTime/60) + " minutes")
    else:
        api.tutils.log("Tests took " + str(elapsedTime) + " seconds")

    api.tutils.info("Sanity passed")

except exceptions.KeyboardInterrupt:
    print "\n\n Keyboard interrupt.... Exiting\n"
    os._exit(1)

except: # catch *all* exceptions
    print "Exception: "
    traceback.print_exc()
    os._exit(1)
