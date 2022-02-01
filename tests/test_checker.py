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

import aiounittest
from synapse.module_api.errors import ConfigError

from tests import Addresses, create_module


class ThreepidCheckerTestCase(aiounittest.AsyncTestCase):
    async def test_no_hs(self) -> None:
        """Tests that the 3PID cannot register if the endpoint responds without a
        homeserver name.
        """
        await self._test_check_if_allowed(Addresses.NO_HS, False)

    async def test_wrong_hs(self) -> None:
        """Tests that the 3PID cannot register if the endpoint responds with the wrong
        homeserver name.
        """
        await self._test_check_if_allowed(Addresses.WRONG_HS, False)

    async def test_requires_invite_missing(self) -> None:
        """Tests that the 3PID can register if the endpoint responds without a
        "requires_invite" parameter (since it defaults to false).
        """
        await self._test_check_if_allowed(Addresses.REQUIRES_INVITE_MISSING, True)

    async def test_no_invite_needed(self) -> None:
        """Tests that the 3PID can register if no invite is needed."""
        await self._test_check_if_allowed(Addresses.NO_INVITE_NEEDED, True)

    async def test_invited_missing(self) -> None:
        """Tests that the 3PID cannot register if the endpoint responds without an
        "invited" parameter (since it defaults to false) and "requires_invite" is true.
        """
        await self._test_check_if_allowed(Addresses.INVITED_MISSING, False)

    async def test_not_invited(self) -> None:
        """Tests that the 3PID cannot register if the endpoint responds without a pending
        invite and "requires_invite" is true.
        """
        await self._test_check_if_allowed(Addresses.NOT_INVITED, False)

    async def test_invited(self) -> None:
        """Tests that the 3PID can register if the endpoint responds with a pending invite
        and "requires_invite" is true.
        """
        await self._test_check_if_allowed(Addresses.INVITED, True)

    async def test_not_invited_registration(self) -> None:
        """Tests that a 3PID that shouldn't be allowed to be associated with a local
        account is only correctly blocked during user registration if the
        "only_check_at_registration" configuration flag is set to true.
        """
        # While registering.
        await self._test_check_if_allowed(
            address=Addresses.NOT_INVITED,
            expected_result=False,
            only_registration=True,
            registration=True,
        )
        # Not in a user registration.
        await self._test_check_if_allowed(
            address=Addresses.NOT_INVITED,
            expected_result=True,
            only_registration=True,
            registration=False,
        )

    async def _test_check_if_allowed(
        self,
        address: str,
        expected_result: bool,
        only_registration: bool = False,
        registration: bool = False,
    ) -> None:
        """Calls the "check_if_allowed" callback on a new instance of the module and
        compare its return value with the expected result.
        """
        config = {"only_check_at_registration": only_registration}
        module = create_module(config)
        res = await module.check_if_allowed("email", address, registration)
        self.assertEqual(res, expected_result)

    async def test_config_missing_url(self) -> None:
        """Tests that the module raises an error if configured without a URL."""
        with self.assertRaises(ConfigError):
            create_module({"url": None})

    async def test_config_url_bad_type(self) -> None:
        """Tests that the module raises an error if configured with a URL that's not a
        string.
        """
        with self.assertRaises(ConfigError):
            create_module({"url": 1})

    async def test_config_url_not_http(self) -> None:
        """Tests that the module raises an error if configured with a URL that's not an
        HTTP(S) URL.
        """
        with self.assertRaises(ConfigError):
            create_module({"url": "ftp://foo"})

    async def test_config_good_url(self) -> None:
        """Tests that the module can be initialised with an HTTP(S) URL."""
        create_module({"url": "http://foo"})
