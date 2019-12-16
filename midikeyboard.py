import Quartz
import pygame.midi
import asyncio

class MIDIListener():
    
    keydict={
        #36:0x35,#esc
        #37:0x7A,#F1
        #38:0x78,#F2
        #39:0x63,#F3
        #40:0x76,#F4
        #41:0x60,#F5
        #42:0x61,#F6
        #43:0x62,#F7
        #36:0x64,#F8
        #44:0x65,#F9
        #45:0x6D,#F10
        #46:0x67,#F11
        #47:0x6F,#F12
        38:0x35,#esc
        48:0x0C,#q
        49:0x00,#a
        50:0x06,#z
        51:0x0D,#w
        52:0x01,#s
        53:0x07,#x
        54:0x0E,#e
        55:0x02,#d
        56:0x08,#c
        57:0x0F,#r
        58:0x03,#f
        59:0x09,#v
        60:0x11,#t
        61:0x05,#g
        62:0x0B,#b
        63:0x10,#y
        64:0x04,#h
        65:0x2D,#n
        66:0x20,#u
        67:0x26,#j
        68:0x2E,#m
        69:0x22,#i
        70:0x28,#k
        71:0x2B,#,
        72:0x1F,#o
        73:0x25,#l
        74:0x2F,#.
        75:0x23,#p
        76:0x29,#;
        77:0x2C,#/
        78:0x21,#{
        79:0x27,#'
        80:0x1E,#}
        81:0x2A,#\
        82:0x32,#`quote
        83:0x4E,#-
        84:0x45,#+
        88:0x7B,#左矢印
        89:0x7D,#下矢印
        90:0x7E,#上矢印
        91:0x7C,#右矢印
        93:0x30,#tab
        94:0x33,#delete
        95:0x31,#space
        96:0x24,#return
    }
    keydict_num={
        151:0x1D,#0
        86:0x1D,#0
        166:0x12,#1
        92:0x12,#1
        160:0x12,#1
        93:0x13,#2
        171:0x13,#2
        195:0x13,#2
        214:0x14,#3
        202:0x14,#3
        233:0x15,#4
        216:0x17,#5
        252:0x16,#6
        199:0x1A,#7
        211:0x1A,#7
        281:0x1C,#8
        87:0x1C,#8
        217:0x19,#9
    }
    '''
    kVK_Command = 0x37,
    kVK_Shift = 0x38,
    kVK_CapsLock = 0x39,
    kVK_Option = 0x3A,
    kVK_Control = 0x3B,
    '''

    def __init__(self):
        self.shift = False
        self.command = False
        self.switcher = False
        self.mousedown = False
        self.pedaldown = False
        self.keydown = 0
        self.keyup = 0
        self.keyup_continue = 0
        self.event_log = []

        pygame.init()
        pygame.midi.init()
        input_id = pygame.midi.get_default_input_id()
        self.midi_input = pygame.midi.Input(input_id)

    def __call__(self):

        self.position = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))	# 座標取得

        if self.midi_input.poll():
            events = self.midi_input.read(10) # 10イベント分読み込む
            for event in events:
                #debug
                #print(event)

                #switcher
                if event[0][0] == 144 and event[0][1] == 36:
                    self.switcher = True
                elif event[0][0] == 128 and event[0][1] == 36:
                    self.switcher = False

                #pedal
                if event[0][0] == 176 and event[0][1] == 64 and event[0][2] == 127:
                    self.pedaldown = True
                elif event[0][0] == 176 and event[0][1] == 64 and event[0][2] == 0:
                    self.pedaldown = False
                if self.pedaldown is True:
                    if self.switcher:
                        self.command = True
                        self.shift = False
                    else:
                        self.shift = True
                        self.command = False
                else:
                    self.shift = False
                    self.command = False
                    self.send_key(0x3B, True)
                    self.send_key(0x3B, False)

                #使いづらい
                #プラグ抜くときにevent[0][2]が0の状態では抜けない
                #elif event[0][0] == 176 and event[0][1] == 11:
                #    #control pedal
                #    self.command = event[0][2] > 0
                #    if self.command is False:
                #        self.send_key(0x3B, True)
                #        self.send_key(0x3B, False)

                #click - C2#
                if event[0][0] == 144 and event[0][1] == 37:
                    self.single_click(Quartz.kCGEventLeftMouseDown) #1
                    self.mousedown = True
                elif event[0][0] == 128 and event[0][1] == 37:
                    self.single_click(Quartz.kCGEventLeftMouseUp) #2
                    self.mousedown = False

                #move - stick
                if event[0][0] == 224:
                    self.move_pointer(event[0][2])

                #alphabet
                if event[0][0] == 144 and event[0][2] > 37:
                    #順番にqazwsxedcrfvtgbyhnujmikolp
                    if event[0][1] in MIDIListener.keydict:
                        note_num=MIDIListener.keydict[event[0][1]]
                        self.send_key(note_num, True)
                        self.send_key(note_num, False)
                        self.keydown+=1
                elif event[0][0] == 128 and event[0][2] > 0:
                        self.keyup+=1
                self.event_log.append(event)

                #number
                for i in reversed(range(len(self.event_log))):
                    if i+3==len(self.event_log):
                        if self.event_log[i][0][0] == 176 and (self.event_log[i][0][2] == 86 or self.event_log[i][0][2] == 87):
                            num_hash=self.event_log[i][0][2]+self.event_log[i+1][0][2]+self.event_log[i+2][0][1]
                            if num_hash in MIDIListener.keydict_num:
                                note_num=MIDIListener.keydict_num[num_hash]
                                self.send_key(note_num, True)
                                self.send_key(note_num, False)
                                self.event_log=[]

            #double click
            clickflag=0
            for i in reversed(range(len(self.event_log))):
                if len(self.event_log)>2 and (self.event_log[i][0][0]==224 or self.event_log[i-1][0][0]==224 or self.event_log[i-2][0][0]==224):
                    break
                elif clickflag==2 and self.keyup_continue<6:
                    self.double_click()
                    self.event_log=[]
                    clickflag=0
                    break
                elif self.event_log[i][0][0]==144 and self.event_log[i][0][1]==37:
                    clickflag += 1
            else:
                clickflag = 0

            self.keyup_continue = 0
        else:
            self.keyup_continue += 1

            #連続移動
            if len(self.event_log)>0 and self.event_log[-1][0][0] == 224 and not self.event_log[-1][0][2] == 64:
                self.move_pointer(self.event_log[-1][0][2])

            #連続入力
            if self.keyup_continue > 30 and self.keyup_continue%6 == 0:
                if len(self.event_log) > 0 and not self.keyup == self.keydown:
                    event=self.event_log[-1]
                    if event[0][0] == 144 and event[0][2] > 37:
                        #順番にqazwsxedcrfvtgbyhnujmikolp
                        if event[0][1] in MIDIListener.keydict:
                            note_num = MIDIListener.keydict[event[0][1]]
                            self.send_key(note_num, True)
                            self.send_key(note_num, False)

    def send_key(self, key_code, down):
        event = Quartz.CGEventCreateKeyboardEvent(None, key_code, down)
        if self.shift:
            Quartz.CGEventSetFlags(event, Quartz.kCGEventFlagMaskShift)
        elif self.command:
            Quartz.CGEventSetFlags(event, Quartz.kCGEventFlagMaskCommand)
        else:
            Quartz.CGEventSetFlags(event, 0)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    
    def single_click(self, down):
        event = Quartz.CGEventCreateMouseEvent(None, down, self.position, 0)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def double_click(self):
        event = Quartz.CGEventCreateMouseEvent(None, 1, self.position, 0)
        Quartz.CGEventSetIntegerValueField(event, 1, 2)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        Quartz.CGEventSetType(event, 2)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        Quartz.CGEventSetType(event, 1)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        Quartz.CGEventSetType(event, 2)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def move_pointer(self, dist):
        if self.pedaldown:
            self.position.y += dist-64
            #self.position.y = max(self.position.y,0)
        else:
            self.position.x += dist-64
            #self.position.x = max(self.position.x,0)
        if self.mousedown:
            event = Quartz.CGEventCreateMouseEvent(None, 6, self.position, 0) #6がドラッグのなんか
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        else:
            Quartz.CGDisplayMoveCursorToPoint(0, self.position)

async def periodic_call(intvl, func):
    while True:
        func()
        await asyncio.sleep(intvl)

if __name__ == '__main__':
    midi_listener = MIDIListener()
    task = asyncio.Task(periodic_call(0.01, midi_listener))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)