import time
import threading
from google.cloud import firestore
import json

with open("firebase_key.json") as secret:
    # cred = credentials.Certificate(json.load(secret))
    cred = json.load(secret)
# firebase_admin.initialize_app(cred)
db = firestore.Client.from_service_account_info(cred)
reviews = db.collection('review_test')
callback_done = threading.Event()
def on_snapshot(snapshot, changes, read_time):
    print("Data Changed")
    for change in changes:
        print(change.document.id)
    # for doc in snapshot:
    #     print(f'{doc.to_dict()}')
    callback_done.set()
reviews_watch = reviews.on_snapshot(on_snapshot)

while True:
    print("blablabla")
    time.sleep(0.1)

# for i in range(35):
#     for j in range(100):
#         new_doc_ref = review_test_ref.document()
#         batch.set(new_doc_ref, review_gen.generate_review())
#     batch.commit()




# while True:
#     time.sleep(0.1)

# print(db.document('review'))
# collection = db.collection('review').stream()
# start = time.time_ns()
# reviews = []
# for doc in review_test_ref:
#     reviews.append(doc.to_dict())

# print((time.time_ns() - start) / 1000000000.0)