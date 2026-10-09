import io
from PIL import Image

def create_test_image():
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="green")
    image.save(file, "JPEG")
    file.seek(0)
    return file

def test_upload_invalid_extension(auth_client):
    data = {
        "leaf_image": (io.BytesIO(b"malicious script"), "hack.sh")
    }
    response = auth_client.post("/crop/detect/analyze", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"Invalid file format" in response.data

def test_upload_no_file(auth_client):
    response = auth_client.post("/crop/detect/analyze", data={}, content_type="multipart/form-data", follow_redirects=True)
    assert b"Please select a leaf photograph" in response.data

def test_upload_valid_leaf_image(auth_client):
    img = create_test_image()
    data = {
        "leaf_image": (img, "sample_leaf.jpg")
    }
    response = auth_client.post("/crop/detect/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Diagnostic Pathology Report" in response.data
    assert b"Tomato" in response.data
