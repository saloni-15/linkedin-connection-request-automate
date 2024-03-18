from dotenv import load_dotenv
import os

load_dotenv()

def message_to_recruiter(connection_name, company_name):
    file_path = "message.txt"
    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read the entire contents of the file as a string
            text = file.read()
            formatted_text = text.format(connection_name=connection_name, company_name=company_name, resume_link=os.getenv('RESUME_LINK'))
        return formatted_text
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None