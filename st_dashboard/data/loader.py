import pandas as pd
import streamlit as st

from src.mongo.mongo_db_client import get_collection
from st_dashboard.data.transforms import enrich_dataframe

DB_NAME = "renderboard"
COLLECTION_NAME = "assetGenJobs"

BASE_PROJECTION = {
    "_id": 1,
    "jobId": 1,
    "userId": 1,
    "createdAt": 1,
    "updatedAt": 1,
    "status": 1,
    "modelConfig.id": 1,
    "modelConfig.name": 1,
    "modelConfig.modelTitle": 1,
    "modelConfig.modelType": 1,
    "modelConfig.outputType": 1,
    "modelConfig.provider": 1,
    "modelConfig.inputs": 1,
    "modelConfig.costConfig.defaultCost": 1,
    "modelConfig.costConfig.rules": 1,
    "modelConfig.modelMetaData.openAIModelId": 1,
    "qualityAnalysis.score": 1,
    "qualityAnalysis.rewrittenPrompt": 1,
    "qualityAnalysis.reasoning": 1,
    "qualityAnalysis.transformedScore": 1,
    "qualityAnalysis.qualityCheckStatus": 1,
    "resultDownloadedAt": 1,
    "error.code": 1,
    "error.message": 1,
}


@st.cache_resource
def get_collection_cached():
    return get_collection(DB_NAME, COLLECTION_NAME)


@st.cache_data(ttl=900)
def load_raw_data(query=None):
    collection = get_collection_cached()
    query = query or {}
    cursor = collection.find(query, BASE_PROJECTION, max_time_ms=10000)
    df = pd.json_normalize(cursor)
    return df


@st.cache_data(ttl=900)
def load_data(query=None):
    df = load_raw_data(query=query)
    if df.empty:
        return df
    return enrich_dataframe(df)
