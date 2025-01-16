from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import yt_dlp
import time
import os
import re


def setup_chrome_driver():
    """Setup Chrome with basic options"""
    chrome_options = Options()

    # Suppress DevTools logging
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])

    # Add additional options to improve stability
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-notifications")

    # Uncomment below line if you don't want to see the browser
    # chrome_options.add_argument("--headless")

    return webdriver.Chrome(options=chrome_options)


def determine_category(title):
    """
    Determine the category based on video title
    Add more keywords and categories as needed
    """
    title = title.lower()

    categories = {
        'anime': [
            'dragon ball', 'naruto', 'one piece', 'bleach', 'attack on titan',
            'demon slayer', 'my hero academia', 'jujutsu', 'anime', 'boruto',
            'manga', 'hunter x hunter', 'death note', 'wind breaker', 'one punch', "amv", "eren",
            "luffy", "zoro", "nami", "vegita"
        ],
        'tv_series': [
            'friends', 'big bang theory', 'sheldon', 'breaking bad', 'game of thrones',
            'stranger things', 'series', 'episode', 'season', 'show', 'sitcom',
            'netflix', 'tv series', 'suits',
        ],
        'gaming': [
            'gameplay', 'gaming', 'playthrough', 'minecraft', 'fortnite',
            'game', 'ps5', 'xbox', 'nintendo', 'walkthrough', 'lets play',
            'stream', 'gaming moments'
        ],
        'music': [
            'music video', 'song', 'concert', 'live performance', 'mv',
            'official music', 'lyrics', 'album', 'official video', 'ft.',
            'featuring', 'rap', 'hip hop', 'rock'
        ],
        'movies': [
            'movie', 'film', 'cinema', 'trailer', 'teaser', 'behind the scenes',
            'movie scene', 'film review', 'movie review'
        ],
        'educational': [
            'tutorial', 'how to', 'learn', 'education', 'course',
            'lesson', 'guide', 'explained', 'documentary', 'history',
            'science', 'math', 'programming'
        ]
    }

    for category, keywords in categories.items():
        if any(keyword in title for keyword in keywords):
            return category

    return 'others'  # Default category if no match found


def download_video(url, base_path):
    """Download video using yt-dlp"""
    try:
        # First get video info to determine category
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', '')
            category = determine_category(title)

            # Create category subfolder
            output_path = os.path.join(base_path, category)
            if not os.path.exists(output_path):
                os.makedirs(output_path)

        # Updated options for reliable video+audio download
        ydl_opts = {
            # More flexible format selection
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
            'format_sort': [
                'res:1080',
                'res:720',
                'fps:30',
                'codec:h264'
            ],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(f"Downloaded to category: {category}")
            return True

    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False


def download_channel_videos(channel_url, download_path, start_from=0):
    """
    Get all videos from YouTube channel and download them
    Parameters:
        channel_url: URL of the YouTube channel
        download_path: Base path for downloads (will be organized by categories)
        start_from: Skip first N videos (useful for resuming downloads)
    """
    driver = setup_chrome_driver()
    video_urls = []
    no_new_videos_count = 0

    try:
        # Navigate to channel
        print(f"Accessing channel: {channel_url}")
        driver.get(channel_url)

        # Scroll to load more videos
        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight")
        videos_found = 0

        while True:  # Keep scrolling until no more videos
            # Scroll down
            driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)  # Wait for content to load

            initial_video_count = len(video_urls)

            # Get all video elements (both regular videos and shorts)
            wait = WebDriverWait(driver, 10)
            regular_videos = driver.find_elements(
                By.CSS_SELECTOR, "#video-title")
            shorts = driver.find_elements(
                By.CSS_SELECTOR, "a.shortsLockupViewModelHostEndpoint")

            # Process regular videos
            for video in regular_videos:
                url = video.get_attribute('href')
                if url and url not in video_urls and not '/shorts/' in url:
                    video_urls.append(url)
                    videos_found += 1
                    print(f"Found regular video ({videos_found}): {
                          video.get_attribute('title')}")

            # Process shorts
            for short in shorts:
                href = short.get_attribute('href')
                if href.startswith('/shorts/'):
                    url = f"https://www.youtube.com{href}"
                elif href.startswith('https://'):
                    url = href
                else:
                    continue

                if url and url not in video_urls:
                    video_urls.append(url)
                    videos_found += 1
                    print(f"Found short ({videos_found}): {url}")

            # Check if we found any new videos in this scroll
            if len(video_urls) == initial_video_count:
                no_new_videos_count += 1
            else:
                no_new_videos_count = 0

            # If we haven't found new videos in 5 scrolls, assume we're done
            if no_new_videos_count >= 5:
                print(
                    "\nNo new videos found after multiple scrolls. Assuming all videos have been found.")
                break

            # Check if we can scroll more
            new_height = driver.execute_script(
                "return document.documentElement.scrollHeight")
            if new_height == last_height:
                time.sleep(3)
                new_height = driver.execute_script(
                    "return document.documentElement.scrollHeight")
                if new_height == last_height:
                    print("\nReached end of page.")
                    break
            last_height = new_height

            # Print progress every 100 videos
            if videos_found % 100 == 0:
                print(f"\nFound {videos_found} videos so far...")

        print(f"\nFound total of {len(video_urls)
                                  } videos. Starting downloads...")

        # Save URLs to a file in case we need to resume later
        with open('video_urls.txt', 'a') as f:
            for url in video_urls:
                f.write(f"{url}\n")

        # Download videos
        for i, url in enumerate(video_urls[start_from:], start_from + 1):
            print(f"\nDownloading video {i}/{len(video_urls)}")
            print(f"URL: {url}")

            try:
                success = download_video(url, download_path)
                if success:
                    print(f"Successfully downloaded video {i}")
                else:
                    print(f"Failed to download video {i}")
                    with open('failed_downloads.txt', 'a') as f:
                        f.write(f"{url}\n")

            except Exception as e:
                print(f"Error downloading video {i}: {str(e)}")
                with open('failed_downloads.txt', 'a') as f:
                    f.write(f"{url}\n")

            # Save progress every 10 videos
            if i % 10 == 0:
                print(f"\nProgress saved: {
                      i}/{len(video_urls)} videos processed")

    except Exception as e:
        print(f"Error during process: {str(e)}")
        import traceback
        print(traceback.format_exc())

    finally:
        driver.quit()


def main():
    # List of channel URLs to process
    channels = [
        #"https://www.youtube.com/@CareerGenie1/shorts"
        # Add more channels as needed
    ]

    # Base download directory
    download_path = os.path.join(os.getcwd(), "downloads")

    # Process each channel
    for channel_url in channels:
        print(f"\nProcessing channel: {channel_url}")
        try:
            download_channel_videos(channel_url, download_path)
        except Exception as e:
            print(f"Error processing channel {channel_url}: {str(e)}")
            continue


if __name__ == "__main__":
    main()
