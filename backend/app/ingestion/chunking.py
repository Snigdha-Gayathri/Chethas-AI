from __future__ import annotations
import uuid
import re

class AdaptiveChunker:
    def chunk_text(self, text: str, metadata: dict = None) -> list[dict]:
        """Chunk text respecting document structure."""
        metadata = metadata or {}
        # Simple fallback to size chunking
        return self.chunk_by_size(text, metadata=metadata)
    
    def chunk_by_headers(self, text: str, metadata: dict = None) -> list[dict]:
        """Split by markdown headers."""
        metadata = metadata or {}
        chunks = []
        sections = re.split(r"(^#+\s+.*$)", text, flags=re.MULTILINE)
        current_header = ""
        current_content = ""
        
        for part in sections:
            if re.match(r"^#+\s+", part):
                if current_content.strip():
                    chunks.append({
                        "content": current_header + "\n" + current_content.strip(),
                        "metadata": {**metadata, "header": current_header.strip()}
                    })
                current_header = part.strip()
                current_content = ""
            else:
                current_content += part
                
        if current_content.strip():
            chunks.append({
                "content": current_header + "\n" + current_content.strip(),
                "metadata": {**metadata, "header": current_header.strip()}
            })
            
        return chunks
    
    def chunk_by_size(self, text: str, chunk_size: int = 512, overlap: int = 50, metadata: dict = None) -> list[dict]:
        """Fixed-size chunking with overlap."""
        metadata = metadata or {}
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = text[start:end]
            chunks.append({
                "content": chunk_content,
                "metadata": {**metadata, "chunk_start": start, "chunk_end": end}
            })
            start += chunk_size - overlap
            
        return chunks
    
    def chunk_parent_child(self, text: str, parent_size: int = 2000, child_size: int = 400, metadata: dict = None) -> list[dict]:
        """Create parent-child chunk hierarchy."""
        metadata = metadata or {}
        chunks = []
        parent_chunks = self.chunk_by_size(text, chunk_size=parent_size, overlap=200, metadata=metadata)
        
        for p_chunk in parent_chunks:
            parent_id = str(uuid.uuid4())
            p_chunk["metadata"]["chunk_id"] = parent_id
            p_chunk["metadata"]["type"] = "parent"
            chunks.append(p_chunk)
            
            child_chunks = self.chunk_by_size(p_chunk["content"], chunk_size=child_size, overlap=50, metadata=metadata)
            for c_chunk in child_chunks:
                c_chunk["metadata"]["parent_id"] = parent_id
                c_chunk["metadata"]["type"] = "child"
                c_chunk["metadata"]["chunk_id"] = str(uuid.uuid4())
                chunks.append(c_chunk)
                
        return chunks
