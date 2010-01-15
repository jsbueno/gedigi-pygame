#!/usr/bin/python
# coding: utf-8

import pygame
from pygame.locals import *

import unicodedata

from effects import Waves, Colors, EffectedChar, CharEffect, LineEffect, CharWalk, CharTranslucence, CharRot, CharImplode
from editor_utils import  DURATIONENDED, Coord, dirties, clears, cached

WIDTH, HEIGHT = 800, 600

class QuitEditor(Exception):
    pass

def setup():
    global SCREEN, FONT
    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    FONT = pygame.font.Font ("VeraSeBd.ttf", 25)

class KeyboardMaps(object):
    # Dead key and unicode composition data
    # as used in pt_BR. Expand for other langs, FIXME
    # for diferentiation in case of composition conflicts
    unicode_composition = {
    u"`": u"\u0300",
    u"'": u"\u0301",
    u"^": u"\u0302",
    u"~": u"\u0303",
    u"¨": u"\u0308",
    # can't get a shift + 6 = "¨" from pygame as well.
    # compositing " as ¨ as a workaround
    u'"': u"\u0308"
    }
    # keyboard maps: just create a string with every key with a
    # shift symbol, followed by its symbol
    # SDL bug: pt_BR key for grave and acute accents
    # and the one for tilde and circunflex
    # do not even generate a keypressed event :-(
    # (discovery: with shift, one gets a 0x00 key code for
    # the them accent - hardcoding the grave accent at least)
    map_pt_BR = u"'\"1!2@3#4$5%6¨7&8*9(0)-_=+[{~^]},<.>;:\|/?"
    map_alt_pt_BR = u"\"¬1¹2²3³4£5¢6¬7{8[9]0}-\=§q/w?e€r®tŧy←u↓i→oøpþ[ªaæsßdðfđgŋhħjjkĸlł]ºz«x»c©v“b”mµ,─.·\º/°"
    map_alt_shift_pt_BR = u"1¡2½3¾4¼5⅜6¨7⅞8™9±0°-¿=˛tŦy¥iıoØpÞ[¯aÆs§dÐfªgŊhĦjJk&lŁç˝z<x>c©v‘b’,×.÷;˙\˘/¿"

    def set_keymap(self, keymap_name):
        try:
            keymap = getattr(Editor, "map_" + keymap_name)
            keymap_alt = getattr(Editor, "map_alt_" + keymap_name)
            keymap_alt_shift = getattr(Editor, "map_alt_shift_" + keymap_name)
        except AttributeError:
            raise ValueError ("Unknown Keymap")
        keymaper = lambda key_map: dict((key_map[i], key_map[i + 1]) for i in xrange(0, len(key_map), 2))
        self.keymap = keymaper(keymap)
        self.keymap_alt = keymaper(keymap_alt)
        self.keymap_alt_shift = keymaper(keymap_alt_shift)


class Text(object):
    def __init__(self, font, width=200, color=(255,255,255), text="", max_lines=1, effect_callback=None):
        self.text = text
        self.font = font
        self.width = width
        self.color = color
        self.max_lines = max_lines
        #Does not insert text if it does not fit
        self.strict = True
        # counts the number of times the text was rendered:
        self.rendered = 0
        # indicates whether content changed since last 
        # rendering: used by the caching decorators
        self.effected_chars = {}
        self.effect_callback = effect_callback
        self.dirty()
    
    def _words(self):
        #return self.text.split()
        words = []
        word = []
        in_space = False
        for char in self.text:
            if char.isspace():
                if not in_space and word:
                    words.append("".join(word))
                    in_space = True
                    word = []
            else:
                if in_space and word:
                    words.append("".join(word))
                    in_space = False
                    word = []
            word.append(char)
        if word:
            words.append("".join(word))
        return words
            
    
    def _render_line(self, this_line, line, line_offset):
        #FIXME: for words wider than self.width
        if isinstance(this_line, list):
            this_line = u"".join(this_line)
        self.lines.append(this_line)
        surface = self.font.render(this_line, True, self.color)
        x = 0 
        line_part = []
        for index, char in enumerate(this_line):
            true_index = index + line_offset
            if true_index in self.effected_chars:
                if line_part:
                    x += self.font.size(u"".join(line_part))[0]
                    line_part = []
                width = self.font.size(char)[0]
                ef = self.effected_chars[true_index]
                # Prepare to update chars in callback
                # after line effects are applied
                self.loading_chars.append ((ef,
                    true_index, line, x, width))
                x += width
            else:
                line_part.append(char)
        self.surf_lines.append(surface)
        
        
    def load_chars(self, surfaces):
        for char, pos, line, x, width in self.loading_chars:
            surface = surfaces[line]
            # print ord(self.text[pos]), self.text[pos], r, surface.get_size()
            # Sometimes a font.size difference due to kerning 
            # will make r wider than it should (it
            # is happening withthe letter 'j' with the font I am using for devel)
            r = (x, 0, min(width, surface.get_width() - x) , surface.get_height())
            char_surface = surface.subsurface(r).copy()
            char.load(pos, line, (x,0), char_surface)
            surface.fill((0,0,0,0), r)
    def __getitem__(self, index):
        return self.text.__getitem__(index)
    def __len__(self):
        return len(self.text)
    
    @dirties
    def insert(self, index, value, 
               effected=False):
        old_text = self.text
        self.text = self.text[0:index] + value + self.text[index:]
        self.offset_effected(index, 1)
        #should raise an exception when the text don't fit
        if self.strict:
            self.render()
            if (len(self.lines) > self.max_lines or
                any(rendered_line.get_width() > self.width 
                    for rendered_line in self.surf_lines)):
                self.text = old_text
                return
        if effected:
            self.effect_callback(index, value)

    @dirties
    def delete(self, index):
        self.text = self.text[:index]  + self.text[index + 1:]
        if index in self.effected_chars:
            del self.effected_chars[index]
        self.offset_effected(index, -1)
    
    def offset_effected (self, index, offset):
        if offset < 0:
            comp = cmp
        else:
            comp = lambda a, b: -cmp(a, b)
        for effected in sorted(self.effected_chars.keys(), comp):
            if effected < index:
                continue
            if effected > index:
                del self.effected_chars[effected]
            else:
                self.effected_chars[effected + offset] = self.effected_chars[effected]
                del self.effected_chars[effected]
                

    @cached
    @clears
    def render(self):
        self.loading_chars = []
        self.surf_lines = []
        self.lines = []
        line_number = 0
        this_line = []
        line_offset = 0
        for word in self._words():
            tentative_line = u"".join(this_line) + word
            if self.font.size(tentative_line)[0] > self.width:
                str_this_line = u"".join(this_line)
                self._render_line(str_this_line, line_number, line_offset)
                line_offset += len(str_this_line)
                line_number += 1
                this_line = [word]
            else:
                this_line.append(word)
        else:
            if this_line:
                self._render_line(u"".join(this_line), line_number, line_offset)
        self.rendered += 1
        return self.surf_lines
    
    @cached
    def get_cursor_rect(self, pos, width=2):
        line, pos = self.get_cursor_line(pos)
        if self.lines:
            h_pix_pos, fh = self.font.size(self.lines[line][:pos])
        else:
            h_pix_pos = 0
            fh = self.font.size("|")[1]
        v_pix_pos = fh * line
        return pygame.Rect(h_pix_pos, v_pix_pos, width, fh)
    
    @cached
    def get_cursor_line(self, pos):
        if pos < 0:
            return 0, 0
        line = 0
        while (line < len(self.lines) and
            pos > len(self.lines[line])):
            pos -= len(self.lines[line])
            line += 1
        if line >= len(self.lines):
            if self.lines:
                line = len(self.lines) - 1
                pos = len(self.lines[-1])
            else:
                line = 0
                pos = 0
        return line, pos

    def _nearest_h_pos(self, line, reference, ch_pos, last_pos=None):
        if last_pos is None:
            last_pos = ch_pos
        pix_pos, fh = self.font.size(self.lines[line][:last_pos])
        m_size, fh= self.font.size("m")
        if abs(pix_pos - reference) < m_size * 0.6:
            return last_pos
        direction = int(- (pix_pos - reference) / abs(pix_pos - reference))
        if last_pos + direction < 0:
            return 0
        if last_pos + direction >= len(self.lines[line]):
            return len(self.lines[line])
        return self._nearest_h_pos(line, reference, ch_pos, last_pos + direction)
    
    def cursor_vert(self, pos, v_mov):
        """
           Calculates the new cursor position relative to
           the text body when moving it vertically
           (by v_mov lines)
        """
        #FIXME: make it remember the original
        #h_pos for consecutive vertical movements
        # (probably will have to internalize
        #  the cursor position in this object)
        line, h_pos = self.get_cursor_line(pos)
        new_line = line + v_mov
        if new_line < 0 or new_line >= len(self.lines):
            return pos
        #Quick and dirty:
        #return pos + v_mov * len(self.lines[line])
        h_pix_pos, fh = self.font.size(self.lines[line][:h_pos])
        new_h_pos = self._nearest_h_pos(new_line, h_pix_pos, h_pos)
        return sum(len(self.lines[i]) for i in xrange(new_line)) + new_h_pos

    def dirty(self):
        self._dirty = True

class Editor(KeyboardMaps):
    def __init__(self, screen,
                 rect=None, font=None,
                 text="",
                 color=(0, 0, 0),
                 background=(255, 255, 255),
                 clip=None,
                 keymap="pt_BR"):
        self.screen = screen
        if rect is None:
            self.rect = screen.get_rect()
        else:
            self.rect = pygame.rect.Rect(rect)
        if font is None:
            self.font = pygame.font.Font ("VeraSeBd.ttf", 25)
        else:
            self.font = font
        if clip is None:
            self.clip = self.rect
        else:
            self.clip = clip
        lines = int(self.rect.height) / self.font.size("|")[1]
        self.text = Text(self.font, self.rect.width, color, text, lines, self.effect_callback)
        self.margin = 5
        self.color = color 
        self.cursor_color = color
        self.cursor_rate = 15
        self.background = background
        self.cursor = 0
        self.phase = 0
        self.effects = []
        self.char_effects = []
        self.set_keymap(keymap)
        self.last_char = None
        self.update()
    
    def effect_callback(self, index, value):
        char = EffectedChar(index, 0, self.char_effects)
        self.text.effected_chars[index] = char
    
    def keypressed(self, key):
        char = ""
        mods = pygame.key.get_mods()
        shift = mods & KMOD_SHIFT
        # the 16384 bellow is the actual code
        # for RALT I am gettin here  #pygamebug
        alt = mods & (KMOD_ALT | 16384)
        if key == K_ESCAPE:
            raise QuitEditor
        elif key == K_BACKSPACE:
            if self.cursor > 0:
                self.text.delete(self.cursor - 1)
                self.cursor -= 1
        elif key == K_DELETE:
            self.text.delete(self.cursor)
        elif key == K_RIGHT:
            if self.cursor <= len(self.text):
                self.cursor += 1
        elif key == K_LEFT:
            if self.cursor > 0:
                self.cursor -= 1
        elif key == K_UP:
            self.cursor = self.text.cursor_vert(self.cursor, -1)
        elif key == K_DOWN:
            self.cursor = self.text.cursor_vert(self.cursor, 1)
        elif key == 0 and shift: # SDL pt_BR map bug, see above
            char = u"`"
        # FIXME: pt_BR keyboard specific:
        elif key == ord(u"ç"):
            if shift:
                char = u"Ç"
            else:
                char = u"ç"
        elif 32 <= key <= 127:
            char = unichr(key)
            
            if char in self.keymap_alt_shift and alt and shift:
                char = self.keymap_alt_shift[char]
            elif char in self.keymap_alt and alt:
                char = self.keymap_alt[char]
            elif char in self.keymap and shift:
                char = self.keymap[char]
            if char.isalpha() and shift:
                char = char.upper()
        if char in Editor.unicode_composition:
            if  self.last_char == char:
                char = char
                self.last_char = None
            else:
                self.last_char = char
                char = ""
        elif self.last_char and char:
            extended = char + Editor.unicode_composition[self.last_char]
            extended = unicodedata.normalize("NFC", extended)
            if len(extended) == 1:
                char = extended
            else:
                char = self.last_char + char
            self.last_char = None
        self.insert(self.cursor, char)
        self.cursor += len(char)
        
    def insert(self, position, text):
        for char in text:
            self.text.insert(position, char, bool(self.char_effects))
            position += 1

    def update(self):
        original_clip = self.screen.get_clip()
        self.screen.set_clip(self.clip)
        pygame.draw.rect(self.screen, self.background , self.rect)
        surfaces = self.text.render()
        
        surfaces = self.apply_line_effects(surfaces)
        self.text.load_chars(surfaces)
        top = self.rect.top
        linecoords = {}
        for i, line in enumerate(surfaces):
            coords = Coord((self.rect.left + self.margin, top + self.margin))
            self.screen.blit(line, coords)
            linecoords[i] = coords
            top += line.get_height()
        self.apply_char_effects(linecoords)
        self.draw_cursor()
        self.screen.set_clip(original_clip)
        
    def apply_char_effects(self, linecoords):
        effected_chars = self.text.effected_chars
        to_die = []
        for pos, char in effected_chars.items():
            result = char.update()
            self.screen.blit(char.surface,
                 linecoords[char.line] + char.pix_pos +
                 char.pix_offset)
            if result <= DURATIONENDED:
                to_die.append(pos)
        for dying in to_die:
            del self.text.effected_chars[dying]
        if to_die:
            self.text.dirty()
        
    def draw_cursor(self):
        if not (self.phase // self.cursor_rate) % 2:
            return
        cursor_rect = self.text.get_cursor_rect(self.cursor)
        pygame.draw.rect(self.screen, self.cursor_color,
            (self.rect.left + self.margin + 
                cursor_rect.left,
             self.rect.top + self.margin +
                cursor_rect.top, 
             cursor_rect.width, cursor_rect.height))
    

    def apply_line_effects(self, lines):
        self.phase += 1
        new_lines = lines[:]
        for effect in self.effects:
            for i, line in enumerate(new_lines):
                new_lines[i] = effect(line, i,self.phase)
        if not self.effects and self.char_effects:
            new_lines = []
            for line in lines:
                new_lines.append(line.copy())
        return new_lines
    
    def add_char_effect(self, effect, **parameters):
        self.char_effects.append(CharEffect(effect, **parameters))

    def add_line_effect(self, effect, **parameters):
        self.effects.append(LineEffect(effect, **parameters))
        
if __name__ == "__main__":
    setup()
    pygame.draw.rect(SCREEN, (255,255,255), (10, 10, 600, 200), 3 )
    pygame.display.flip()
    editor = Editor(SCREEN, (15, 15, 590, 190), text="""Unicamp -  IA """, font=FONT)
    """cows cows cows MOOOOOOooooooo cows go moo when they poo cows   Tractoooorrr   I mmilk my cows moooooo mooo mooo tractor  i am a farmer  mooooooooooooooo  tractor"""
    #
    #editor.add_line_effect(Colors)
    #editor.add_line_effect(Waves, amplitude=0.3, align="center")
    #editor.add_char_effect(CharWalk)
    #editor.add_char_effect(CharTranslucence)
    editor.add_char_effect("CharImplode")
    editor.add_char_effect(CharRot, angle=-720, scale=1.5, duration=45)
    try:
        while True:
            pygame.event.pump()
            event = pygame.event.poll()
            while event.type != NOEVENT:
                if event.type == pygame.KEYDOWN:
                    editor.keypressed(event.key)
                event = pygame.event.poll()
            editor.update()
            pygame.display.flip()
            pygame.time.delay(30)

    finally:
        pygame.quit()
