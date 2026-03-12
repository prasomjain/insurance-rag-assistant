import pandas as pd
import random
from faker import Faker
import os
from datetime import datetime, timedelta

fake = Faker()

DIAGNOSES = [
    ("E11.9", "Type 2 diabetes mellitus without complications"),
    ("E10.9", "Type 1 diabetes mellitus without complications"),
    ("I10", "Essential primary hypertension"),
    ("J45.909", "Unspecified asthma uncomplicated"),
    ("M54.50", "Low back pain unspecified"),
    ("E78.5", "Hyperlipidemia unspecified"),
    ("F41.9", "Anxiety disorder unspecified"),
    ("K21.9", "Gastro-esophageal reflux disease without esophagitis"),
    ("G43.909", "Migraine unspecified not intractable without status migrainosus"),
    ("L20.9", "Atopic dermatitis unspecified"),
    ("N39.0", "Urinary tract infection site not specified"),
    ("M17.11", "Unilateral primary osteoarthritis right knee"),
]

def generate_data(num_claims=2000):
    print(f"Generating {num_claims} claims...")
    
    # 1. Generate Doctors/Providers
    specialties = ['Cardiology', 'Orthopedics', 'Pediatrics', 'Dermatology', 'Neurology', 'General Practice']
    doctors = []
    for _ in range(50):
        doctors.append({
            'provider_id': fake.uuid4(),
            'provider_name': f"Dr. {fake.last_name()}",
            'specialty': random.choice(specialties)
        })
    df_doctors = pd.DataFrame(doctors)
    
    # 2. Generate Patients
    patients = []
    for _ in range(200):
        patients.append({
            'patient_id': fake.uuid4(),
            'patient_name': fake.name(),
            'dob': fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            'gender': random.choice(['M', 'F'])
        })
    df_patients = pd.DataFrame(patients)
    
    # 3. Generate Claims
    claims = []
    statuses = ['Approved', 'Denied', 'Pending']
    denial_reasons = [
        'Medical Necessity Not Met',
        'Prior Authorization Missing',
        'Duplicate Claim',
        'Out of Network Provider',
        'Coding Error',
        'Policy Terminated'
    ]
    
    start_date = datetime.now() - timedelta(days=365)
    
    for _ in range(num_claims):
        doctor = random.choice(doctors)
        patient = random.choice(patients)
        status = random.choice(statuses)
        diagnosis_code, diagnosis_name = random.choice(DIAGNOSES)
        
        claim_date = fake.date_between(start_date=start_date, end_date='today')
        amount = round(random.uniform(100, 5000), 2)
        
        denial_reason = None
        if status == 'Denied':
            denial_reason = random.choice(denial_reasons)
            
        claims.append({
            'claim_id': f"CLM-{10000 + _}",
            'patient_id': patient['patient_id'],
            'provider_id': doctor['provider_id'],
            'claim_date': claim_date.isoformat(),
            'diagnosis_code': diagnosis_code,
            'diagnosis_name': diagnosis_name,
            'procedure_code': fake.bothify(text='#####'),
            'amount': amount,
            'status': status,
            'denial_reason': denial_reason if denial_reason else ''
        })
        
    df_claims = pd.DataFrame(claims)
    
    # Merge for a denormalized view (easier for RAG text generation)
    df_full = df_claims.merge(df_patients, on='patient_id').merge(df_doctors, on='provider_id')
    
    output_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(output_dir, exist_ok=True)
    
    df_full.to_csv(os.path.join(output_dir, 'claims_full.csv'), index=False)
    print(f"Data generated at {output_dir}/claims_full.csv")

if __name__ == "__main__":
    generate_data()
