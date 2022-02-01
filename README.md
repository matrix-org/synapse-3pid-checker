# 3PID checker for Synapse

A module that checks whether a 3PID (email address, phone number) can be allowed to be
registered on the local homeserver by querying a remote backend.

## Installation

From the virtual environment that you use for Synapse, install this module with:
```shell
pip install path/to/synapse-3pid-checker
```
(If you run into issues, you may need to upgrade `pip` first, e.g. by running
`pip install --upgrade pip`)

Then alter your homeserver configuration, adding to your `modules` configuration:
```yaml
modules:
  - module: threepid_checker.ThreepidChecker
    config:
      # The URL to send requests to when checking if a 3PID can be registered. See below
      # for more information.
      # Required.
      url: https://foo/bar
```

The configured URL will be hit by a `GET` HTTP request, with 2 parameters to qualify the 3PID:

* `medium`: The 3PID's medium (`email` for an email address, `msisdn` for a phone number)
* `address`: The 3PID's address

The server at that URL is expected to respond with a JSON object that contains the following keys:

* `hs` (string): Required. The name of the homeserver the 3PID is allowed to be registered
                 on. The 3PID will be denied if this is absent from the response's body.
* `requires_invite` (bool): Optional. Whether an invite is required for this 3PID to register 
                            on this homeserver. What qualifies as an invite is left to the
                            server serving the configured URL to define. Defaults to `false`.
* `invited` (bool): Optional. Whether there is a pending invite for the 3PID. Defaults to `false`.

The module will deny the 3PID's registration based on the response if:

* `hs` does not match the homeserver's configured server name, or is missing, or
* `requires_invite` is `true` and `invited` is `false` or missing

The 3PID will be allowed to register otherwise.


## Development

In a virtual environment with pip ≥ 21.1, run
```shell
pip install -e .[dev]
```

To run the unit tests, you can either use:
```shell
tox -e py
```
or
```shell
trial tests
```

To run the linters and `mypy` type checker, use `./scripts-dev/lint.sh`.


## Releasing

The exact steps for releasing will vary; but this is an approach taken by the
Synapse developers (assuming a Unix-like shell):

 1. Set a shell variable to the version you are releasing (this just makes
    subsequent steps easier):
    ```shell
    version=X.Y.Z
    ```

 2. Update `setup.cfg` so that the `version` is correct.

 3. Stage the changed files and commit.
    ```shell
    git add -u
    git commit -m v$version -n
    ```

 4. Push your changes.
    ```shell
    git push
    ```

 5. When ready, create a signed tag for the release:
    ```shell
    git tag -s v$version
    ```
    Base the tag message on the changelog.

 6. Push the tag.
    ```shell
    git push origin tag v$version
    ```

 7. Create a source distribution and upload it to PyPI:
    ```shell
    python -m build
    twine upload dist/threepid_checker-$version*
    ```
