from abc import ABC, abstractmethod
from pathlib import Path
import pypdf
import re

# 1. Interfaz Base para todos los Extractores
class BaseExtractor(ABC):
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extrae el contenido de texto del archivo dado."""
        pass

    @abstractmethod
    def extract_metadata(self, file_path: Path) -> dict:
        """Extrae metadatos básicos (autor, fecha creación, etc.)."""
        pass

# 2. Implementación Específica para PDF
class PDFExtractor(BaseExtractor):
    def _clean_text(self, text: str) -> str:
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()

    def extract_text(self, file_path: Path) -> str:
        extracted_text = []
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                raw_text = page.extract_text()
                if raw_text:
                    cleaned = self._clean_text(raw_text)
                    extracted_text.append(f"--- Página {page_num + 1} ---\n{cleaned}")
        return "\n\n".join(extracted_text)

    def extract_metadata(self, file_path: Path) -> dict:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            meta = reader.metadata
            return {
                "pages": len(reader.pages),
                "author": meta.author if meta else None,
                "title": meta.title if meta else None,
            }

# 3. Manager/Orquestador Principal
class ContentExtractionTool:
    def __init__(self):
        self._extractors = {}

    def register_extractor(self, extension: str, extractor: BaseExtractor):
        self._extractors[extension.lower()] = extractor

    def extract(self, file_path: str) -> dict:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in self._extractors:
            raise ValueError(f"Formato de archivo no soportado: {ext}")

        extractor = self._extractors[ext]
        return {
            "filename": path.name,
            "text": extractor.extract_text(path),
            "metadata": extractor.extract_metadata(path),
        }

# --- Ejemplo de uso ---
if __name__ == "__main__":
    tool = ContentExtractionTool()
    tool.register_extractor(".pdf", PDFExtractor())

    Resultado = tool.extract("../test_etc.pdf")
    print(Resultado)