from mock_ingest import parse_mock_posts

result = parse_mock_posts()
print(f"Ingested {result['ingested']} posts, skipped {result['skipped']}")
