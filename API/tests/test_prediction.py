import requests
import os

# Define the base URL for the API
BASE_URL = "http://localhost:8000" 

# Test for the prediction endpoint
def test_prediction_endpoint():
    # Define the endpoint URL
    prediction_url = f"{BASE_URL}/api/predict"
    
    # Prepare the payload with text and image
    product_description_1 = "Concepts And Case Analysis In The Law Of Contracts"
    product_description_2 = "Magic The Gathering  Sage Des Jachères   X4  Lorwyn Vf"
    image_1 = "image_1299103555_product_103817069.jpg"
    image_2 = "image_963966948_product_244966353.jpg"

    # Get paths for each test image
    image_dir = os.path.join(os.path.dirname(__file__), "test_images")
    image_path_1 = os.path.abspath(os.path.join(image_dir, image_1))
    image_path_2 = os.path.abspath(os.path.join(image_dir, image_2))


    # First request : with one description and one image
    # predict.py which defines the api/predict endpoint expects images as UploadFile objects
    with open(image_path_1, "rb") as img_file_1:
        files_1 = {"images": (image_1, img_file_1, "image/jpeg")}
        payload_1 = {"descriptions": [product_description_1]}
        
        # Send a POST request to the prediction endpoint
        response_1 = requests.post(prediction_url, data=payload_1, files=files_1)
        # Check if a prediction was returned as expected
        assert response_1.status_code == 200, f"Expected status code 200 but got {response_1.status_code}"
    

    # Second request : with two descriptions and two images
    # predict.py which defines the api/predict endpoint expects images as UploadFile objects
    with open(image_path_1, "rb") as img_file_1, open(image_path_2, "rb") as img_file_2:
        files_2 = [("images", (image_1, img_file_1, "image/jpeg")), ("images", (image_2, img_file_2, "image/jpeg"))]
        payload_2 = {"descriptions": [product_description_1, product_description_2]}
        
        # Send a POST request to the prediction endpoint
        response_2 = requests.post(prediction_url, data=payload_2, files=files_2)
        # Check if a prediction was returned as expected
        assert response_2.status_code == 200, f"Expected status code 200 but got {response_2.status_code}"
