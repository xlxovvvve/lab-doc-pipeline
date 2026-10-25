"""validator —— 产物一致性校验。"""
from .consistency import (
    ConsistencyReport,
    Mismatch,
    verify_alignment,
    verify_document_structure,
)

__all__ = [
    "ConsistencyReport",
    "Mismatch",
    "verify_alignment",
    "verify_document_structure",
]
