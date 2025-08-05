"""
Postman Collection and Environment Importer for the API Testing Application
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from .models import Collection, Request, Environment


class PostmanImporter:
    """Imports Postman collections and environments and converts them to our internal format."""
    
    @staticmethod
    def import_collection(file_path: str) -> List[Collection]:
        """Import a Postman collection file and return a list of collections."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle Postman collection format
            if 'info' in data and 'item' in data:
                # This is a Postman collection
                return PostmanImporter._import_postman_collection(data)
            else:
                # This might be our internal format or a simple collection
                return [Collection.from_dict(data)]
                
        except Exception as e:
            raise Exception(f"Failed to import collection: {str(e)}")
    
    @staticmethod
    def import_environment(file_path: str) -> List[Environment]:
        """Import a Postman environment file and return a list of environments."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle Postman environment format
            if 'id' in data and 'name' in data and 'values' in data:
                # This is a Postman environment
                return PostmanImporter._import_postman_environment(data)
            else:
                # This might be our internal format
                return [Environment.from_dict(data)]
                
        except Exception as e:
            raise Exception(f"Failed to import environment: {str(e)}")
    
    @staticmethod
    def import_file(file_path: str) -> Tuple[List[Collection], List[Environment]]:
        """Import a file and return both collections and environments."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collections = []
            environments = []
            
            # Check if it's a Postman collection
            if 'info' in data and 'item' in data:
                collections = PostmanImporter._import_postman_collection(data)
            
            # Check if it's a Postman environment
            elif 'id' in data and 'name' in data and 'values' in data:
                environments = PostmanImporter._import_postman_environment(data)
            
            # Check if it's a Postman workspace (contains multiple collections/environments)
            elif 'collections' in data or 'environments' in data:
                if 'collections' in data:
                    for coll_data in data['collections']:
                        collections.extend(PostmanImporter._import_postman_collection(coll_data))
                if 'environments' in data:
                    for env_data in data['environments']:
                        environments.extend(PostmanImporter._import_postman_environment(env_data))
            
            # Check if it's our internal format
            else:
                # Try to determine if it's a collection or environment
                if 'requests' in data or 'folders' in data:
                    collections = [Collection.from_dict(data)]
                elif 'variables' in data:
                    environments = [Environment.from_dict(data)]
            
            return collections, environments
                
        except Exception as e:
            raise Exception(f"Failed to import file: {str(e)}")
    
    @staticmethod
    def _import_postman_collection(data: Dict[str, Any]) -> List[Collection]:
        """Import a Postman collection format."""
        collections = []
        
        # Get collection info
        info = data.get('info', {})
        collection_name = info.get('name', 'Imported Collection')
        collection_description = info.get('description', '')
        
        # Create main collection
        main_collection = Collection(
            name=collection_name,
            description=collection_description,
            id=data.get('info', {}).get('_postman_id', '')
        )
        
        # Process items (requests and folders)
        items = data.get('item', [])
        PostmanImporter._process_items(items, main_collection)
        
        collections.append(main_collection)
        return collections
    
    @staticmethod
    def _import_postman_environment(data: Dict[str, Any]) -> List[Environment]:
        """Import a Postman environment format."""
        environments = []
        
        # Get environment info
        env_name = data.get('name', 'Imported Environment')
        env_id = data.get('_postman_id', '')
        
        # Create environment
        environment = Environment(
            name=env_name,
            id=env_id
        )
        
        # Process variables
        values = data.get('values', [])
        for value in values:
            key = value.get('key', '')
            val = value.get('value', '')
            enabled = value.get('enabled', True)
            
            if key and enabled:
                environment.set_variable(key, val)
        
        environments.append(environment)
        return environments
    
    @staticmethod
    def _process_items(items: List[Dict[str, Any]], parent_collection: Collection):
        """Process Postman items (requests and folders)."""
        for item in items:
            if 'item' in item:
                # This is a folder
                folder = PostmanImporter._create_folder_from_item(item)
                parent_collection.folders.append(folder)
            else:
                # This is a request
                request = PostmanImporter._create_request_from_item(item)
                if request:
                    parent_collection.add_request(request)
    
    @staticmethod
    def _create_folder_from_item(item: Dict[str, Any]) -> Collection:
        """Create a folder (collection) from a Postman item."""
        folder_name = item.get('name', 'Unnamed Folder')
        folder_description = item.get('description', '')
        
        folder = Collection(
            name=folder_name,
            description=folder_description,
            id=item.get('_postman_id', '')
        )
        
        # Process items in the folder
        sub_items = item.get('item', [])
        PostmanImporter._process_items(sub_items, folder)
        
        return folder
    
    @staticmethod
    def _create_request_from_item(item: Dict[str, Any]) -> Optional[Request]:
        """Create a request from a Postman item."""
        try:
            name = item.get('name', 'Unnamed Request')
            request_data = item.get('request', {})
            
            # Get method and URL
            method = request_data.get('method', 'GET')
            url_data = request_data.get('url', {})
            
            # Handle different URL formats
            if isinstance(url_data, str):
                url = url_data
            elif isinstance(url_data, dict):
                url = url_data.get('raw', '')
                # Handle query parameters
                query_params = url_data.get('query', [])
                params = {}
                for param in query_params:
                    if param.get('key') and param.get('value'):
                        params[param['key']] = param['value']
            else:
                url = ''
                params = {}
            
            # Get headers
            headers = {}
            header_data = request_data.get('header', [])
            for header in header_data:
                if header.get('key') and header.get('value'):
                    headers[header['key']] = header['value']
            
            # Get body
            body_data = request_data.get('body', {})
            body = ''
            body_type = 'none'
            
            if body_data:
                body_mode = body_data.get('mode', '')
                if body_mode == 'raw':
                    body = body_data.get('raw', '')
                    body_type = 'raw'
                elif body_mode == 'urlencoded':
                    form_data = body_data.get('urlencoded', [])
                    form_dict = {}
                    for form_item in form_data:
                        if form_item.get('key') and form_item.get('value'):
                            form_dict[form_item['key']] = form_item['value']
                    body = json.dumps(form_dict)
                    body_type = 'x-www-form-urlencoded'
                elif body_mode == 'formdata':
                    form_data = body_data.get('formdata', [])
                    form_dict = {}
                    for form_item in form_data:
                        if form_item.get('key') and form_item.get('value'):
                            form_dict[form_item['key']] = form_item['value']
                    body = json.dumps(form_dict)
                    body_type = 'form-data'
            
            # Get scripts
            event_data = item.get('event', [])
            pre_request_script = ''
            tests_script = ''
            
            for event in event_data:
                if event.get('listen') == 'prerequest':
                    script_data = event.get('script', {})
                    if script_data.get('type') == 'text/javascript':
                        pre_request_script = script_data.get('exec', [''])[0]
                elif event.get('listen') == 'test':
                    script_data = event.get('script', {})
                    if script_data.get('type') == 'text/javascript':
                        tests_script = script_data.get('exec', [''])[0]
            
            # Create request
            request = Request(
                name=name,
                method=method,
                url=url,
                headers=headers,
                params=params,
                body=body,
                body_type=body_type,
                pre_request_script=pre_request_script,
                tests=tests_script,
                description=item.get('description', ''),
                id=item.get('_postman_id', '')
            )
            
            return request
            
        except Exception as e:
            print(f"Warning: Failed to create request from item: {e}")
            return None 