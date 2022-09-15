import requests
import json
import tkinter as tk
import random
from setuptools import Command
import vlc
import os 

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

WIN_WIDTH = 500
WIN_HEIGHT = 500
FONT_SIZE = 26
TEXT_OFFSET = 50

def create_pitch_dict():
    # Load dictionaries
    frequency_dict_json = json.loads(open("C:\\Users\\Leevi\\projects\\JS\\pitchaccent\\term_meta_bank_1.json", encoding="UTF-8").read())
    pitch_dict_json = []
    for i in range(1, 14):
        pitch_dict_json.extend(json.loads(open("C:\\Users\\Leevi\\Downloads\\kanjium_pitch_accents\\term_meta_bank_{}.json".format(i), encoding="UTF-8").read()))

    def find_pitch(term: str) -> dict:
        for entry in pitch_dict_json:
            if entry[0] == term:
                return entry[2]

    common_pitch_dict = open("C:\\Users\\Leevi\\projects\\JS\\pitchaccent\\common_pitch.json", mode="w", encoding="UTF-8")
    common_pitch_dict.write('[')

    for entry in frequency_dict_json:
        if len(entry[0]) == 1:
            continue
        pitch = find_pitch(entry[0])
        if pitch != None:
            common_pitch_dict.write("[\"{}\", \"{}\", {}],".format(entry[0], pitch["reading"], pitch["pitches"]).replace('\'', '\"'))

    common_pitch_dict.write(']')
    common_pitch_dict.close()
    print("done")

class Pitch:
    def __init__(self, dictionary: list, canvas: tk.Canvas):
        self.word = ""
        self.reading = ""
        self.pitch = []
        self.audio = 0
        self.pitch_dictionary = dictionary
        self.canvas = canvas
        self.volume = 50
        self.next_or_show = True
        self.speed = 1

    def get_accent_color(self, down_step: int, word_len: int) -> str:
        if down_step == 0:
            return "blue"
        if down_step == 1:
            return "red"
        if down_step == word_len:
            return "green"
        else:
            return "orange"

    def draw_word(self, canvas: tk.Canvas, text: str, y_offset, color: str="black"):
        x = WIN_WIDTH // 2
        y = WIN_HEIGHT // 2 + y_offset - TEXT_OFFSET
        canvas.create_text(x, y, font=("Helvetica", FONT_SIZE), text=text, fill=color)

    def draw_pitch_line(self, canvas: tk.Canvas, center_x: int, center_y: int, word_len: int, pitch: int):
        is_even = True if word_len % 2 == 0 else False
        offset = 0 if is_even else 3 * FONT_SIZE // 4
        font_width = FONT_SIZE * 1.4

        step = 1
        is_low = True if pitch != 1 else False
        for i in range(-(word_len // 2), word_len // 2 + (0 if is_even else 1)):

            # Add 1.5 font size offset down if pitch is low
            y = center_y
            if is_low:
                y += FONT_SIZE * 1.5

            y -= TEXT_OFFSET

            # Calculate x start and end position
            x_start = center_x - offset + font_width * i
            x_end = center_x - offset + font_width * i + font_width
            canvas.create_line(x_start, y, x_end, y)

            # Check if down step occurs
            if step == pitch:
                is_low = True
                canvas.create_line(x_end, y, x_end, y + FONT_SIZE * 1.5)

            # Check first step is done and pitch needs to swapped
            if pitch != 1 and step == 1:
                is_low = False
                canvas.create_line(x_end, y, x_end, y - FONT_SIZE * 1.5)
            
            step += 1

    # Get a random word from a dictionary
    def get_random_word(self):
        self.word, self.reading, self.pitch = random.choice(self.pitch_dictionary)

    def next_click(self):
        if self.next_or_show:
            while (not self.random_click()):
                continue
        else:
            self.play_audio()
            self.show_word()
        self.next_or_show = not self.next_or_show

    def random_click(self) -> bool:
        self.get_random_word()
        # Check that audio is found and word has only one pitch pattern
        if (self.get_audio_from_file() or self.get_audio_from_url()) and len(self.pitch) == 1:
            self.play_audio()
        else:
            #self.random_click()
            return False

        # Draw new word and reading to canvas
        canvas.delete("all")
        self.draw_word(canvas, self.word, -FONT_SIZE)
        self.draw_word(canvas, self.reading, FONT_SIZE // 2 + FONT_SIZE // 4)
        return True

    def show_word(self):
        count = 0
        for p in self.pitch:
            color = self.get_accent_color(p["position"], len(self.reading))
            self.draw_word(canvas, self.reading, count * FONT_SIZE * 2 + FONT_SIZE // 2 + FONT_SIZE // 4, color)
            self.draw_pitch_line(canvas, WIN_WIDTH // 2, WIN_HEIGHT // 2 + count * FONT_SIZE * 2, len(self.reading), p["position"])
            count += 1

    def get_audio_from_url(self) -> bool:
        audio_url = "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?&kanji={}&kana={}".format(self.word, self.reading)
        # Check if audio for word was found
        # If audio is not found 5s long temp audio is returned from source
        response = requests.get(audio_url)
        if response.headers["Content-length"] == "52288":
            print("No audio found for word:", self.word)
            self.word = "No audio"
            return False

        self.audio = vlc.Media(audio_url)
        return True

    def get_audio_from_file(self) -> bool:
        audio_url = "{}\\audio\\{}.mp3".format(DIR_PATH, self.word)
        if not os.path.exists(audio_url):
            print("No audio file found for word:", self.word)
            return False
        self.audio = vlc.Media(audio_url)
        return True

    def play_audio(self):
        media_player = vlc.MediaPlayer()
        media_player.set_media(self.audio)
        media_player.audio_set_volume(self.volume)
        media_player.set_rate(pitch.speed)
        media_player.play()


if __name__ == '__main__':
    print(DIR_PATH)
    #create_pitch_dict() # Run to create common_pitch.json pitch dictionary
    common_pitch_dict = open(DIR_PATH + "\\common_pitch.json", mode="r", encoding="UTF-8")
    common_pitch_dict_list = json.loads(common_pitch_dict.read())

    #for i in common_pitch_dict_list:
    #    print(i[0])
    #    audio_url = "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?&kanji={}&kana={}".format(i[0], i[1])
    #
    #    # Check if audio for word was found
    #    # If audio is not found 5s long temp audio is returned from source
    #    response = requests.get(audio_url)
    #    if response.headers["Content-length"] == "52288":
    #        print("No audio found for word:", i[0])
    #        continue
    #
    #    with open("{}\\audio\\{}.mp3".format(DIR_PATH, i[0]), 'wb') as f:
    #        f.write(response.content)
    #        f.close()

    window = tk.Tk()
    canvas = tk.Canvas(window, width=WIN_WIDTH, height=WIN_HEIGHT)
    window.title("Accent")
    window.geometry('{}x{}'.format(WIN_WIDTH, WIN_HEIGHT))

    pitch = Pitch(common_pitch_dict_list, canvas)

    button_next = tk.Button(window, text="Next", font=("Arial", 14), command=pitch.next_click, width=6)
    button_next.place(relx=0.42, rely=0.75, anchor = 'center')

    button_replay = tk.Button(window, text="Replay", font=("Arial", 14), command=pitch.play_audio, width=6)
    button_replay.place(relx=0.58, rely=0.75, anchor = 'center')

    def update_volume(self):
        pitch.volume = volume_slider.get()

    volume_slider = tk.Scale(window, command=update_volume, from_=100, to=0)
    volume_slider.set(pitch.volume)
    volume_slider.place(relx=0.95, rely=0.5, anchor = 'center')

    def update_speed(self):
        pitch.speed = speed_slider.get()

    speed_slider = tk.Scale(window, command=update_speed, from_=2, to=0, resolution=0.05)
    speed_slider.set(pitch.speed)
    speed_slider.place(relx=0.05, rely=0.5, anchor = 'center')

    canvas.pack()
    window.mainloop()