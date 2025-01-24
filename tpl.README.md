<p align="center">
  <img src="src/play-store-icon.png" width="128"/>
</p>
<p align="center">
  <img alt="OS-iOS" src="https://img.shields.io/badge/iOS-gray?style=flat-square"/>
  <img alt="OS-iPadOS" src="https://img.shields.io/badge/iPadOS-gray?style=flat-square"/>
  <img alt="License" src="https://img.shields.io/github/license/petarov/google-app-ids?style=square">
</p>

# Apple Bundle IDs

Apple's Bundle IDs for native iPhone and iPad apps.

The table below shows the name and bundle ID for each native iPhone and iPad app. Bundle IDs are case sensitive.

  *  **%%APPS_COUNT%%** apps - built on %%BUILD_TIMESTAMP%% - v%%VERSION%%

| Icon | App Name | Bundle ID |
| --- | --- | --- |
%%APPS%%

# Installation

Install and update [using npm](https://github.com/petarov/apple-bundle-ids/pull/1#issuecomment-809714435):

    npm install github:petarov/apple-bundle-ids

Or just use the compiled `csv` and `json` files from `dist/`

# Contributing

The list gets auto-rebuild several times a month, so there's no need to add apps manually to this list.

If you find other issues, just open a [pull request](https://github.com/petarov/apple-bundle-ids/pulls).

# Building

Requires Python `3.x` and working Internet connection.

Run the following to install dependencies, build all `dist/` files and generate a new `README.md` file:

    ./make

# License

[MIT License](LICENSE)