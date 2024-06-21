from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import faiss
import joblib
from google.cloud import storage, firestore
import io
import tempfile
import requests
from datetime import datetime

# Create Flask app

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

def save_results_to_firestore(user_id, skills_input, recommended_jobs):
    timestamp = datetime.utcnow().isoformat()
    doc_id = f"{timestamp}_{user_id}_{skills_input.replace(' ', '_')}"
    doc_ref = firestore_client.collection('job_recommendations').document(doc_id)
    doc_ref.set({
        'user_id': user_id,
        'skills': skills_input,
        'recommended_jobs': recommended_jobs,
        'timestamp': timestamp
    })

AUTH_API_BASE_URL = "https://us-central1-joblens-capstone.cloudfunctions.net/auth-api"

def validate_token(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f"{AUTH_API_BASE_URL}/validate-token", headers=headers)
    return response.json()

@app.route('/recommend-jobs', methods=['POST'])
def recommend_jobs():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Token is missing'}), 401
    
    validation_response = validate_token(token.split(' ')[1])
    if validation_response['status'] != 'success':
        return jsonify({'status': 'error', 'message': 'Token is invalid or expired'}), 401

    current_user = validation_response['data']['id']

    data = request.json
    skills_input = data.get('skills')
    if not skills_input:
        return jsonify({'error': 'Skills input is required'}), 400
    
    recommended_jobs = get_recommendations(faiss_index, tfidf, svd, skills_input)
    save_results_to_firestore(current_user, skills_input, recommended_jobs)
    return jsonify({'recommended_jobs': recommended_jobs})

@app.route('/recommendation-history', methods=['GET'])
def get_recommendation_history():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Token is missing'}), 401
    
    validation_response = validate_token(token.split(' ')[1])
    if validation_response['status'] != 'success':
        return jsonify({'status': 'error', 'message': 'Token is invalid or expired'}), 401

    current_user = validation_response['data']['id']

    docs = firestore_client.collection('job_recommendations').where('user_id', '==', current_user).stream()
    history = []
    for doc in docs:
        data = doc.to_dict()
        history.append({
            'skills': data['skills'],
            'recommended_jobs': data['recommended_jobs'],
            'timestamp': data['timestamp']
        })
    return jsonify({'history': history})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
