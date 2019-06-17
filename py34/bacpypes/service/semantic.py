#!/usr/bin/env python

from ..debugging import bacpypes_debugging, ModuleLogger
from ..capability import Capability

from ..pdu import GlobalBroadcast

from ..apdu import WhoIsRequest, IAmRequest, IHaveRequest, SimpleAckPDU
from ..errors import ExecutionError, InconsistentParameters, \
    MissingRequiredParameter, ParameterOutOfRange
from ..task import FunctionTask

from .device import WhoHasIHaveServices

# some debugging
_debug = 0
_log = ModuleLogger(globals())

#
#   SemanticQuery SemanticAnswer Services
#

@bacpypes_debugging
class SemanticQueryServices(WhoHasIHaveServices): #extending WhoHasIHave to reuse i_have service.

    def __init__(self):
        if _debug: SemanticQueryServices._debug("__init__")
        Capability.__init__(self)

    def do_SemanticQueryRequest(self, apdu):
        """Respond to a Who-Has request."""
        if _debug: SemanticQueryServices._debug("do_SemanticQueryRequest, %r", apdu)

        # ignore this if there's no local device
        if not self.localDevice:
            if _debug: WhoIsIAmServices._debug("    - no local device")
            return

        # find the object
        objs = []
        if apdu.tags is not None:
            # TODO: Implement this
            pdb.set_trace()
            raise NotImplementedError("who_has with tags")
        else:
            raise InconsistentParameters("object identifier or object name required")

        # maybe we don't have it
        if not objs:
            return

        # send out the response
        for obj in objs:
            self.i_have(obj, address=apdu.pduSource)

