import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name, args',
        (
            ('news:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
            ('news:detail', pytest.lazy_fixture('pk_for_args'))
        )
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
        ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_pk_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_pk_for_args'))
    )
)
def test_pages_availability_for_different_users(
    parametrized_client, name, expected_status, args
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_pk_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_pk_for_args'))
    )
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
