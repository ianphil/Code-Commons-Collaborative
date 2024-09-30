import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize

# Download the required tokenizer models
nltk.download('punkt')  # Download the sentence tokenizer
nltk.download('punkt_tab')

# Method to load and preprocess the book text
def load_and_preprocess_book(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        book_text = f.read()

    # Split the text into paragraphs
    book_paragraphs = book_text.split('\n\n')  # Split on double newlines
    # Clean up each paragraph
    book_paragraphs = [para.replace('\n', ' ').strip() for para in book_paragraphs if len(para.strip().split()) > 5]
    return book_paragraphs

# Method to generate embeddings using Sentence-BERT
def generate_embeddings(sentences, model_name='all-mpnet-base-v2'):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences, convert_to_tensor=True)
    return np.array([embedding.cpu().numpy() for embedding in embeddings])

# Method to initialize FAISS and add embeddings
def initialize_faiss_index(embeddings):
    dimension = embeddings.shape[1]  # Dimensionality of embeddings
    index = faiss.IndexFlatL2(dimension)  # Use L2 distance
    index.add(embeddings)  # Add the embeddings to the index
    return index

# Method to query the FAISS index
def search_faiss_index(index, query, model, sentences, top_k=5):
    query_embedding = model.encode([query], convert_to_tensor=True).cpu().numpy()
    distances, indices = index.search(np.array(query_embedding), top_k * 2)  # Get more results to filter duplicates
    
    # Remove duplicates and limit to top_k results
    seen = set()
    results = []
    for idx in indices[0]:
        sentence = sentences[idx]
        if sentence not in seen:
            seen.add(sentence)
            results.append(sentence)
        if len(results) == top_k:
            break
    return results

# Main function to run the process
def main():
    # Load and preprocess the book
    file_path = "books/A Christmas Carol in Prose Being a Ghost Story of Christmas by Charles Dickens 534 - 46.txt"
    book_paragraphs = load_and_preprocess_book(file_path)
    
    # Generate embeddings
    embeddings = generate_embeddings(book_paragraphs)
    
    # Initialize and populate FAISS index
    index = initialize_faiss_index(embeddings)
    
    # Example query
    model = SentenceTransformer('all-mpnet-base-v2')  # Load the same model used for embeddings
    query = "What is Scrooge's view on Christmas?"
    results = search_faiss_index(index, query, model, book_paragraphs)
    
    # Print the results
    print("Top results for the query:")
    for result in results:
        print(result)
        print('---')

if __name__ == "__main__":
    main()
