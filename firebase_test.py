import time
import reviews
import firebase_admin
import threading
from google.oauth2 import service_account
from firebase_admin import credentials, firestore
import json

with open("firebase-admin-key.json") as secret:
    cred = firebase_admin.credentials.Certificate(json.load(secret))
    # secret.seek(0)
    # print(json.load(secret))
# credentials.Certificate("firebase-admin-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
batch = db.batch()

review_test_ref = db.collection('review_test').stream()


# for i in range(35):
#     for j in range(100):
#         new_doc_ref = review_test_ref.document()
#         batch.set(new_doc_ref, reviews.generate_review())
#     batch.commit()


# callback_done = threading.Event()
# def on_snapshot(snapshot, changes, read_time):
#     print("Data Changed")
#     for doc in snapshot:
#         print(f'{doc.to_dict()}')
#     callback_done.set()

# col_review = db.collection('review')
# review_watcher = col_review.on_snapshot(on_snapshot)

# while True:
#     time.sleep(0.1)

# print(db.document('review'))
# collection = db.collection('review').stream()
start = time.time_ns()
reviews = []
for doc in review_test_ref:
    reviews.append(doc.to_dict())

print((time.time_ns() - start) / 1000000000.0)