def test_view(db, client, django_assert_num_queries):
    with django_assert_num_queries(13):
        response = client.get('')
        assert response.status_code == 200
