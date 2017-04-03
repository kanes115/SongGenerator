import os
from random import choice
from miditime.miditime import MIDITime
import shutil
import sys
import copy
import argparse


class Sounds:
    sounds = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'H': 71}
    sounds_list = ['C', 'D', 'E', 'F', 'G', 'A', 'H']


class Dur:
    intervals = [0, 2, 4, 5, 7, 9, 11, 12,  14, 16, 17, 19, 21, 23, 24]

    def __init__(self, starting_pitch):
        self.starting_pitch = starting_pitch
        self.pitches = [starting_pitch] * 15
        self.build()

    def build(self):
        self.pitches = list( map(lambda x, y: x + y, self.intervals, self.pitches) )

    def build_lowered(self):
        self.pitches = list( map( lambda m: m - 13*3, list(map(lambda x, y: x + y, self.intervals, self.pitches)) ) )


class Tone:

    def __init__(self, start=-1, end=1, pitch=60, velocity=100):
        self.velocity = velocity
        self.pitch = pitch
        self.end = end
        self.start = start

    def get_length(self):
        return self.end - self.start

    def get_midi_format(self):
        return [self.start, self.pitch, self.velocity, self.end - self.start]

    def __repr__(self):
        return str(self.start) + "-" + str(self.end) + "-" + str(self.pitch)





class Melody:
    melodiesCount = 0
    basename = "melody"

    def __init__(self, tempo=450, high_pitch_vel=93, low_pitch_vel=100, gama='C', length=200 ):
        self.length = length
        self.gama = gama
        gama = Dur(Sounds.sounds[gama])
        self.high_range = gama.pitches
        gama.build_lowered()
        self.low_range = gama.pitches
        self.high_pitch_vel = high_pitch_vel
        self.low_pitch_vel = low_pitch_vel
        self.tempo = tempo
        self.name = self.basename + "_" + str(self.melodiesCount) + ".mid"    #name of a melodyfile
        self.high_tones = []
        self.low_tones = []
        Melody.melodiesCount += 1

    def __repr__(self):
        result = "name:" + self.name + '\n'
        result += "highpitch_velocity:" + str(self.high_pitch_vel) + '\n' + "lowpitch_velocity:" \
                 + str(self.low_pitch_vel) + '\n' + "tempo:" + str(self.tempo) + '\n'
        result += "hightones:"
        for t in self.high_tones:
            result += t.__repr__() + "$"
        result += "\nlowtones:"
        for t in self.low_tones:
            result += t.__repr__() + "$"
        result += "\ngama:" + str(self.gama)
        result += "\nlength:" + str(self.length)
        return result

    # Generates a random song according to melodies gama
    def generate_random(self):
        self.__make_random_tones()

    def add_note(self, start, end, pitch):
        if pitch in self.high_range:
            self.high_tones.append(Tone(start, end, pitch, self.high_pitch_vel))
        elif pitch in self.low_range:
            self.low_tones.append(Tone(start, end, pitch, self.low_pitch_vel))
        else:
            raise Exception("Not a proper tone! " + str(pitch) + str(self.high_range))

    def save(self):
        mymidi = MIDITime(self.tempo, self.name)
        mymidi.add_track(list(map(lambda t: t.get_midi_format(), self.high_tones))
                            + list(map(lambda t: t.get_midi_format(), self.low_tones)))
        mymidi.save_midi()

    def get_random_hightone(self):
        return choice(self.high_tones)

    def get_random_lowtone(self):
        return choice(self.low_tones)

    def get_hightone_after(self, time):
        min_diff = 1000000
        min_ton = Tone(-1)

        for ton in self.high_tones:
            if 0 <= ton.start - time < min_diff:
                min_diff = ton.start - time
                min_ton = ton

        if min_ton.start == -1:
            return None
        return min_ton

    def get_lowtone_after(self, time):
        min_diff = 1000000
        min_ton = Tone(-1)

        for ton in self.low_tones:
            if 0 <= ton.start - time < min_diff:
                min_diff = ton.start - time
                min_ton = ton

        if min_ton.start == -1:
            return None
        return min_ton

    # Private methods

    def __make_random_tones(self):

        t = 0
        while t < self.length:
            sound_len = choice(range(12))
            self.high_tones.append(Tone( t, t + sound_len, choice(self.high_range), self.high_pitch_vel ))
            t += sound_len

        t = 0
        while t < self.length:
            sound_len = choice(range(12))
            self.low_tones.append(Tone(t, t + sound_len, choice(self.low_range), self.high_pitch_vel))
            t += sound_len






class FileBuilder:

    foldername = "midis_info"
    info_postfix = '_info.txt'

    def __init__(self, dest):
        """destination is path to a place where a new folder with songs will be created or where the folder with songs is (in order to load them)"""
        self.dest = dest
        if not os.path.exists(self.dest):
            raise Exception("Folder not found")
        self.working_dir = self.dest + "/" + self.foldername

    def save_melody_with_info(self, melody):
        name = melody.name + self.info_postfix

        try:
            if not os.path.exists(self.working_dir):
                os.makedirs(self.working_dir)

            file = open(self.working_dir + "/" + name, 'w')
            file.write(melody.__repr__())
            file.close()
            melody.save()
            shutil.copy(melody.name, self.working_dir)
            os.remove(melody.name)

        except:
            print('Error opening file')
            os.remove(melody.name)
            return

    def load_melody(self, melodyname):
        filepath = self.working_dir + "/" + melodyname + self.info_postfix
        file = open(filepath, "r")
        lines = file.readlines()
        highpitchvel = int(lines[1].split(':')[1])
        lowpitchvel = int(lines[2].split(':')[1])
        tempo = int(lines[3].split(':')[1])
        gama = lines[6].split(":")[1][0]
        length = int(lines[7].split(":")[1])

        melody = Melody(tempo, highpitchvel, lowpitchvel, gama, length)

        high_tones = lines[4].split(":")[1].split("$")
        high_tones.pop()                                        # deleting end of line char
        for x in high_tones:
            melody.add_note(*map(lambda s: int(s), x.split("-")))

        low_tones = lines[5].split(":")[1].split("$")
        low_tones.pop()                                         # deleting end of line char
        for x in low_tones:
            melody.add_note(*map(lambda s: int(s), x.split("-")))

        return melody

    def amount_of_infofiles(self):
        import glob
        self.check_folder_existence()
        return len(glob.glob1(self.working_dir, "*.mid_info.txt"))

    def check_folder_existence(self):
        if not os.path.exists(self.working_dir):
            raise Exception("Working dir not found")




class Parser:

    tempos = range(380, 450)
    highvels = range(90, 110)
    lowvels = range(80, 95)

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("path", help="Path to the working directory where a folder with songs will be created")
        parser.add_argument("--start", nargs="*", help="This is the mode of a program.")
        parser.add_argument("--generate", nargs="*", type=int, choices=[i for i in range(11)], help="This is the mode of a program.")
        args = parser.parse_args()

        self.path = args.path
        self.builder = FileBuilder(self.path)

        if args.start and args.generate:
            raise Exception("Can't specify both start and generate.")

        if args.start:
            if len(args.start) != 3:
                raise Exception("Invalid amount of arguments in --start.")
            self.is_start = True
            try:
                self.songs_amount = int(args.start[0])
                self.length = int(args.start[1])
                self.gama = args.start[2]
                if self.gama not in ["C", "D", "E", "F", "G", "A", "H"]:
                    raise Exception("Invalid format of arguments.")
            except ValueError:
                raise Exception("Invalid format of arguments.")
            return
        elif args.generate:
            self.is_start = False
            self.marks = []
            self.marks_no = len(args.generate)
            self.songs_amount = self.marks_no
            if not self.__correct_marks_no():
                raise Exception("Incorrect marks number")
            for m in range(len(args.generate)):
                try:
                    mark = int(args.generate[m])
                except ValueError:
                    raise Exception("Invalid format of arguments.")
                if mark < 0 or mark > 10:
                    raise Exception("Mark has to be between 0 an 10")
                self.marks.append(mark)
            return

        raise Exception("Error while parsing cmd.")

    def generate_start_songs(self, gama):
        for x in range(self.songs_amount):
            melody = Melody( choice(self.tempos), choice(Parser.highvels),
                             choice(Parser.lowvels), gama, self.length )
            melody.generate_random()
            self.builder.save_melody_with_info(melody)


    # Returns list of tuples (Melody, Mark)
    def get_melodies_marks(self):
        if self.is_start:
            raise Exception("Must be in generate mode.")
        melodies = []
        for x in range(self.marks_no):
            melodies.append((self.builder.load_melody(Melody.basename + "_" + str(x) + ".mid"), self.marks[x]))
        return melodies

    # private functions

    def __correct_marks_no(self):
        return self.builder.amount_of_infofiles() == self.marks_no




class GeneticMixer:

    mutation_ratio = 0.01

    # gets list of tuples (Melody, Mark)
    def __init__(self, listof_melodies_marks):
        self.listof_melodies_marks = listof_melodies_marks
        self.pool = self.__create_pool()


    def avg_tempo(self):
        tempos = list( map( lambda x: x.tempo, self.pool ) )
        return int(sum(tempos) / len(tempos))

    def avg_highpitch_vel(self):
        high_pitch_vel = list( map( lambda x: x.high_pitch_vel, self.pool ) )
        return int(sum(high_pitch_vel) / len(high_pitch_vel))

    def avg_lowpitch_vel(self):
        low_pitch_vel = list( map( lambda x: x.low_pitch_vel, self.pool ) )
        return int(sum(low_pitch_vel) / len(low_pitch_vel))

    #generates new song on basis of the pool
    def generate_next_song(self):
        import random
        melody = Melody(self.avg_tempo(), self.avg_highpitch_vel(),
                            self.avg_lowpitch_vel(), self.pool[0].gama, self.pool[0].length)
        length = self.pool[0].length
        gama = Dur(Sounds.sounds[melody.gama])
        t = 0
        while t < length:
            current_melody = copy.deepcopy(choice(self.pool))
            tone = copy.deepcopy(current_melody.get_hightone_after(t))

            if tone is None:
                last_t = Tone()
                last_t.pitch = current_melody.get_random_hightone().pitch
                last_t.start = t
                last_t.end = current_melody.length
                last_t.velocity = current_melody.get_random_hightone().velocity
                melody.high_tones.append(last_t)
                t += last_t.get_length()
                break

            new_tone = copy.deepcopy(tone)


            if random.uniform(0.0, 1.0) < GeneticMixer.mutation_ratio:
                sound_len = choice( range(12) )
                new_tone = Tone(t, t + sound_len, choice(gama.pitches), choice(range(80, 100)) )

            melody.high_tones.append(new_tone)
            t += new_tone.get_length()

        t = 0
        while t < length:
            current_melody = copy.deepcopy(choice(self.pool))
            tone = copy.deepcopy(current_melody.get_lowtone_after(t))

            if tone is None:
                last_t = Tone()
                last_t.pitch = current_melody.get_random_lowtone().pitch
                last_t.start = t
                last_t.end = current_melody.length
                last_t.velocity = current_melody.get_random_lowtone().velocity
                melody.low_tones.append(last_t)
                t += last_t.get_length()
                break

            new_tone = copy.deepcopy(tone)

            if random.uniform(0.0, 1.0) < GeneticMixer.mutation_ratio:
                sound_len = choice(range(12))
                new_tone = Tone(t, t + sound_len, choice(gama.pitches), choice(range(80, 100)))

            melody.low_tones.append(new_tone)
            t += new_tone.get_length()
        return melody

    # Private functions

    def __create_pool(self):
        pool = []
        for m in self.listof_melodies_marks:
            for i in range(m[1]):
                pool.append(m[0])
        return pool



p = Parser()

if p.is_start:
    p.generate_start_songs(p.gama)
    exit(0)

melodies = p.get_melodies_marks()
g = GeneticMixer(melodies)

newmelodies = []
Melody.melodiesCount = 0
for x in range(p.songs_amount):
    song = g.generate_next_song()
    newmelodies.append(song)
for mel in newmelodies:
    p.builder.save_melody_with_info(mel)

