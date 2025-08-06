__artifacts_v2__ = {
    "frames": {
        "name": "Frames",
        "description": "Counts video frames",
        "author": "@AlexisBrignoni",
        "creation_date": "2025-08-06",
        "last_update_date": "2025-08-06",
        "requirements": "none",
        "category": "Video",
        "notes": "",
        "paths": ('*/*.*'),
        "output_types": "standard",
        "artifact_icon": "twitter",
    }
}

    
import cv2
import inspect
import os
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows, artifact_processor, check_in_media

def count_video_frames(video_path):
    """
    Counts the total number of frames in a given video file.

    Args:
        video_path (str): The path to the video file.

    Returns:
        int: The total number of frames in the video, or -1 if an error occurs.
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return -1
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frame_count

@artifact_processor
def frames(files_found, report_folder, seeker, wrap_text):
    artifact_info = inspect.stack()[0]
    data_list = []
    allframes = 0
    
    for file_found in files_found:
        file_found = str(file_found)
        
        filename = os.path.basename(file_found)
        
        if filename.startswith('.'):
            pass
        
        else:
            total_frames = count_video_frames(file_found)
            
            if total_frames != -1:
                
                for tentative_media in files_found:
                    if filename in tentative_media:
                        media_path = Path(tentative_media )
                        
                        filenamem = (media_path.name)
                        filepath = str(media_path.parents[1])
                        
                        #logfunc(f'{filename}-{artifact_info}')
                        media_item = check_in_media(tentative_media, filenamem)
                        break
                    
                data_list.append((media_item,filename, total_frames,file_found))
                logfunc(f"The video '{filename}' contains {total_frames} frames.")
                allframes = allframes + total_frames
                
        
            
    data_headers = (('Image', 'media'),'Filename','Total Frames','File Source')
    
    return data_headers, data_list, f'Total frames for all media: {allframes}'

