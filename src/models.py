"""
Data models for the API Testing Application
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Request:
    """Represents an API request."""
    
    name: str
    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    body_type: str = "none"  # none, form-data, x-www-form-urlencoded, raw
    pre_request_script: str = ""
    tests: str = ""
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "params": self.params,
            "body": self.body,
            "body_type": self.body_type,
            "pre_request_script": self.pre_request_script,
            "tests": self.tests,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Request':
        """Create request from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            method=data.get("method", "GET"),
            url=data.get("url", ""),
            headers=data.get("headers", {}),
            params=data.get("params", {}),
            body=data.get("body", ""),
            body_type=data.get("body_type", "none"),
            pre_request_script=data.get("pre_request_script", ""),
            tests=data.get("tests", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


@dataclass
class Collection:
    """Represents a collection of API requests."""
    
    name: str
    description: str = ""
    requests: List[Request] = field(default_factory=list)
    folders: List['Collection'] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_request(self, request: Request):
        """Add a request to the collection."""
        self.requests.append(request)
        self.updated_at = datetime.now().isoformat()
    
    def remove_request(self, request_id: str):
        """Remove a request from the collection."""
        self.requests = [req for req in self.requests if req.id != request_id]
        self.updated_at = datetime.now().isoformat()
    
    def get_request(self, request_id: str) -> Optional[Request]:
        """Get a request by ID."""
        for request in self.requests:
            if request.id == request_id:
                return request
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert collection to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "requests": [req.to_dict() for req in self.requests],
            "folders": [folder.to_dict() for folder in self.folders],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Collection':
        """Create collection from dictionary."""
        collection = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )
        
        # Load requests
        for req_data in data.get("requests", []):
            request = Request.from_dict(req_data)
            collection.requests.append(request)
        
        # Load folders
        for folder_data in data.get("folders", []):
            folder = Collection.from_dict(folder_data)
            collection.folders.append(folder)
        
        return collection


@dataclass
class Environment:
    """Represents an environment with variables."""
    
    name: str
    variables: Dict[str, str] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def set_variable(self, key: str, value: str):
        """Set an environment variable."""
        self.variables[key] = value
        self.updated_at = datetime.now().isoformat()
    
    def get_variable(self, key: str) -> Optional[str]:
        """Get an environment variable."""
        return self.variables.get(key)
    
    def remove_variable(self, key: str):
        """Remove an environment variable."""
        if key in self.variables:
            del self.variables[key]
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert environment to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "variables": self.variables,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Environment':
        """Create environment from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            variables=data.get("variables", {}),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


@dataclass
class Response:
    """Represents an API response."""
    
    status_code: int
    headers: Dict[str, str]
    body: str
    response_time: float
    size: int
    url: str
    method: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self.body,
            "response_time": self.response_time,
            "size": self.size,
            "url": self.url,
            "method": self.method,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """Create response from dictionary."""
        return cls(
            status_code=data.get("status_code", 0),
            headers=data.get("headers", {}),
            body=data.get("body", ""),
            response_time=data.get("response_time", 0.0),
            size=data.get("size", 0),
            url=data.get("url", ""),
            method=data.get("method", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        ) 