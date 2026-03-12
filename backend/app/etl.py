import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os

# Initialize ChromaDB
# Persist data to 'chroma_db' folder
CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), "../chroma_db")
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

# Use a lightweight local embedding model
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="claims_collection",
    embedding_function=sentence_transformer_ef
)

def run_etl():
    data_path = os.path.join(os.path.dirname(__file__), "../data/claims_full.csv")
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    print("Loading data...")
    df = pd.read_csv(data_path)
    
    # Prepare documents and metadata
    documents = []
    metadatas = []
    ids = []
    
    print(f"Processing {len(df)} records...")
    
    for index, row in df.iterrows():
        # Create a rich text representation for embedding
        # This "chunk" contains all key info so the semantic search can find it
        diagnosis_name = row.get('diagnosis_name', '') if hasattr(row, 'get') else ''
        diagnosis_text = f"{row['diagnosis_code']}"
        if pd.notna(diagnosis_name) and str(diagnosis_name).strip():
            diagnosis_text += f" ({diagnosis_name})"

        text_chunk = (
            f"Claim ID: {row['claim_id']}. "
            f"Patient: {row['patient_name']} (ID: {row['patient_id']}, DOB: {row['dob']}). "
            f"Provider: {row['provider_name']} ({row['specialty']}). "
            f"Date: {row['claim_date']}. "
            f"Status: {row['status']}. "
            f"Amount: ${row['amount']}. "
            f"Diagnosis: {diagnosis_text}. "
        )
        
        if row['status'] == 'Denied':
            text_chunk += f"Denial Reason: {row['denial_reason']}."
            
        documents.append(text_chunk)
        
        # Store structured data in metadata for filtering/retrieval if needed
        metadatas.append({
            "claim_id": row['claim_id'],
            "patient_id": row['patient_id'],
            "provider_id": row['provider_id'],
            "status": row['status'],
            "date": row['claim_date'],
            "amount": float(row['amount']),
            "diagnosis_code": row['diagnosis_code'],
            "diagnosis_name": str(diagnosis_name) if pd.notna(diagnosis_name) else "",
            "denial_reason": row['denial_reason'] if 'denial_reason' in row else "",
        })
        
        ids.append(row['claim_id'])
        
    # Add to collection in batches to avoid memory issues
    batch_size = 500
    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        print(f"Indexing batch {i} to {end}...")
        collection.upsert(
            documents=documents[i:end],
            metadatas=metadatas[i:end],
            ids=ids[i:end]
        )
        
    print("ETL Complete. Data indexed in ChromaDB.")

if __name__ == "__main__":
    run_etl()
