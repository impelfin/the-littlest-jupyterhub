The **User Environment** is a conda environment that is shared by all users
in the JupyterHub. Libraries installed in this environment are immediately
available to all users. Admin users can install packages in this environment
with `sudo -E`.

1. Log in as an admin user and open a Terminal in your Jupyter Notebook.

   ```{image} ../images/notebook/new-terminal-button.png
   :alt: New Terminal button under New menu
   ```

2. Install [gdal](https://anaconda.org/conda-forge/gdal) from [conda-forge](https://conda-forge.org/).

   ```bash
   sudo -E conda install -c conda-forge gdal
   ```

   The `sudo -E` is very important!

3. Install [there](https://pypi.org/project/there) with `pip`

   ```bash
   sudo -E pip install there
   ```

The packages `gdal` and `there` are now available to all users in JupyterHub.
If a user already had a python notebook running, they have to restart their notebook's
kernel to make the new libraries available.

See [](#howto/user-env/user-environment) for more information.
