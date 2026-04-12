import requests
import sys
import os
import time
import json

# --- Configuration ---
BASE_URL = "https://api.pinocch.com"
UPLOAD_URL = f"{BASE_URL}/v1/documents"
RESULT_BASE_URL = f"{BASE_URL}/v1/results/{{task_id}}?file_type={{format}}"
ALL_RESULTS_STATUS_URL = f"{BASE_URL}/v1/all_results/{{task_id}}"
ALL_RESULTS_DOWNLOAD_URL = f"{BASE_URL}/v1/all_results/{{task_id}}?file_type={{format}}"
CHECK_INTERVAL = 10  # seconds
MAX_WAIT_TIME = 3600  # maximum wait time in seconds (60 minutes)
MAX_RETRIES = 30  # maximum retry attempts for transient errors
RETRY_DELAY = 5  # delay between retries in seconds

def get_auth_headers(username, api_token):
    """Get authentication headers if credentials are provided."""
    if username and api_token:
        return {
            'Username': username,
            'Authorization': f'Bearer {api_token}'
        }
    print("Operating in trial mode (no authentication)...")
    return {}

def extract_completed_pages(resp_json):
    """Extract completed pages from response JSON."""
    if not isinstance(resp_json, dict):
        return []
    
    # First try to get completed_pages directly
    completed_pages = resp_json.get('completed_pages', [])
    if not completed_pages:
        # If no completed_pages field, extract from page_details
        page_details = resp_json.get('page_details', [])
        if page_details:
            completed_pages = [page.get('page_number', i+1) for i, page in enumerate(page_details) if page.get('page_content')]
    return completed_pages

def check_content_completeness(content, fmt):
    """Check if content is complete (not just task_id)."""
    if isinstance(content, dict):
        has_content = False
        if content.get('page_details') or content.get('content') or content.get('text') or content.get('data'):
            has_content = True
        elif len(content.keys()) > 1:  # More than just task_id
            has_content = True
        return has_content
    elif isinstance(content, str):
        return "No page-specific results found" not in content
    return False

def handle_response(response, headers, task_id, fmt, is_final_check=False):
    """Handle API response and return status, data, error_message, completed_pages."""
    resp_text = response.text
    resp_json = None
    
    try:
        resp_json = response.json()
    except ValueError:
        pass
    
    # Handle transient server errors (502, 503, 504)
    if response.status_code in [502, 503, 504]:
        if resp_json and isinstance(resp_json, dict):
            has_task_id = resp_json.get('task_id') is not None
            has_content = resp_json.get('page_details') is not None or \
                         resp_json.get('content') is not None or \
                         resp_json.get('data') is not None or \
                         resp_json.get('text') is not None
            if has_task_id and has_content:
                print(f"Server returned {response.status_code} but included valid result data")
                completed_pages = extract_completed_pages(resp_json)
                return 'completed', resp_json, None, completed_pages
        print(f"Server error {response.status_code} received - will retry")
        return 'retry', None, f"Server error: {response.status_code}", []
    
    # Critical Logic: Detect Errors without task_id
    if resp_json and isinstance(resp_json, dict) and 'message' in resp_json:
        message = resp_json['message']
        if "Invalid authentication token" in message or "Credits are not enough" in message:
            print(f"Critical Error detected: {message}")
            return 'error', resp_json, message, []
        if not (resp_json.get('content') or resp_json.get('data') or resp_json.get('task_id')):
            print(f"API Error detected: {message}")
            return 'error', resp_json, message, []
    
    # Success/Processing Logic (200, 202)
    if response.status_code >= 200 and response.status_code < 300:
        if resp_json and isinstance(resp_json, dict):
            completed_pages = extract_completed_pages(resp_json)
            status_field = resp_json.get('status', '').lower()
            is_completed = status_field == 'completed'
            
            # If status is COMPLETED or all pages completed, fetch final results
            if is_completed or (resp_json.get('total_page_number') and len(completed_pages) >= int(resp_json.get('total_page_number'))):
                if not is_final_check:
                    print(f"Status is {'COMPLETED' if is_completed else 'ALL PAGES DONE'} - fetching final results...")
                    server_fmt = 'markdown' if fmt == 'md' else fmt
                    final_url = ALL_RESULTS_DOWNLOAD_URL.format(task_id=task_id, format=server_fmt)
                    final_response = requests.get(final_url, headers=headers, verify=True, timeout=60)
                    final_resp_text = final_response.text
                    
                    try:
                        final_resp_json = final_response.json()
                        if not check_content_completeness(final_resp_json, fmt):
                            print("WARNING: Incomplete results - continuing to poll...")
                            return 'processing', resp_json, "External API returned incomplete results", completed_pages
                        return 'completed', final_resp_json, None, completed_pages
                    except ValueError:
                        if "No page-specific results found" in final_resp_text:
                            print("WARNING: No results found - continuing to poll...")
                            return 'processing', resp_json, "External API returned incomplete results", completed_pages
                        return 'completed', final_resp_text, None, completed_pages
            
            # Check for actual content fields
            has_content = 'content' in resp_json or 'text' in resp_json or 'data' in resp_json or 'page_details' in resp_json
            if has_content and is_completed:
                print(f"Got content! Keys: {list(resp_json.keys())}")
                print(f"Completed pages: {sorted(completed_pages)}")
                return 'completed', resp_json, None, completed_pages
            else:
                print(f"Task still processing{' - ' + str(sorted(completed_pages)) if completed_pages else ''}")
                return 'processing', resp_json, None, completed_pages
        elif resp_text:
            return 'completed', resp_text, None, []
        return 'processing', None, None, []
    
    elif response.status_code == 404 or response.status_code == 202:
        return 'processing', None, None, []
    
    else:
        error_msg = resp_json.get('message', 'Unknown error') if resp_json and isinstance(resp_json, dict) else 'Unknown error'
        return 'error', resp_json, f"HTTP Status {response.status_code}: {error_msg}", []

def upload_file(username, api_token, file_path):
    """Uploads the PDF file and returns the task_id."""
    if not os.path.exists(file_path):
        return None, f"Error: File not found at {file_path}"

    file_name = os.path.basename(file_path)
    headers = get_auth_headers(username, api_token)
    
    for attempt in range(MAX_RETRIES):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/pdf')}
                print(f"Uploading {file_name}... (Attempt {attempt + 1}/{MAX_RETRIES})")
                response = requests.post(UPLOAD_URL, headers=headers, files=files, verify=True, timeout=180)
                
                if 200 <= response.status_code < 300:
                    resp_json = response.json()
                    task_id = resp_json.get('task_id') or resp_json.get('id') or resp_json.get('data', {}).get('id')
                    
                    if task_id:
                        print(f"Upload successful. Task ID: {task_id}")
                        return task_id, None
                    else:
                        server_message = resp_json.get('message', '')
                        num_pages = resp_json.get('num_pages', 0)
                        err_msg = f"Upload failed: {server_message}" + (f" (Document pages: {num_pages})" if num_pages else "")
                        print(err_msg)
                        return None, err_msg
                elif response.status_code in [502, 503, 504]:
                    err_msg = f"Server error {response.status_code}. Attempt {attempt + 1}/{MAX_RETRIES}"
                    print(err_msg)
                    if attempt < MAX_RETRIES - 1:
                        print(f"Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        return None, f"Upload failed after {MAX_RETRIES} attempts. Status: {response.status_code}. Response: {response.text}"
                elif response.status_code == 402:
                    try:
                        resp_json = response.json()
                        error_msg = resp_json.get('error', 'Payment Required')
                        err_msg = f"Upload failed: {error_msg}"
                    except ValueError:
                        err_msg = f"Upload failed. Status Code: {response.status_code}. Response: {response.text}"
                    print(err_msg)
                    return None, err_msg
                else:
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
    
    return None, "Upload failed unexpectedly"

def check_result(username, api_token, task_id, fmt, is_final_check=False):
    """Check OCR result status and return (status, data, error_message, completed_pages)."""
    url = ALL_RESULTS_STATUS_URL.format(task_id=task_id) if not is_final_check else RESULT_BASE_URL.format(task_id=task_id, format='markdown' if fmt == 'md' else fmt)
    if is_final_check:
        print("Using regular results endpoint for final check...")
    else:
        print("Using all_results endpoint to check status...")
    
    headers = get_auth_headers(username, api_token)
    
    try:
        response = requests.get(url, headers=headers, verify=True, timeout=60)
        return handle_response(response, headers, task_id, fmt, is_final_check)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        print(f"Network error during check: {str(e)} - will retry")
        return 'retry', None, f"Network error: {str(e)}", []
    except Exception as e:
        return 'error', None, f"Exception during check: {str(e)}", []

def write_result_to_file(file_path, content):
    """Write content (string or dict) to file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(content, dict):
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
            else:
                f.write(str(content))
        print(f"Output written to {file_path}")
    except Exception as e:
        print(f"Failed to write to file {file_path}: {e}")

def write_task_id_file(task_id_path, task_id, pdf_path):
    """Write task ID info to JSON file."""
    try:
        task_info = {
            "task_id": task_id,
            "pdf_path": pdf_path,
            "submit_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(task_id_path, 'w', encoding='utf-8') as f:
            json.dump(task_info, f, ensure_ascii=False, indent=2)
        print(f"Task ID info written to {task_id_path}")
    except Exception as e:
        print(f"Warning: Failed to write task ID file {task_id_path}: {e}")

def main():
    # Check if using existing task_id mode
    if len(sys.argv) >= 4 and sys.argv[1] == '--task-id':
        print("Using existing task ID mode...")
        if len(sys.argv) < 5:
            print("Usage: python handler.py --task-id <task_id> [<username> <secret>] <result_path> <format>")
            print("Example 1 (with authentication): python handler.py --task-id TASK123 user pass result.json json")
            print("Example 2 (trial mode): python handler.py --task-id TASK123 result.json json")
            sys.exit(1)
        
        task_id = sys.argv[2]
        if len(sys.argv) == 5:
            # Trial mode with task_id
            username, secret, result_path, fmt = None, None, sys.argv[3], sys.argv[4].lower()
        else:
            # Authenticated mode with task_id
            username, secret, result_path, fmt = sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6].lower()
        task_id_path = None
        pdf_path = None
    else:
        # Normal upload mode
        if len(sys.argv) < 5:
            print("Usage: python handler.py [<username> <secret>] <pdf_path> <result_path> <format> <task_id_path>")
            print("Example 1 (with authentication): python handler.py user pass file.pdf result.json json task.json")
            print("Example 2 (trial mode): python handler.py file.pdf result.json json task.json")
            sys.exit(1)

        # Determine if we're in trial mode or authenticated mode
        if len(sys.argv) == 5:
            username, secret, pdf_path, result_path, fmt, task_id_path = None, None, sys.argv[1], sys.argv[2], sys.argv[3].lower(), sys.argv[4]
        else:
            username, secret, pdf_path, result_path, fmt, task_id_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].lower(), sys.argv[6]
        
        # 1. Upload
        task_id, upload_err = upload_file(username, secret, pdf_path)
        
        if not task_id:
            error_payload = {"status": "failed", "stage": "upload", "message": upload_err}
            write_result_to_file(result_path, error_payload)
            sys.exit(1)
        
        # 2. Write task ID file
        write_task_id_file(task_id_path, task_id, pdf_path)

    if fmt not in ['json', 'md']:
        print("Error: Format must be 'json' or 'md'")
        sys.exit(1)

    # 2. Poll for results
    print(f"Starting polling every {CHECK_INTERVAL} seconds...")
    elapsed_time, consecutive_retries = 0, 0
    
    while elapsed_time < MAX_WAIT_TIME:
        time.sleep(CHECK_INTERVAL)
        elapsed_time += CHECK_INTERVAL
        
        status, data, error_msg, completed_pages = check_result(username, secret, task_id, fmt)
        
        if status == 'completed':
            print("OCR Processing completed!")
            content_to_save = data.get('content') or data.get('text') or data.get('data') or json.dumps(data, ensure_ascii=False, indent=2) if isinstance(data, dict) else str(data)
            write_result_to_file(result_path, content_to_save)
            print("--- Result Content Preview ---")
            preview_text = json.dumps(content_to_save, ensure_ascii=False, indent=2) if isinstance(content_to_save, dict) else str(content_to_save)
            print(preview_text[:500] + ("..." if len(preview_text) > 500 else ""))
            sys.exit(0)
            
        elif status == 'retry':
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
            continue
            
        elif status == 'error':
            print(f"Stopping due to error: {error_msg}")
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
            consecutive_retries = 0
            if completed_pages:
                print(f"Still processing... ({elapsed_time}s elapsed)")
                print(f"Completed pages: {sorted(completed_pages)}")
                print(f"Total completed: {len(completed_pages)}")
            else:
                print(f"Still processing... ({elapsed_time}s elapsed)")
                print("No pages completed yet")

    # Timeout case - final check
    print(f"Timeout: Result not ready after {MAX_WAIT_TIME} seconds. Performing final check...")
    status, data, error_msg, _ = check_result(username, secret, task_id, fmt, is_final_check=True)
    
    if status == 'completed':
        print("Final check: OCR Processing completed!")
        content_to_save = data.get('content') or data.get('text') or data.get('data') or json.dumps(data, ensure_ascii=False, indent=2) if isinstance(data, dict) else str(data)
        write_result_to_file(result_path, content_to_save)
        print("--- Result Content Preview ---")
        preview_text = json.dumps(content_to_save, ensure_ascii=False, indent=2) if isinstance(content_to_save, dict) else str(content_to_save)
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
