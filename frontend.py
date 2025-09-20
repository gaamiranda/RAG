import flet as ft
from database import DatabaseConnection
from dotenv import load_dotenv
from pdfprocessing import pdf_data_extraction
from text_handling import *
from ingest import *
import os
load_dotenv()

def functionX(file_path):
    print(file_path)
    metadata = pdf_data_extraction(file_path)
    chunks = chunk_text(metadata["content"])
    embeddings = chunks_embedding(chunks)
    DatabaseConnection().store_document_in_db(metadata, chunks, embeddings)

def functionY(user_input):
	embedding = process_query(user_input)
	similar_chunks = search_similar_chunks(embedding)
	final_answer = generate_answer(similar_chunks, user_input)
	return final_answer

def main(page: ft.Page):
    page.title = "File Processing Workflow"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    # UI Components
    status_text = ft.Text("Please select a file to start", size=16)
    file_info = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_600)
    user_input_field = ft.TextField(
        label="Enter your input",
        width=400,
        visible=False
    )
    submit_button = ft.ElevatedButton(
        "Submit Input",
        visible=False,
        icon=ft.Icons.SEND
    )
    result_text = ft.Text("", size=14, color=ft.Colors.GREEN_600, selectable=True)
    upload_button = ft.ElevatedButton(
        "Upload File",
        icon=ft.Icons.CLOUD_UPLOAD,
        visible=False
    )
    
    # Store selected files for upload
    selected_files_for_upload = []
    
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file = e.files[0]  # Take the first file
            
            # Store files for upload (web version)
            selected_files_for_upload.clear()
            selected_files_for_upload.extend(e.files)
            
            file_info.value = f"Selected: {file.name} ({file.size} bytes)"
            status_text.value = "File selected! Click 'Upload File' to process."
            upload_button.visible = True
            page.update()
        else:
            status_text.value = "No file selected"
            page.update()
    
    # Handle file upload progress
    def on_upload_progress(e: ft.FilePickerUploadEvent):
        print(f"Upload progress: {e.file_name} - Progress: {e.progress}")
        
        if e.error:
            status_text.value = f"Upload error: {e.error}"
            status_text.color = ft.Colors.RED_400
            page.update()
            return
            
        if e.progress == 1.0:  # Upload complete
            # File is now uploaded to the upload directory
            uploaded_file_path = os.path.join("uploads", e.file_name)
            print(f"Upload complete. File saved to: {uploaded_file_path}")
            
            if os.path.exists(uploaded_file_path):
                # Process the uploaded file
                status_text.value = "Processing file..."
                page.update()
                
                try:
                    # Step 1: Call functionX with the uploaded file path
                    file_result = functionX(uploaded_file_path)
                    
                    # Step 2: Show input field and ask user for input
                    status_text.value = "File processed! Please enter your input below:"
                    user_input_field.visible = True
                    submit_button.visible = True
                    upload_button.visible = False
                    
                    # Store file result for later use
                    page.session.set("file_result", file_result)
                    
                except Exception as ex:
                    status_text.value = f"Error processing file: {str(ex)}"
                    status_text.color = ft.Colors.RED_400
                
                page.update()
            else:
                status_text.value = f"Error: Uploaded file not found"
                status_text.color = ft.Colors.RED_400
                page.update()
    
    # Handle upload button click
    def upload_files(e):
        if selected_files_for_upload:
            upload_list = []
            for f in selected_files_for_upload:
                upload_list.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=page.get_upload_url(f.name, 600),
                    )
                )
            
            status_text.value = "Uploading file..."
            upload_button.visible = False
            page.update()
            
            file_picker.upload(upload_list)
        else:
            status_text.value = "No files selected for upload"
            page.update()
    
    # Handle file picker button click
    def pick_files_handler(e):
        try:
            file_picker.pick_files(
                dialog_title="Select a file to process",
                allow_multiple=False
            )
        except Exception as ex:
            status_text.value = f"Error opening file picker: {str(ex)}"
            status_text.color = ft.Colors.RED_400
            page.update()
    
    # Create file picker
    file_picker = ft.FilePicker(
        on_result=on_file_result,
        on_upload=on_upload_progress
    )
    page.overlay.append(file_picker)
    page.update()
    
    # Handle user input submission
    def on_submit_input(e):
        user_input = user_input_field.value.strip()
        if not user_input:
            user_input_field.error_text = "Please enter some input"
            page.update()
            return
        
        user_input_field.error_text = None
        status_text.value = "Processing your input..."
        submit_button.disabled = True
        page.update()
        
        # Step 3: Call functionY with file result and user input
        try:
            file_result = page.session.get("file_result")
            final_result = functionY(user_input)
            
            # Step 4: Show the result
            result_text.value = final_result
            status_text.value = "Complete! Result:"
            status_text.color = ft.Colors.GREEN_600
            
            # Reset for next use
            reset_button.visible = True
            
        except Exception as ex:
            status_text.value = f"Error processing input: {str(ex)}"
            status_text.color = ft.Colors.RED_400
        finally:
            submit_button.disabled = False
        
        page.update()
    
    # Reset function for new workflow
    def reset_workflow(e):
        status_text.value = "Please select a file to start"
        status_text.color = None
        file_info.value = ""
        user_input_field.value = ""
        user_input_field.visible = False
        user_input_field.error_text = None
        submit_button.visible = False
        result_text.value = ""
        reset_button.visible = False
        upload_button.visible = False
        selected_files_for_upload.clear()
        page.session.clear()
        page.update()
    
    submit_button.on_click = on_submit_input
    user_input_field.on_submit = on_submit_input
    upload_button.on_click = upload_files
    
    reset_button = ft.ElevatedButton(
        "Start Over",
        icon=ft.Icons.REFRESH,
        visible=False,
        on_click=reset_workflow
    )
    
    # Layout
    page.add(
        ft.Column([
            ft.Text("File Processing Workflow", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Web Version - Upload Required", size=12, color=ft.Colors.GREY),
            ft.Divider(),
            
            # Step 1: File selection and upload
            ft.ElevatedButton(
                "Select File",
                icon=ft.Icons.UPLOAD_FILE,
                on_click=pick_files_handler
            ),
            upload_button,
            file_info,
            
            ft.Divider(),
            
            # Status and progress
            status_text,
            
            # Step 2: User input
            user_input_field,
            submit_button,
            
            ft.Divider(),
            
            # Step 4: Results
            result_text,
            reset_button,
            
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Create uploads directory for web mode
if not os.path.exists("uploads"):
    os.makedirs("uploads")

if __name__ == "__main__":
    # Force web mode with uploads enabled
    ft.app(target=main, view=ft.WEB_BROWSER, upload_dir="uploads")