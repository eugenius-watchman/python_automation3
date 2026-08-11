"""
BSS Professional YouTube Downloader
Robust tool for downloading YouTube videos with error handling, progress tracking
and multiple download options.

Author: Wacthmam Eugenius
Date: 2026
Version: 1.0.0
"""

# libraries
from pytube import YouTube
from pytube.exceptions import PytubeError
import os
import sys
from datetime import datetime
import argparse

class YouTubeDownloader:
    """
    BSS Professional YouTube video downloader class with comprehensive features.
    Handles downloading, error handling and user feedback.
    """
    
    def __init__(self, download_path=None):
        """
        Initialise downloader with download path
        Args:
            download_path(str): Directory to save downloade videos
                                if None, use current directory
        """
        
        # set download path with fallback
        if download_path is None:
            # use current download path 
            self.download_path = os.getcwd()
        else:
            # ensure path exists
            self.download_path = download_path
            self._ensure_directory_exists()
        
        
        # initialise logging
        self.log_file = os.path.join(self.download_path, 'download_log.txt')
        self._initialise_log()
        
        # track download stats
        self.download_count = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
        
    
    def _ensure_directory_exists(self):
        """
        create download dir if it dne
        NB: private method (starts with underscore)...for internal use only
        """
        try:
            # check if dir exists
            if not os.path.exists(self.download_path):
                # creat dir ... and any parent dir
                os.makedirs(self.downlaod_path)
                print(f"Created directory: {self.download_path}")
        except Exception as e:
            print(f"Error creating directory: {self.download_path}") 
            # fall back to current dir
            self.download_path = os.getcwd()
            print(f" Using current directory: {self.download_path}") 
            
    
    def _initialise_log(self):
        """
        initialise log file with header
        private method ...called during initialisation
        """  
        try:
            with open(self.log_file, 'a') as log:
                # write header with timestamp
                log.write("\n" + "="*60 + "\n")
                log.write(f"BSS YOUTUBE DOWNLOAD LOG\n")
                log.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log.write(f"Download directory: {self.download_path}\n")
                log.write("="*60 + "\n")
        except Exception as e:
            print(f"Warning: Could not create file: {e}")
            
    
    def _log_download(self, video_title, status, details=""):
        """
        Log download activity to file
        
        Args:
            video_title(str): Title of video
            status(str): Success or Failed
            details(str): Additional details about download
        """
        try:
            # open file in append mode
            with open(self.log_file, 'a') as log:
                # create timestamp for log entry
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # write log entry
                log.write(f"[{timestamp}] {status}: {video_title} - {details}")
        except Exception as e:
            # silent fail for logging errors ...don't stop the program
            pass
        
    def get_video_info(self, url):
        """
        Get and display video info without downloading
        
        Args:
            url(str): YouTube video URL
            
        Returns:
            YouTube: YT obj if successful, None if failed
        """
        try:
            print("\n" + "="*50)
            print("FETCHING VIDEO INFORMATION...")
            print("="*50)
            
            # creat YT obj
            # sends req to YT to get video data
            yt = YouTube(url)
                
            # display video info
            print(f"\n Title: {yt.title}")
            print(f"Views: {yt.views:,}")
            print(f"Length: {yt.length} seconds ({yt.length//60} minutes)")
            print(f"Uploaded: {yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else 'Unknown'}")
            print(f"Rating: {yt.rating:.2f}")
            print(f"Descripting preview: {yt.description[:100]}")
            print(f"Author: {yt.author}")
            
            # show available streams ...qlty options
            print("\n Available Streams:")
            # get all video streams ...not audio only
            video_streams = yt.streams.filter(progressive=True)
            
            # display each available option
            for stream in video_streams:
                print(f"  - {stream.resolution} ({stream.filesize_mb:.1f} MB) - {stream.mime_type}")
            
            return yt
        
        except Exception as e:
            # handle each error 
            print(f"\n Error fetching video: {e}")
            print(" Possible reasons:")
            print(" - Invalid URL")
            print(" - Video is private or deleted")
            print(" - Network connection issues")
            return None
        
    def download_video(self, url, quality='highest', output_filename=None):
        """
        Download YT video with specified quality
        
        Args:
            url(str):YT video url
            quality: 'highest', 'lowest' or specific resolution '720p'
            output_filename(str): custom filename for downloaded video
            
        Returns:
            bool: True if successful, False otherwise
        """
        # total download attempts
        self.download_count += 1
        
        try:
            print("\n" + "="*50)
            print("STARTING DOWNLOADING...")
            print("="*50)
            
            # create YT obj with callback progress
            yt = YouTube(
                url,
                on_progress_callback=self._progress_callback, # show download progress
                on_complete_callback=self._complete_callback # show completion
            )
            
            # get video title...for display and logging
            video_title = yt.title
            
            # select the appropriate stream based on qlty
            if quality == 'highest':
                # highest resolution
                stream = yt.streams.get_highest_resolution()
            elif quality == 'lowest':
                # lowest resolution
                stream = yt.streams.get_lowest_resolution()
            else:
                # get specific resolution
                stream = yt.streams.filter(res=quality).first()
                # if not found...fall back to highest
                if stream == None:
                    print(f" Quality '{quality}' not found. Using highest resolution.")
                    stream = yt.streams.get_highest_resolution()
                                
            # check is there is a stream
            if stream is None:
                print("No available streams found.")
                self._log_download(video_title, "FAILED", "No streams available")
                self.failed_downloads += 1
                return False
            
            # show download info
            print(f"\n Downloading: {video_title}")
            print(f" Quality: {stream.resolution}")
            print(f" Size:{stream.filesize_mb:.1f}MB")
            print(f" Saving to: {self.download_path}")
            
            # Determine output filename
            if output_filename is None:
                #use video title with sanitised filename
                # remove xters that arenot safe for filenames
                safe_title = "".join(c for c in video_title if c.isalnum() or c in " -_")
                filename = f"{safe_title}.mp4"
            else:
                #use custom filename ...ensure it has right ext
                if not output_filename.endswith('.mp4'):
                    filename = f"{output_filename}.mp4"
                else:
                    filename = output_filename
            
            # full path for download
            download_path = os.path.join(self.download_path, filename)        
        
            # check if file exists
            if os.path.exists(download_path):
                print(f"File already exists: {filename}")
                choice = input(" Overwrite? (y/n): ").lower()
                if choice != 'y':
                    print(" Download cancelled.")
                    return False
                            
            # perform the download
            print("\n Downloading...")
            stream.download(output_path=self.download_path, filename=filename)
            
            #update stats
            self.successful_downloads += 1
            self._log_download(video_title, "SUCCESS", f"Quality: {stream.resolution}")
            
            print(f"\n Download Complete!")
            print(f" File saved: {filename}")
            print(f" Location: {self.download_path}")
            
            return True
        
        except PytubeError as e:
            #handle pytube-specific errors
            print(f"\n Pytube Error: {e}")
            self._log_download(url, "FAILED", f"Pytube Error: {e}")
            self.failed_downloads += 1
            return False
        
        except Exception as e:
            #handle other errors
            print(f"\n Unexpected Error: {e}")
            self._log_download(url, "FAILED", f"Unexpected Error: {e}")
            self.failed_downloads += 1
            return False
        
    def _progress_callback(self, stream, chunk, bytes_remaining):
        """
        Callback function to show downlaod progress
        Called automatically by pytube during download
        
        Args:
            stream: stream being downloaded
            chunk: chunk of data just downloaded
            bytes_remaining: Bytes left to download
        """
        #calc total file size
        total_size = stream.filesize
        #calc bytes downloaded so far
        bytes_downloaded = total_size - bytes_remaining
        #calc percentage complete
        percentage = (bytes_downloaded/ total_size) * 100
        
        #progress bar ...20 blocks for pbar
        bar_length = 20
        filled_length= int(bar_length * bytes_downloaded // total_size)
        # create bar with = for downloaded and . for remaing
        bar = '=' * filled_length + '.' * (bar_length - filled_length)
        
        # print progress ...using \r to overwrite same line
        print(f'\n Progress: |{bar}| {percentage:.1f}%', end='')
        
        # add newline when complete
        if percentage >= 100:
            print()
            
    def _complete_callback(self, stream, file_path):
        """
        callback fxn called when download is complete
        
        Args:
            stream: the stream that downloaded
            file_path: path where file was saved
        """
        print(f"\n Downloaded to: {file_path}")
        
    
    def downlaod_from_file(self, file_path, quality='highest'):
        """
         Download multiple videos from text file containing URLs
         
         Args:
            file_path(str): path to text file with URLs ...one per line
            quality(str): quality for all downloads
            
        Returns:
            tuple: (total_urls, successful, failed)        
        """
        try:
            # chceck if file exists
            if not os.path.exists(file_path):
                print(f"File not founf: {file_path}")
                return 0, 0, 0
            
            # read urls from file 
            with open(file_path, 'r') as file:
                # real lines...strip whitespace...remove empty lines
                urls = [line.strip() for line in file if line.strip()]
                
            print(f"\n Found {len(urls)} URLs in file")
            print("="*50)
            
            #track stats 
            total = len(urls)
            successful = 0
            failed = 0
            
            # download each video
            for i, url in enumerate(urls, i):
                print(f"\n[{i}/{total}] Processing URL: {url}")
                
                #download video
                if self.download_video(url, quality):
                    successful =+ 1
                else: 
                    failed += 1
                
                # show progress
                print(f" Progress: {i}/{total} videos processed")
                
                
            # show summary
            print("\n" + "="*50)
            print("BATCH DOWNLOAD SUMMARY")
            print("="*50)
            print(f" Successful: {successful}")
            print(f" Failed: {failed}")
            print(f"Saved to: {self.download_path}")
            
            return total, successful, failed

        except Exception as e:
            print(f"Error reading file: {e}")
            return 0, 0, 0
        
    
    def show_statistics(self):
        """
        Display download stats
        """
        print("\n" + "="*50)
        print("DOWNLOAD STATISTICS")
        print("="*50)
        print(f"Total download attempted: {self.download_count}")
        print(f"Successful: {self.successful_downloads}")
        print(f"Failed: {self.failed_downloads}")
        if self.download_count > 0:
            success_rate = (self.successful_downloads / self.download_count) * 100
            print(f"Succes rate: {success_rate:.1f}%")
        print(f"Log file: {self.log_file}")
        print("="*50)
        

def main():
    """
    Main fxn...entry point for CL usage
    """
    # create arg parser for professional CLI
    parser = argparse.ArgumentParser(
        description='BSS Professional YouTube Video Downloader',
        example='Example: python downloader.py https://youtube.com/watch?v=xxx -q 720p -o my_video'
    )
    
    # add args 
    parser.add_argument('url', 
                        nargs='?',
                        help='Youtube video URL to download')
    
    parser.add_argument('-d', '--directory',
                        default=None,
                        help='Download directory path')
    
    parser.add_argument('-q', '--quality',
                        default='highest',
                        help='Video quality: highest, lowest, or resolution like 720p')
    
    parser.add_argument('-o', '--output',
                        default=None,
                        help='Output filename (without extension)')
    
    parser.add_argument('-i', '--info',
                        action=None,
                        help='Show video information without downloading')
    
    parser.add_argument('-b', '--batch',
                        default=None,
                        help='Batch download from text file with URLs')
    
    parser.add_argument('-s', '--stats',
                        action='store_true',
                        help='Show download statistics'
                        )
    
    # parse arguments
    args = parser.parse_args()
    
    # create downloader instance
    downloader = YouTubeDownloader(args.directory)
    
    # handle different modes
    if args.stats:
        # show stats and exit
        downloader.show_statistics()
        return
    
    if args.batch:
        # batch download mode
        print("Batch Download Mode")
        print("="*50)
        downloader.downlaod_from_file(args.batch, args.quality)
        return
    
    if args.url is None:
        # no URL provided...show help
        parser.print_help()
        print("\n" + "="*50)
        print("INTERACTIVE MODE")
        print("="*50)
        # interactive mode ...ask for URL
        url = input("Enter YouTube URL ...or 'Quit' to exit").strip()
        if url.lower() == 'quit':
            return
        args.url = url
        
    # get video info first if requested
    if args.info:
        yt = downloader.get_video_info(args.url)
        if yt is None:
            return
        
    # download video
    print("\n Start download...")
    downloader.download_video(args.url, args.quality, args.output)
    
    # show final stats
    downloader.show_statistics()
    
# entry point ...
if __name__ == "__main__":
    main()
