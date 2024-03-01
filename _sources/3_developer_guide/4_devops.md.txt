<br>

# CI/CD

This section describes the DevOps strategy - that is, the tools and processes used to ensure efficient project delivery. This is primarily the CI/CD pipeline that runs via GitHub Actions.

<br>

## Automating Testing
Reference - `.github/workflows/CI.yml`

This workflow runs all the unit tests in `tests/` when a pull request is created and updated. This enables peers to validate that all tests pass without having to pull the code and test it locally. It also provides the added benefit of ensuring compatibility with other OS as the GitHub runner can be configured to support Windows, Linux, and MacOS.

The script first installs the external dependencies `ffmpeg` and `Tesseract` before installing the Python dependencies in `requirements.txt` and running the unit tests in `tests/`. The overall runtime is approximately 12 minutes. Refer to the below for a visual walkthrough:

```{tab} PR

Tests are run when a PR is made or changed. The green check indicates all tests have passed, a yellow circle means a run is in progress, and a red 'x' signals there is an error.

```{image} ../resources/cicd_pr.png
:align: center
```
```{tab} More details

This component appears at the bottom of a PR and shows the results of the workflow.

```{image} ../resources/cicd_tests.png
:align: center
```
```{tab} Workflow

This screen shows each step in a workflow

```{image} ../resources/cicd_workflow.png
:align: center
```
```{tab} Actions tab

This tab shows all workflows.

```{image} ../resources/cicd_actions_tab.png
:align: center
```
```{tab} Summary

If the workflow fails, it is helpful to view the `Summary` through the Actions tab to see where the error is.

```{image} ../resources/cicd_summary.png
:align: center
```

<br>

## Automating Documentation

This workflow enables the automatic updating of the [project documentation](https://hc-sc-ocdo-bdpd.github.io/file-processing-tools/) which is hosted on GitHub pages. As an overview:

1. The documentation is built into a static website in the `docs/build/html` folder via `./make html`
2. The `docs/build/html` folder is extracted and pushed to the `gh-pages` branch
3. Another workflow is automatically triggered to publish the `index.html` file to GitHub pages

In this way, a single push to the `documentation` branch is able to trigger a series of actions to ultimately update the project website.
