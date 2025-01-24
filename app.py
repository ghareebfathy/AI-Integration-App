# Import required libraries
import flet as ft  # GUI framework
import google.generativeai as genai  # Google's Gemini AI
import os
from dotenv import load_dotenv  # For loading environment variables
import requests  # For Hugging Face API calls
import cohere  # For Cohere API
import anthropic  # For Claude API
import replicate  # For Replicate API
import openai  # For OpenAI API
from dotenv import set_key, dotenv_values  # For updating .env file
load_dotenv()

# Environment variables configuration for API keys
API_KEY_ENV_VAR = "GEMINI_API_KEY"
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
HUGGINGFACE_API_KEY_ENV_VAR = "HUGGINGFACE_API_KEY"
COHERE_API_KEY_ENV_VAR = "COHERE_API_KEY"
CLAUDE_API_KEY_ENV_VAR = "CLAUDE_API_KEY"
REPLICATE_API_KEY_ENV_VAR = "REPLICATE_API_KEY"


def main(page: ft.Page):
    # Configure main window properties
    page.title = "AI Integration App"
    page.window.width = 550
    page.window.height = 740
    page.window.min_width = 550
    page.window.min_height = 740

    # Load API keys from environment variables
    api_keys = {
        "Gemini": os.getenv(API_KEY_ENV_VAR),
        "OpenAI": os.getenv(OPENAI_API_KEY_ENV_VAR),
        "HuggingFace": os.getenv(HUGGINGFACE_API_KEY_ENV_VAR),
        "Cohere": os.getenv(COHERE_API_KEY_ENV_VAR),
        "Claude": os.getenv(CLAUDE_API_KEY_ENV_VAR),
        "Replicate": os.getenv(REPLICATE_API_KEY_ENV_VAR),
    }

    selected_model = "Gemini"  # Default model selection

    # Create UI elements
    user_input = ft.TextField(
        label="Enter your input",
        multiline=True,
        expand=True,
        border_color="#35C1F1"
    )

    # Result display configuration
    result_output = ft.Text(value="", size=16)
    result_container = ft.Container(
        content=ft.ListView(spacing=10),
        border=ft.border.all(1, ft.Colors.GREY),
        expand=True,
        height=500,
        visible=False,
        padding=20,
        margin=ft.margin.only(left=30, right=30)
    )

    # API Key management functions
    def set_api_key_dialog(api_type):
        """Create dialog for setting API keys"""
        current_api_key = api_keys.get(api_type, "")
        dialog = ft.AlertDialog(
            title=ft.Text(f"Set {api_type} API Key"),
            content=ft.TextField(value=current_api_key if current_api_key else "", password=True,
                                 hint_text=f"Enter {api_type} API Key"),
            actions=[
                ft.TextButton(
                    "Save", on_click=lambda e: save_api_key(e, dialog, api_type)),
                ft.TextButton(
                    "Cancel", on_click=lambda e: close_dialog(dialog)),
            ],
        )
        return dialog

    def set_api_key(api_type):
        """Show API key setting dialog"""
        dialog = set_api_key_dialog(api_type)
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def save_api_key(e, dialog, api_type):
        """Save API key to environment and update .env file"""
        new_key = dialog.content.value.strip()
        if new_key:
            api_keys[api_type] = new_key
            env_var_name = f"{api_type.upper()}_API_KEY"

            # Update .env file
            set_key('.env', env_var_name, new_key)
            # Update in-memory environment
            os.environ[env_var_name] = new_key

            # Show confirmation
            snack_bar = ft.SnackBar(
                ft.Text(f"{api_type} API Key Saved Permanently!"))
            page.overlay.append(snack_bar)
            snack_bar.open = True
        else:
            # Show error for empty key
            snack_bar = ft.SnackBar(
                ft.Text(f"{api_type} API Key cannot be empty!", color="red"))
            page.overlay.append(snack_bar)
            snack_bar.open = True

        dialog.open = False
        page.update()

    # Conversation management functions
    def start_new_conversation(e):
        """Reset input and output fields"""
        user_input.value = ""
        result_output.value = ""
        result_container.visible = False
        page.update()

    # API calling function
    def call_api(event):
        """Handle API calls based on selected model"""
        input_text = user_input.value.strip()
        if not input_text:
            # Show error for empty input
            result_output.value = "Please enter some text."
            result_output.color = "red"
            result_container.visible = False
            page.update()
            return

        api_key = api_keys.get(selected_model)
        if not api_key:
            # Show error if API key not set
            result_output.value = f"{selected_model} API Key is not set in environment variables. Please set it first."
            result_output.color = "red"
            result_container.visible = False
            page.update()
            return

        try:
            # Handle different AI models
            if selected_model == "Gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(input_text)
                api_response_text = response.text

            elif selected_model == "OpenAI":
                openai.api_key = api_key
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": input_text}]
                )
                api_response_text = response.choices[0].message.content

            # ... (similar blocks for other AI services)

            # Display results with markdown formatting
            markdown_output = ft.Markdown(
                api_response_text,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme="Monokai",
            )

            # Build result row with copy button
            result_row = ft.Row(
                controls=[
                    ft.Container(content=markdown_output, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.COPY,
                        tooltip="Copy",
                        on_click=lambda e: copy_to_clipboard(e, api_response_text)
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            # Update UI with results
            result_container.content.controls = [result_row]
            result_container.visible = True
            user_input.value = ""
            page.update()

        except Exception as e:
            # Show API errors
            result_output.value = f"{selected_model} API Error: {e}"
            result_output.color = "red"
            result_container.visible = False
            page.update()

    # UI interaction functions
    def toggle_collapse(e):
        """Toggle settings menu visibility"""
        collapsed_content.visible = not collapsed_content.visible
        page.update()

    def model_changed(e):
        """Handle model selection changes"""
        nonlocal selected_model
        selected_model = model_dropdown.value
        page.update()

    # ... (remaining UI configuration code)

if __name__ == "__main__":
    ft.app(target=main)
