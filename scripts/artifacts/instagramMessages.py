__artifacts_v2__ = {
    "instagramMessages": {  # This should match the function name exactly
        "name": "Instagram Archive - Messages",
        "description": "Parses Instagram messages",
        "author": "@AlexisBrignoni",
        "creation_date": "2021-08-30",
        "last_update_date": "2025-07-03",
        "requirements": "none",
        "category": "Instagram Archive",
        "notes": "",
        "paths": ('*/messages/inbox/*'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "instagram",
        "html_columns": ['Media','Reactions'],
    }
}

import os
import datetime
import json
from pathlib import Path	

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, utf8_in_extended_ascii, media_to_html

@artifact_processor
def instagramMessages(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        filename = os.path.basename(file_found)
        
        if filename.startswith('message_1.json'):
            
            with open(file_found, "r") as fp:
                deserialized = json.load(fp)
        
            participants = deserialized.get('participants')
            names = ''
            for name in participants:
                names = names + f'{name["name"]}, '
            names = names.strip()[:-1]
            names = utf8_in_extended_ascii(names)[1]
            
            for x in deserialized['messages']:
                agregator_reac = ''
                agregator = ''
                
                sender_name = x.get('sender_name', '')
                sender_name = utf8_in_extended_ascii(sender_name)[1]
                
                timestamp = x.get('timestamp_ms', '')
                
                share = x.get('share','')
                link =''
                if share:
                    link = share.get('link','')
                    share_text = share.get('share_text','')
                    share_text = utf8_in_extended_ascii(share_text)[1]
                    content_owner = share.get('original_content_owner', '')
                    content_owner = utf8_in_extended_ascii(content_owner)[1]
                    agregator = f'<a href={link} target="_blank" >{link}</><br><br>'
                    if share_text:
                        agregator = agregator + f'Shared Text: {share_text}<br><br>'
                    if content_owner:
                        agregator = agregator + f'Original Content Owner: {content_owner}'
                    
                
                reactions = x.get('reactions', '')
                if reactions:
                    counter = 0
                    agregator_reac = agregator_reac + ('<table>')
                    for reac in reactions:
                        if counter == 0:
                            agregator_reac = agregator_reac +('<tr>')
                        reaction = reac.get('reaction', '')
                        reaction = utf8_in_extended_ascii(reaction)[1]
                        actor = reac.get('actor', '')
                        actor = utf8_in_extended_ascii(actor)[1]
                            
                        counter = counter + 1
                        agregator_reac = agregator_reac + f'<td>{reaction}<br>{actor}</td>'
                        #hacer uno que no tenga html
                        if counter == 2:
                            counter = 0
                            agregator_reac = agregator_reac + ('</tr>')
                    if counter == 1:
                        agregator_reac = agregator_reac + ('</tr>')
                    agregator_reac = agregator_reac + ('</table><br>')
                
                if timestamp > 0:
                    timestamp = (datetime.datetime.fromtimestamp(int(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                content = x.get('content', '' )
                content = utf8_in_extended_ascii(content)[1]
                type = x.get('type', '')
                is_unsent = x.get('is_unsent', '')
                
                photos = x.get('photos', '')
                if photos:
                    counter = 0
                    agregator = agregator + ('<table>')
                    for pics in photos:
                        if counter == 0:
                            agregator = agregator +('<tr>')
                        pictures = pics.get('uri', '')
                        time = pics.get('creation_timestamp', '')
                        if time > 0:
                            time= (datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S'))
                        
                        thumb = media_to_html(pictures, files_found, report_folder)
                        
                        counter = counter + 1
                        agregator = agregator + f'<td>{thumb}</td>'
                        #hacer uno que no tenga html
                        if counter == 2:
                            counter = 0
                            agregator = agregator + ('</tr>')
                    if counter == 1:
                        agregator = agregator + ('</tr>')
                    agregator = agregator + ('</table><br>')
                
                videos = x.get('videos', '')
                if videos:
                    counter = 0
                    agregator = agregator + ('<table>')
                    for vids in videos:
                        if counter == 0:
                            agregator = agregator + ('<tr>')
                        movie = vids.get('uri', '')
                        time = vids.get('creation_timestamp', '')
                        if time > 0:
                            time= (datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S'))
                        
                        thumb = media_to_html(movie, files_found, report_folder)
                        
                        counter = counter + 1
                        agregator = agregator + f'<td>{thumb}</td>'
                        #hacer uno que no tenga html
                        if counter == 2:
                            counter = 0
                            agregator = agregator + ('</tr>')
                    if counter == 1:
                        agregator = agregator + ('</tr>')
                    agregator = agregator + ('</table><br>')
                        
                data_list.append((timestamp, names, sender_name, content, agregator, agregator_reac, is_unsent, type, file_found))
    
    data_headers = (('Timestamp','datetime'), 'Participants', 'Sender', 'Content', 'Media', 'Reactions', 'Is unsent', 'Type','Source File')
    return data_headers, data_list, 'See source path(s) below'