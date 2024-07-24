# encoding: utf-8
import logging
import re
import datetime

import mock
import pytest

from ckanext.datagovtheme import helpers
import ckan.tests.factories as factories
import ckan.lib.helpers as h


################
# get_login_url
################


@pytest.mark.ckan_config('ckanext.saml2auth.enable_ckan_internal_login', 'false')
def test_saml2_login_url():
    """ test saml2 URL on Catalog-next """
    actual_login_url = helpers.get_login_url()
    assert '/user/saml2login' == actual_login_url


@pytest.mark.ckan_config('ckanext.saml2auth.enable_ckan_internal_login', 'true')
def test_login_url():
    """ test saml2 URL on Catalog-next """
    actual_login_url = helpers.get_login_url()
    assert '/user/login' == actual_login_url

##############
# api_doc_url
##############


@mock.patch('ckanext.datagovtheme.helpers.h')
def test_api_doc_url(mock_ckan_lib_helpers):
    mock_ckan_lib_helpers.lang.return_value = 'en'
    mock_ckan_lib_helpers.ckan_version.return_value = '2.8.7'

    api_doc_url = helpers.api_doc_url()

    assert 'https://docs.ckan.org/en/2.8/api/index.html' == api_doc_url

##################
# get_bureau_info
##################


def assert_url(actual_url, expected_bureau_code):
    # In CKAN 2.9, the url_for is returning a path ending in / which does not
    # happen in 2.8. Include an optional ending / in the path, use URL encoded
    # characters.
    bureau_url_re = re.compile('/dataset/?\\?q=bureauCode%3A%22(?P<agency_part>[0-9]{3})%3A(?P<bureau_part>[0-9]{2})%22')

    match = bureau_url_re.match(actual_url)
    assert match, 'URL should match pattern /dataset?q=bureauCode:"000:00"'

    agency_part = match.group('agency_part')
    bureau_part = match.group('bureau_part')
    assert "%s:%s" % (agency_part, bureau_part) == expected_bureau_code


def test_get_bureau_info_blm():
    bureau_code = '010:04'
    bureau_info = helpers.get_bureau_info(bureau_code)

    assert bureau_info['title'] == 'Bureau of Land Management'
    assert bureau_info['code'] == bureau_code
    assert bureau_info['logo'] == '/images/logos/010-04.png'
    assert_url(bureau_info['url'], bureau_code)


def test_get_bureau_info_logo_jpg():
    """Assert that bureau logos as jpg are found."""
    bureau_code = '418:00'
    bureau_info = helpers.get_bureau_info(bureau_code)

    assert bureau_info['title'] == 'National Endowment for the Humanities'
    assert bureau_info['code'] == bureau_code
    assert bureau_info['logo'] == '/images/logos/418-00.jpg'
    assert_url(bureau_info['url'], bureau_code)


def test_get_bureau_info_logo_missing():
    """Assert that bureaus with missing logos are still identified."""
    bureau_code = '915:00'
    bureau_info = helpers.get_bureau_info(bureau_code)

    assert bureau_info['title'] == 'Federal National Mortgage Association'
    assert bureau_info['code'] == bureau_code
    assert bureau_info['logo'] is None
    assert_url(bureau_info['url'], bureau_code)


def test_get_bureau_info_list():
    """Given a list of bureau codes, the first code is assumed."""
    bureau_code = '010:04'
    bureau_info = helpers.get_bureau_info([bureau_code, '418:00'])

    assert bureau_info['title'] == 'Bureau of Land Management'
    assert bureau_info['code'] == bureau_code
    assert bureau_info['logo'] == '/images/logos/010-04.png'
    assert_url(bureau_info['url'], bureau_code)


def test_get_bureau_info_invalid():
    """Assert None is returned and a warning is logged."""
    helpers_logger = logging.getLogger('ckanext.datagovtheme.helpers')
    with mock.patch.object(helpers_logger, 'warning') as mock_log_warning:
        bureau_info = helpers.get_bureau_info('01004')

        assert bureau_info is None
        mock_log_warning.assert_called_once_with('bureau code is invalid code=01004')


def test_get_bureau_info_none():
    """Assert None is returned"""
    bureau_info = helpers.get_bureau_info(None)

    assert bureau_info is None


##################
# ngda
##################


def test_is_tagged_ngda():
    """Assert that package with ngda tag returns true."""
    dataset_ngda = factories.Dataset(
        name="dataset-ngda", title="Dataset NGDA", tags=[{"name": "nGda"}]
    )
    dataset_non_ngda = factories.Dataset(
        name="dataset-non-ngda", title="Dataset Non NGDA", tags=[{"name": "non-ngda"}]
    )

    assert helpers.is_tagged_ngda(dataset_ngda) is True
    assert helpers.is_tagged_ngda(dataset_non_ngda) is False


##################
# recent view
##################


@pytest.fixture
def track(app):
    """Post some data to /_tracking directly.

    This simulates what's supposed when you view a page with tracking
    enabled (an ajax request posts to /_tracking).

    """

    def func(url, type_="page", ip="199.204.138.90", browser="firefox"):
        params = {"url": url, "type": type_}
        extra_environ = {
            # The tracking middleware crashes if these aren't present.
            "HTTP_USER_AGENT": browser,
            "REMOTE_ADDR": ip,
            "HTTP_ACCEPT_LANGUAGE": "en",
            "HTTP_ACCEPT_ENCODING": "gzip, deflate",
        }
        app.post("/_tracking", params=params, extra_environ=extra_environ)

    return func


def update_tracking_summary():
    """Update CKAN's tracking summary data."""

    import ckan.cli.tracking as tracking
    import ckan.model

    date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    tracking.update_all(engine=ckan.model.meta.engine, start_date=date)


def test_get_pkgs_popular_count(track):
    factories.Organization(name='myorg')
    factories.Dataset(id="view-id-1", name="view-id-1")
    factories.Dataset(id="view-id-2", name="view-id-2")
    factories.Dataset(id="view-id-3", name="view-id-3", private=True, owner_org="myorg")

    ids = "view-id-1,view-id-2,view-id-3,view-id-4"
    # before any views, all datasets should have 0 views
    # private view-id-3 and non-existent view-id-4 should not be counted
    assert helpers.get_pkgs_popular_count(ids) == {
        'view-id-1': {'recent': 0, 'total': 0},
        'view-id-2': {'recent': 0, 'total': 0}
    }

    url = h.url_for("dataset.read", id="view-id-1")
    track(url)
    update_tracking_summary()

    # after dataset 1 is viewed, it should have a view count of 1, dataset 2 should still have 0
    assert helpers.get_pkgs_popular_count(ids) == {
        'view-id-1': {'recent': 1, 'total': 1},
        'view-id-2': {'recent': 0, 'total': 0}
    }
