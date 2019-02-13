import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


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
        self.gamekb=types.InlineKeyboardMarkup()
        self.message=None
        

class Donkey(Minigame):
    
    def __init__(self, id=-1001058783080):
        global currentgame
        super().__init__(id)
        self.name='Поймай осла'
        self.code='donkey'
        self.playernumber=3
        self.winscore=2
        self.size=[5, 5]
        self.button='⬛️'
        self.data='null'
        self.donkey='🐴'
        self.dplace=[]
        self.dspeed=2
        self.text='Идёт набор в игру! Требуется игроков: '+str(self.playernumber)
        if currentgame==[]:
            bot.send_message(self.id, text, reply_markup=self.kb)
            currentgame.append(self)
        else:
            currentgame[0].timer.cancel()
            currentgame=[]
            bot.send_message(self.id, 'Предыдущая игра была удалена!')
            currentgame.append(self)
        
    def begin(self):
        if self.dplace==[]:
            g=1    # Горизонталь
            v=1    # Вертикаль
            dv=random.randint(1,self.size[1])  # v осла
            dg=random.randint(1,self.size[0])  # g осла
            d=str(dg)+str(dv)
            self.dplace=d
        else:
            d=self.dplace
        self.draw()
        self.timer=threading.Timer(8, self.endturn)
        self.timer.start()
        
    def endturn(self):
        self.movedonkey()
        self.timer=threading.Timer(8, self.begin)
        self.timer.start()
        
        
    def draw(self):
        g=1
        v=1
        while g<=self.size[0]:
            buttons=[]
            while v<=self.size[1]:
                if str(g)+str(v)!=d:
                    txt=self.button
                else:
                    txt=self.donkey
                buttons.append(types.InlineKeyboardButton(text=txt, callback_data=self.code+' '+str(g)+str(v)))
                v+=1
            self.gamekb.add(buttons)
            g+=1
        if self.message!=None:
            medit('Угадайте, куда пойдёт осёл:', self.message.chat.id, self.message.message_id, reply_markup=self.gamekb)
        else:
            self.message=bot.send_message(self.id, 'Угадайте, куда пойдёт осёл:', reply_markup=self.gamekb)
        
    def movedonkey(self):
        i=0
        while i<self.dspeed:
            x=[-1, 1]
            x=random.choice(x)
            dg=self.dplace[0]
            dv=self.dplace[1]
            site=random.choice('g', 'v')
            if site=='g':
                dg+=x
                if dg>self.size[0]:
                    dg=1
                if dg<1:
                    dg=self.size[0]
            elif site=='v':
                dv+=x
                if dv>self.size[1]:
                    dv=1
                if dv<1:
                    dv=self.size[1]
            
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
    user=call.from_user
    if call.data=='join':
        game=currentgame[0]
        if game.started==False and len(game.players)<game.playernumber:
            if user.id not in game.players:
                game.players.update({user.id:Player(user)})
                bot.send_message(self.id, user.first_name+' присоединился!')
                if len(game.players)==game.playernumber:
                    game.begin()
            
        

print('7777')
bot.polling(none_stop=True,timeout=600)


