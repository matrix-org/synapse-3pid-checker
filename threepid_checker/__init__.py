# Copyright 2022 The Matrix.org Foundation C.I.C.
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

from typing import Any, Dict

import attr
from synapse.module_api import ModuleApi
from synapse.module_api.errors import ConfigError


@attr.s(auto_attribs=True, frozen=True)
class ThreepidCheckerConfig:
    url: str
    only_check_at_registration: bool = False


class ThreepidChecker:
    def __init__(self, config: ThreepidCheckerConfig, api: ModuleApi):
        # Keep a reference to the config and Module API
        self._api = api
        self._config = config

        self._http_client = api.http_client

        self._api.register_password_auth_provider_callbacks(
            is_3pid_allowed=self.check_if_allowed,
        )

    @staticmethod
    def parse_config(config: Dict[str, Any]) -> ThreepidCheckerConfig:
        """Checks that required config options are in the correct format and parses them
        into a ThreepidCheckerConfig.

        Args:
            config: The raw configuration dict.

        Returns:
            The parsed configuration.
        """
        if "url" not in config:
            raise ConfigError('"url" is a required configuration parameter')

        if not isinstance(config["url"], str) or not config["url"].startswith("http"):
            raise ConfigError('"url" needs to be an HTTP(S) URL')

        return ThreepidCheckerConfig(**config)

    async def check_if_allowed(
        self, medium: str, address: str, registration: bool
    ) -> bool:
        """Sends an HTTP(s) request to the configured URL and check if the data it
        responds with allows the given 3PID to be associated with a local account.

        Note that this function does not check if an error is raised by the HTTP client.
        The idea is that Synapse will catch that error, log it and fail the user's
        request, which is what we want anyway.

        Args:
            medium: The 3PID's medium.
            address: The 3PID's address.
            registration: Whether the check is happening while registering a new user.

        Returns:
            Whether the 3PID can register.
        """
        if registration is False and self._config.only_check_at_registration is True:
            # TODO: test
            return True

        data = await self._http_client.get_json(
            self._config.url,
            {"medium": medium, "address": address},
        )

        # Check for invalid response
        if "hs" not in data:
            return False

        # Check if this 3PID can be associated on this homeserver
        if data.get("hs") != self._api.server_name:
            return False

        if data.get("requires_invite", False) and not data.get("invited", False):
            # Requires an invite but hasn't been invited
            return False

        return True
