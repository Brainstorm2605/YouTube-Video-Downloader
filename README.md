## YouTube Video Downloader
This is a Python-based tool that helps you download and organize YouTube videos in bulk. It categorizes videos into folders (e.g., Anime, TV Series, Gaming, etc.) based on keywords in the video titles. It supports downloading regular videos and YouTube Shorts.
# Why is this Different?
No ads or unwanted interruptions.
Simple categorization of videos for better organization.
Ideal for downloading videos from entire channels quickly and efficiently.
## Requirements
Before running the tool, ensure you have:
1) Python 3.x installed.
2) The required dependencies installed. Run:
    pip install -r requirements.txt
3) A compatible Chrome WebDriver installed (match your Chrome browser version).
# How to Use
1. Clone the Repository
git clone https://github.com/Brainstorm2605/YouTube-Video-Downloader.git
cd YouTube-Video-Downloader
2. Setup Dependencies
Install the required Python packages:
pip install -r requirements.txt
3. Modify the Code
# Open the main.py file and:
  Add YouTube channel URLs in the channels list:
  channels = [
      "https://www.youtube.com/@ChannelName/videos"
  ]
  (Optional) Uncomment chrome_options.add_argument("--headless") to run Chrome in the background without displaying the browser:
  chrome_options.add_argument("--headless")
4. Run the Script
  Execute the script:
  python main.py
5. Find Downloads
   Videos will be saved in a downloads folder, organized by categories (Anime, Gaming, etc.).

# What This Tool Does
  Fetches all video URLs from a YouTube channel.
  Determines the category of each video based on keywords in the title.
  Downloads videos into categorized subfolders.
  Saves a list of video URLs for easy resumption and logs failed downloads.
# Important Notes
  Ensure chromedriver is in your PATH or update the driver path in setup_chrome_driver() if needed.
  If you encounter permission issues while creating folders, run the script with administrative privileges.
  Feel free to contribute or report any issues! 😊
