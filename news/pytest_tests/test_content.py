import pytest

from django.urls import reverse

from yanews import settings


@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
def test_news_count(admin_client, url_news_home):
    response = admin_client.get(url_news_home)
    object_list = response.context['object_list']
    news_cout = len(object_list)
    assert news_cout == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
def test_news_sorted(admin_client, url_news_home):
    response = admin_client.get(url_news_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('several_comments')
@pytest.mark.django_db
def test_comment_order(admin_client, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    response = admin_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_user, form_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
@pytest.mark.django_db
def test_pages_contain_form(parametrized_user, form_in_list, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    response = parametrized_user.get(url)
    assert ('form' in response.context) is form_in_list
