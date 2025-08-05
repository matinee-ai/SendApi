"""
Batch Request Runner for the API Testing Application
"""

import time
from PySide6.QtCore import QThread, Signal
from .request_runner import RequestRunner


class BatchRequestRunner(QThread):
    """Runs multiple requests sequentially."""
    
    request_completed = Signal(object, dict, dict)  # request, response, test_results
    all_completed = Signal(list)  # list of results
    
    def __init__(self, requests, environment, parent=None):
        super().__init__(parent)
        self.requests = requests
        self.environment = environment
        self.results = []
        self.current_index = 0
        self.runners = []  # Keep references to runners
    
    def run(self):
        """Run all requests sequentially."""
        print(f"BatchRequestRunner: Starting batch run with {len(self.requests)} requests")
        self.results = []
        
        for i, request in enumerate(self.requests):
            print(f"BatchRequestRunner: Running request {i+1}/{len(self.requests)}: {request.name}")
            
            # Convert request to dict format
            request_data = {
                "method": request.method,
                "url": request.url,
                "headers": request.headers,
                "params": request.params,
                "body": request.body,
                "body_type": request.body_type,
                "pre_request_script": request.pre_request_script,
                "tests": request.tests
            }
            
            try:
                # Create and run single request synchronously
                runner = RequestRunner(request_data, self.environment)
                self.runners.append(runner)  # Keep reference
                
                # Run the request synchronously
                runner.start()
                runner.wait()  # Wait for completion
                
                # Get response and test results directly
                response = runner.get_response()
                test_results = runner.get_test_results()
                
                if response is None:
                    # Handle case where no response was received
                    response = {"error": "No response received", "status_code": 0}
                    test_results = {"passed": False, "results": ["No response received"]}
                
                print(f"BatchRequestRunner: Request {request.name} completed with status {response.get('status_code', 'Unknown')}")
                
            except Exception as e:
                print(f"BatchRequestRunner: Error running request {request.name}: {str(e)}")
                response = {"error": str(e), "status_code": 0}
                test_results = {"passed": False, "results": [f"Request failed: {str(e)}"]}
            
            # Store result
            result = {
                "request": request,
                "response": response,
                "test_results": test_results,
                "tests_passed": test_results.get("passed", False) if isinstance(test_results, dict) else False
            }
            self.results.append(result)
            
            # Emit signal for this request
            print(f"BatchRequestRunner: Emitting request_completed signal for {request.name}")
            self.request_completed.emit(request, response, test_results)
            
            # Small delay between requests (reduced for faster execution)
            time.sleep(0.1)
        
        # Emit signal for all completed
        print(f"BatchRequestRunner: Emitting all_completed signal with {len(self.results)} results")
        self.all_completed.emit(self.results) 