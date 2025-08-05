"""
Unit tests for the postman_importer module.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from src.postman_importer import PostmanImporter
from src.models import Collection, Request, Environment


class TestPostmanImporter(unittest.TestCase):
    """Test cases for the PostmanImporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_collection_data = {
            "info": {
                "name": "Test Collection",
                "description": "A test collection"
            },
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "url": {
                            "raw": "https://api.example.com/test",
                            "host": ["api", "example", "com"],
                            "path": ["test"]
                        }
                    },
                    "response": []
                },
                {
                    "name": "Test Folder",
                    "item": [
                        {
                            "name": "Nested Request",
                            "request": {
                                "method": "POST",
                                "header": [],
                                "body": {
                                    "mode": "raw",
                                    "raw": '{"key": "value"}'
                                },
                                "url": {
                                    "raw": "https://api.example.com/post"
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        self.sample_environment_data = {
            "id": "test-env-id",
            "name": "Test Environment",
            "values": [
                {"key": "API_URL", "value": "https://api.example.com", "enabled": True},
                {"key": "API_KEY", "value": "test-key-123", "enabled": True},
                {"key": "DISABLED_VAR", "value": "disabled-value", "enabled": False}
            ]
        }
        
        self.sample_workspace_data = {
            "collections": [self.sample_collection_data],
            "environments": [self.sample_environment_data]
        }
    
    def test_import_collection_postman_format(self):
        """Test importing a Postman collection format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_collection_data, f)
            file_path = f.name
        
        try:
            collections = PostmanImporter.import_collection(file_path)
            
            self.assertEqual(len(collections), 1)
            collection = collections[0]
            
            self.assertEqual(collection.name, "Test Collection")
            self.assertEqual(collection.description, "A test collection")
            self.assertEqual(len(collection.requests), 1)
            self.assertEqual(len(collection.folders), 1)
            
            # Check main request
            request = collection.requests[0]
            self.assertEqual(request.name, "Test Request")
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.url, "https://api.example.com/test")
            self.assertEqual(request.headers["Content-Type"], "application/json")
            
            # Check folder
            folder = collection.folders[0]
            self.assertEqual(folder.name, "Test Folder")
            self.assertEqual(len(folder.requests), 1)
            
            # Check nested request
            nested_request = folder.requests[0]
            self.assertEqual(nested_request.name, "Nested Request")
            self.assertEqual(nested_request.method, "POST")
            self.assertEqual(nested_request.url, "https://api.example.com/post")
            self.assertEqual(nested_request.body, '{"key": "value"}')
            
        finally:
            os.unlink(file_path)
    
    def test_import_collection_internal_format(self):
        """Test importing our internal collection format."""
        internal_collection_data = {
            "name": "Internal Collection",
            "description": "Internal format collection",
            "requests": [
                {
                    "name": "Internal Request",
                    "method": "PUT",
                    "url": "https://api.example.com/put",
                    "headers": {"Authorization": "Bearer token"},
                    "params": {},
                    "body": "",
                    "body_type": "raw",
                    "pre_request_script": "",
                    "tests": ""
                }
            ],
            "folders": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(internal_collection_data, f)
            file_path = f.name
        
        try:
            collections = PostmanImporter.import_collection(file_path)
            
            self.assertEqual(len(collections), 1)
            collection = collections[0]
            
            self.assertEqual(collection.name, "Internal Collection")
            self.assertEqual(collection.description, "Internal format collection")
            self.assertEqual(len(collection.requests), 1)
            
            request = collection.requests[0]
            self.assertEqual(request.name, "Internal Request")
            self.assertEqual(request.method, "PUT")
            self.assertEqual(request.url, "https://api.example.com/put")
            self.assertEqual(request.headers["Authorization"], "Bearer token")
            
        finally:
            os.unlink(file_path)
    
    def test_import_environment_postman_format(self):
        """Test importing a Postman environment format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_environment_data, f)
            file_path = f.name
        
        try:
            environments = PostmanImporter.import_environment(file_path)
            
            self.assertEqual(len(environments), 1)
            environment = environments[0]
            
            self.assertEqual(environment.name, "Test Environment")
            self.assertEqual(len(environment.variables), 2)  # Only enabled variables
            self.assertEqual(environment.variables["API_URL"], "https://api.example.com")
            self.assertEqual(environment.variables["API_KEY"], "test-key-123")
            self.assertNotIn("DISABLED_VAR", environment.variables)
            
        finally:
            os.unlink(file_path)
    
    def test_import_environment_internal_format(self):
        """Test importing our internal environment format."""
        internal_environment_data = {
            "name": "Internal Environment",
            "variables": {
                "INTERNAL_VAR": "internal-value",
                "ANOTHER_VAR": "another-value"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(internal_environment_data, f)
            file_path = f.name
        
        try:
            environments = PostmanImporter.import_environment(file_path)
            
            self.assertEqual(len(environments), 1)
            environment = environments[0]
            
            self.assertEqual(environment.name, "Internal Environment")
            self.assertEqual(len(environment.variables), 2)
            self.assertEqual(environment.variables["INTERNAL_VAR"], "internal-value")
            self.assertEqual(environment.variables["ANOTHER_VAR"], "another-value")
            
        finally:
            os.unlink(file_path)
    
    def test_import_file_collection(self):
        """Test importing a file that contains a collection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_collection_data, f)
            file_path = f.name
        
        try:
            collections, environments = PostmanImporter.import_file(file_path)
            
            self.assertEqual(len(collections), 1)
            self.assertEqual(len(environments), 0)
            
            collection = collections[0]
            self.assertEqual(collection.name, "Test Collection")
            
        finally:
            os.unlink(file_path)
    
    def test_import_file_environment(self):
        """Test importing a file that contains an environment."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_environment_data, f)
            file_path = f.name
        
        try:
            collections, environments = PostmanImporter.import_file(file_path)
            
            self.assertEqual(len(collections), 0)
            self.assertEqual(len(environments), 1)
            
            environment = environments[0]
            self.assertEqual(environment.name, "Test Environment")
            
        finally:
            os.unlink(file_path)
    
    def test_import_file_workspace(self):
        """Test importing a workspace file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_workspace_data, f)
            file_path = f.name
        
        try:
            collections, environments = PostmanImporter.import_file(file_path)
            
            self.assertEqual(len(collections), 1)
            self.assertEqual(len(environments), 1)
            
            collection = collections[0]
            environment = environments[0]
            
            self.assertEqual(collection.name, "Test Collection")
            self.assertEqual(environment.name, "Test Environment")
            
        finally:
            os.unlink(file_path)
    
    def test_import_file_error_handling(self):
        """Test error handling when importing invalid files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            file_path = f.name
        
        try:
            with self.assertRaises(Exception):
                PostmanImporter.import_file(file_path)
        finally:
            os.unlink(file_path)
    
    def test_import_file_nonexistent(self):
        """Test importing a nonexistent file."""
        with self.assertRaises(Exception):
            PostmanImporter.import_file("nonexistent_file.json")
    
    def test_process_items(self):
        """Test processing Postman items."""
        items = [
            {
                "name": "Test Request",
                "request": {
                    "method": "GET",
                    "url": {"raw": "https://api.example.com/test"}
                }
            },
            {
                "name": "Test Folder",
                "item": [
                    {
                        "name": "Nested Request",
                        "request": {
                            "method": "POST",
                            "url": {"raw": "https://api.example.com/post"}
                        }
                    }
                ]
            }
        ]
        
        collection = Collection("Test Collection")
        PostmanImporter._process_items(items, collection)
        
        self.assertEqual(len(collection.requests), 1)
        self.assertEqual(len(collection.folders), 1)
        
        request = collection.requests[0]
        self.assertEqual(request.name, "Test Request")
        self.assertEqual(request.method, "GET")
        
        folder = collection.folders[0]
        self.assertEqual(folder.name, "Test Folder")
        self.assertEqual(len(folder.requests), 1)
        
        nested_request = folder.requests[0]
        self.assertEqual(nested_request.name, "Nested Request")
        self.assertEqual(nested_request.method, "POST")
    
    def test_create_request_from_item(self):
        """Test creating a request from a Postman item."""
        item = {
            "name": "Test Request",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"},
                    {"key": "Authorization", "value": "Bearer token"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": '{"key": "value"}'
                },
                "url": {
                    "raw": "https://api.example.com/test",
                    "query": [
                        {"key": "param1", "value": "value1"}
                    ]
                }
            }
        }
        
        request = PostmanImporter._create_request_from_item(item)
        
        self.assertEqual(request.name, "Test Request")
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.url, "https://api.example.com/test")
        self.assertEqual(request.headers["Content-Type"], "application/json")
        self.assertEqual(request.headers["Authorization"], "Bearer token")
        self.assertEqual(request.params["param1"], "value1")
        self.assertEqual(request.body, '{"key": "value"}')
    
    def test_create_request_from_item_minimal(self):
        """Test creating a request from a minimal Postman item."""
        item = {
            "name": "Minimal Request",
            "request": {
                "method": "GET",
                "url": {"raw": "https://api.example.com/minimal"}
            }
        }
        
        request = PostmanImporter._create_request_from_item(item)
        
        self.assertEqual(request.name, "Minimal Request")
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.url, "https://api.example.com/minimal")
        self.assertEqual(request.headers, {})
        self.assertEqual(request.params, {})
        self.assertEqual(request.body, "")
    
    def test_create_folder_from_item(self):
        """Test creating a folder from a Postman item."""
        item = {
            "name": "Test Folder",
            "item": [
                {
                    "name": "Request 1",
                    "request": {
                        "method": "GET",
                        "url": {"raw": "https://api.example.com/1"}
                    }
                },
                {
                    "name": "Request 2",
                    "request": {
                        "method": "POST",
                        "url": {"raw": "https://api.example.com/2"}
                    }
                }
            ]
        }
        
        folder = PostmanImporter._create_folder_from_item(item)
        
        self.assertEqual(folder.name, "Test Folder")
        self.assertEqual(len(folder.requests), 2)
        
        request1 = folder.requests[0]
        self.assertEqual(request1.name, "Request 1")
        self.assertEqual(request1.method, "GET")
        
        request2 = folder.requests[1]
        self.assertEqual(request2.name, "Request 2")
        self.assertEqual(request2.method, "POST")


if __name__ == "__main__":
    unittest.main() 