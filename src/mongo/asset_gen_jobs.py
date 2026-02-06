from src.mongo.mongo_db_client import get_collection

COLLECTION = get_collection("renderboard", "assetGenJobs")

BASE_PROJECTION = {
    "_id": 1,
    "jobId": 1,
    "createdAt": 1,
    "updatedAt": 1,
    "status": 1,
    "userId": 1,
    "modelConfig.id": 1,
    "modelConfig.name": 1,
    "modelConfig.provider": 1,
    "error.code": 1,
    "error.message": 1,
}

def fetch_jobs(
    model_ids=None,
    status=None,
    limit=None,
    projection=None,
):
    query = {}

    if model_ids:
        query["modelConfig.id"] = {"$in": model_ids}

    if status:
        query["status"] = status

    cursor = COLLECTION.find(
        query,
        projection or BASE_PROJECTION
    )

    if limit:
        cursor = cursor.limit(limit)

    return list(cursor)