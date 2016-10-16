#!/usr/bin/python
# coding: utf-8
import sys
import math
import json
import random
import pygame

sys.setrecursionlimit(10000)


def round_spiral(pos, radius, rounds, step, rotation):
    x, y = pos
    maxTheta = rounds * 2 * math.pi
    awayStep = radius/maxTheta
    theta = step/awayStep

    while theta <= maxTheta:
        away = awayStep * theta
        around = theta + rotation
        newX = x + math.cos(around) * away
        newY = y + math.sin(around) * away
        theta += step/away
        yield (int(newX), int(newY))


def square_spiral(pos, radius, rounds, step, rotation):
    x, y = pos
    sx = sy = 0
    step = radius/rounds
    dx = 1
    dy = 0
    i = 3
    for _ in xrange((rounds+rounds+1)**2):
        yield x, y
        x = x+dx*step
        y = y+dy*step
        sx += dx
        sy += dy
        if (abs(sx) == abs(sy) and i < 3) or (abs(sy)+1 == abs(sx) and i == 3):
            if i < 3:
                i += 1
            else:
                i = 0
            dx, dy = -dy, dx


def weight_words(strFilename, lstExclude=[], intCutoff=10):
    lstReplace = [".", ",", "\n", "(", ")"]
    fh = open(strFilename, "rb")
    strText = fh.read()
    for r in lstReplace:
        strText = strText.replace(r, "")
    lstText = strText.split(" ")
    dctWords = {}
    dctFull = {}

    for w in lstText:
        # w = w.lower()
        if len(w) > 2 and w.lower() not in lstExclude:
            if w not in dctWords:
                dctFull[w] = w
                dctWords[w] = 0
            dctWords[w] += 1
        # elif w not in lstExclude:
            # print w.lower()
            # pass
    dctOut = {}
    lstSuffix = ["ed", "s", "d", "en"]
    lstDel = []
    for w in dctWords:
        for suffix in lstSuffix:
            if w.endswith(suffix):
                shortWord = w[:-len(suffix)]
                if shortWord in dctWords:
                    dctWords[shortWord] += dctWords[w]
                    lstDel.append(w)
    for x in set(lstDel):
        del dctWords[x]
    lstSorted = sorted(dctWords, key=lambda x: dctWords[x], reverse=True)
    lstWeights = [dctWords[_] for _ in lstSorted]
    for w in lstSorted[:intCutoff]:
        dctOut[w] = dctWords[w]*1.0/max(lstWeights[:intCutoff])

    return dctOut, dctFull


class Rect(object):
    def __init__(self, x, y, w, h):
        self.x = self.l = x
        self.y = self.t = y
        self.w = w
        self.h = h
        self.b = y + h
        self.r = x + w

    def coords(self):
        return [(self.x, self.y), (self.x+self.w, self.y+self.h)]

    def intersect(self, rect):
        if (rect.l < self.r and rect.r > self.l and
                rect.t < self.b and rect.b > self.t):
            return True
        else:
            return False

    def draw(self, draw):
        draw.rectangle([(self.l, self.t), (self.r, self.b)],
                       outline="red")


class PyWord(object):
    def __init__(self, strText, intSize, strFont,
                 intRotation, tplColor, intBorder=1):
        self.font = pygame.font.SysFont(strFont, intSize)
        strText = strText.replace("~", " ")
        self.txt = strText
        self.x = 0
        self.y = 0
        txt = self.font.render(strText, True, tplColor)
        txt = pygame.transform.rotozoom(txt, intRotation, 1.0)
        self.w, self.h = txt.get_size()
        self.w += intBorder*2
        self.h += intBorder*2
        self.img = pygame.Surface((self.w, self.h))
        self.img = self.img.convert_alpha()

        self.img.fill((255, 255, 255, 0))
        self.img.blit(txt, (intBorder, intBorder))

        self.msk = pygame.Surface((self.w, self.h))
        self.msk = self.msk.convert_alpha()
        self.msk.fill((255, 255, 255, 0))
        mtxt = self.font.render(strText, True, (255, 0, 255, 128))
        mtxt = pygame.transform.rotate(mtxt, intRotation)

        self.msk.blit(mtxt, (0, 0))
        self.msk.blit(mtxt, (0, intBorder))
        self.msk.blit(mtxt, (0, intBorder*2))

        self.msk.blit(mtxt, (intBorder, 0))
        self.msk.blit(mtxt, (intBorder, intBorder))
        self.msk.blit(mtxt, (intBorder, intBorder*2))

        self.msk.blit(mtxt, (intBorder*2, 0))
        self.msk.blit(mtxt, (intBorder*2, intBorder))
        self.msk.blit(mtxt, (intBorder*2, intBorder*2))

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.mask = pygame.mask.from_surface(self.msk, 0)

    def setCoords(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        # self.rect = pygame.Rect(self.x-self.w/2, self.y-self.h/2, self.w, self.h)

    def intersect(self, word):
        if self.rect.colliderect(word.rect):
            offset = (word.x-self.x, word.y-self.y)
            if self.mask.overlap(word.mask, offset) is None:
                return False
            else:
                return True
        else:
            return False

    def draw(self, screen, drawBorder=False):
        if drawBorder:
            screen.blit(self.msk, (self.x, self.y))
        screen.blit(self.img, (self.x, self.y))


def draw_overlap(m1, m2, screen):
    m = m1.mask.overlap_mask(m2.mask, (m2.x-m1.x, m2.y-m1.y))
    olist = m.outline()
    if len(olist) > 1:
        olist = [(
            _[0]+(m2.x-(m2.x-m1.x)),
            _[1]+(m2.y-(m2.y-m1.y))) for _ in olist]
        pygame.draw.polygon(screen, (255, 0, 255, 128), olist, 0)


def animated():
    w, h = (851, 315)
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((w, h), pygame.SRCALPHA, 32)

    background = (25, 25, 25)
    screen.fill((255, 255, 255))

    intMax = 128
    intMin = 8
    intLimit = 100
    intMinAngle = 0
    intMaxAngle = 90
    intRotSteps = 2
    intBorder = 0
    strFilename = "thesis_christian.txt"
    # random.seed(strFilename)
    if intMinAngle == intMaxAngle:
        lstRotations = [intMinAngle]
    else:
        lstRotations = range(intMinAngle, intMaxAngle+1,
                             (intMaxAngle-intMinAngle)/(intRotSteps-1))

    lstColors = [(255, 255, 255), tucolors.bricsblue60, tucolors.bricsblue40,
                 tucolors.tured, tucolors.bricsgreen40, (255, 255, 255)]
    strFont = "bluehighway"  # nexussanspro
    border = pygame.Rect(intBorder, intBorder, w-2*intBorder, h-2*intBorder)
    with open("exclude.txt", "rb") as fh:
        lstExclude = fh.read().split("\n")

    dctWords, dctFull = weight_words(strFilename,
                                     lstExclude,
                                     intLimit)
    lstWords = sorted(dctWords.keys(),
                      key=lambda x: dctWords[x],
                      reverse=False)

    intAllWords = len(lstWords)

    strTitle = "WordCloud - {} - {}/{} ({:.1%}) done!"

    cw = w/2
    ch = h/2
    lstPlaced = []
    running = True
    currentWord = None
    last = None
    while running:
        pygame.display.set_caption(strTitle.format(
            strFilename, len(lstPlaced), intAllWords,
            (1.0*len(lstPlaced)/intAllWords)))
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, background, border)
        for wrd in lstPlaced:
            wrd.draw(screen)
        if lstWords or currentWord is not None:
            # Pop new word if needed
            if currentWord is None:
                newWord = lstWords.pop()
                intSize = int((1-dctWords[newWord])*intMin+dctWords[newWord]*intMax)
                # print newWord, dctWords[newWord], intSize
                currentWord = PyWord(newWord, intSize,
                                     strFont, random.choice(lstRotations),
                                     random.choice(lstColors))
                currentWord.setCoords(cw, ch)
                r = w if w > h else h
                spiral = round_spiral((cw, ch), r, 50, 20, 0)
            else:
                # Move word on spiral
                nx, ny = spiral.next()
                nx -= currentWord.w/2
                ny -= currentWord.h/2
                currentWord.setCoords(nx, ny)

            match = None
            if border.contains(currentWord.rect):
                if last is not None and last.intersect(currentWord):
                    match = last
                    for wrd in lstPlaced:
                        wrd.draw(screen)
                else:
                    for wrd in lstPlaced:
                        # Check overlap
                        if wrd != last and match is None and wrd.intersect(currentWord):
                            match = last = wrd
                            break
            else:
                match = border
                for wrd in lstPlaced:
                    # Draw placed words
                    wrd.draw(screen)

            # Draw current word
            currentWord.draw(screen)

            # Draw current overlap
            if match is not None:
                if match != border:
                    draw_overlap(currentWord, match, screen)
            else:
                lstPlaced.append(currentWord)
                currentWord = None
        else:
            for wrd in lstPlaced:
                wrd.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # font = pygame.font.SysFont("nexussanspro", 16)
        # tw, th = font.size("(c) 2016")
        # txt = font.render("(c) 2016", True, (55, 55, 55))
        # screen.blit(txt, (w-tw, h-th))
        pygame.display.flip()

        clock.tick(120)


def main():
    with open("config.json") as fh:
        cfg = json.load(fh)

    w, h = (cfg["image_width"], cfg["image_height"])
    intBorder = cfg["image_border"]
    strMaskName = cfg["image_mask"]
    tplBackground = cfg["image_background"]

    intMax = cfg["font_max"]
    intMin = cfg["font_min"]
    intSpacing = cfg["font_spacing"]
    strFont = cfg["font_file"]
    lstColors = cfg["font_colors"]

    strFilename = cfg["words_file"]
    intLimit = cfg["words_limit"]

    intMinAngle = cfg["angle_min"]
    intMaxAngle = cfg["angle_max"]
    intRotSteps = cfg["angle_steps"]

    if strMaskName is not None:
        maskImage = pygame.image.load(strMaskName)
        w, h = maskImage.get_size()
        mask = pygame.mask.from_surface(maskImage, 0)
    else:
        mask = pygame.mask.Mask((w, h))
        mask.fill()
    mask.invert()

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((w, h))
    screen.fill(tplBackground)

    # random.seed(strFilename)
    if intMinAngle == intMaxAngle:
        lstRotations = [intMinAngle]
    else:
        lstRotations = range(intMinAngle, intMaxAngle+1,
                             (intMaxAngle-intMinAngle)/(intRotSteps-1))

    border = pygame.Rect(intBorder, intBorder, w-2*intBorder, h-2*intBorder)

    strTitle = "WordCloud - {}"
    pygame.display.set_caption(strTitle.format(strFilename))

    fnt = pygame.font.SysFont(strFont, 16)
    tw, th = fnt.size("Please wait...")
    txt = fnt.render("Please wait...", True, (128, 128, 128))
    screen.blit(txt, (w/2-tw/2, h/2-th/2))
    pygame.display.flip()

    with open("exclude.txt", "rb") as fh:
        lstExclude = fh.read().split("\n")

    dctWords, dctFull = weight_words(strFilename,
                                     lstExclude,
                                     intLimit)
    lstWords = sorted(dctWords.keys(),
                      key=lambda x: dctWords[x],
                      reverse=True)
    # print dctWords

    cw = w/2
    ch = h/2
    lstPlaced = []
    running = True
    currentWord = None
    last = None

    # random.seed(strFilename)

    for strWord in lstWords:
        intSize = int((1-dctWords[strWord])*intMin+dctWords[strWord]*intMax)
        currentWord = PyWord(strWord, intSize,
                             strFont, random.choice(lstRotations),
                             random.choice(lstColors),
                             intSpacing)
        last = None
        r = w if w > h else h
        for nx, ny in round_spiral((cw, ch), r, 100, 20, 0):
            match = None
            nx -= currentWord.w/2
            ny -= currentWord.h/2
            currentWord.setCoords(nx, ny)

            if (border.contains(currentWord.rect) and
                    not mask.overlap(currentWord.mask, (currentWord.x, currentWord.y))):
                if last is not None and last.intersect(currentWord):
                    match = last
                else:
                    for wrd in lstPlaced:
                        if wrd != last and match is None and wrd.intersect(currentWord):
                            match = last = wrd
                            break
            else:
                match = border
            if match is None:
                lstPlaced.append(currentWord)
                break
    strMsg = "Please wait..."
    intAlpha = 255
    intDecr = 4
    if len(lstPlaced) != len(lstWords):
        print "Only {} of {} words placed!".format(
            len(lstPlaced), len(lstWords))
    while running:
        screen.fill(tplBackground)
        pygame.draw.rect(screen, tplBackground, border)

        currentWord.draw(screen)
        for wrd in lstPlaced:
            wrd.draw(screen)
        if strMsg is not None:
            if intAlpha > 0:
                overlay = pygame.Surface((w, h))
                overlay.fill(tplBackground)
                fnt = pygame.font.SysFont(strFont, 16)
                tw, th = fnt.size(strMsg)
                txt = fnt.render(strMsg, True, (0, 0, 0))
                overlay.blit(txt, (cw-tw/2, ch-th/2))
                overlay.set_alpha(intAlpha)
                screen.blit(overlay, (0, 0))
                intAlpha -= intDecr
            else:
                strMsg = None
                intAlpha = 255

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.mod == 1024 and event.key == 115:
                    pygame.image.save(
                        screen,
                        "{}_{}x{}.png".format(strFilename, w, h))
                    strMsg = "Image saved as {}_{}x{}.png".format(strFilename, w, h)
                    intAlpha = 255
                    intDecr = 2
        pygame.display.flip()

        clock.tick(120)


def test():
    w, h = (500, 500)
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((w, h), pygame.SRCALPHA, 32)
    pygame.display.set_caption("WordCloud")
    screen.fill((255, 255, 255))

    lstRects = []
    lstCircles = []
    spiral1 = round_spiral((250, 250), 250, 10, 10, 0)
    spiral2 = square_spiral((250, 250), 250, 10, 10, 0)
    running = True
    while running:
        try:
            x, y = next(spiral1)
        except StopIteration:
            pass
        finally:
            lstRects.append(pygame.Rect(x-2, y-2, 4, 4))
        try:
            x, y = next(spiral2)
        except StopIteration:
            pass
        finally:
            lstCircles.append((x, y))
        screen.fill((255, 255, 255))

        for rect in lstRects:
            pygame.draw.rect(screen, (255, 0, 0), rect)
        for circ in lstCircles:
            pygame.draw.circle(screen, (0, 0, 255), circ, 4)

        for event in pygame.event.get():
            # print event
            if event.type == pygame.QUIT:
                running = False

        pygame.draw.rect(screen, (0, 0, 0, 0), (499, 499, 2, 2))
        pygame.display.flip()
        clock.tick(30)
        # print int(clock.get_fps())

if __name__ == '__main__':
    # print pygame.font.get_fonts()
    # main()
    main()
    # pygame.init()
    # scr = pygame.display.set_mode((400, 300), pygame.SRCALPHA, 32)
    # wrd = PyWord("Cluster", 128, "arial.ttf", 0, (255, 0, 0))
    # scr = pygame.display.set_mode((wrd.w, wrd.h), pygame.SRCALPHA, 32)
    # scr.blit(wrd.img, (0, 0))
    # pygame.display.flip()

    # running = True
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
