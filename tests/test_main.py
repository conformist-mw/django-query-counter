def test_view(db, client, django_assert_num_queries):
    with django_assert_num_queries(13):
        response = client.get('')
        assert response.status_code == 200


def test_view_with_decorator(
    db, client, django_assert_num_queries, capsys, settings,
):
    settings.INSTALLED_APPS.append('query_counter')
    settings.MIDDLEWARE.append('query_counter.middleware.DjangoQueryCounterMiddleware')

    with django_assert_num_queries(13):
        response = client.get('')
        assert response.status_code == 200

    out, err = capsys.readouterr()
    assert 'Duplicate queries:' in out
    assert 'Target: / urls.index' in out


def test_dqc_enabled_false_suppresses_output(
    db, client, django_assert_num_queries, capsys, settings,
):
    settings.INSTALLED_APPS.append('query_counter')
    settings.MIDDLEWARE.append('query_counter.middleware.DjangoQueryCounterMiddleware')
    settings.DQC_ENABLED = False

    with django_assert_num_queries(13):
        response = client.get('')
        assert response.status_code == 200

    out, err = capsys.readouterr()
    assert out == ''
