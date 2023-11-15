(howto-auth-dummy)=

# Authenticate _any_ user with a single shared password

```{warning}
The **Dummy Authenticator** lets _any_ user log in with the given password.
This authenticator is **extremely insecure**, so do not use it if you can
avoid it.
```

## Enabling the authenticator

1. Always use DummyAuthenticator with a password. You can communicate this
   password to all your users via an out of band mechanism (like writing on
   a whiteboard). Once you have selected a password, configure TLJH to use
   the password by executing the following from an admin console.

   ```bash
   sudo tljh-config set auth.DummyAuthenticator.password <password>
   ```

   Remember to replace `<password>` with the password you choose.

2. Enable the authenticator and reload config to apply configuration:

   ```bash
   sudo tljh-config set auth.type dummy
   ```

   ```bash
   sudo tljh-config reload
   ```

Users who are currently logged in will continue to be logged in. When they
log out and try to log back in, they will be asked to provide a username and
password.

## Changing the password

The password used by DummyAuthenticator can be changed with the following
commands:

```bash
tljh-config set auth.DummyAuthenticator.password <new-password>
```

```bash
tljh-config reload
```
