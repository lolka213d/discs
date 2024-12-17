import os
import yt_dlp
import spotipy
import asyncio
from spotipy.oauth2 import SpotifyClientCredentials

class MusicDownloader:
    def __init__(self, downloads_dir):
        self.downloads_dir = downloads_dir
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="267f27acdc5846a7a85f23290e53c755",
            client_secret="35596835a624473b8474ec2ce03d6f04"
        ))
        self.yt_client_id = ""
        self.yt_client_secret = ""

    def get_search_results(self, query):
        if not query:
            return []
            
        search_results = []
        
        try:
            yt_results = self._search_youtube(query, limit=10)
            if yt_results:
                search_results.extend(yt_results)
        except Exception as e:
            print(f"YouTube search error: {e}")
        
        try:
            spotify_results = self._search_spotify(query, limit=10)
            if spotify_results:
                search_results.extend(spotify_results)
        except Exception as e:
            print(f"Spotify search error: {e}")
        
        print(f"Search query: {query}")
        print(f"Results found: {len(search_results)}")
        
        return search_results

    def _search_youtube(self, query, limit=10):
        search_query = f"ytsearch{limit}:{query} official audio"
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'age_limit': 99,
                'default_search': 'auto',
                'format': 'bestaudio',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(search_query, download=False)
                if results and 'entries' in results:
                    return [{
                        'title': entry.get('title', ''),
                        'duration': str(entry.get('duration_string', '')),
                        'callback_data': f"yt_{entry.get('id', '')}",
                        'source': 'youtube'
                    } for entry in results['entries']]
        except Exception as e:
            print(f"YouTube search error: {e}")
        return []

    def _search_spotify(self, query, limit=10):
        try:
            results = self.sp.search(q=query, limit=limit, type='track')
            tracks = results['tracks']['items']
            return [{
                'title': track['name'],
                'duration': self._format_duration(track['duration_ms']),
                'callback_data': f"sp_{track['id']}",
                'source': 'spotify'
            } for track in tracks]
        except Exception as e:
            print(f"Spotify search error: {e}")
        return []

    def _format_duration(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    async def download_song(self, url, format='mp3'):
        try:
            ydl_opts = {
                'format': 'bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format,
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.downloads_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'verbose': True,
                'age_limit': 99,
                'prefer_ffmpeg': True,
                'cookiefile': 'cookies.txt',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Origin': 'https://www.youtube.com',
                    'Referer': 'https://www.youtube.com/'
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Starting download for URL: {url}")
                info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                
                if info:
                    title = info.get('title', 'unknown')
                    file_path = os.path.join(self.downloads_dir, f"{title}.{format}")
                    print(f"Download completed. File path: {file_path}")
                    
                    if os.path.exists(file_path):
                        return file_path, title
                        
                    for ext in ['m4a', 'webm', format]:
                        temp_path = os.path.join(self.downloads_dir, f"{title}.{ext}")
                        if os.path.exists(temp_path):
                            return temp_path, title
                
                print("Download failed - no file found")
                return None, None

        except Exception as e:
            print(f"Download error in downloader: {e}")
            return None, None

    async def process_spotify_link(self, url, format='mp3'):
        try:
            if 'track' in url:
                track_id = url.split('/')[-1].split('?')[0]
                track_info = self.sp.track(track_id)
                search_query = f"{track_info['name']} {track_info['artists'][0]['name']}"
                youtube_url = await self.search_on_youtube(search_query)
                if youtube_url:
                    return await self.download_song(youtube_url, format)
            elif 'playlist' in url:
                playlist_id = url.split('/')[-1].split('?')[0]
                results = self.sp.playlist_tracks(playlist_id)
                tracks = []
                for item in results['items']:
                    track = item['track']
                    search_query = f"{track['name']} {track['artists'][0]['name']}"
                    youtube_url = await self.search_on_youtube(search_query)
                    if youtube_url:
                        file_path, title = await self.download_song(youtube_url, format)
                        if file_path:
                            tracks.append((file_path, title))
                return tracks
        except Exception as e:
            print(f"Spotify processing error: {e}")
        return None

    async def search_on_youtube(self, query):
        try:
            search_query = f"ytsearch1:{query} official audio"
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'age_limit': 99,
                'default_search': 'auto',
                'format': 'bestaudio',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = await asyncio.get_event_loop().run_in_executor(None, ydl.extract_info, search_query, False)
                if results and 'entries' in results and results['entries']:
                    return f"https://youtube.com/watch?v={results['entries'][0]['id']}"
        except Exception as e:
            print(f"YouTube search error: {e}")
        return None
