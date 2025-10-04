import os, uuid
from dotenv import load_dotenv
from llama_cloud.client import LlamaCloud
from llama_cloud.core.api_error import ApiError

load_dotenv()
client = LlamaCloud(token=os.environ["LLAMA_CLOUD_API_KEY"])

def list_names():
    try:
        items = client.pipelines.list_pipelines()  # adjust if method differs
        return [p.name for p in items]
    except Exception as e:
        print("List failed:", e)
        return []

existing = set(list_names())
base_name = os.getenv("HYBRID_PIPELINE_NAME", "my-hybrid-pipeline")
name = base_name if base_name not in existing else f"{base_name}-{uuid.uuid4().hex[:8]}"
print("Using pipeline name:", name)

req = {
    "name": name,
    "sparse_model_config": {"model_type": "splade"},
}

try:
    pipeline = client.pipelines.upsert_pipeline(request=req)
    print("Upsert OK. ID:", pipeline.id)
except ApiError as e:
    print("ApiError:", e)
    try:
        print("Body:", e.body)
    except Exception:
        pass
