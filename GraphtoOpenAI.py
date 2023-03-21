# Install required packages
# Microsoft Graph Python SDK for interacting with OneNote
# OpenAI Python library for interacting with OpenAI API
pip install msgraph-sdk
pip install openai

# Import required libraries
import os
import openai
from msgraph.core import GraphClient, SDKClientException
from msgraph.auth_provider import DeviceCodeAuthProvider

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up Microsoft Graph API credentials from environment variables
CLIENT_ID = os.getenv("MS_GRAPH_CLIENT_ID")
CLIENT_SECRET = os.getenv("MS_GRAPH_CLIENT_SECRET")
TENANT_ID = os.getenv("MS_GRAPH_TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# Function to get an authenticated Graph client
def get_authenticated_client():
    # Set up the authentication provider
    auth_provider = DeviceCodeAuthProvider(CLIENT_ID, CLIENT_SECRET, AUTHORITY, SCOPE)
    # Create and return the Graph client
    graph_client = GraphClient(auth_provider)
    return graph_client

# Function to generate a response using the OpenAI API
def generate_response(prompt):
    # Make the API request with the provided prompt
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    # Return the generated text
    return response.choices[0].text.strip()

# Function to create a new OneNote notebook and a page with the generated response
def create_notebook_and_page(graph_client, notebook_name, page_title, prompt):
    # Prepare the notebook data
    notebook_data = {
        "displayName": notebook_name
    }
    # Create the notebook
    notebook = graph_client.me.onenote.notebooks.create(notebook_data).execute()

    # Generate a response using the OpenAI API
    generated_response = generate_response(prompt)

    # Create the page HTML with the generated response
    page_html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{page_title}</title>
            </head>
            <body>
                <p>{generated_response}</p>
            </body>
        </html>
    """

    # Set the content type for the page request
    headers = {
        "Content-Type": "application/xhtml+xml"
    }

    # Get the section ID and create the page
    section_id = notebook.sections[0].id
    page = graph_client.me.onenote.sections[section_id].pages.create(page_html, headers=headers).execute()

    # Return the created notebook and page
    return notebook, page

# Main execution
if __name__ == "__main__":
    # Get the authenticated Graph client
    graph_client = get_authenticated_client()

    # Set notebook name, page title, and prompt
    notebook_name = "OpenAI Responses"
    page_title = "Generated Response Example"
    prompt = "Your OpenAI API prompt goes here"

    # Create the notebook and page
    notebook, page = create_notebook_and_page(graph_client, notebook_name, page_title, prompt)

    # Print the results
    print(f"Created a new notebook '{notebook.displayName}' with a page titled '{page.title}'")
