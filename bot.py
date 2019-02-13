import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)  

#client=MongoClient(os.environ['database'])
#db=client.trugminigames
#users=db.users

allgames=['donkey']
currentgame=[]

class Minigame:
    
    def __init__(self, id=-1001058783080):
        self.playernumber=1
        self.players={}
        self.id=id
        self.winscore=1
        self.kb=types.InlineKeyboardMarkup()
        self.kb.add(types.InlineKeyboardButton(text='Присоединиться', callback_data='join'))
        self.text='None'
        self.started=False
        self.gamekb=types.InlineKeyboardMarkup(4)
        self.message=None
        

class Donkey(Minigame):
    
    def __init__(self, id=-1001058783080):
        global currentgame
        super().__init__(id)
        self.name='Поймай осла'
        self.code='donkey'
        self.playernumber=1
        self.winscore=2
        self.size=[4, 4]
        self.button='⬜️'
        self.data='null'
        self.donkey='🐴'
        self.dplace=None
        self.dspeed=2
        self.turn=1
        self.text='Идёт набор в игру! Требуется игроков: '+str(self.playernumber)
        if currentgame==[]:
            bot.send_message(self.id, self.text, reply_markup=self.kb)
            currentgame.append(self)
        else:
            currentgame[0].timer.cancel()
            currentgame=[]
            bot.send_message(self.id, 'Предыдущая игра была удалена!')
            currentgame.append(self)
        
    def begin(self):
        if self.dplace==None:
            g=1    # Горизонталь
            v=1    # Вертикаль
            dv=random.randint(1,self.size[1])  # v осла
            dg=random.randint(1,self.size[0])  # g осла
            d=str(dg)+str(dv)
            self.dplace=d
        else:
            d=self.dplace
        self.draw()
        self.timer=threading.Timer(5, self.endturn)
        self.timer.start()
        
    def endturn(self):
        self.movedonkey()
        self.timer=threading.Timer(5, self.begin)
        self.timer.start()
        self.turn+=1
        
        
    def draw(self):
        self.gamekb=None
        self.gamekb=types.InlineKeyboardMarkup(self.size[1])
        g=1
        d=self.dplace
        while g<=self.size[0]:
            print('g='+str(g))
            buttons=[]
            v=1
            while v<=self.size[1]:
                print('v='+str(v))
                if str(g)+str(v)!=d:
                    txt=self.button
                else:
                    txt=self.donkey
                buttons.append(types.InlineKeyboardButton(text=txt, callback_data=self.code+' '+str(g)+str(v)))
                v+=1
            self.gamekb.add(*buttons)
            g+=1
        if self.message!=None:
            medit('Угадайте, куда пойдёт осёл:\n\nТекущий ход: '+str(self.turn), self.message.chat.id, self.message.message_id, reply_markup=self.gamekb)
        else:
            self.message=bot.send_message(self.id, 'Угадайте, куда пойдёт осёл.\n\nТекущий ход: '+str(self.turn), reply_markup=self.gamekb)
        
        
    def movedonkey(self):
        i=0
        while i<self.dspeed:
            x=[-1, 1]
            x=random.choice(x)
            dg=int(self.dplace[0])
            dv=int(self.dplace[1])
            site=random.choice(['g', 'v'])
            if site=='g':
                dg+=x
                if dg>self.size[0]:
                    dg-=2
                if dg<1:
                    dg+=2
            elif site=='v':
                dv+=x
                if dv>self.size[1]:
                    dv-=2
                if dv<1:
                    dv+=2
            self.dplace=str(dg)+str(dv)
            print('self.dplace= '+self.dplace)
            i+=1
            self.draw()
            time.sleep(1)
        
        
        
        
        
        
     
class Player:
    
    def __init__(self, user):
        self.id=user.id
        self.name=user.first_name
        self.username=user.username
        self.score=0
        self.choice=None
        
        
    
@bot.message_handler(commands=['test'])
def test(m):
    if m.chat.id!=m.from_user.id:
        Donkey(m.chat.id)
    
    
    
   
@bot.callback_query_handler(func=lambda call:True)
def inline(call): 
    try:
        user=call.from_user
        if call.data=='join':
            game=currentgame[0]
            if game.started==False and len(game.players)<game.playernumber:
                if user.id not in game.players:
                    game.players.update({user.id:Player(user)})
                    bot.send_message(call.message.chat.id, user.first_name+' присоединился!')
                    if len(game.players)==game.playernumber:
                        game.begin()
    except Exception as e:
          print('Ошибка:\n', traceback.format_exc())
          bot.send_message(441399484, traceback.format_exc())
        

print('7777')
bot.polling(none_stop=True,timeout=600)


