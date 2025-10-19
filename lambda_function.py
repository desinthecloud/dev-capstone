import boto3
import os
import json
import secrets
from botocore.exceptions import ClientError

# Initialize the S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Received event:", event)  # Log the received event
    # Check if the request is for generating a pre-signed URL
    if event.get('rawPath', '/') == '/generate-presigned-url':
        return generate_presigned_url(event)  # Pass the event here
    
    # For other requests, serve static files
    return serve_static_file(event)
    
def generate_presigned_url(event):
    upload_bucket = os.environ['UPLOAD_BUCKET']
    
    # Generate a secure random 12-character string for the object key
    object_key = f"uploads/{secrets.token_urlsafe(12)}"
    
    content_type = event['queryStringParameters'].get('content-type', 'binary/octet-stream')
    expiration = 3600
    try:
        response = s3.generate_presigned_url('put_object',
                                             Params={'Bucket': upload_bucket,
                                                     'Key': object_key,
                                                     'ContentType': content_type},
                                             ExpiresIn=expiration)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'upload_url': response})
        }
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error generating pre-signed URL'})
        }

def serve_static_file(event):
    # Extract the requested file name from the event's rawPath
    raw_path = event.get('rawPath', '/')
    file_name = raw_path.split('/')[-1] if raw_path != '/' else 'upload.html'
    print(f"Requested file: {file_name}")  # Log the requested file name
    
    # Handle favicon.ico gracefully - return 204 No Content
    if file_name == 'favicon.ico':
        print("Favicon requested but not available, returning 204 No Content")
        return {
            'statusCode': 204,
            'headers': {'Content-Type': 'image/x-icon'},
            'body': ''
        }
    
    # Determine the content type based on the file extension
    content_type = "text/html"
    if file_name.endswith('.js'):
        content_type = "application/javascript"
    elif file_name.endswith('.css'):
        content_type = "text/css"
    print(f"Content-Type set to: {content_type}")  # Log the determined content type
    
    # Use the environment variable to get the bucket name for website assets
    bucket_name = os.environ['WEBSITE_ASSETS_BUCKET']
    print(f"Fetching '{file_name}' from bucket '{bucket_name}'")  # Log the S3 get_object request
    
    try:
        # Fetch the requested file from the S3 bucket
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        file_content = response['Body'].read().decode('utf-8')
        
        # Return the file content in the response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': content_type},
            'body': file_content,
            'isBase64Encoded': False
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            print(f"File '{file_name}' not found in S3, returning 404")
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/plain'},
                'body': f"File '{file_name}' not found"
            }
        else:
            print(f"Error fetching '{file_name}' from S3: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'text/plain'},
                'body': 'Error fetching file from S3'
            }
    except Exception as e:
        print(f"Unexpected error fetching '{file_name}' from S3: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Error fetching file from S3'
        }
