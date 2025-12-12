from flask import Flask, request, jsonify
import os
import math
from huggingface_hub import InferenceClient

app = Flask(__name__)

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_MODEL = os.environ.get("HF_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Normalize model id: if user passed a short name like "paraphrase-multilingual-MiniLM-L12-v2",
# prepend the `sentence-transformers/` namespace which is usually required for these models.
if HF_MODEL and "/" not in HF_MODEL:
    HF_MODEL = f"sentence-transformers/{HF_MODEL}"

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN environment variable not set. Create a token on https://huggingface.co and set HF_TOKEN.")

client = InferenceClient(api_key=HF_TOKEN)

# configure logging
import logging, traceback
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def l2_normalize(vec):
    # Ensure we operate on Python floats (not numpy.float32) so result is JSON-serializable
    s = sum(float(v) * float(v) for v in vec)
    n = math.sqrt(s) if s > 0 else 1.0
    return [float(v) / n for v in vec]

@app.route("/embed", methods=["POST"])
def embed():
    data = request.get_json(force=True) or {}
    texts = data.get("texts") or ([data.get("text")] if data.get("text") else [])
    if not texts:
        return jsonify({"error": "no text(s) provided"}), 400

    # Try primary model, if repo not found try a small fallback list of hosted models
    tried_models = []
    last_exc = None
    fallback_models = [HF_MODEL, "sentence-transformers/all-MiniLM-L6-v2", "all-mpnet-base-v2"]
    for model_id in fallback_models:
        if model_id in tried_models:
            continue
        tried_models.append(model_id)
        try:
            resp = client.feature_extraction(texts, model=model_id)
            # record which model succeeded for logs
            if model_id != HF_MODEL:
                logger.info("Fell back to model: %s", model_id)
            break
        except Exception as e:
            last_exc = e
            # If repository not found or 404, continue to next fallback; otherwise log and continue
            logger.warning("Model %s failed: %s", model_id, str(e))
            continue
    else:
        # all attempts failed
        logger.exception("All model attempts failed")
        return jsonify({"error": "HF Inference error", "details": str(last_exc)}), 502

    try:
        embeddings_norm = [l2_normalize(vec) for vec in resp]
    except Exception:
        return jsonify({"error": "invalid embedding format", "response": resp}), 502

    return jsonify(embeddings_norm)


@app.errorhandler(Exception)
def handle_exception(e):
    # Log exception with traceback and return 500 with minimal info
    tb = traceback.format_exc()
    logger.error("Unhandled exception: %s", tb)
    return jsonify({"error": "internal_server_error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))