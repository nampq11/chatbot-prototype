import json 
from enum import Enum
from typing import List
from pymongo import MongoClient
from src.app.agent.workflow.chains import get_chat_model
from src.config import settings

class KnowledgeGraph:
    def __init__(self, documents: List[str]):
        self.documents = documents
        self.nodes = []
        self.edges = []
        