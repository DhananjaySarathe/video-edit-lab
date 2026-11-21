"""Original screen actions and edits shown with purpose-built interfaces and real plates."""
from functools import lru_cache
from math import sin

from PIL import Image, ImageDraw

from preview_common import ease, font, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, PORTRAIT, chip, words
from preview_hook_showcase_short_evidence import BLUE, card, conclusion, small
from preview_hook_showcase_short_optics import GREEN, RED, RULE, stage
from preview_plates import shot


def cursor(d,x,y):
    d.polygon(((x,y),(x+4,y+24),(x+10,y+15),(x+20,y+13)),fill=INK,outline=PAPER)


def button(d, at, text, active=False):
    x,y=at
    length=max(81,round(font(17).getlength(text))+26)
    d.rounded_rectangle((x,y,x+length,y+36),5,fill=GREEN if active else '#dce6d7',outline=RULE,width=1)
    words(d,(x+13,y+18),text,17,PAPER if active else INK)


def blank_error(t):
    frame,d=stage(('Open on the', 'real save error.'))
    card(d,(18,170,342,472))
    words(d,(31,201),'Export name',23,INK)
    fixed=t>=2.7
    d.rounded_rectangle((31,255,325,303),6,outline=GREEN if fixed else RED,width=2)
    value='Studio opening'[:int(22*progress(t,2.7,3.55))]
    if value:
        words(d,(40,278),value,22,INK)
    words(d,(36,326),'Required field' if not value else 'Valid name',16,RED if not value else GREEN)
    button(d,(34,380),'Save',t>=3.6)
    if .95<=t<2.7:
        d.line((285,336,296,308),fill=RED,width=3)
        d.polygon(((296,308),(288,315),(300,318)),fill=RED)
    cursor(d,102 if t<.95 else 78,405 if t<.95 or t>=3.6 else 274)
    conclusion(d,'“Studio opening” saved' if 3.7<=t else 'The missing name blocks the save')
    return frame


def linked_output(t):
    frame,d=stage(('Put the setting', 'beside the result.'))
    on=t>=1.87
    base=shot('host-live',.45+min(2.3,t*.45),1.1,-37,0,(302,176))
    frame.paste(base,(28,229))
    chip(d,(35,241),'Preview',INK,PAPER,13)
    if on:
        d.rounded_rectangle((51,355,308,386),5,fill=INK)
    words(d,(180,370),'Bring the foreground back.',17,PAPER,'mm')
    if t>=.95:
        card(d,(27,164,330,218))
        words(d,(38,189),'Caption background',16,INK)
        d.rounded_rectangle((254,175,316,204),14,fill=GREEN if on else '#9ba899')
        px=301 if on else 270
        d.ellipse((px-10,179,px+10,200),fill=PAPER)
        if 1.47<=t<2.15:
            cursor(d,270,189)
    else:
        chip(d,(28,172),'Export only',INK,PAPER,15)
    if t>=2.7:
        conclusion(d,'Same source frame / setting on')
    return frame


def safe_corner(t):
    image=shot('editing-live',.2+t*.34,1.03,0,0,PORTRAIT)
    d=ImageDraw.Draw(image)
    p=sin(t*2.2)
    x,y=round(96+43*p),round(332+17*p)
    d.rounded_rectangle((x-12,y-36,x+195,y+76),6,fill='#f1ecdf',outline=INK,width=2)
    words(d,(x,y-17),'Practice profile',17,INK)
    d.line((x,y,x+174,y),fill=RULE)
    words(d,(x,y+16),'Account',13,INK)
    if t < .95:
        words(d,(x,y+48),'demo_acct_028',21,INK,weight='mono')
    else:
        d.rounded_rectangle((x-2,y+32,x+178,y+62),3,fill=INK)
        if t<2.7:
            d.rounded_rectangle((x-6,y+28,x+182,y+66),5,outline=GOLD,width=2)
    chip(d,(22,539),'Mask stays on the same panel',INK,MINT,16)
    return image


def hold_menu(t):
    frame,d=stage(('Keep the menu', 'open through the cue.'))
    card(d,(21,173,339,472))
    words(d,(36,206),'Export size',23,INK)
    fixed=t>=2.7
    closed=t<.95 or t>=4.5
    button(d,(36,245),'1080 px' if t<4.5 else '2160 px',t>=4.5)
    if not closed:
        for i,label in enumerate(('720 px','1080 px','2160 px')):
            y=291+i*39
            d.rounded_rectangle((36,y,252,y+35),4,fill=MINT if i==2 and fixed else '#e4e9db')
            words(d,(45,y+17),label,19,INK)
        cursor(d,149,395 if fixed else 265)
    if t<.95 or t>1.65:
        conclusion(d,'Choose 2160 px' if t<4.5 else '2160 px confirmed')
    return frame


def lag(t):
    frame,d=stage(('Wait for the', 'confirmation.'))
    card(d,(20,181,340,476))
    words(d,(34,218),'Save a sample note',21,INK)
    words(d,(34,276),'Rehearsal at 15:30',21,INK)
    d.line((33,304,322,304),fill=RULE)
    if t<.95:
        button(d,(34,332),'Save',True)
        if t>.32:
            chip(d,(24,526),'Cut here hides the result',INK,PAPER,16)
    elif t < 3.47:
        d.arc((40,339,76,375),int(t*590),int(t*590)+235,fill=GREEN,width=5)
        words(d,(91,357),'Saving…',23,INK)
    else:
        words(d,(37,347),'✓  Saved',31,GREEN)
        small(d,(38,399),'Rehearsal at 15:30')
        conclusion(d,'Cut after this state appears')
    if t < 1.25:
        cursor(d,63,353)
    return frame


def saved_button(t):
    frame, draw = stage(('Did the edit', 'really save?'))
    base = shot('coffee-live', .85, size=(304, 170))
    frame.paste(base, (28, 171))
    card(draw, (25, 352, 335, 476))
    too_early = t < .95
    confirming = 1.48 <= t < 2.41
    confirmed = t >= 2.41
    button(draw, (40, 365), '✓ Saved' if confirmed else 'Saving…' if confirming else 'Save grade', confirmed)
    if .4 <= t < .95:
        chip(draw, (38, 258), 'Saved!', '#a74831', PAPER, 19)
    elif confirming:
        draw.arc((270, 363, 300, 392), round(t * 400), round(t * 400) + 205, fill=GREEN, width=4)
    if t < 1.53:
        cue = sin(progress(t, 1.28, 1.52) * 3.141593)
        cursor(draw, 104, 396 - round(12 * cue))
    small(draw, (41, 445), 'Still waiting' if too_early or confirming else 'Version 2 written' if confirmed else 'Tap once')
    conclusion(draw, 'Start the explanation after ✓' if confirmed else 'Wait for the button itself')
    return frame


@lru_cache(maxsize=6)
def display(tick, wide=False):
    stamp=tick/20
    image=shot('host-live',stamp,1.01,-48 if wide else -66, -12,(316,222))
    d=ImageDraw.Draw(image)
    px=273 if wide else 340
    if stamp>=.65:
        d.ellipse((px-27,153,px+27,207),fill='#db8e60',outline=GOLD,width=3)
        d.ellipse((px-6,176,px+6,188),fill=INK)
    return image


def hidden_punchline(t):
    frame,d=stage(('The crop lost', 'the reveal.'))
    stamp = min(2.15, .42+t if t<1.05 else .52 + (t-1.05)*.70)
    wide=t>=1.69
    frame.paste(display(round(stamp*20),wide),(22,185))
    if wide:
        d.ellipse((272,320,320,382),outline=GOLD,width=3)
    chip(d,(22,479),'Wider crop reveals the prop' if wide else 'Tight crop hides the prop',INK,MINT,15)
    if t>=2.55:
        chip(d,(22,529),'Next shot / cut on the look',INK,PAPER,15)
    return frame


def trim_black(t):
    frame,d=stage(('What is the', 'first export frame?'))
    fixed=t>=1.8
    picture=t>=.48 if t<.95 else fixed
    if picture:
        source=min(2.4, max(0.,t-1.8 if fixed else t-.48))
        frame.paste(shot('host-live',source,1.22,-31,-20,(308,182)),(26,190))
    else:
        d.rectangle((26,190,334,372),fill='#090c0b')
    chip(d,(32,198),'First frame / final export' if t>=2.7 else 'Program',INK,PAPER,15)
    d.rounded_rectangle((26,407,334,477),6,fill='#d9e2d1',outline=RULE)
    x=28 if fixed else 97
    d.rounded_rectangle((x,422,325,457),3,fill=GREEN)
    words(d,(x+10,439),'Presenter',16,PAPER)
    if not fixed:
        words(d,(35,439),'BLACK',13,RED)
    d.line((28,399,28,476),fill=RED,width=2)
    conclusion(d,'First visible frame at 0:00' if fixed else 'Remove empty head')
    return frame


def switch_mode(t):
    frame,d=stage(('Label the', 'mode change.'))
    active=t>=1.75
    card(d,(19,177,341,483))
    words(d,(33,205),'Canvas',21,INK)
    d.rounded_rectangle((34,244,325,408),5,fill='#e5eadc')
    offset=round(56*ease(progress(t,2.55,4.12))) if active else 0
    d.rounded_rectangle((107+offset,279,187+offset,365),5,fill='#bc6d52',outline=INK)
    if active:
        for u,v in ((107,279),(187,279),(107,365),(187,365)):
            d.rectangle((u+offset-3,v-3,u+offset+3,v+3),fill=GREEN)
    if 1.75<=t<3.1:
        chip(d,(42,251),'Move mode',INK,MINT,15)
    button(d,(35,425),'Move' if active else 'Select',True)
    if t>2.7:
        cursor(d,171+offset,322)
    return frame


def practice_offline(t):
    frame,d=stage(('Will the saved', 'item open offline?'))
    card(d,(23,165,337,487))
    connected=t>=4.31
    chip(d,(34,181),'Wi-Fi connected' if connected else 'Offline',INK,PAPER,16)
    q=t>=1.83
    box=(38,237,321,280)
    d.rounded_rectangle(box,5,outline=GREEN,width=2)
    words(d,(49,257),'Gate checklist' if q else 'Search saved notes',17,INK)
    if q or t<1.2:
        d.rectangle((40,309,322,388),fill='#dbe8d8')
        words(d,(47,332),'Gate checklist',22,INK)
        small(d,(48,364),'Saved on this device')
    if t>=2.8:
        small(d,(39,443),'Opening saved copy ✓')
    conclusion(d,'Original practice interface')
    if 1.2<=t<2.42:
        cursor(d,58,255)
    return frame


def undo_draft(t):
    frame,d=stage(('Can undo bring', 'back the words?'))
    card(d,(21,167,341,485))
    words(d,(34,204),'Schematic notes',24,INK)
    d.line((33,234,323,234),fill=RULE)
    words(d,(36,263),'First measure the opening.',17,INK)
    present=not 1.27<=t<1.98
    if t<3.15 and present:
        words(d,(36,302),'Use the smaller spacer.',17,BLUE if t>=1.98 else INK)
    if t<3.15:
        button(d,(37,348),'Undo',1.27<=t<1.98)
        small(d,(41,438),'Current draft / 14:12')
    else:
        small(d,(39,336),'Earlier revision / 14:09')
        chip(d,(35,375),'Earlier draft ended after line 1.',INK,PAPER,14)
    conclusion(d,'Saved revisions came from this example')
    return frame


def phone_state(t):
    frame,d=stage(('It says ready.', 'Then it reverts.'))
    ready=t<.95
    card(d,(24,185,337,465))
    words(d,(37,216),'Test controller',22,INK)
    button(d,(37,269),'Connect',True)
    small(d,(42,338),'Current state')
    words(d,(40,380),'Ready' if ready else 'Needs pairing',28,GREEN if ready else RED)
    if t>=2.55:
        small(d,(39,431),'First check: paired device')
    if t<1.45:
        cursor(d,98,294)
    conclusion(d,'Staged interface / one visible state change')
    return frame


def original_date(t):
    frame,d=stage(('The date is', 'on the back.'))
    source=shot('walk-live',1.1,1,-70,0,(300,203))
    flip=ease(progress(t,.7,1.34)) if t<2.55 else 1-ease(progress(t,2.55,3.03))
    thickness=max(5,round(300*abs(1-2*flip)))
    photo=Image.new('RGB',(300,203),'#f9f5e6')
    p=ImageDraw.Draw(photo)
    if flip>.5:
        words(p,(150,101),'18 OCT 2024',27,INK,'mm',weight='mono')
        words(p,(150,143),'PRACTICE ARCHIVE',14,RULE,'mm')
    else:
        photo.paste(source,(0,0))
    frame.paste(photo.resize((thickness,203),Image.Resampling.BICUBIC),(180-thickness//2,229))
    if t>=2.55:
        chip(d,(29,464),'18 Oct 2024 / example date',INK,MINT,15)
    return frame


def tracked_note(t):
    base=shot('room',0,size=(535,790))
    x=round(82 + 57*sin(t*1.33))
    y=round(69 + 19*sin(t*1.64))
    sticky=(264,309)
    if t>=.95:
        detail=ImageDraw.Draw(base)
        detail.rectangle((sticky[0],sticky[1],sticky[0]+119,sticky[1]+75),fill=GOLD,outline=INK,width=2)
        words(detail,(sticky[0]+9,sticky[1]+32),'KEEP CLEAR',16,INK)
    im=base.crop((x,y,x+360,y+640))
    d=ImageDraw.Draw(im)
    if t<.95:
        d.rectangle((210,236,329,310),fill=GOLD,outline=INK,width=2)
        words(d,(219,273),'KEEP CLEAR',16,INK)
    elif t<2.7:
        px,py=sticky[0]-x,sticky[1]-y
        d.line((px,py,px-52,py-46),fill=GOLD,width=3)
        chip(d,(max(13,px-134),max(54,py-70)),'Wall track',INK,PAPER,15)
    chip(d,(17,515),'Note drifts on the wall' if t<.95 else 'Note locked to the wall plane')
    return im


SCENES={}
for family, entries in (
    ('specific-fix',{31:blank_error,34:linked_output,35:safe_corner,36:hold_menu,37:switch_mode,38:lag,85:saved_button,90:trim_black,95:tracked_note}),
    ('live-contradiction',{61:practice_offline,62:undo_draft}),
    ('turning-point',{3:hidden_punchline,78:original_date,81:phone_state}),
):
    SCENES.update({f'hook-short-{family}-{n:03}':scene for n,scene in entries.items()})
POSTERS={key:.65 for key in SCENES}
