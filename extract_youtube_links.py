import os
import re
import requests


## Checkt, ob die Youtube-Links noch verfügbar sind.

def extract_youtube_links_from_file(file_path):
    youtube_link_pattern = re.compile(
    r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&list=[\w-]+)?|https?://youtu\.be/[\w-]+|https?://www\.youtube\.com/playlist\?list=[\w-]+)'
)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        links = youtube_link_pattern.findall(content)
    return links

def is_youtube_video_available(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return False

        html = response.text.lower()

        unavailable_indicators = [
            "video nicht mehr verfügbar",
            "video unavailable",
            "not available",
            "this video is unavailable",
            "player-unavailable",
            "video wurde entfernt",
            "video has been removed",
            "errorcode",  # YouTube Errorcodes im JSON
            "\"playabilityStatus\"",
            "\"status\":\"error\""
        ]

        if any(indicator in html for indicator in unavailable_indicators):
            return False

        # Beispiel: Suche nach JSON-Bereich "playabilityStatus":{"status":"ERROR"}
        if '"playabilitystatus":{"status":"error"' in html.replace(" ", ""):
            return False

        return True
    except requests.RequestException:
        return False


def find_md_files_and_check_links(base_dir):
    youtube_links_status = {}

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.md'):
                full_path = os.path.join(root, file)
                print(f"Prüfe Datei: {full_path}")  # Debug
                links = extract_youtube_links_from_file(full_path)
                print(f"Gefundene Links: {links}")  # Debug
                for link in links:
                    if link not in youtube_links_status:
                        reachable = is_youtube_video_available(link)
                        youtube_links_status[link] = reachable

    return youtube_links_status

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    status = find_md_files_and_check_links(base_dir)
    print(is_youtube_video_available("https://youtu.be/dQw4w9WgXcQ"))  # Sollte True ausgeben

    print("\n🎬 Youtube-Link-Status:")
    for link, reachable in status.items():
        status_text = "✅ ERREICHBAR" if reachable else "❌ NICHT ERREICHBAR"
        print(f"{link} -> {status_text}")

    input("Drücke Enter zum Beenden...")  # Fenster offen halten

if __name__ == "__main__":
    main()
