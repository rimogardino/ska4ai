import os
from pathlib import Path
import psutil
import ffmpeg
from PIL import Image, ImageOps
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
    # base witdth resolution depends on video orientation
    # I do not think there is a base for both
    # if the width is not devisible by the base it will throw an error
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
        # Probe the input video to detect HDR metadata or resolution
        video_streams = ffmpeg.probe(input_path, select_streams="v")
        scaled_width = get_video_orientation_width(video_streams)
        
        # Base filter options
        filter_chain = [
            f"scale={scaled_width}:-2",  # Maintain aspect ratio with new width
            "setsar=1:1"  # Set pixel aspect ratio to square
        ]
        
        # Check if the video has HDR metadata
        video_metadata = video_streams["streams"][0]
        color_primaries = video_metadata.get("color_primaries", "bt709")
        transfer_characteristics = video_metadata.get("transfer_characteristics", "bt709")
        
        if color_primaries != "bt709" or transfer_characteristics != "bt709":
            # Apply tone mapping for HDR to SDR conversion
            filter_chain.append("zscale=t=linear:npl=100")  # Linear tone mapping
            filter_chain.append("format=gbrpf32le")
            filter_chain.append("zscale=p=bt709")
            filter_chain.append("tonemap=tonemap=hable:desat=0")
            filter_chain.append("zscale=t=bt709:m=bt709:r=tv")  # Convert color space to BT.709
            filter_chain.append("format=yuv420p")  # Ensure compatibility with SDR
        
        # Finalize filter chain
        vf = ",".join(filter_chain)
        
        # Run the ffmpeg command
        # This seems to produce bigger veritcal videos.
        ffmpeg.input(input_path).output(
            output_path,
            vf=vf,
            vcodec="libx264",  # Use H.264 codec for compatibility
            preset="medium",   # Set encoding speed/quality tradeoff
            crf=20,            # Adjust quality (lower CRF = higher quality)
            maxrate="3M",      # Limit bitrate (example: 1 Mbps)
            bufsize="5M",      # Set buffer size for bitrate control
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
            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")
            # Handle EXIF orientation to prevent unintended rotation
            ImageOps.exif_transpose(image, in_place=True)
            image.thumbnail((900, 900))
            image.save(output_path, quality=80, optimize=True)
