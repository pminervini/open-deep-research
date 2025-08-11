import json
import os
import shutil
import textwrap
from pathlib import Path

def get_image_description(file_name: str, question: str, visual_inspection_tool) -> str:
    prompt = f"""Write a caption of 5 sentences for this image. Pay special attention to any details that might be useful for someone answering the following question:
{question}. But do not try to answer the question directly!
Do not add any information that is not present in the image."""
    return visual_inspection_tool(image_path=file_name, question=prompt)

def get_document_description(file_path: str, question: str, document_inspection_tool) -> str:
    prompt = f"""Write a caption of 5 sentences for this document. Pay special attention to any details that might be useful for someone answering the following question:
{question}. But do not try to answer the question directly!
Do not add any information that is not present in the document."""
    return document_inspection_tool.forward_initial_exam_mode(file_path=file_path, question=prompt)

def get_single_file_description(file_path: str, question: str, visual_inspection_tool, document_inspection_tool):
    file_extension = file_path.split(".")[-1]
    if file_extension in ["png", "jpg", "jpeg"]:
        file_description = f" - Attached image: {file_path}"
        file_description += (
            f"\n     -> Image description: {get_image_description(file_path, question, visual_inspection_tool)}"
        )
        return file_description
    elif file_extension in ["pdf", "xls", "xlsx", "docx", "doc", "xml"]:
        image_path = file_path.split(".")[0] + ".png"
        if os.path.exists(image_path):
            description = get_image_description(image_path, question, visual_inspection_tool)
            file_path = image_path
        else:
            description = get_document_description(file_path, question, document_inspection_tool)
        file_description = f" - Attached document: {file_path}"
        file_description += f"\n     -> File description: {description}"
        return file_description
    elif file_extension in ["mp3", "m4a", "wav"]:
        return f" - Attached audio: {file_path}"
    else:
        return f" - Attached file: {file_path}"

def get_zip_description(file_path: str, question: str, visual_inspection_tool, document_inspection_tool):
    folder_path = file_path.replace(".zip", "")
    os.makedirs(folder_path, exist_ok=True)
    shutil.unpack_archive(file_path, folder_path)

    prompt_use_files = ""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            prompt_use_files += "\n" + textwrap.indent(
                get_single_file_description(file_path, question, visual_inspection_tool, document_inspection_tool),
                prefix="    ",
            )
    return prompt_use_files

