import requests

from src.y2_ingest_svc import Apartment


class ApartamentImageDownloader:
    def download_all_images(self, apt: Apartment):
        id = apt['token']
        for idx, image in enumerate(apt['metadata']['images']):
            self.download_image(f"{id} - {idx}", image) #padstart

    def download_image(self, image_name, image_url, save_directory="images"):
        """Downloads an image from a URL and saves it to the specified directory."""
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            with open(f"./images/{image_name}", 'wb') as img_file:
                for chunk in response.iter_content(chunk_size=8192):
                    img_file.write(chunk)
            print(f"Image downloaded successfully")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {image_url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")