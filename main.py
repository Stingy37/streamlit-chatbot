import logging
import json
import streamlit as st
import openai
import os
import PyPDF2
import io
import sqlite3
import base64  # For base64 encoding
import pytesseract  # For OCR
from PIL import Image  # For image handling
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 


if 'logging_initialized' not in st.session_state:
    # Indicate that logging has been initialized
    st.session_state.logging_initialized = True

    # Remove the existing log file to reset it
    if os.path.exists('app.log'):
        os.remove('app.log')

    # Reset logging handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        filename='app.log',
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


# Function to set custom backgrounds and styles
def set_custom_background():
   # Background image path
   background_image_path = '/Users/andyshi/Documents/gpt_o1_access/background_art/background_2.jpg'


   # Encode the background image
   @st.cache_data
   def get_base64_image(image_file):
       with open(image_file, 'rb') as f:
           data = f.read()
       return base64.b64encode(data).decode()


   img_base64 = get_base64_image(background_image_path)


   # Custom CSS
   custom_css = f'''
   <style>
   /* Set the background for the entire app */
   .stApp {{
       background: url("data:image/jpg;base64,{img_base64}") no-repeat center center fixed;
       background-size: 115%; 
       background-position: 0px center;
   }}
   /* Keep the main content area's default background */
   .block-container {{
       background-color: rgba(14,17,23,0.2);  /* Default dark theme background color with 0.5 opacity */
       position: relative;
       padding-top: 2rem;
       backdrop-filter: blur(30px);
   }}
   /* Gradient transition */
   .block-container::before {{
       content: "";
       position: absolute;
       top: 0;
       left: -15%;
       width: 130%;
       height: 100%;
       background: linear-gradient(to right, rgba(0,0,0,0), rgba(14,17,23,0.5) 20%, rgba(14,17,23,0.5) 80%, rgba(0,0,0,0));
       pointer-events: none;
       backdrop-filter: blur(10px);
   }}
   </style>
   '''
  
   st.markdown(custom_css, unsafe_allow_html=True)


   hide_streamlit_style = """
           <style>
           /* Hide Streamlit header */
           header {visibility: hidden;}
           /* Hide Streamlit hamburger menu */
           #MainMenu {visibility: hidden;}
           </style>
           """
  
   st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Call the function to set custom backgrounds and styles
set_custom_background()


# Initialize the database
def init_db():
   conn = sqlite3.connect("chat_history.db")
   cursor = conn.cursor()


   # Create chats table
   cursor.execute("""
       CREATE TABLE IF NOT EXISTS chats (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT NOT NULL,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       );
   """)


   # Create messages table
   cursor.execute("""
       CREATE TABLE IF NOT EXISTS messages (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           chat_id INTEGER,
           role TEXT,
           content TEXT,
           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY(chat_id) REFERENCES chats(id)
       );
   """)


   conn.commit()
   conn.close()


init_db()


# Initialize session state
if "model" not in st.session_state:
   st.session_state.model = "gpt-4-turbo"  # Default model


if "document_text" not in st.session_state:
   st.session_state.document_text = {}  # Use a dictionary to store document texts per chat_id


if "active_chat_id" not in st.session_state:
   st.session_state.active_chat_id = None


# Sidebar for chat sessions
st.sidebar.title("Chat Sessions")


# Connect to the database
conn = sqlite3.connect("chat_history.db")
cursor = conn.cursor()


# Fetch all chats
cursor.execute("SELECT id, name FROM chats ORDER BY created_at DESC")
chats = cursor.fetchall()


chat_names = [chat[1] for chat in chats]
chat_ids = [chat[0] for chat in chats]


# Select or create a chat
if chats:
   selected_chat_index = st.sidebar.selectbox(
       "Select a chat session",
       range(len(chat_names)),
       format_func=lambda idx: chat_names[idx],
   )
   st.session_state.active_chat_id = chat_ids[selected_chat_index]
else:
   st.session_state.active_chat_id = None
   st.sidebar.info("No chat sessions. Create a new one below.")


# Button to create a new chat
new_chat_name = st.sidebar.text_input("New chat name")
if st.sidebar.button("Create New Chat"):
   if new_chat_name.strip():
       # Connect to the database
       conn = sqlite3.connect("chat_history.db")
       cursor = conn.cursor()


       # Check if the chat name already exists
       cursor.execute("SELECT id FROM chats WHERE name = ?", (new_chat_name.strip(),))
       existing_chat = cursor.fetchone()


       if existing_chat:
           st.sidebar.error("A chat with that name already exists. Please choose another name.")
       else:
           cursor.execute("INSERT INTO chats (name) VALUES (?)", (new_chat_name.strip(),))
           conn.commit()
           st.sidebar.success(f"Chat '{new_chat_name}' created.")
           st.session_state.active_chat_id = cursor.lastrowid  # Set the new chat as active
           st.session_state.messages = []  # Clear messages for the new chat
           st.rerun()


       # Close the database connection
       conn.close()
   else:
       st.sidebar.error("Please enter a chat name.")


# Delete chat
if st.session_state.active_chat_id:
   if st.sidebar.button("Delete Chat"):
       chat_id = st.session_state.active_chat_id
       conn = sqlite3.connect("chat_history.db")
       cursor = conn.cursor()
       cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
       cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
       conn.commit()
       conn.close()
       st.sidebar.success("Chat deleted.")
       # Remove document_text for this chat
       if chat_id in st.session_state.document_text:
           del st.session_state.document_text[chat_id]
       st.session_state.active_chat_id = None
       st.session_state.messages = []
       st.rerun()


# Rename chat
if st.session_state.active_chat_id:
   rename_chat_name = st.sidebar.text_input("Rename chat")
   if st.sidebar.button("Rename"):
       if rename_chat_name.strip():
           conn = sqlite3.connect("chat_history.db")
           cursor = conn.cursor()
           cursor.execute("""
               UPDATE chats SET name = ? WHERE id = ?
           """, (rename_chat_name.strip(), st.session_state.active_chat_id))
           conn.commit()
           conn.close()
           st.sidebar.success("Chat renamed.")
           st.rerun()
       else:
           st.sidebar.error("Please enter a valid chat name.")


# Close the database connection
conn.close()


# Load messages for the active chat
def load_chat_messages(chat_id):
   conn = sqlite3.connect("chat_history.db")
   cursor = conn.cursor()
   cursor.execute("""
       SELECT role, content FROM messages
       WHERE chat_id = ?
       ORDER BY timestamp ASC
   """, (chat_id,))
   messages = cursor.fetchall()
   conn.close()
   return [{"role": role, "content": content} for role, content in messages]


if st.session_state.active_chat_id:
   st.session_state.messages = load_chat_messages(st.session_state.active_chat_id)
else:
   st.session_state.messages = []


# File uploader for PDFs, .py files, and images
uploaded_file = st.file_uploader(" ", type=["pdf", "py", "png", "jpg", "jpeg"])


# Handle file upload
if uploaded_file is not None and st.session_state.active_chat_id:
   chat_id = st.session_state.active_chat_id
   file_extension = os.path.splitext(uploaded_file.name)[1].lower()
   if file_extension == ".pdf":
       # Use PyPDF2 to read the PDF file
       pdf_reader = PyPDF2.PdfReader(uploaded_file)
       text = ""
       for page_num in range(len(pdf_reader.pages)):
           page = pdf_reader.pages[page_num]
           text += page.extract_text()
       # Store the extracted text for this chat session
       st.session_state.document_text[chat_id] = text
       st.success("PDF text extracted and stored.")
   elif file_extension == ".py":
       # Read the .py file
       code = uploaded_file.getvalue().decode("utf-8")
       # Store the code for this chat session
       st.session_state.document_text[chat_id] = code
       st.success(".py file code extracted and stored.")
   elif file_extension in [".png", ".jpg", ".jpeg"]:
       # Use PIL and pytesseract to read the image and extract text
       try:
           image = Image.open(uploaded_file)
           extracted_text = pytesseract.image_to_string(image)
           if extracted_text.strip():
               # Store the extracted text for this chat session
               st.session_state.document_text[chat_id] = extracted_text
               st.success("Text extracted from image and stored.")
           else:
               st.warning("No text found in the image.")
       except Exception as e:
           st.error(f"An error occurred while processing the image: {e}")
   else:
       st.error("Unsupported file type. Please upload a PDF, .py file, or an image.")


def handle_user_input():
    user_input = st.session_state.input_box
    if user_input.strip() and st.session_state.active_chat_id:
        chat_id = st.session_state.active_chat_id
        # Add user message to session state
        user_message = {"role": "user", "content": user_input.strip()}
        st.session_state.messages.append(user_message)
        # Save user message to the database
        conn = sqlite3.connect("chat_history.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)
        """, (chat_id, user_message["role"], user_message["content"]))
        conn.commit()
        conn.close()
        # Prepare messages for the API call
        messages = []
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            if role == "user":
                # Get the document_text specific to the current chat_id
                document_text = st.session_state.document_text.get(chat_id, "")
                if document_text:
                    user_input_with_context = (
                        f"Answer my question based on the following text:\n\n"
                        f"{document_text}\n\n"
                        f"Here's my question: {content}\n\n"
                        f"Finally, here are some more instructions for you to format your answer in, which you may ignore if not necessary:\n\n"
                        f"1. If your answer contains mathematical terms, you must enclose ANY AND ALL expressions within $$ for proper rendering. For example, $$ MATH_TERM $$."
                        f"1a. Also, anything with subscripts or superscripts must be enclosed similarly within $$ __ $$, like Zeff for ENC\n\n"
                    )
                else:
                    user_input_with_context = (
                        f"Here's my question: {content}\n\n"
                        f"Here are some more instructions for you to format your answer in, which you may ignore if not necessary:\n\n"
                        f"1. If your answer contains mathematical terms, you must enclose ANY AND ALL expressions within $$ for proper rendering. For example, $$ MATH_TERM $$."
                        f"1a. Also, anything with subscripts or superscripts must be enclosed similarly within $$ __ $$, like Zeff for ENC\n\n"
                    )
                messages.append({"role": role, "content": user_input_with_context})
            else:
                messages.append(message)
        # Log the messages being sent to the API
        logging.info(f"Sending messages to OpenAI API:\n{json.dumps(messages, indent=2)}")
        try:
            # Generate GPT response
            with st.spinner("Assistant is typing..."):
                response = openai.ChatCompletion.create(
                    model=st.session_state.model,
                    messages=messages,
                )
            reply = response["choices"][0]["message"]["content"]
            assistant_message = {"role": "assistant", "content": reply}
            st.session_state.messages.append(assistant_message)
            # Save assistant message to the database
            conn = sqlite3.connect("chat_history.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)
            """, (chat_id, assistant_message["role"], assistant_message["content"]))
            conn.commit()
            conn.close()
        except Exception as e:
            # Handle exception
            error_message = {"role": "assistant", "content": f"Error: {e}"}
            st.session_state.messages.append(error_message)
            # Save error message to the database
            conn = sqlite3.connect("chat_history.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)
            """, (chat_id, error_message["role"], error_message["content"]))
            conn.commit()
            conn.close()
        # Clear input box
        st.session_state.input_box = ""
    else:
        st.error("Please select or create a chat session.")
        

# Display chat history
for message in st.session_state.messages:
   with st.chat_message(message["role"]):
       if message["role"] == "user":
           st.text(message["content"])
       else:
           st.markdown(message["content"])


input_height = 225 if len(st.session_state.messages) == 0 else 100


# Message input and send button
st.text_area(
   "Type your message here:",
   key="input_box",
   height=input_height,
)


st.selectbox(
   "Choose a model:",
   options=["o1-preview", "gpt-4-turbo", "o1-mini"],
   key="model",
)


st.button("Send", on_click=handle_user_input, disabled=not st.session_state.active_chat_id)

