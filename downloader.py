import os
import yt_dlp
from concurrent.futures import ThreadPoolExecutor

def download_video_as_mp3(url, output_dir="downloads"):
    """
    Download a single video from YouTube as MP3 using yt-dlp.
    Assumes FFmpeg is installed and available via Homebrew.
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # yt-dlp options with 10 concurrent downloads and 8 fragment downloads
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': False,  # Automatically handles playlists
            'concurrent_fragment_downloads': 8,  # Number of fragments to download in parallel
        }

        # Create yt-dlp object to get video info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info without downloading
            info_dict = ydl.extract_info(url, download=False)

            # Check if the video is private or delisted
            if info_dict.get('availability', 'unavailable') != 'public':
                print(f"Video '{url}' is private or delisted. Skipping video.")
                return  # Skip this video

            title = info_dict.get('title', 'Unknown Title')
            file_name = f"{title}.mp3"
            output_file = os.path.join(output_dir, file_name)

            # Check if the file already exists
            if os.path.exists(output_file):
                print(f"File '{file_name}' already exists. Skipping download.")
                return  # Skip downloading if the file exists

            # Proceed with download if file doesn't exist and it's not private or delisted
            print(f"Downloading '{file_name}'...")
            ydl.download([url])

        print(f"\nDownload completed for {url}!")
    except yt_dlp.utils.DownloadError as e:
        # Handle download errors (e.g., private videos, errors)
        print(f"Error downloading {url}: {e}")
        return  # Skip this video and move on to the next one
    except Exception as e:
        print(f"Error processing {url}: {e}")

def download_playlist(url, output_dir="downloads", max_threads=10):
    """
    Download an entire playlist from YouTube as MP3 using multiple threads.
    """
    try:
        # yt-dlp options to get playlist video URLs
        ydl_opts = {
            'extract_flat': True,  # Only extract URLs without downloading video
            'force_generic_extractor': True,  # Ensure consistent extraction of URLs
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get the playlist info
            result = ydl.extract_info(url, download=False)

            if 'entries' in result:
                # Extract all video URLs from the playlist
                video_urls = [entry['url'] for entry in result['entries']]

                # Create a ThreadPoolExecutor to download videos concurrently
                with ThreadPoolExecutor(max_threads) as executor:
                    executor.map(lambda url: download_video_as_mp3(url, output_dir), video_urls)

                print("\nAll videos from the playlist have been downloaded!")
            else:
                print("No videos found in the playlist.")

    except Exception as e:
        print(f"Error processing playlist {url}: {e}")

if __name__ == "__main__":
    url = input("Enter YouTube video or playlist URL: ")
    output_dir = input("Enter output directory (default: 'downloads'): ") or "downloads"
    
    # If the URL is a playlist, we handle it accordingly
    if 'playlist' in url:
        download_playlist(url, output_dir)
    else:
        download_video_as_mp3(url, output_dir)