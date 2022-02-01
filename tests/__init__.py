from typing import Any, Dict, Optional

from mock import Mock
from synapse.module_api import ModuleApi

from threepid_checker import ThreepidChecker


class Addresses:
    """Known addresses for tests."""

    NO_HS = "nohs@test"
    WRONG_HS = "wronghs@test"
    REQUIRES_INVITE_MISSING = "rimissing@test"
    NO_INVITE_NEEDED = "dontinvite@test"
    INVITED_MISSING = "invitedmissing@test"
    NOT_INVITED = "notinvited@test"
    INVITED = "invited@test"
    INVITED_NOT_REQUIRED = "invitednotrequired@test"


class MockHttpClient:
    async def get_json(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mocks the get_json method of Synapse's HTTP client.

        Args:
            url: The URL to query. We're ignoring it for tests.
            params: The parameters for the request.

        Returns:
            A dict which content depends on the 3PID address passed in the parameters.

        Raises:
            RuntimeError if the provided address isn't known.
        """
        address = params["address"]
        if address == Addresses.NO_HS:
            return {}
        elif address == Addresses.WRONG_HS:
            return {"hs": "othertest"}
        elif address == Addresses.REQUIRES_INVITE_MISSING:
            return {"hs": "test"}
        elif address == Addresses.NO_INVITE_NEEDED:
            return {"hs": "test", "requires_invite": False}
        elif address == Addresses.INVITED_MISSING:
            return {"hs": "test", "requires_invite": True}
        elif address == Addresses.NOT_INVITED:
            return {"hs": "test", "requires_invite": True, "invited": False}
        elif address == Addresses.INVITED:
            return {"hs": "test", "requires_invite": True, "invited": True}

        raise RuntimeError("Unknown address provided in test")


def create_module(config_override: Dict[str, Any] = {}) -> ThreepidChecker:
    # Create a mock based on the ModuleApi spec, but override some mocked functions
    # because some capabilities are needed for running the tests.
    module_api = Mock(spec=ModuleApi)
    module_api.http_client = MockHttpClient()
    module_api.server_name = "test"

    config_override.setdefault("url", "http://foo")
    config = ThreepidChecker.parse_config(config_override)

    return ThreepidChecker(config, module_api)
