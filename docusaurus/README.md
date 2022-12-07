# Website

This website is built using [Docusaurus 2](https://docusaurus.io/), a modern static website generator.

## Installation and update

```sh
npm install
npm install @docusaurus/core@latest @docusaurus/preset-classic@latest
```

### Local Development

```sh
npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

### Build

```sh
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Deployment

```sh
GIT_USER=<Your GitHub username> USE_SSH=true npm run deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

## Search bar configuration

Local Search for Docusaurus is used to enable search indexation for the documentation. Full [documentation](https://github.com/cmfcmf/docusaurus-search-local).

```sh
npm install @cmfcmf/docusaurus-search-local
```
