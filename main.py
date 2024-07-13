import pickle
import math
from googleapiclient.discovery import build, BatchHttpRequest
from googleapiclient.errors import HttpError

# Load credentials from token.pickle
with open('token.pickle', 'rb') as token:
    credentials = pickle.load(token)

def callback(request_id, response, exception):
    if exception:
        print(f'An error occurred: {exception}')
    else:
        print(f'Deleted: {request_id}')

try:
    # Build the Drive service
    service = build('drive', 'v3', credentials=credentials)

    # Specify the shared drive ID
    shared_drive_id = 'your-shared-drive-id'

    # List all files and folders in the shared drive
    results = service.files().list(
        corpora='drive',
        driveId=shared_drive_id,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        q=f"'{shared_drive_id}' in parents",
        pageSize=1000,
        fields="files(id, name)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        batch_size = 100  # Set the batch size to a reasonable limit (e.g., 100)
        num_batches = math.ceil(len(items) / batch_size)

        for i in range(num_batches):
            batch = service.new_batch_http_request(callback=callback)
            start_index = i * batch_size
            end_index = min(start_index + batch_size, len(items))
            for item in items[start_index:end_index]:
                batch.add(service.files().delete(fileId=item['id'], supportsAllDrives=True))
            batch.execute()

except Exception as e:
    print(f'An error occurred: {e}')
