This directory contains the sources of the Zing website and content pages.
Note the documentation contents are read from the _docs/_ directory one level
above.


## Developing

In order to work on the website or doc contents and preview the results, you can
fire up the development server with:

```shell
npm start
```

Then open a web browser in the hostname and port indicated in the console
output. This allows live-previewing any types of changes as they are performed.


## Publishing

This step is not automated via CI yet. In the meantime, the following command
builds and publishes the static pages to GitHub pages.

```shell
GIT_USER=<your-gh-username> USE_SSH=true npm run publish-gh-pages
```
