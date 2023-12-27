from datetime import datetime, timedelta
import pytest

from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews import settings


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Новый текст комментария'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    return comment


@pytest.fixture
def pk_for_args(news):
    return news.pk,


@pytest.fixture
def comment_pk_for_args(comment):
    return comment.pk,


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Just text',
            date=today - timedelta(days=index)
            )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def url_news_home():
    return reverse('news:home')


@pytest.fixture
def several_comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Text {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment_form_data():
    return {
        'text': COMMENT_TEXT
    }


@pytest.fixture
def new_comment_data():
    return {
        'text': NEW_COMMENT_TEXT
    }