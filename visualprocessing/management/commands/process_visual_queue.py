import os
from pathlib import Path
import psutil
import ffmpeg
from PIL import Image, ExifTags
from django.core.management.base import BaseCommand
from django.conf import settings
from visualprocessing.models import VisualsQueue


HORIZONTAL = 960
VERTICAL = 360
PROCESS_VISUAL_QUEUE_PATH = '/home/android/.cargo/bin/dufs'


def is_queue__processing_running():
    for process in psutil.process_iter(['name']):
        if os.getpid() == process.pid:
            continue
        # Should we check for is_running() as well?
        if 'python3' in process.info['name'] and _check_process_visual_queue_cmd_args(process):
            print("Found process", process, process.cmdline())
            return True
    return False

def _check_process_visual_queue_cmd_args(process):
    match = True
    args = process.cmdline()
    if 'manage.py' not in args[1] or 'process_visual_queue' not in args[2]:
        match = False
    return match

def get_video_orientation_width(video_info):
	video_info = video_info["streams"][0]
	orientation  = HORIZONTAL
	width = video_info["coded_width"]
	height = video_info["coded_height"]
	if height > width:
		orientation  = VERTICAL
	return orientation


class Command(BaseCommand):
    help = 'Process visuals in the queue'

    def handle(self, *args, **options):
        """
        Process visuals in the queue.
        
        Reduce the resolution and bitrate of the video while keeping the aspect ratio.
        
        Resize the images to 900x900 while keeping the aspect ratio.
        """
        if is_queue__processing_running():
            print("Queue is already being processed...")
            return

        print('Processing visuals in the queue...')
        while True:
            queue_item = VisualsQueue.objects.first()
            if not queue_item:
                break
            print(f"Processing: {queue_item.visual}")
            os.chdir(settings.MEDIA_ROOT)
            print(f"CWD: {Path.cwd()}")
            print(f"File type: {queue_item.file_type}")
            input_path = queue_item.visual
            print("Processing path", input_path)
            base, _ = os.path.splitext(input_path)
            output_path_video = f"{base}_processed.mp4"
            output_path_image = f"{base}_processed.jpg"
            print("output_path", output_path_video, output_path_image)
            # If it exists it's probably because of an error
            # not sure deleting is the right move
            if os.path.exists(output_path_video) and os.path.exists(output_path_image):
                print("File already exists, skipping")
                queue_item.delete()
                continue

            if queue_item.file_type.startswith('video'):
                try:
                    self.transcode_to_small_video(input_path, output_path_video)
                except ffmpeg.Error as e:
                    print(f"ffmpeg error: {e}")
                    print('stdout:', e.stdout.decode('utf8'))
                    print('stderr:', e.stderr.decode('utf8'))
                    continue
            else:
                try:
                    self.transcode_to_small_image(input_path, output_path_image)
                except Exception as e:
                    print(f"image processing error: {e}")
                    continue
            queue_item.delete()
            print(f"Done with: {queue_item.visual}")

    def transcode_to_small_video(self, input_path, output_path):
        """Reduse the resolution and bitrate of the video while keeping the aspect ratio"""
        print("Calling ffmpeg")
        # base witdth resolution depends on video orientation
        # I do not think there is a base for both
        # if the width is not devisible by the base it will throw an error
        video_streams = ffmpeg.probe(input_path, select_streams = "v")
        scaled_width = get_video_orientation_width(video_streams)
        # This seems to produce bigger veritcal videos.
        # ffmpeg -i input.mp4 -vf scale=480:-2,setsar=1:1 -c:v libx264 -preset slower -crf 20 output.mp4
        ffmpeg.input(input_path).output(
                                        output_path,
                                        vf=f"scale={scaled_width}:-2,setsar=1:1",
                                        vcodec="libx264",
                                        preset="slower",
                                        crf=20,
                                        ).run(overwrite_output=True)
        print(f"Finished transcoding: {input_path}")

    def transcode_to_small_image(self, input_path, output_path):
        """
        Resize the images to 900x900 while keeping the aspect ratio.
        
        This uses pillow to generate a thumbnail as that keeps the original aspect ratio.
        """
        with Image.open(input_path) as image:
            # thumbnail modifies the image in place, so we need to copy it
            image = image.copy()
            # Handle EXIF orientation to prevent unintended rotation
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = image._getexif()
                if exif is not None:
                    orientation_value = exif.get(orientation, None)
                    if orientation_value == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation_value == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation_value == 8:
                        image = image.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                # Ignore if no EXIF data or orientation key is missing
                pass

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.thumbnail((900, 900))
            image.save(output_path, quality=80, optimize=True)
