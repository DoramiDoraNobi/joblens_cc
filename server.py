from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import faiss
import joblib
from google.cloud import storage, firestore
import io
import tempfile

app = Flask(__name__)

# Initialize Cloud Storage and Firestore clients
storage_client = storage.Client()
firestore_client = firestore.Client()

# Load models and data directly from GCS
bucket_name = 'joblens-capstone-ml'
tfidf_model_path = 'models/tfidf_model.pkl'
svd_model_path = 'models/svd_model.pkl'
faiss_model_path = 'models/faiss_index.idx'
data_path = 'data/jobs3.csv'

def load_model_from_gcs(bucket_name, model_path):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(model_path)
    model_file = io.BytesIO()
    blob.download_to_file(model_file)
    model_file.seek(0)
    return joblib.load(model_file)

tfidf = load_model_from_gcs(bucket_name, tfidf_model_path)
svd = load_model_from_gcs(bucket_name, svd_model_path)

bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(faiss_model_path)
faiss_index_file = io.BytesIO()
blob.download_to_file(faiss_index_file)
faiss_index_file.seek(0)

with tempfile.NamedTemporaryFile() as temp_file:
    temp_file.write(faiss_index_file.read())
    temp_file.flush()
    faiss_index = faiss.read_index(temp_file.name)

blob = bucket.blob(data_path)
data_file = io.BytesIO()
blob.download_to_file(data_file)
data_file.seek(0)
df = pd.read_csv(data_file)

def get_recommendations(index, tfidf, svd, skills_input, n_recommendations=10):
    skills_tfidf = tfidf.transform([skills_input])
    skills_reduced = svd.transform(skills_tfidf)
    distances, indices = index.search(skills_reduced, n_recommendations)
    return df['job_title'].iloc[indices[0]].tolist()

@app.route('/recommend-jobs', methods=['POST'])
def recommend_jobs():
    data = request.json
    skills_input = data.get('skills')
    if not skills_input:
        return jsonify({'error': 'Skills input is required'}), 400
    
    recommended_jobs = get_recommendations(faiss_index, tfidf, svd, skills_input)
    save_results_to_firestore(skills_input, recommended_jobs)
    return jsonify({'recommended_jobs': recommended_jobs})

def save_results_to_firestore(skills_input, recommended_jobs):
    doc_ref = firestore_client.collection('job_recommendations').document()
    doc_ref.set({
        'skills': skills_input,
        'recommended_jobs': recommended_jobs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
