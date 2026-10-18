"""Escape untrusted document text before adding the generator's own markup."""
from html import escape

def escape_document_data(value):
    if isinstance(value,str): return escape(value,quote=False)
    if isinstance(value,list): return [escape_document_data(item) for item in value]
    if isinstance(value,dict): return {key:escape_document_data(item) for key,item in value.items()}
    return value
