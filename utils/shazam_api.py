import asyncio
from shazamio import Shazam

class ShazamAPI:
    def __init__(self):
        self.shazam = Shazam()

    async def recognize_song(self, file_path: str) -> dict:
        try:
            result = await self.shazam.recognize_song(file_path)
            if result and 'track' in result:
                track = result['track']
                return {
                    'title': track.get('title', 'Unknown'),
                    'artist': track.get('subtitle', 'Unknown Artist'),
                    'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown Album'),
                    'genre': track.get('genres', {}).get('primary', 'Unknown Genre')
                }
            return None
        except Exception as e:
            print(f"Shazam recognition error: {e}")
            return None
