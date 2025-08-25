__artifacts_v2__ = {
    "snapchatconvb": {
        "name": "snapchatconvb",
        "description": "",
        "author": "Alexis Brignoni",
        "version": "0.0.1",
        "date": "2025-08-25",
        "requirements": "none",
        "category": "Snapchat Returns",
        "notes": "",
        "paths": ('*/conversations.csv','*.jpeg','*.unknown','*.mp4','*.png'),
        "output_types": "none",
        "function": "snapchatconvb",
        "output_types": "lava",
        "artifact_icon": "image",
    }
}
import os
import csv
from datetime import datetime, timezone
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows, artifact_processor, check_in_media

@artifact_processor
def snapchatconvb(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        
        if filename.startswith('conversations.csv'):
            
            headers = []
            rows = []
            legend = ''
            
            # Step 1: find the separator line
            sep_line = None
            with open(file_found, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if "=" in line and set(line.strip()) == {"="}:
                        sep_line = i
                        break
                    else:
                        legend = legend + line
                        
            # Step 2: open again, skip rows until after separator
            with open(file_found, "r", encoding="utf-8") as f:
                for _ in range(sep_line + 1):
                    next(f)  # skip lines before header
                    
                reader = csv.reader(f)
                headers = next(reader)  # first row after separator = headers
                
                # helper to find column indices
                def get_index(col_name):
                    try:
                        return headers.index(col_name)
                    except ValueError:
                        return None
                    
                # columns to reorder
                important_cols = ["timestamp", "sender_username", "recipient_username", "text", "media_id"]
                important_indices = [get_index(col) for col in important_cols]
                
                # Step 3: build reordered rows
                for row in reader:
                    reordered = []
                    for idx, col in zip(important_indices, important_cols):
                        if idx is not None and idx < len(row):
                            val = row[idx]
                            if col == "timestamp" and val.strip():
                                try:
                                    dt_obj = datetime.strptime(val, "%Y-%m-%d %H:%M:%S %Z")
                                    reordered.append(dt_obj)
                                except Exception:
                                    reordered.append(None)  # invalid timestamp
                            else:
                                reordered.append(val)
                        else:
                            reordered.append('')
                    # add remaining values
                    remaining = [val for i, val in enumerate(row) if i not in important_indices]
                    rows.append(reordered + remaining)
                    
            # Step 4: updated headers
            important_headers = [headers[i] if i is not None else "" for i in important_indices]
            remaining_headers = [col for i, col in enumerate(headers) if i not in important_indices]
            reordered_headers = important_headers + remaining_headers
            reordered_headers[0] = ('Timestamp','datetime')
            reordered_headers[4] = ('Images','media')
            
            
            for row in rows:
                if row[4] != '':
                    for tentative_media in files_found:
                        if row[4] in tentative_media:
                            media_path = Path(tentative_media)
                            filenamem = media_path.name 
                            media_item = check_in_media(tentative_media,filenamem)
                            row[4] = media_item
                            break
            for row in rows:
                logfunc(str(row))
                            
        return reordered_headers,rows,file_found
        
            
        
    