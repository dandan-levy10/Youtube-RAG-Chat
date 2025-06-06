# tests/test_summary.py


# client = TestClient(app)

# def test_summary_success():
#     resp = client.post(
#         "/api/summarise/",
#         json={"video_url": "https://www.youtube.com/watch?v=pmAseUOEB_s"}
#     )
#     assert resp.status_code == 200
#     body = resp.json()
#     assert body["video_id"] == "pmAseUOEB_s"
#     assert isinstance(body["summary"], str) and len(body["summary"]) > 0

# def test_summary_bad_url():
#     resp = client.post(
#         "/api/summarise/",
#         json={"video_url": "not-a-valid-url"}
#     )
#     assert resp.status_code == 422  # Pydantic validation
