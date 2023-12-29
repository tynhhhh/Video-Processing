from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
from pydub import AudioSegment
from django.conf import settings
import librosa
import os
import cv2
from api.models import Subclips, ParentFolder
import random
import numpy as np
from joblib import Parallel, delayed
from tempfile import NamedTemporaryFile
from django.core.files.uploadedfile import TemporaryUploadedFile

def output_path(parent_folder_name, folder_name, output_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    media_subvid_folder = os.path.join(settings.MEDIA_ROOT, parent_folder_name, folder_name)
    outputname = str(output_name).split('.')[0]
    unique_name = f'{outputname}_{timestamp}'
    
    path = os.path.join(media_subvid_folder, f"{unique_name}_.mp4")
    os.makedirs(media_subvid_folder, exist_ok=True)
    return path

def TypeChecker_CV2(file_clip):
    if isinstance(file_clip, str):
        return cv2.VideoCapture(file_clip)
    elif hasattr(file_clip, 'temporary_file_path'):
        return cv2.VideoCapture(file_clip.temporary_file_path())
    else:
        raise ValueError("Invalid file_clip argument")

def TypeChecker_MVP(file_clip):
    if isinstance(file_clip, TemporaryUploadedFile):
        # Use the temporary file directly
        clip = file_clip.temporary_file_path() if hasattr(file_clip, 'temporary_file_path') else None
    else:
        clip = file_clip
    return clip

def ListChecker(file_clip):
    if type(file_clip) is not list:
        return list([file_clip])

def WriteVideo(video_frames, path, fps=None):

    if not fps:
        video_frames.write_videofile(path, codec='libx264', audio_codec='aac')
    else:
        video_frames.write_videofile(path, codec="libx264", audio_codec="aac", fps=fps)



# API cutting original video into sub videos
def AutoCutting(file_clips, dur_input):
    file_clips = ListChecker(file_clips)

    for a_clip in file_clips:
        a_clip_name = TypeChecker_MVP(a_clip)
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

                path = output_path('subvid', folder_name, output_name)

                sub_clip.write_videofile(path, codec='libx264')

            clip.close()

            


from moviepy.editor import VideoFileClip
from django.core.files.storage import default_storage
import tempfile


# API inserting logo
def InsertLogo(file_clip, logo, position='top-left'):
    vid = TypeChecker_CV2(file_clip)

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

        output_name = f'logo_inserted_{file_name}'
        path = output_path('logovid',folder_name, output_name)
        
        
        return video_clip, path


# API concatenator
def ResolutionChanger(video_file,target_resolution = (1920,1080)):       
    cap = TypeChecker_CV2(video_file)

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
        # Change "frame" into "img_with_border_rgb" get concatenate original color and the same resolution (1920,1080)
        all_frames.append(frame) # img_with_border_rgb

        perc = round(i / int(frame_count) * 100, 2)

        print(f'Processing... {perc}%')
        i += 1
    
    audio_temp_path = video_file.temporary_file_path()
    with ImageSequenceClip(all_frames, fps=fps) as video_clip:
        audio = AudioFileClip(audio_temp_path)
        video_clip = video_clip.set_audio(audio)
        return video_clip

def VideoConcatenator(video_files):
    concat_frames = [ResolutionChanger(video) for video in video_files]

    # Combine the clips into a single concatenated clip
    final_clip = concatenate_videoclips(concat_frames, method="compose")

    # Extract the base filename from the first video file
    if video_files and isinstance(video_files[0], TemporaryUploadedFile):
        filename = os.path.splitext(video_files[0].name)[0]
        output_name = f'concatenated_video_{filename}.mp4'
    else:
        output_name = 'concatenated_video.mp4'

    path = output_path('concatvid', filename, output_name)

    return final_clip, path

# API bluring video

def process_frame_parallel(frame, blur_strength=15):
    # Apply Gaussian blur to the frame
    blurred_frame = cv2.GaussianBlur(frame, (blur_strength, blur_strength), 0)
    return blurred_frame

from datetime import datetime



def BluringVideo(video_file, blur_strength=15, num_jobs=-1):
    vid = TypeChecker_MVP(video_file)
    if not vid:
        return 0
    
    video_clip = VideoFileClip(vid)
    fps=video_clip.fps
    # Process frames in parallel
    processed_frames = Parallel(n_jobs=num_jobs, backend='threading')(
        delayed(process_frame_parallel)(frame, blur_strength) for frame in video_clip.iter_frames()
    )

    with ImageSequenceClip(processed_frames, fps=fps) as blurred_clip:
        audio = AudioFileClip(video_file.temporary_file_path())
        blurred_clip = blurred_clip.set_audio(audio)

        outputname = video_file.name
        foldername = os.path.splitext(outputname)[0]
        path = output_path('blurvid', foldername, outputname)

        return blurred_clip, path


def ChangingSpeed(video_file, speed_factor):
    video_path = TypeChecker_MVP(video_file)  # Corrected from 'video_path' to 'video_file'
    if not video_path:
        return 0

    video_name = os.path.basename(video_path)
    output_name = f'sc_{video_name}'

    clip = VideoFileClip(video_path)
    fps=clip.fps
    # Speed up the video by a factor of 2
    speedup_clip = clip.fx(vfx.speedx, speed_factor)

    # Extract audio from the original video
    original_audio = clip.audio

    # Save the audio to a temporary WAV file
    temp_audio_name = 'temp_file.wav'
    temp_audio_path = os.path.join(settings.TEMP_DIR, temp_audio_name)

    original_audio.write_audiofile(temp_audio_path, codec='pcm_s16le', fps=original_audio.fps)

    # Load the audio using librosa
    song, fs = librosa.load(temp_audio_path)

    # Use librosa to stretch the audio without changing pitch
    song_2_times_faster = librosa.effects.time_stretch(song, rate=speed_factor)

    # Convert the NumPy array to an AudioSegment using pydub
    audio_segment = AudioSegment(
        np.array(np.int16(song_2_times_faster * 32767), dtype=np.int16).tobytes(),
        frame_rate=fs,
        sample_width=2,
        channels=1
    )
    audio_segment.export(temp_audio_path)

    audio = AudioFileClip(temp_audio_path)
    # Set the sped-up audio to the video clip
    final_clip = speedup_clip.set_audio(audio)

    # Export the final video
    path = output_path('scvid', video_name, output_name)
    # final_clip.write_videofile(path, codec="libx264", audio_codec="aac", fps=clip.fps)

    # Close the video clips
    clip.close()
    speedup_clip.close()
    final_clip.close()
    os.remove(temp_audio_path)
    print(final_clip)
    return final_clip, path, fps


