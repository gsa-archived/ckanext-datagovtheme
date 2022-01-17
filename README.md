# ckanext-datagovtheme

[![CircleCI](https://circleci.com/gh/GSA/ckanext-datagovtheme.svg?style=svg)](https://circleci.com/gh/GSA/ckanext-datagovtheme)

Data.gov theme, branding, and UI customizations for
[catalog.data.gov](https://catalog.data.gov/) as a [CKAN](https://ckan.org/)
extension.


## Features

_TODO document these better._

- Provides a new spatial query view (overrides [ckanext-spatial](https://github.com/ckan/ckanext-spatial) some front end)


## Usage


### Requirements

_TODO: document how ckanext-datagovtheme interacts with third-party extensions, maybe
in the context of Features above._

These extensions are required.

- [ckanext-harvest](https://github.com/ckan/ckanext-harvest)

Additionally, ckanext-datagovtheme has "weak" dependencies on these extensions.
The dependency might be on templates, template helpers, or other functionality.

- [ckanext-archiver](https://github.com/ckan/ckanext-archiver)
- [ckanext-dcat](https://github.com/ckan/ckanext-dcat)
- [ckanext-qa](https://github.com/ckan/ckanext-qa)

This extension is compatible with these versions of CKAN.

CKAN version | Compatibility
------------ | -------------
<=2.7        | no
2.8          | yes
2.9          | [complete](https://github.com/GSA/datagov-ckan-multi/issues/567)


### Configuration

_TODO: what configuraiton options exist?_


## Development

### Requirements

- GNU Make
- Docker Compose


### Setup

Build the docker containers. You'll want to do this anytime the dependencies
change (requirements.txt, dev-requirements.txt).

    $ make build

Start the containers.

    $ make up

CKAN will start at [localhost:5000](http://localhost:5000).

Clean up the environment.

    $ make down

Open a shell to run commands in the container.

    $ docker-compose exec ckan bash

If you're unfamiliar with docker-compose, see our
[cheatsheet](https://github.com/GSA/datagov-deploy/wiki/Docker-Best-Practices#cheatsheet)
and the [official docs](https://docs.docker.com/compose/reference/).

For additional make targets, see the help.

    $ make help


### Testing

They follow the guidelines for [testing CKAN extensions](https://docs.ckan.org/en/2.8/extensions/testing-extensions.html#testing-extensions).

To run the extension tests:

    $ make test

Lint your code.

    $ make lint

#### Common issues

We have seen issues with `datagovtheme not installed`.
If this is the case, run `python setup.py develop` in the container.

### Matrix builds

The existing development environment assumes a full catalog.data.gov test setup. This makes
it difficult to develop and test against new versions of CKAN (or really any
dependency) because everything is tightly coupled and would require us to
upgrade everything at once which doesn't really work. A new make target
`test-legacy` is introduced with a new `docker-compose.legacy.yml` file in order
to run tests in the legacy docker environment.

The "new" development environment drops as many dependencies as possible. It is
not meant to have feature parity with
[GSA/catalog.data.gov](https://github.com/GSA/catalog.data.gov/) or
[GSA/inventory-app](https://github.com/GSA/inventory-app/). Tests should mock
external dependencies where possible.

In order to support multiple versions of CKAN, or even upgrade to new versions
of CKAN, we support development and testing through the `CKAN_VERSION`
environment variable.

    $ make CKAN_VERSION=2.8 test
    $ make CKAN_VERSION=2.9 test


Other docker-compose make targets work in both new and legacy environments through
the `COMPOSE_FILE` make variable. To test the legacy environment:

    $ make COMPOSE_FILE=docker-compose.legacy.yml up
    $ make COMPOSE_FILE=docker-compose.legacy.yml test-legacy

_Note: the test-legacy target only works in the legacy docker environment._

Variable | Description | Default
-------- | ----------- | -------
CKAN_VERSION | Version of CKAN to use. | 2.8
COMPOSE_FILE | docker-compose service description file. | docker-compose.yml
