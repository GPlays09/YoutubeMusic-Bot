from pytube import YouTube, exceptions
import moviepy.editor as mp
#import os
import time
import uiautomation as auto
import eyed3
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from pathlib import Path


def get_address():
    try:
        class BrowserWindow:
            def __init__(self, browser_name, window_index=1):
                if browser_name == 'Firefox':
                    addr_bar = auto.Control(Depth=1, ClassName='MozillaWindowClass', foundIndex=window_index) \
                        .ToolBarControl(AutomationId='nav-bar').ComboBoxControl(Depth=1, foundIndex=1) \
                        .EditControl(Depth=1, foundIndex=1)
                else:
                    win = auto.Control(Depth=1, ClassName='Chrome_WidgetWin_1', SubName=browser_name,
                                       foundIndex=window_index)
                    win_pane = win.PaneControl(Depth=1, Compare=lambda control, _depth: control.Name != '')
                    if browser_name == 'Edge':
                        addr_pane = win_pane.PaneControl(Depth=1, foundIndex=1).PaneControl(Depth=1, foundIndex=2) \
                            .PaneControl(Depth=1, foundIndex=1).ToolBarControl(Depth=1, foundIndex=1)
                    elif browser_name == 'Opera':
                        addr_pane = win_pane.GroupControl(Depth=1, foundIndex=1).PaneControl(Depth=1, foundIndex=1) \
                            .PaneControl(Depth=1, foundIndex=2).GroupControl(Depth=1, foundIndex=1) \
                            .GroupControl(Depth=1, foundIndex=1).ToolBarControl(Depth=1, foundIndex=1) \
                            .EditControl(Depth=1, foundIndex=1)
                    else:
                        addr_pane = win_pane.PaneControl(Depth=1, foundIndex=2).PaneControl(Depth=1, foundIndex=1) \
                            .PaneControl(Depth=1, Compare=lambda control, _depth:
                        control.GetFirstChildControl() and control.GetFirstChildControl().ControlTypeName ==
                        'ButtonControl')
                    addr_bar = addr_pane.GroupControl(Depth=1, foundIndex=1).EditControl(Depth=1)
                assert addr_bar is not None
                self.addr_bar = addr_bar

            @property
            def current_tab_url(self):
                """Get current tab url."""
                return self.addr_bar.GetValuePattern().Value

            @current_tab_url.setter
            def current_tab_url(self, value: str):
                """Set current tab url."""
                self.addr_bar.GetValuePattern().SetValue(value)

        browser = BrowserWindow(selection)  # 'Firefox'
        return browser.current_tab_url

    except LookupError:
        print('Connection timeout')


def start():
    home = str(Path.home())
    save_path = home + '\\Music'

    try:
        yt = YouTube(get_address())

        print('Download starting...')

        video_title = yt.title
        song_title = video_title
        author = yt.author
        thumbnail = yt.thumbnail_url

        # remove "- Topic" from author #
        author = author.split(' - ')[0]

        # clean the title of bad symbols #
        banned_symbols = ['!', '@', '"', '$', ',', "/", "'", '.']

        for char in video_title:
            for x in range(len(banned_symbols)):
                if char == banned_symbols[x]:
                    video_title = video_title.replace(char, "")

        # download mp4 from yt music #
        stream = yt.streams.first()
        stream.download(save_path, video_title)

    except exceptions.RegexMatchError or exceptions.VideoUnavailable:
        print('invalid link /  video unavailable')
        return None

    try:
        song_title = video_title.split(' - ')[1]
    except:
        pass

    # mp4 to mp3 #
    clip = mp.VideoFileClip(save_path + "\\" + video_title + ".mp4")
    clip.audio.write_audiofile(save_path + "\\" + song_title + ".mp3")
    clip.close()
    time.sleep(10)
    os.remove(save_path + "\\" + video_title + ".mp4")

    # PROPERTIES #

    # THUMBNAIL #
    # download thumbnail image #
    response = requests.get(thumbnail)
    image = open(save_path + '\\' + song_title + ".jpeg", "wb")
    image.write(response.content)
    image.close()

    # set song's cover photo as thumbnail image and remove thumbnail image #
    cover = MP3(save_path + "\\" + song_title + ".mp3", ID3=ID3)
    cover.tags.add(APIC(mime='image/jpeg', type=3, data=open(save_path + '\\' + song_title + ".jpeg", 'rb').read()))
    cover.save()
    os.remove(save_path + '\\' + song_title + ".jpeg")

    # ARTIST #
    song = eyed3.load(save_path + "\\" + song_title + ".mp3")
    song.tag.artist = author
    song.tag.save()

    print('Downloaded ' + "'" + song_title + "'")


# UI #
print('\nIn the browser where you play music you can ONLY have 1 tab open \nbecause it can only detect '
      'active tab and not all. And the track\nmust be open so that you see its thumbnail enlarged on the\nleft of the'
      ' screen not just on the bottom center of your screen.'
      '\nFor support contact me Instagram: cheating.society'
      '\n'
      '\nEdge type: 1'
      '\nFirefox type: 2'
      '\nOpera type: 3')

i = input()
if i == '1':
    selection = 'Edge'
elif i == '2':
    selection = 'Firefox'
elif i == '3':
    selection = 'Opera'

print('Running...')


while True:

    old = get_address()
    time.sleep(10)
    new = get_address()

    if old != new:
        print("\nNew link detected.")
        start()
