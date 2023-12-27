from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


User = get_user_model()


class TestHomePage(TestCase):

    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        today = datetime.today()
        all_news = [
            News(title=f'Новость {index}',
                 text='Just text',
                 date=today - timedelta(days=index)
                 )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)

    def test_news_count(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_cout = len(object_list)
        self.assertEqual(news_cout, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_sorted(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title='Test news', text='Just text'
        )
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Commentator')
        now = timezone.now()
        for index in range(2):
            comment = Comment.objects.create(
                news=cls.news, author=cls.author, text=f'Text {index}',
            )
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comment_order(self):
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        self.assertLess(all_comments[0].created, all_comments[1].created)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
