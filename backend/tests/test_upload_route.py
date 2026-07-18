"""
Tests for the upload route.
"""

from fastapi.testclient import TestClient
from app.main import app


def test_upload_route_exists():
    """Test that the upload route exists and is accessible."""
    client = TestClient(app)
    # We won't actually upload a file in this basic test
    # just check that the route exists
    response = client.post("/api/upload")
    # Should return 422 (Unprocessable Entity) because no file was sent
    assert response.status_code == 422


if __name__ == "__main__":
    test_upload_route_exists()
    print("Upload route test passed!")