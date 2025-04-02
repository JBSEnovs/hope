import os
import tempfile
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class DocumentProcessor:
    """Class for processing and ingesting medical documents"""
    
    def __init__(self, api_key=None):
        """Initialize the document processor"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings(api_key=self.api_key)
        self.db_directory = os.path.join(os.getcwd(), "chroma_db")
        
        # Create the directory if it doesn't exist
        os.makedirs(self.db_directory, exist_ok=True)
        
        # Initialize or load the vector store
        self.vector_store = self._initialize_vector_store()
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150
        )
    
    def _initialize_vector_store(self) -> Chroma:
        """Initialize or load the vector store"""
        try:
            return Chroma(
                persist_directory=self.db_directory,
                embedding_function=self.embeddings
            )
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            # If loading fails, create a new one
            return Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.db_directory
            )
    
    def process_file(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """Process a file and add it to the vector store"""
        try:
            # Create a temporary file to store the content
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Load documents based on file type
            if file_name.lower().endswith('.pdf'):
                loader = PyPDFLoader(temp_path)
            elif file_name.lower().endswith('.docx'):
                loader = Docx2txtLoader(temp_path)
            elif file_name.lower().endswith('.txt'):
                loader = TextLoader(temp_path)
            else:
                os.unlink(temp_path)
                return {"success": False, "error": "Unsupported file format"}
            
            # Load and split the document
            documents = loader.load()
            chunks = self.text_splitter.split_documents(documents)
            
            # Add metadata to track the source
            for chunk in chunks:
                if not chunk.metadata:
                    chunk.metadata = {}
                chunk.metadata["source"] = file_name
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            self.vector_store.persist()
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return {
                "success": True, 
                "document_id": file_name,
                "chunks": len(chunks)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_documents(self, query: str, num_results: int = 5) -> List[Document]:
        """Search for documents relevant to a query"""
        try:
            return self.vector_store.similarity_search(query, k=num_results)
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_sources(self) -> List[str]:
        """Get list of all document sources in the vector store"""
        try:
            # This is a simple approach - in a real implementation, you'd want
            # to query the underlying database more efficiently
            all_docs = self.vector_store.get()
            sources = set()
            if all_docs and 'metadatas' in all_docs:
                for metadata in all_docs['metadatas']:
                    if metadata and 'source' in metadata:
                        sources.add(metadata['source'])
            return list(sources)
        except Exception as e:
            print(f"Error getting document sources: {e}")
            return [] 