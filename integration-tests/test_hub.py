import asyncio
import grp
import pwd
import secrets
import subprocess
from functools import partial
from os import system

import pytest
import requests
from hubtraf.auth.dummy import login_dummy
from hubtraf.user import User
from jupyterhub.utils import exponential_backoff
from packaging.version import Version as V

from tljh.normalize import generate_system_username

# Use sudo to invoke it, since this is how users invoke it.
# This catches issues with PATH
TLJH_CONFIG_PATH = ["sudo", "tljh-config"]

# This *must* be localhost, not an IP
# aiohttp throws away cookies if we are connecting to an IP!
HUB_URL = "http://localhost"


def test_hub_up():
    r = requests.get(HUB_URL)
    r.raise_for_status()


def test_hub_version():
    r = requests.get(HUB_URL + "/hub/api")
    r.raise_for_status()
    info = r.json()
    assert V("4") <= V(info["version"]) <= V("5")


async def test_user_code_execute():
    """
    User logs in, starts a server & executes code
    """
    username = secrets.token_hex(8)

    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "auth.type", "dummy"
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
        ).wait()
    )

    async with User(username, HUB_URL, partial(login_dummy, password="")) as u:
        assert await u.login()
        await u.ensure_server_simulate(timeout=60, spawn_refresh_time=5)
        await u.start_kernel()
        await u.assert_code_output("5 * 4", "20", 5, 5)


async def test_user_server_started_with_custom_base_url():
    """
    User logs in, starts a server with a custom base_url & executes code
    """
    # This *must* be localhost, not an IP
    # aiohttp throws away cookies if we are connecting to an IP!
    base_url = "/custom-base"
    custom_hub_url = f"{HUB_URL}{base_url}"
    username = secrets.token_hex(8)

    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "auth.type", "dummy"
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "base_url", base_url
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
        ).wait()
    )

    async with User(username, custom_hub_url, partial(login_dummy, password="")) as u:
        assert await u.login()
        await u.ensure_server_simulate(timeout=60, spawn_refresh_time=5)

        # unset base_url to avoid problems with other tests
        assert (
            0
            == await (
                await asyncio.create_subprocess_exec(
                    *TLJH_CONFIG_PATH, "unset", "base_url"
                )
            ).wait()
        )
        assert (
            0
            == await (
                await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
            ).wait()
        )


async def test_user_admin_add():
    """
    User is made an admin, logs in and we check if they are in admin group
    """
    # This *must* be localhost, not an IP
    # aiohttp throws away cookies if we are connecting to an IP!
    username = secrets.token_hex(8)

    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "auth.type", "dummy"
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "add-item", "users.admin", username
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
        ).wait()
    )

    async with User(username, HUB_URL, partial(login_dummy, password="")) as u:
        assert await u.login()
        await u.ensure_server_simulate(timeout=60, spawn_refresh_time=5)

        # Assert that the user exists
        assert pwd.getpwnam(f"jupyter-{username}") is not None

        # Assert that the user has admin rights
        assert f"jupyter-{username}" in grp.getgrnam("jupyterhub-admins").gr_mem


async def test_long_username():
    """
    User with a long name logs in, and we check if their name is properly truncated.
    """
    username = secrets.token_hex(32)

    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "auth.type", "dummy"
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
        ).wait()
    )

    try:
        async with User(username, HUB_URL, partial(login_dummy, password="")) as u:
            assert await u.login()
            await u.ensure_server_simulate(timeout=60, spawn_refresh_time=5)

            # Assert that the user exists
            system_username = generate_system_username(f"jupyter-{username}")
            assert pwd.getpwnam(system_username) is not None

            await u.stop_server()
    except:
        # If we have any errors, print jupyterhub logs before exiting
        subprocess.check_call(["journalctl", "-u", "jupyterhub", "--no-pager"])
        raise


async def test_user_group_adding():
    """
    User logs in, and we check if they are added to the specified group.
    """
    # This *must* be localhost, not an IP
    # aiohttp throws away cookies if we are connecting to an IP!
    username = secrets.token_hex(8)
    groups = {"somegroup": [username]}
    # Create the group we want to add the user to
    system("groupadd somegroup")

    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "auth.type", "dummy"
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH,
                "add-item",
                "users.extra_user_groups.somegroup",
                username,
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
        ).wait()
    )

    try:
        async with User(username, HUB_URL, partial(login_dummy, password="")) as u:
            assert await u.login()
            await u.ensure_server_simulate(timeout=60, spawn_refresh_time=5)

            # Assert that the user exists
            system_username = generate_system_username(f"jupyter-{username}")
            assert pwd.getpwnam(system_username) is not None

            # Assert that the user was added to the specified group
            assert f"jupyter-{username}" in grp.getgrnam("somegroup").gr_mem

            await u.stop_server()
            # Delete the group
            system("groupdel somegroup")
    except:
        # If we have any errors, print jupyterhub logs before exiting
        subprocess.check_call(["journalctl", "-u", "jupyterhub", "--no-pager"])
        raise


async def test_idle_server_culled():
    """
    User logs in, starts a server & stays idle for a while.
    (the user's server should be culled during this period)
    """
    username = secrets.token_hex(8)

    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "auth.type", "dummy"
            )
        ).wait()
    )
    # Check every 5s for idle servers to cull
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "services.cull.every", "5"
            )
        ).wait()
    )
    # Apart from servers, also cull users
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "services.cull.users", "True"
            )
        ).wait()
    )
    # Cull servers and users after a while, regardless of activity
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "services.cull.max_age", "15"
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
        ).wait()
    )

    async with User(username, HUB_URL, partial(login_dummy, password="")) as u:
        # Login the user
        assert await u.login()

        # Start user's server
        await u.ensure_server_simulate(timeout=60, spawn_refresh_time=5)
        # Assert that the user exists
        assert pwd.getpwnam(f"jupyter-{username}") is not None

        # Check that we can get to the user's server
        user_url = u.notebook_url / "api/status"
        r = await u.session.get(user_url, allow_redirects=False)
        assert r.status == 200

        # Extract the xsrf token from the _xsrf cookie set after visiting
        # /hub/login with the u.session
        hub_cookie = u.session.cookie_jar.filter_cookies(
            str(u.hub_url / "hub/api/user")
        )
        assert "_xsrf" in hub_cookie
        hub_xsrf_token = hub_cookie["_xsrf"].value

        # Check that we can talk to JupyterHub itself
        # use this as a proxy for whether the user still exists
        async def hub_api_request():
            r = await u.session.get(
                u.hub_url / "hub/api/user",
                headers={
                    # Referer is needed for JupyterHub <=3
                    "Referer": str(u.hub_url / "hub/"),
                    # X-XSRFToken is needed for JupyterHub >=4
                    "X-XSRFToken": hub_xsrf_token,
                },
                allow_redirects=False,
            )
            return r

        r = await hub_api_request()
        assert r.status == 200

        # Wait for culling
        # step 1: check if the server is still running
        timeout = 30

        async def server_stopped():
            """Has the server been stopped?"""
            r = await u.session.get(user_url, allow_redirects=False)
            print(f"{r.status} {r.url}")
            return r.status != 200

        await exponential_backoff(
            server_stopped,
            "Server still running!",
            timeout=timeout,
        )

        # step 2. wait for user to be deleted
        async def user_removed():
            # Check that after a while, the user has been culled
            r = await hub_api_request()
            print(f"{r.status} {r.url}")
            return r.status == 403

        await exponential_backoff(
            user_removed,
            "User still exists!",
            timeout=timeout,
        )


async def test_active_server_not_culled():
    """
    User logs in, starts a server & stays idle for a while
    (the user's server should not be culled during this period).
    """
    # This *must* be localhost, not an IP
    # aiohttp throws away cookies if we are connecting to an IP!
    username = secrets.token_hex(8)

    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "auth.type", "dummy"
            )
        ).wait()
    )
    # Check every 5s for idle servers to cull
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "services.cull.every", "5"
            )
        ).wait()
    )
    # Apart from servers, also cull users
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "services.cull.users", "True"
            )
        ).wait()
    )
    # Cull servers and users after a while, regardless of activity
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(
                *TLJH_CONFIG_PATH, "set", "services.cull.max_age", "30"
            )
        ).wait()
    )
    assert (
        0
        == await (
            await asyncio.create_subprocess_exec(*TLJH_CONFIG_PATH, "reload")
        ).wait()
    )

    async with User(username, HUB_URL, partial(login_dummy, password="")) as u:
        assert await u.login()
        # Start user's server
        await u.ensure_server_simulate(timeout=60, spawn_refresh_time=5)
        # Assert that the user exists
        assert pwd.getpwnam(f"jupyter-{username}") is not None

        # Check that we can get to the user's server
        user_url = u.notebook_url / "api/status"
        r = await u.session.get(user_url, allow_redirects=False)
        assert r.status == 200

        async def server_has_stopped():
            # Check that after a while, we can still reach the user's server
            r = await u.session.get(user_url, allow_redirects=False)
            print(f"{r.status} {r.url}")
            return r.status != 200

        try:
            await exponential_backoff(
                server_has_stopped,
                "User's server is still reachable (good!)",
                timeout=15,
            )
        except asyncio.TimeoutError:
            # timeout error means the test passed - the server didn't go away while we were waiting
            pass
        else:
            pytest.fail(f"Server at {user_url} got culled prematurely!")
