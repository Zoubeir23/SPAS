#!/usr/bin/env python
"""Test API predictions endpoint with ML model."""
import requests
import json

BASE_URL = 'http://localhost:8000/api'

def main():
    # Login
    resp = requests.post(f'{BASE_URL}/auth/login/', json={
        'email': 'admin@isi.edu', 
        'password': 'password123'
    })
    token = resp.json()['access']
    print('Login OK!')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check ML Models
    print('\n=== ML Models ===')
    resp = requests.get(f'{BASE_URL}/ml/models/', headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        models = data.get('results', data) if isinstance(data, dict) else data
        for m in models:
            status = m.get('status', 'unknown')
            accuracy = m.get('accuracy', 'N/A')
            print(f"  {m['name']} v{m['version']} - Status: {status}, Accuracy: {accuracy}%")
    
    # List students
    print('\n=== Students with risk scores ===')
    resp = requests.get(f'{BASE_URL}/students/', headers=headers)
    for s in resp.json()['results']:
        print(f"  {s['full_name']}: score={s['risk_score']}, level={s['risk_level']}")
    
    # Generate predictions
    print('\n=== Generate predictions ===')
    resp = requests.post(f'{BASE_URL}/predictions/predictions/generate/', headers=headers, json={})
    print(f'Status: {resp.status_code}')
    data = resp.json()
    
    if resp.status_code == 200 and 'predictions' in data:
        model_info = data.get('model_used', data.get('model_version', 'unknown'))
        print(f"Model used: {model_info}")
        print(f"Total predictions: {data.get('total_predictions', data.get('total', 0))}")
        for p in data['predictions']:
            print(f"  {p['student_name']}: score={p['risk_score']}, level={p['risk_level']}")
    else:
        print(json.dumps(data, indent=2))
    
    # Check updated students
    print('\n=== Updated students ===')
    resp = requests.get(f'{BASE_URL}/students/', headers=headers)
    for s in resp.json()['results']:
        print(f"  {s['full_name']}: score={s['risk_score']}, level={s['risk_level']}")
    
    # Check training jobs
    print('\n=== Training Jobs ===')
    resp = requests.get(f'{BASE_URL}/ml/training-jobs/', headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        jobs = data.get('results', data) if isinstance(data, dict) else data
        for j in jobs[:3]:
            print(f"  Job {j['id']}: {j['name']} - Status: {j['status']}, Algorithm: {j.get('algorithm', 'N/A')}")


if __name__ == '__main__':
    main()
