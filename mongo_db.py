import pymongo
from local_logger import logss as logs
def dump_feedback(data):
    try:
        client = pymongo.MongoClient("mongodb+srv://aryan:Elon2003@cluster0.obq5u.mongodb.net/?retryWrites=true&w=majority")
        logs().info("mongodb-connection %s", client)
        database = client['review_scrapper']
        collection = database['feedbacks']
        collection.insert_one(data)
        client.close()
    except Exception as e:
        logs().exception(e)


