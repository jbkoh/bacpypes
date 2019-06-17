#!/usr/bin/env python
import pdb

"""
This application presents a 'console' prompt to the user asking for Who-Is and I-Am
commands which create the related APDUs, then lines up the corresponding I-Am
for incoming traffic and prints out the contents.
"""

import sys

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.consolecmd import ConsoleCmd

from bacpypes.core import run, enable_sleeping

from bacpypes.pdu import Address, GlobalBroadcast, LocalBroadcast
from bacpypes.apdu import WhoIsRequest, IAmRequest, WhoHasRequest, SemanticQueryRequest
from bacpypes.primitivedata import CharacterString
from bacpypes.basetypes import ServicesSupported, NameValue
from bacpypes.errors import DecodingError

from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.apdu import WhoHasObject, IHaveRequest
from bacpypes.service.semantic import SemanticQueryServices
from bacpypes.constructeddata import Array, ArrayOf

# some debugging
_debug = 1
_log = ModuleLogger(globals())

# globals
this_device = None
this_application = None


@bacpypes_debugging
class WhoHasIHaveApplication(BIPSimpleApplication):

    def __init__(self, *args):
        if _debug: WhoHasIHaveApplication._debug("__init__ %r", args)
        BIPSimpleApplication.__init__(self, *args)

        # keep track of requests to line up responses
        self._request = None

    def request(self, apdu):
        if _debug: WhoHasIHaveApplication._debug("request %r", apdu)

        # save a copy of the request
        self._request = apdu

        # forward it along
        BIPSimpleApplication.request(self, apdu)

    def confirmation(self, apdu):
        if _debug: WhoHasIHaveApplication._debug("confirmation %r", apdu)

        # forward it along
        BIPSimpleApplication.confirmation(self, apdu)

    def indication(self, apdu):
        if _debug: WhoHasIHaveApplication._debug("indication %r", apdu)

        if (isinstance(self._request, WhoIsRequest)) and (isinstance(apdu, IAmRequest)):
            device_type, device_instance = apdu.iAmDeviceIdentifier
            if device_type != 'device':
                raise DecodingError("invalid object type")

            if (self._request.deviceInstanceRangeLowLimit is not None) and \
                (device_instance < self._request.deviceInstanceRangeLowLimit):
                pass
            elif (self._request.deviceInstanceRangeHighLimit is not None) and \
                (device_instance > self._request.deviceInstanceRangeHighLimit):
                pass
            else:
                # print out the contents
                sys.stdout.write('pduSource = ' + repr(apdu.pduSource) + '\n')
                sys.stdout.write('iAmDeviceIdentifier = ' + str(apdu.iAmDeviceIdentifier) + '\n')
                sys.stdout.write('maxAPDULengthAccepted = ' + str(apdu.maxAPDULengthAccepted) + '\n')
                sys.stdout.write('segmentationSupported = ' + str(apdu.segmentationSupported) + '\n')
                sys.stdout.write('vendorID = ' + str(apdu.vendorID) + '\n')
                sys.stdout.flush()
        elif isinstance(self._request, SemanticQueryRequest) and isinstance(apdu, IHaveRequest):
            sys.stdout.write('pduSource = ' + repr(apdu.pduSource) + '\n')
            sys.stdout.write('deviceIdentifier' + repr(apdu.deviceIdentifier) + '\n')
            sys.stdout.write('objectIdentifier' + repr(apdu.objectIdentifier) + '\n')
            sys.stdout.write('objectName' + repr(apdu.objectName) + '\n')
            sys.stdout.flush()


        # forward it along
        BIPSimpleApplication.indication(self, apdu)


#
#   WhoHasIHaveConsoleCmd
#

@bacpypes_debugging
class WhoHasIHaveConsoleCmd(ConsoleCmd):

    def do_semantic(self, args):
        """semantic [ <addr> ] """
        args = args.split()
        if _debug: WhoHasIHaveConsoleCmd._debug("do_semantic %r", args)

        tags = ArrayOf(NameValue)([
            NameValue(name=CharacterString('a'),
                      value=CharacterString('temperature_sensor')), # NOTE: Hardcode the tags for now.
            #NameValue(name=CharacterString('a'),
            #          value=CharacterString('temperature_setpoint')), # NOTE: Hardcode the tags for now.
        ])
        request = SemanticQueryRequest(
            tags = tags,
        )
        if len(args) > 0:
            request.pduDestination = Address(args[0])
            del args[0]
        else:
            request.pduDestination = LocalBroadcast()

        # away it goes
        this_application.request(request)


def main():
    global this_device
    global this_application

    # parse the command line arguments
    args = ConfigArgumentParser(description=__doc__).parse_args()

    if _debug: _log.debug("initialization")
    if _debug: _log.debug("    - args: %r", args)

    # make a device object
    this_device = LocalDeviceObject(
        objectName=args.ini.objectname,
        objectIdentifier=int(args.ini.objectidentifier),
        maxApduLengthAccepted=int(args.ini.maxapdulengthaccepted),
        segmentationSupported=args.ini.segmentationsupported,
        vendorIdentifier=int(args.ini.vendoridentifier),
        )

    # make a simple application
    this_application = WhoHasIHaveApplication(this_device, args.ini.address)
    this_application.add_capability(SemanticQueryServices)

    # make a console
    this_console = WhoHasIHaveConsoleCmd()
    if _debug: _log.debug("    - this_console: %r", this_console)

    # enable sleeping will help with threads
    enable_sleeping()

    _log.debug("running")

    run()

    _log.debug("fini")

if __name__ == "__main__":
    main()
