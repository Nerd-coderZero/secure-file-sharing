# tests/test_files.py
from fastapi.testclient import TestClient
import pytest
import os
from app.main import app
from tests.test_auth import setup_database  # reuse the fixture

client = TestClient(app)

def get_token(user_type):
    response = client.post(
        "/auth/login",
        data={"username": f"{user_type}@example.com", "password": "password"}
    )
    return response.json()["access_token"]

def test_upload_file_ops_user():
    token = get_token("ops")
    
    # Create a test PPTX file
    with open("test.pptx", "wb") as f:
        f.write(b"test content")
    
    with open("test.pptx", "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.pptx", f, "application/vnd.openxmlformats-officedocument.presentationml.presentation")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Cleanup
    os.remove("test.pptx")
    
    assert response.status_code == 201
    assert "File uploaded successfully" in response.json()["message"]

def test_upload_file_invalid_extension():
    token = get_token("ops")
    
    # Create a test text file
    with open("test.txt", "wb") as f:
        f.write(b"test content")
    
    with open("test.txt", "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Cleanup
    os.remove("test.txt")
    
    assert response.status_code == 400
    assert "Only" in response.json()["detail"]

def test_client_cannot_upload():
    token = get_token("client")
    
    # Create a test PPTX file
    with open("test.pptx", "wb") as f:
        f.write(b"test content")
    
    with open("test.pptx", "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.pptx", f, "application/vnd.openxmlformats-officedocument.presentationml.presentation")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Cleanup
    os.remove("test.pptx")
    
    assert response.status_code == 403

def test_list_files():
    # First upload a file as ops user
    ops_token = get_token("ops")
    with open("test.docx", "wb") as f:
        f.write(b"test content")
    
    with open("test.docx", "rb") as f:
        client.post(
            "/api/upload",
            files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers={"Authorization": f"Bearer {ops_token}"}
        )
    
    # Cleanup
    os.remove("test.docx")
    
    # Now list files as client user
    client_token = get_token("client")
    response = client.get(
        "/api/files",
        headers={"Authorization": f"Bearer {client_token}"}
    )
    
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_download_link():
    # First upload a file as ops user
    ops_token = get_token("ops")
    with open("test.xlsx", "wb") as f:
        f.write(b"test content")
    
    with open("test.xlsx", "rb") as f:
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers={"Authorization": f"Bearer {ops_token}"}
        )
    
    # Cleanup
    os.remove("test.xlsx")
    
    file_id = upload_response.json()["id"]
    
    # Get download link as client user
    client_token = get_token("client")
    response = client.get(
        f"/api/download-file/{file_id}",
        headers={"Authorization": f"Bearer {client_token}"}
    )
    
    assert response.status_code == 200
    assert "download_link" in response.json()
    assert "success" in response.json()["message"]