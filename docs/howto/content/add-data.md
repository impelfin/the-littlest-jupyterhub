(howto-content-add-data)=

# Adding data to the JupyterHub

This section covers how to add data to your JupyterHub either from the internet
or from your own machine. To learn how to **share data** that is already
on your JupyterHub, see [](/howto/content/share-data).

:::{note}
When you add data using the methods on this page, you will **only add it
to your user directory**. This is not a place that is accessible to others.
For information on sharing this data with users on the JupyterHub, see
[](/howto/content/share-data).
:::

## Adding data from your local machine

The easiest way to add data to your JupyterHub is to use the "Upload" user
interface. To do so, follow these steps:

1. First, navigate to the Jupyter Notebook interface home page. You can do this
   by going to the URL `<my-hub-url>/user/<my-username>/tree`.

2. Click the "Upload" button to open the file chooser window.

   ```{image} ../../images/content/upload-button.png
   :alt: The upload button in Jupyter.
   ```

3. Choose the file you wish to upload. You may select multiple files if you
   wish.

4. Click "Upload" for each file that you wish to upload.

   ```{image} ../../images/content/file-upload-buttons.png
   :alt: Multiple file upload buttons.
   ```

5. Wait for the progress bar to finish for each file. These files will now
   be on your JupyterHub, your home user's home directory.

To learn how to **share** this data with new users on the JupyterHub,
see [](/howto/content/share-data).

## Downloading data from the command line

If the data of interest is on the internet, you may also use code in order
to download it to your JupyterHub. There are several ways of doing this, so
we'll cover the simplest approach using the unix tool `wget`.

1. Log in to your JupyterHub and open a terminal window.

   ```{image} ../../images/notebook/new-terminal-button.png
   :alt: New terminal button.
   ```

2. Use `wget` to download the file to your current directory in the terminal.

   ```bash
   wget <MY-FILE-URL>
   ```

### Example: Downloading the [gapminder](https://www.gapminder.org/) dataset.

In this example we'll download the [gapminder](https://www.gapminder.org/)
dataset, which contains information about country GDP and live expectancy over
time. You can download it from your browser [at this link](https://swcarpentry.github.io/python-novice-gapminder/files/python-novice-gapminder-data.zip).

1. Log in to your JupyterHub and open a terminal window.

   ```{image} ../../images/notebook/new-terminal-button.png
   :alt: New terminal button.
   ```

2. Use `wget` to download the gapminder dataset to your current directory in
   the terminal.

   ```bash
   wget https://swcarpentry.github.io/python-novice-gapminder/files/python-novice-gapminder-data.zip
   ```

3. This is a **zip** file, so we'll need to download a unix tool called "unzip"
   in order to unzip it.

   ```bash
   sudo apt install unzip
   ```

4. Finally, unzip the file:

   ```bash
   unzip python-novice-gapminder-data.zip
   ```

5. Confirm that your data was unzipped. It could be in a folder called `data/`.

To learn how to **share** this data with new users on the JupyterHub,
see [](/howto/content/share-data).

% TODO: Downloading data with the "download" module in Python? https://github.com/choldgraf/download
