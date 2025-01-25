<p align="center">
  <img src="%%LOGO_PATH%%app-store.png" width="128"/>
</p>
<p align="center">
  <img alt="OS-iOS" src="https://img.shields.io/badge/iOS-gray?style=flat-square"/>
  <img alt="OS-iPadOS" src="https://img.shields.io/badge/iPadOS-gray?style=flat-square"/>
  <img alt="License" src="https://img.shields.io/github/license/petarov/google-app-ids?style=square">
</p>

# Apple Bundle IDs

Apple's Bundle IDs for native iPhone and iPad apps. The table below shows the name and bundle ID for each native iPhone and iPad app. Bundle IDs are case sensitive.

This list is updated automatically twice a month, but only if changes on Apple's Bundle IDs website are detected.

**%%APPS_COUNT%%** apps - v%%VERSION%% built on %%BUILD_TIMESTAMP%%

%%L10N_LINKS%%

| Icon | App Name | Bundle ID |
| --- | --- | --- |
%%APPS%%

# Installation

Install and update NPM:

    npm install github:petarov/apple-bundle-ids

Or just use the compiled `csv` and `json` files from `dist/`

# Contributing

The list gets auto-rebuilt 2 times a month, so there's no need to add apps manually to it.

If you find other issues, just open a [pull request](https://github.com/petarov/apple-bundle-ids/pulls).

# Building

Requires Python `3.x` and working Internet connection.

Run the following to install dependencies, build all `dist/` files and generate all `README.md` translations:

    ./make

After first generating the files, the script will not regenerate anything if no updates are found on Apple's
website. To force delete the `build.lock` file generated on first run.

# License

[MIT License](LICENSE)