from __future__ import print_function

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import cv2
import time 
import os.path

# Scope needed to upload files
SCOPES = ['https://www.googleapis.com/auth/drive.file']

 

def get_drive_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "autonex_drive.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def upload_frame_to_drive(frame, file_name="frame.jpg"):
    # Save frame temporarily
    temp_path = "temp_frame.jpg"
    cv2.imwrite(temp_path, frame)

    service = get_drive_service()

    file_metadata = {"name": file_name}
    media = MediaFileUpload(temp_path, resumable=True)

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print("Uploaded Frame. File ID:", uploaded_file.get("id"))

    # Optional: delete after upload
    os.remove(temp_path)
def main():
    # Your RTSP URL
    rtsp_url = "rtsp://username:password@camera-ip-address:554/stream"

    # Open the RTSP stream
    cap = cv2.VideoCapture(0)

    i=0
    
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame.")
            break

        # Display the frame
        # cv2.imshow("RTSP Stream", frame)

        # Press 'q' to quit
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        i+=1
        upload_frame_to_drive(frame,f"frame_{i}.jpg")
        time.sleep(5)
    cap.release()
    cv2.destroyAllWindows()
    


if __name__ == "__main__":
    main()
