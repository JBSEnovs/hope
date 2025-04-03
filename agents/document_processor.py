import os
import tempfile
import json
from typing import List, Dict, Any
import re
import shutil

class DocumentProcessor:
    """Class for processing and ingesting medical documents"""
    
    def __init__(self):
        """Initialize the document processor"""
        self.documents_dir = os.path.join(os.getcwd(), "data", "documents")
        
        # Create the directory if it doesn't exist
        os.makedirs(self.documents_dir, exist_ok=True)
        
        # Initialize the document index
        self.index_file = os.path.join(self.documents_dir, "document_index.json")
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load the document index"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.document_index = json.load(f)
            except Exception as e:
                print(f"Error loading document index: {e}")
                self.document_index = {"documents": []}
        else:
            self.document_index = {"documents": []}
            self._save_index()
    
    def _save_index(self):
        """Save the document index"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.document_index, f, indent=2)
        except Exception as e:
            print(f"Error saving document index: {e}")
    
    def process_file(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """Process a file and save it to the documents directory"""
        try:
            # Generate a unique identifier for the document
            doc_id = f"{len(self.document_index['documents']) + 1}_{file_name}"
            safe_filename = re.sub(r'[^\w\-\.]', '_', doc_id)
            doc_path = os.path.join(self.documents_dir, safe_filename)
            
            # Save the file content
            with open(doc_path, 'wb') as f:
                f.write(file_content)
            
            # Update the document index
            document_info = {
                "id": doc_id,
                "filename": file_name,
                "path": doc_path,
                "added_timestamp": str(os.path.getmtime(doc_path))
            }
            
            self.document_index["documents"].append(document_info)
            self._save_index()
            
            return {
                "success": True, 
                "document_id": doc_id,
                "path": doc_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_documents(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Simple keyword search for documents"""
        try:
            results = []
            query_terms = query.lower().split()
            
            for doc in self.document_index["documents"]:
                # Simple matching based on filename
                score = sum(1 for term in query_terms if term in doc["filename"].lower())
                
                # If filename matches, add to results
                if score > 0:
                    results.append({
                        "document_id": doc["id"],
                        "filename": doc["filename"],
                        "score": score,
                        "content": self._extract_document_preview(doc["path"])
                    })
            
            # Sort by score and limit results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:num_results]
        
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def _extract_document_preview(self, doc_path: str, max_chars: int = 500) -> str:
        """Extract a preview of the document content"""
        try:
            # For text files
            if doc_path.lower().endswith('.txt'):
                with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(max_chars)
                    return content + ("..." if len(content) >= max_chars else "")
            
            # For other files, just return a placeholder
            return f"[Document preview not available for {os.path.basename(doc_path)}]"
            
        except Exception as e:
            print(f"Error extracting document preview: {e}")
            return "[Error extracting document preview]"
    
    def get_document_sources(self) -> List[str]:
        """Get list of all document sources"""
        try:
            return [doc["filename"] for doc in self.document_index["documents"]]
        except Exception as e:
            print(f"Error getting document sources: {e}")
            return []
    
    def get_document_by_id(self, document_id: str) -> Dict[str, Any]:
        """Retrieve a document by its ID"""
        try:
            for doc in self.document_index["documents"]:
                if doc["id"] == document_id:
                    return {
                        "success": True,
                        "document": doc,
                        "preview": self._extract_document_preview(doc["path"])
                    }
            return {"success": False, "error": "Document not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document"""
        try:
            for i, doc in enumerate(self.document_index["documents"]):
                if doc["id"] == document_id:
                    # Remove file
                    if os.path.exists(doc["path"]):
                        os.remove(doc["path"])
                    
                    # Remove from index
                    removed_doc = self.document_index["documents"].pop(i)
                    self._save_index()
                    
                    return {
                        "success": True,
                        "document": removed_doc
                    }
            
            return {"success": False, "error": "Document not found"}
        except Exception as e:
            return {"success": False, "error": str(e)} 