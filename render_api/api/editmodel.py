from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip, concatenate_videoclips
from django.conf import settings
import os
import cv2
from api.models import Subclips, ParentFolder
import random
import numpy as np

from django.core.files.uploadedfile import TemporaryUploadedFile

def AutoCutting(file_clip, dur_input):
    if type(file_clip) is not list:
        file_clip = list([file_clip])

    for a_clip in file_clip:
        if isinstance(a_clip, TemporaryUploadedFile):
            # Use the temporary file directly
            a_clip_name = a_clip.temporary_file_path() if hasattr(a_clip, 'temporary_file_path') else None
        else:
            a_clip_name = a_clip

        if a_clip_name:
            clip = VideoFileClip(a_clip_name)

            video_name = a_clip.name.split('.')[0]
            clip_duration = clip.duration
            num_subclips = int(clip_duration / dur_input)

            # Create a ParentFolder if it doesn't exist for this video
            folder_name = video_name
            parent_folder, created = ParentFolder.objects.get_or_create(title=folder_name)
            

            for i in range(num_subclips):
                start = i * dur_input
                end = min((i + 1) * dur_input, clip_duration)
                output_name = f"edited_{video_name}_output_{i}.mp4"
                sub_clip = clip.subclip(start, end)

                if i == num_subclips - 1:
                    remaining_duration = clip_duration - end
                    if remaining_duration > 0:
                        sub_clip = sub_clip.set_duration(sub_clip.duration + remaining_duration)

                # Determine the relative path to the subclip within the subvid directory
                subclip_relative_path = os.path.join(folder_name, output_name)

                # Create a Subclips instance with the relative path and save it
                subclip = Subclips(subclip_file=subclip_relative_path, duration=sub_clip.duration, parent_clip=parent_folder)
                subclip.save()

                # Define the absolute file path to save the subclip
                media_subvid_folder = os.path.join(settings.MEDIA_ROOT, 'subvid', folder_name)
                path = os.path.join(media_subvid_folder, output_name)

                os.makedirs(media_subvid_folder, exist_ok=True)

                sub_clip.write_videofile(path, codec='libx264')

            clip.close()


from moviepy.editor import VideoFileClip
from django.core.files.storage import default_storage
import tempfile



def InsertLogo(file_clip, logo, position='top-left'):
    if isinstance(file_clip, str):
        vid = cv2.VideoCapture(file_clip)
    elif hasattr(file_clip, 'temporary_file_path'):
        vid = cv2.VideoCapture(file_clip.temporary_file_path())
    else:
        raise ValueError("Invalid file_clip argument")

    media_logovid_folder = os.path.join(settings.MEDIA_ROOT, 'logovid')
    file_name = os.path.splitext(file_clip.name)[0]
    folder_name = file_name
    fps = vid.get(cv2.CAP_PROP_FPS)
    
    ret, frame = vid.read()
    y_vid, x_vid, _ = frame.shape 

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_logo:
        temp_logo.write(logo.read())
        logo_path = temp_logo.name

    if not os.path.isfile(logo_path):
        raise ValueError(f"Invalid logo file: {logo_path}")

    logo_img = cv2.imread(logo_path)
    r_logo = cv2.resize(logo_img, (120, 80))
    height, width, _ = r_logo.shape

    if isinstance(file_clip, str):
        file_name = os.path.basename(file_clip)
    elif isinstance(file_clip, TemporaryUploadedFile):
        file_name = file_clip.name
    else:
        raise ValueError("Invalid file_clip argument")

    valid_video_extensions = ('.mp4', '.avi', '.mkv')
    if any(file_name.lower().endswith(ext) for ext in valid_video_extensions):
        pass
    else:
        raise ValueError(f"Invalid video file: {file_name}")

    logo_position_x, logo_position_y = 0, 0

    y_vid_split = y_vid//3
    x_vid_split = x_vid//3

    base_position = 10
    
    match position:
        case 1, _:
            logo_position_x, logo_position_y = random.randint(base_position, x_vid_split), random.randint(base_position, y_vid_split)
        case 2:
            logo_position_x, logo_position_y = random.randint(x_vid_split, x_vid_split*2), random.randint(base_position, y_vid_split)
        case 3:
            logo_position_x, logo_position_y = random.randint(x_vid_split*2, x_vid_split*3), random.randint(base_position, y_vid_split)
        case 4:
            logo_position_x, logo_position_y = random.randint(base_position, x_vid_split), random.randint(y_vid_split, y_vid_split*2)
        case 5:
            logo_position_x, logo_position_y = random.randint(x_vid_split, x_vid_split*2), random.randint(y_vid_split, y_vid_split*2)
        case 6:
            logo_position_x, logo_position_y = random.randint(x_vid_split*2, x_vid_split*3), random.randint(y_vid_split, y_vid_split*2)    
        case 7:
            logo_position_x, logo_position_y = random.randint(base_position, x_vid_split), random.randint(y_vid_split*2, y_vid_split*3)
        case 8:
            logo_position_x, logo_position_y = random.randint(x_vid_split, x_vid_split*2), random.randint(y_vid_split*2, y_vid_split*3)
        case 9:
            logo_position_x, logo_position_y = random.randint(x_vid_split*2, x_vid_split*3), random.randint(y_vid_split*2, y_vid_split*3)        

    ret, frame = vid.read()
    all_frames = []

    while ret:
        ret, frame = vid.read()
        if not ret:
            break

        roi = frame[logo_position_y:logo_position_y + height, logo_position_x:logo_position_x + width]
        result = cv2.add(roi, r_logo)
        frame[logo_position_y:logo_position_y + height, logo_position_x:logo_position_x + width] = result
        all_frames.append(frame)

    all_frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in all_frames]

    # Convert into a video using a with statement
    with ImageSequenceClip(all_frames_rgb, fps=fps) as video_clip:
        audio = AudioFileClip(file_clip.temporary_file_path())
        video_clip = video_clip.set_audio(audio)
       
        os.remove(logo_path)

        media_subvid_folder = os.path.join(settings.MEDIA_ROOT, 'logovid', folder_name)
        output_name = f'logo_inserted_{file_name}'
        path = os.path.join(media_subvid_folder, output_name)
        
        os.makedirs(media_subvid_folder, exist_ok=True)
        
        video_clip.write_videofile(path, codec='libx264')

def ResolutionChanger(video_file,target_resolution = (1920,1080)):       
    if isinstance(video_file, str):
        cap = cv2.VideoCapture(video_file)
    elif hasattr(video_file, 'temporary_file_path'):
        cap = cv2.VideoCapture(video_file.temporary_file_path())
    else:
        raise ValueError("Invalid video_file argument")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    target_width, target_height = target_resolution[0], target_resolution[1]

    res_scale = target_height / height

    scale_width, scale_height = int(width * res_scale), int(height * res_scale)
    if scale_width % 2 != 0:
        scale_width -= 1

    black_side = (target_width - scale_width) // 2
    side_border = np.zeros((scale_height, black_side, 3), dtype=np.uint8)


    all_frames = []

    i = 1
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        n_frame = cv2.resize(frame, (scale_width, scale_height))
        img_with_border = np.concatenate((side_border, n_frame, side_border), axis=1)

        # Convert from BGR to RGB
        img_with_border_rgb = cv2.cvtColor(img_with_border, cv2.COLOR_BGR2RGB)

        all_frames.append(frame)

        perc = round(i / int(frame_count) * 100, 2)
        

        # out.write(img_with_border_rgb)
        print(f'Processing... {perc}%')
        i += 1
    
    audio_temp_path = video_file.temporary_file_path()
    with ImageSequenceClip(all_frames, fps=fps) as video_clip:
        audio = AudioFileClip(audio_temp_path)
        video_clip = video_clip.set_audio(audio)
        return video_clip

def VideoConcatenator(video_files):
    concat_frames = [ResolutionChanger(video) for video in video_files]
    final_clip = concatenate_videoclips(concat_frames, method="compose")

    media_subvid_folder = os.path.join(settings.MEDIA_ROOT, 'concatvid')

    filename = str(video_files[0].name).split('.')[0]
    output_name = f'concatenated_video_{filename}.mp4'

    path = os.path.join(media_subvid_folder, output_name)
    

    final_clip.write_videofile(path, codec="libx264", audio_codec="aac")
    
    return final_clip