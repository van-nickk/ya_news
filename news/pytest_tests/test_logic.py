from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse


from news.models import Comment, News
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, comment_form_data, pk_for_args
):
    url = reverse('news:detail', args=pk_for_args)
    client.post(url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client, comment_form_data, pk_for_args
):
    url = reverse('news:detail', args=pk_for_args)
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comment_count = Comment.objects.count()
    assert comment_count == 0


@pytest.mark.usefixtures('comment')
@pytest.mark.django_db
def test_author_can_delete_comment(author_client, pk_for_args):
    url = reverse('news:delete', args=pk_for_args)
    news_url = reverse('news:detail', args=pk_for_args)
    response = author_client.post(url)
    assertRedirects(response, news_url + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.usefixtures('comment')
@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, pk_for_args):
    url = reverse('news:delete', args=pk_for_args)
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, pk_for_args, new_comment_data, comment
):
    url = reverse('news:edit', args=pk_for_args)
    response = author_client.post(url, data=new_comment_data)
    news_url = reverse('news:detail', args=pk_for_args)
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == new_comment_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
     reader_client, pk_for_args, new_comment_data, comment
):
    url = reverse('news:edit', args=pk_for_args)
    old_comment_text = comment.text
    response = reader_client.post(url, data=new_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment_text
