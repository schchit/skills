import requests
import sys
import os
import time
import json

# --- Configuration ---
UPLOAD_URL = "https://www.pinocch.cn:8087/v1/documents"
RESULT_BASE_URL = "https://www.pinocch.cn:8087/v1/results/{task_id}?file_type={format}"
ALL_RESULTS_STATUS_URL = "https://www.pinocch.cn:8087/v1/all_results/{task_id}"
ALL_RESULTS_DOWNLOAD_URL = "https://www.pinocch.cn:8087/v1/all_results/{task_id}?file_type={format}"
#UPLOAD_URL =  "http://localhost:5000/v1/documents"
#RESULT_BASE_URL = "http://localhost:5000/v1/results/{task_id}?file_type={format}"
#ALL_RESULTS_STATUS_URL = "http://localhost:5000/v1/all_results/{task_id}"
#ALL_RESULTS_DOWNLOAD_URL = "http://localhost:5000/v1/all_results/{task_id}?file_type={format}"
CHECK_INTERVAL = 10  # seconds
MAX_WAIT_TIME = 3600  # maximum wait time in seconds (60 minutes)
MAX_RETRIES = 30  # maximum retry attempts for transient errors
RETRY_DELAY = 5  # delay between retries in seconds

def upload_file(username, api_token, file_path):
    """Uploads the PDF file and returns the task_id."""
    if not os.path.exists(file_path):
        return None, "Error: File not found at {}".format(file_path)

    file_name = os.path.basename(file_path)
    
    for attempt in range(MAX_RETRIES):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/pdf')}
                headers = {}
                
                # Only add authentication headers if username and api_token are provided
                if username and api_token:
                    headers = {
                        'Username': username,
                        'Authorization': f'Bearer {api_token}'
                    }
                else:
                    print("Uploading in trial mode (no authentication)...")
                
                print(f"Uploading {file_name}... (Attempt {attempt + 1}/{MAX_RETRIES})")
                response = requests.post(UPLOAD_URL, headers=headers, files=files, verify=True, timeout=180)
                
                if response.status_code >= 200 and response.status_code < 300 :
                    resp_json = response.json()
                    task_id = resp_json.get('task_id') or resp_json.get('id') or resp_json.get('data', {}).get('id')
                    
                    if task_id:
                        print(f"Upload successful. Task ID: {task_id}")
                        return task_id, None
                    else:
                        # Use server's error message if available
                        server_message = resp_json.get('message', '')
                        num_pages = resp_json.get('num_pages', 0)
                        if server_message:
                            # Include num_pages in error message if available
                            if num_pages:
                                err_msg = f"Upload failed: {server_message} (Document pages: {num_pages})"
                            else:
                                err_msg = f"Upload failed: {server_message}"
                        else:
                            err_msg = "Upload successful but no Task ID found in response."
                        print(err_msg)
                        return None, err_msg
                elif response.status_code in [502, 503, 504]:
                    # Transient server errors - retry
                    err_msg = f"Server error {response.status_code}. Attempt {attempt + 1}/{MAX_RETRIES}"
                    print(err_msg)
                    if attempt < MAX_RETRIES - 1:
                        print(f"Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        return None, f"Upload failed after {MAX_RETRIES} attempts. Status: {response.status_code}. Response: {response.text}"
                elif response.status_code == 402:
                    # Payment Required - extract error message and include response details
                    try:
                        resp_json = response.json()
                        error_msg = resp_json.get('error', 'Payment Required')
                        err_msg = f"Upload failed: {error_msg}"
                    except ValueError:
                        err_msg = f"Upload failed. Status Code: {response.status_code}. Response: {response.text}"
                    print(err_msg)
                    return None, err_msg
                else:
                    # Client errors or other errors - don't retry
                    err_msg = f"Upload failed. Status Code: {response.status_code}. Response: {response.text}"
                    print(err_msg)
                    return None, err_msg
                    
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            err_msg = f"Network error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}"
            print(err_msg)
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
                continue
            else:
                return None, f"Upload failed after {MAX_RETRIES} attempts due to network error: {str(e)}"
        except Exception as e:
            err_msg = f"Exception during upload: {str(e)}"
            print(err_msg)
            return None, err_msg
    
    # Should not reach here, but just in case
    return None, "Upload failed unexpectedly"

def check_result(username, api_token, task_id, fmt):
    """
    Checks OCR result status using all_results endpoint (without file_type parameter).
    Returns: (status, data, error_message, completed_pages)
    - status: 'completed', 'processing', 'error', 'retry'
    - data: result content or None
    - error_message: specific error string if status is 'error'
    - completed_pages: list of completed page numbers if available
    """
    url = ALL_RESULTS_STATUS_URL.format(task_id=task_id)
    print("Using all_results endpoint to check status and completed pages...")
    
    headers = {}
    
    # Only add authentication headers if username and api_token are provided
    if username and api_token:
        headers = {
            'Username': username,
            'Authorization': f'Bearer {api_token}'
        }
    else:
        print("Checking result in trial mode (no authentication)...")
    
    try:
        response = requests.get(url, headers=headers, verify=True, timeout=60)
        resp_text = response.text
        
        # Log the full response for debugging
        print(f"[DEBUG] API Response Status: {response.status_code}")
        print(f"[DEBUG] API Response Body: {resp_text[:500]}..." if len(resp_text) > 500 else f"[DEBUG] API Response Body: {resp_text}")
        
        # Try to parse JSON first (even for error responses)
        resp_json = None
        try:
            resp_json = response.json()
        except ValueError:
            pass  # Not JSON, will be handled below
        
        # Handle transient server errors (502, 503, 504)
        if response.status_code in [502, 503, 504]:
            # CRITICAL: Check if response contains valid result data despite the error status
            # Some APIs return 502 but include the actual result in the response body
            if resp_json and isinstance(resp_json, dict):
                # Check if we have task_id and page_details (indicates complete result)
                has_task_id = resp_json.get('task_id') is not None
                has_page_details = resp_json.get('page_details') is not None
                has_content = resp_json.get('content') is not None or resp_json.get('data') is not None or resp_json.get('text') is not None
                
                if has_task_id and (has_page_details or has_content):
                    print(f"Server returned {response.status_code} but included valid result data")
                    print(f"Task ID: {resp_json.get('task_id')}, has page_details: {has_page_details}")
                    # Get completed pages if available
                    completed_pages = resp_json.get('completed_pages', [])
                    return 'completed', resp_json, None, completed_pages
            
            # No valid data in response - treat as transient server error and retry
            print(f"Server error {response.status_code} received - will retry")
            return 'retry', None, f"Server error: {response.status_code}", []

        # --- Critical Logic: Detect Errors without task_id ---
        # Check if response has a 'message' field indicating an error, 
        # AND does not have a valid task_id or content indicating success.
        if resp_json and isinstance(resp_json, dict) and 'message' in resp_json:
            message = resp_json['message']
            # Specific known errors
            if "Invalid authentication token" in message or "Credits are not enough" in message:
                print(f"Critical Error detected: {message}")
                return 'error', resp_json, message, []
            
            # Generic error handling if message exists but isn't one of the specific ones
            # and no content/task_id is present
            if not (resp_json.get('content') or resp_json.get('data') or resp_json.get('task_id')):
                 print(f"API Error detected: {message}")
                 return 'error', resp_json, message, []

        # --- Success/Processing Logic (200, 202) ---
        if response.status_code >= 200 and response.status_code < 300:
            # Check for content indicators
            if resp_json and isinstance(resp_json, dict):
                # Extract completed pages from completed_pages or page_details if available
                completed_pages = []
                
                # First try to get completed_pages directly
                completed_pages = resp_json.get('completed_pages', [])
                if not completed_pages:
                    # If no completed_pages field, extract from page_details
                    page_details = resp_json.get('page_details', [])
                    if page_details:
                        # Extract page numbers from completed pages
                        completed_pages = [page.get('page_number', i+1) for i, page in enumerate(page_details) if page.get('page_content')]
                
                # Check status field
                status_field = resp_json.get('status', '')
                is_completed = status_field.lower() == 'completed'
                is_processing = status_field.lower() == 'processing'
                
                # If status is COMPLETED, treat as all pages completed
                if is_completed:
                    print(f"Status is COMPLETED - all pages finished!")
                    # When status is COMPLETED, use all_results endpoint with file_type to get actual OCR content
                    print("Fetching final OCR results using all_results endpoint...")
                    # Convert 'md' to 'markdown' for server compatibility
                    server_fmt = 'markdown' if fmt == 'md' else fmt
                    final_url = ALL_RESULTS_DOWNLOAD_URL.format(task_id=task_id, format=server_fmt)
                    final_response = requests.get(final_url, headers=headers, verify=True, timeout=60)
                    final_resp_text = final_response.text
                    
                    # Log the final response for debugging
                    print(f"[DEBUG] Final OCR Response Status: {final_response.status_code}")
                    print(f"[DEBUG] Final OCR Response Body: {final_resp_text[:500]}..." if len(final_resp_text) > 500 else f"[DEBUG] Final OCR Response Body: {final_resp_text}")
                    
                    # Try to parse final response as JSON
                    final_resp_json = None
                    try:
                        final_resp_json = final_response.json()
                        # Check if the result contains actual content (not just task_id)
                        if isinstance(final_resp_json, dict):
                            has_content = False
                            # Check for page_details or other content fields
                            if final_resp_json.get('page_details'):
                                has_content = True
                            elif final_resp_json.get('content'):
                                has_content = True
                            elif final_resp_json.get('text'):
                                has_content = True
                            elif final_resp_json.get('data'):
                                has_content = True
                            elif len(final_resp_json.keys()) > 1:  # More than just task_id
                                has_content = True
                            
                            if not has_content:
                                print("WARNING: Downloaded result does not contain actual content (only task_id)")
                                print("This indicates the external API is still processing or failed")
                                print("Continuing to poll for results...")
                                return 'processing', resp_json, "External API returned incomplete results, still processing", completed_pages
                    except ValueError:
                        # Not JSON, check if markdown contains error message
                        if "No page-specific results found" in final_resp_text:
                            print("WARNING: Downloaded markdown indicates no results were found")
                            print("This indicates the external API is still processing or failed")
                            print("Continuing to poll for results...")
                            return 'processing', resp_json, "External API returned incomplete results, still processing", completed_pages
                        # Not JSON, return as text
                        return 'completed', final_resp_text, None, completed_pages
                    
                    # Return the final OCR results
                    return 'completed', final_resp_json, None, completed_pages
                
                # Check if all pages are completed (if total_page_number is available)
                total_pages = resp_json.get('total_page_number')
                if total_pages:
                    try:
                        total_pages = int(total_pages)
                        if len(completed_pages) >= total_pages:
                            print(f"All {total_pages} pages completed!")
                            # When all pages are completed, use all_results endpoint with file_type to get actual OCR content
                            print("Fetching final OCR results using all_results endpoint...")
                            # Convert 'md' to 'markdown' for server compatibility
                            server_fmt = 'markdown' if fmt == 'md' else fmt
                            final_url = ALL_RESULTS_DOWNLOAD_URL.format(task_id=task_id, format=server_fmt)
                            final_response = requests.get(final_url, headers=headers, verify=True, timeout=60)
                            final_resp_text = final_response.text
                            
                            # Log the final response for debugging
                            print(f"[DEBUG] Final OCR Response Status: {final_response.status_code}")
                            print(f"[DEBUG] Final OCR Response Body: {final_resp_text[:500]}..." if len(final_resp_text) > 500 else f"[DEBUG] Final OCR Response Body: {final_resp_text}")
                            
                            # Try to parse final response as JSON
                            final_resp_json = None
                            try:
                                final_resp_json = final_response.json()
                                # Check if the result contains actual content (not just task_id)
                                if isinstance(final_resp_json, dict):
                                    has_content = False
                                    # Check for page_details or other content fields
                                    if final_resp_json.get('page_details'):
                                        has_content = True
                                    elif final_resp_json.get('content'):
                                        has_content = True
                                    elif final_resp_json.get('text'):
                                        has_content = True
                                    elif final_resp_json.get('data'):
                                        has_content = True
                                    elif len(final_resp_json.keys()) > 1:  # More than just task_id
                                        has_content = True
                                    
                                    if not has_content:
                                        print("WARNING: Downloaded result does not contain actual content (only task_id)")
                                        print("This indicates that external API is still processing or failed")
                                        print("Continuing to poll for results...")
                                        return 'processing', resp_json, "External API returned incomplete results, still processing", completed_pages
                            except ValueError:
                                # Not JSON, check if markdown contains error message
                                if "No page-specific results found" in final_resp_text:
                                    print("WARNING: Downloaded markdown indicates no results were found")
                                    print("This indicates that external API is still processing or failed")
                                    print("Continuing to poll for results...")
                                    return 'processing', resp_json, "External API returned incomplete results, still processing", completed_pages
                                # Not JSON, return as text
                                return 'completed', final_resp_text, None, completed_pages
                            
                            # Return the final OCR results
                            return 'completed', final_resp_json, None, completed_pages
                    except ValueError:
                        pass
                
                # Check for actual content fields (not just metadata)
                has_content = ('content' in resp_json or 'text' in resp_json or 'data' in resp_json or 
                              'page_details' in resp_json)
                
                if has_content and is_completed:
                    # Has actual content and task is completed
                    print(f"Got content! Keys: {list(resp_json.keys())}")
                    print(f"Completed pages: {sorted(completed_pages)}")
                    print(f"Total completed: {len(completed_pages)}")
                    return 'completed', resp_json, None, completed_pages
                else:
                    # Task is still processing
                    print(f"Task still processing")
                    print(f"Completed pages: {sorted(completed_pages)}")
                    print(f"Total completed: {len(completed_pages)}")
                    return 'processing', resp_json, None, completed_pages
            elif resp_text:
                # Non-dict/non-JSON response with 2xx status - treat as completed (raw text result)
                return 'completed', resp_text, None, []
            
            # No content found - still processing
            return 'processing', None, None, []
        
        elif response.status_code == 404 or response.status_code == 202:
            # Standard "not ready yet" codes
            return 'processing', None, None, []
        
        else:
            # Other HTTP errors
            error_msg = resp_json.get('message', 'Unknown error') if resp_json and isinstance(resp_json, dict) else 'Unknown error'
            return 'error', resp_json, f"HTTP Status {response.status_code}: {error_msg}", []

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        # Network errors - signal to retry
        print(f"Network error during check: {str(e)} - will retry")
        return 'retry', None, f"Network error: {str(e)}", []
    except Exception as e:
        return 'error', None, f"Exception during check: {str(e)}", []

def check_result_final(username, api_token, task_id, fmt):
    """
    Final check using regular results endpoint (called after timeout).
    Returns: (status, data, error_message, completed_pages)
    """
    # Convert 'md' to 'markdown' for server compatibility
    server_fmt = 'markdown' if fmt == 'md' else fmt
    url = RESULT_BASE_URL.format(task_id=task_id, format=server_fmt)
    print("Using regular results endpoint for final check...")
    
    headers = {}
    
    # Only add authentication headers if username and api_token are provided
    if username and api_token:
        headers = {
            'Username': username,
            'Authorization': f'Bearer {api_token}'
        }
    else:
        print("Checking result in trial mode (no authentication)...")
    
    try:
        response = requests.get(url, headers=headers, verify=True, timeout=60)
        resp_text = response.text
        
        # Log the full response for debugging
        print(f"[DEBUG] Final Check Response Status: {response.status_code}")
        print(f"[DEBUG] Final Check Response Body: {resp_text[:500]}..." if len(resp_text) > 500 else f"[DEBUG] Final Check Response Body: {resp_text}")
        
        # Try to parse JSON first (even for error responses)
        resp_json = None
        try:
            resp_json = response.json()
        except ValueError:
            pass  # Not JSON, will be handled below
        
        # Handle transient server errors (502, 503, 504)
        if response.status_code in [502, 503, 504]:
            # CRITICAL: Check if response contains valid result data despite the error status
            # Some APIs return 502 but include the actual result in the response body
            if resp_json and isinstance(resp_json, dict):
                # Check if we have task_id and page_details (indicates complete result)
                has_task_id = resp_json.get('task_id') is not None
                has_page_details = resp_json.get('page_details') is not None
                has_content = resp_json.get('content') is not None or resp_json.get('data') is not None or resp_json.get('text') is not None
                
                if has_task_id and (has_page_details or has_content):
                    print(f"Server returned {response.status_code} but included valid result data")
                    print(f"Task ID: {resp_json.get('task_id')}, has page_details: {has_page_details}")
                    # Get completed pages if available
                    completed_pages = []
                    if isinstance(resp_json, dict):
                        # First try to get completed_pages directly
                        completed_pages = resp_json.get('completed_pages', [])
                        if not completed_pages:
                            # If no completed_pages field, extract from page_details
                            page_details = resp_json.get('page_details', [])
                            if page_details:
                                # Extract page numbers from completed pages
                                completed_pages = [page.get('page_number', i+1) for i, page in enumerate(page_details) if page.get('page_content')]
                    return 'completed', resp_json, None, completed_pages
            
            # No valid data in response - treat as transient server error and retry
            print(f"Server error {response.status_code} received - will retry")
            return 'retry', None, f"Server error: {response.status_code}", []

        # --- Critical Logic: Detect Errors without task_id ---
        # Check if response has a 'message' field indicating an error, 
        # AND does not have a valid task_id or content indicating success.
        if resp_json and isinstance(resp_json, dict) and 'message' in resp_json:
            message = resp_json['message']
            # Specific known errors
            if "Invalid authentication token" in message or "Credits are not enough" in message:
                print(f"Critical Error detected: {message}")
                return 'error', resp_json, message, []
            
            # Generic error handling if message exists but isn't one of the specific ones
            # and no content/task_id is present
            if not (resp_json.get('content') or resp_json.get('data') or resp_json.get('task_id')):
                 print(f"API Error detected: {message}")
                 return 'error', resp_json, message, []

        # --- Success/Processing Logic (200, 202) ---
        if response.status_code >= 200 and response.status_code < 300:
            # Check for content indicators
            if resp_json and isinstance(resp_json, dict):
                # Extract completed pages from completed_pages or page_details if available
                completed_pages = []
                
                # First try to get completed_pages directly
                completed_pages = resp_json.get('completed_pages', [])
                if not completed_pages:
                    # If no completed_pages field, extract from page_details
                    page_details = resp_json.get('page_details', [])
                    if page_details:
                        # Extract page numbers from completed pages
                        completed_pages = [page.get('page_number', i+1) for i, page in enumerate(page_details) if page.get('page_content')]
                
                # Check status field
                status_field = resp_json.get('status', '')
                is_completed = status_field.lower() == 'completed'
                
                # Check for actual content fields (not just metadata)
                has_content = ('content' in resp_json or 'text' in resp_json or 'data' in resp_json or 
                              'page_details' in resp_json)
                
                if has_content or is_completed:
                    # Has actual content or task is marked as completed
                    print(f"Got content from regular results endpoint. Keys: {list(resp_json.keys())}")
                    print(f"Completed pages: {sorted(completed_pages)}")
                    print(f"Total completed: {len(completed_pages)}")
                    return 'completed', resp_json, None, completed_pages
                else:
                    # No content found - still processing
                    return 'processing', None, None, []
            elif resp_text:
                # Non-dict/non-JSON response with 2xx status - treat as completed (raw text result)
                return 'completed', resp_text, None, []
            
            # No content found - still processing
            return 'processing', None, None, []
        
        elif response.status_code == 404 or response.status_code == 202:
            # Standard "not ready yet" codes
            return 'processing', None, None, []
        
        else:
            # Other HTTP errors
            error_msg = resp_json.get('message', 'Unknown error') if resp_json and isinstance(resp_json, dict) else 'Unknown error'
            return 'error', resp_json, f"HTTP Status {response.status_code}: {error_msg}", []

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        # Network errors - signal to retry
        print(f"Network error during final check: {str(e)} - will retry")
        return 'retry', None, f"Network error: {str(e)}", []
    except Exception as e:
        return 'error', None, f"Exception during final check: {str(e)}", []

def write_result_to_file(file_path, content):
    """Helper to write content (string or dict) to file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(content, dict):
                # Use ensure_ascii=False to preserve Chinese characters
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
            else:
                f.write(str(content))
        print(f"Output written to {file_path}")
    except Exception as e:
        print(f"Failed to write to file {file_path}: {e}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python handler.py [<username> <secret>] <pdf_path> <result_path> <format>")
        print("Example 1 (with authentication): python handler.py user pass file.pdf result.json json")
        print("Example 2 (trial mode): python handler.py file.pdf result.json json")
        sys.exit(1)

    # Determine if we're in trial mode or authenticated mode
    if len(sys.argv) == 4:
        # Trial mode - no username and secret provided
        username = None
        secret = None
        pdf_path = sys.argv[1]
        result_path = sys.argv[2]
        fmt = sys.argv[3].lower()
    else:
        # Authenticated mode - username and secret provided
        username = sys.argv[1]
        secret = sys.argv[2]
        pdf_path = sys.argv[3]
        result_path = sys.argv[4]
        fmt = sys.argv[5].lower()

    if fmt not in ['json', 'md']:
        print("Error: Format must be 'json' or 'md'")
        sys.exit(1)

    # 1. Upload
    task_id, upload_err = upload_file(username, secret, pdf_path)
    
    # If upload fails immediately (e.g., file not found), write error and exit
    if not task_id:
        error_payload = {"status": "failed", "stage": "upload", "message": upload_err}
        write_result_to_file(result_path, error_payload)
        sys.exit(1)

    # 2. Poll for results
    print(f"Starting polling every {CHECK_INTERVAL} seconds...")
    elapsed_time = 0
    consecutive_retries = 0
    
    while elapsed_time < MAX_WAIT_TIME:
        time.sleep(CHECK_INTERVAL)
        elapsed_time += CHECK_INTERVAL
        
        status, data, error_msg, completed_pages = check_result(username, secret, task_id, fmt)
        
        if status == 'completed':
            print("OCR Processing completed!")
            
            # Extract content to save
            content_to_save = ""
            if isinstance(data, dict):
                content_to_save = data.get('content') or data.get('text') or data.get('data') or json.dumps(data, ensure_ascii=False, indent=2)
            else:
                content_to_save = str(data)
            
            write_result_to_file(result_path, content_to_save)
            print(f"Output written to {result_path}")
            print("--- Result Content Preview ---")
            # Use json.dumps with ensure_ascii=False for proper Chinese display in preview
            if isinstance(content_to_save, dict):
                preview_text = json.dumps(content_to_save, ensure_ascii=False, indent=2)
            else:
                preview_text = str(content_to_save)
            print(preview_text[:500] + ("..." if len(preview_text) > 500 else ""))
            sys.exit(0)
            
        elif status == 'retry':
            # Transient error - retry with backoff
            consecutive_retries += 1
            print(f"Retry attempt {consecutive_retries}/{MAX_RETRIES} due to: {error_msg}")
            if consecutive_retries >= MAX_RETRIES:
                print(f"Stopping after {MAX_RETRIES} consecutive retry failures: {error_msg}")
                error_payload = {
                    "status": "failed",
                    "stage": "polling",
                    "task_id": task_id,
                    "error_message": f"Failed after {MAX_RETRIES} retry attempts: {error_msg}",
                    "raw_response": data if data else {}
                }
                write_result_to_file(result_path, error_payload)
                sys.exit(1)
            
            print(f"Waiting {RETRY_DELAY} seconds before retry...")
            time.sleep(RETRY_DELAY)
            # Don't count this iteration towards elapsed time for retry purposes
            continue
            
        elif status == 'error':
            # CRITICAL: Stop loop immediately on error (Auth/Credits/etc)
            print(f"Stopping due to error: {error_msg}")
            
            # Construct error object to write to file
            error_payload = {
                "status": "failed",
                "stage": "polling",
                "task_id": task_id,
                "error_message": error_msg,
                "raw_response": data if data else {}
            }
            
            write_result_to_file(result_path, error_payload)
            sys.exit(1)
            
        else:
            # Still processing - reset retry counter
            consecutive_retries = 0
            # Print completed pages information
            if completed_pages:
                print(f"Still processing... ({elapsed_time}s elapsed)")
                print(f"Completed pages: {sorted(completed_pages)}")
                print(f"Total completed: {len(completed_pages)}")
            else:
                print(f"Still processing... ({elapsed_time}s elapsed)")
                print("No pages completed yet")

    # Timeout case - final check using regular results endpoint
    print(f"Timeout: Result not ready after {MAX_WAIT_TIME} seconds. Performing final check...")
    status, data, error_msg, _ = check_result_final(username, secret, task_id, fmt)
    
    if status == 'completed':
        print("Final check: OCR Processing completed!")
        
        # Extract content to save
        content_to_save = ""
        if isinstance(data, dict):
            content_to_save = data.get('content') or data.get('text') or data.get('data') or json.dumps(data, ensure_ascii=False, indent=2)
        else:
            content_to_save = str(data)
        
        write_result_to_file(result_path, content_to_save)
        print(f"Output written to {result_path}")
        print("--- Result Content Preview ---")
        # Use json.dumps with ensure_ascii=False for proper Chinese display in preview
        if isinstance(content_to_save, dict):
            preview_text = json.dumps(content_to_save, ensure_ascii=False, indent=2)
        else:
            preview_text = str(content_to_save)
        print(preview_text[:500] + ("..." if len(preview_text) > 500 else ""))
        sys.exit(0)
    else:
        timeout_msg = f"Timeout: Result not ready after {MAX_WAIT_TIME} seconds."
        print(timeout_msg)
        error_payload = {
            "status": "failed", 
            "stage": "timeout", 
            "message": timeout_msg,
            "task_id": task_id
        }
        write_result_to_file(result_path, error_payload)
        sys.exit(1)

if __name__ == "__main__":
    main()
