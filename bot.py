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


client3=MongoClient(os.environ['database2'])
db2=client3.trug
trugusers=db2.users

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
        self.message=None
        

class Donkey(Minigame):
    
    def __init__(self, id=-1001058783080):
        global currentgame
        super().__init__(id)
        self.name='Поймай осла'
        self.code='donkey'
        self.playernumber=300
        self.winscore=2
        self.emojis=['⚫️','🔴','🔵','❤️','🧡','💛','💚','💙','💜','🖤','🐶','🐱','🐭','🐯','🐺','🐝','🐗','🐴','🐳','🦃','👻','🐧']
        self.size=[5, 5]    # Горизонталь; вертикаль
        self.gamekb=types.InlineKeyboardMarkup(self.size[1])
        self.button='⬜️'
        self.data='null'
        self.donkey='🐴'
        self.dplace=None
        self.dspeed=2
        self.allscore=0
        self.turn=1
        self.fond=0
        s=threading.Timer(180, self.begin)
        s.start()
        self.starttimer=s
        self.stage=None
        self.timer=None
        self.text='Идёт набор в игру! Старт через 3 минуты.'
        if currentgame==[]:
            bot.send_message(self.id, self.text, reply_markup=self.kb)
            currentgame.append(self)
        else:
            if currentgame[0].timer!=None:
                currentgame[0].timer.cancel()
            currentgame=[]
            bot.send_message(self.id, 'Предыдущая игра была удалена!')
            bot.send_message(self.id, self.text, reply_markup=self.kb)
            currentgame.append(self)
        
    def begin(self):
        global currentgame
        if self.dplace==None:
            g=1    # Горизонталь
            v=1    # Вертикаль
            dv=random.randint(1,self.size[1])  # v осла
            dg=random.randint(1,self.size[0])  # g осла
            d=str(dg)+str(dv)
            self.dplace=d
        else:
            d=self.dplace
        self.stage=1
        self.draw()
        self.timer=threading.Timer(5, self.endturn)
        self.timer.start()
        
    def endturn(self):
        global currentgame
        self.stage=2
        self.movedonkey()
        for ids in self.players:
            if self.players[ids].choice==self.dplace:
                self.fond+=1
                self.players[ids].points+=1
            self.players[ids].choice=None
        if self.turn<10:
            self.timer=threading.Timer(5, self.begin)
            self.timer.start()
            self.turn+=1
        else:
            self.allscore=self.fond
            plist=''
            for ids in self.players:
                player=self.players[ids]
                player.percent=(player.points/self.fond)
            for ids in self.players:
                player=self.players[ids]
                player.score=int(player.percent*self.fond)
                self.allscore-=player.score
                if self.allscore<0:
                    while self.allscore<0:
                        player.score-=1
                        self.allscore+=1
            for ids in self.players:
                player=self.players[ids]
                plist+=player.name+': '+str(player.score)+'🍪\n'
                trugusers.update_one({'id':player.id},{'$inc':{'cookies':player.score, 'totalcookies.minigames':player.score}})
            medit('Игра завершена! Полученные куки:\n\n'+plist, self.message.chat.id, self.message.message_id)
            currentgame=[]
            randomgame()
        
        
    def draw(self):
        global currentgame
        self.gamekb=None
        self.gamekb=types.InlineKeyboardMarkup(self.size[1])
        g=1
        d=self.dplace
        dots=[]
        for ids in self.players:
            if self.players[ids].choice!=None:
                dots.append([self.players[ids], self.players[ids].choice])
        while g<=self.size[0]:
            print('g='+str(g))
            buttons=[]
            v=1
            while v<=self.size[1]:
                t=0
                print('v='+str(v))
                for ids in dots:
                    if ids[1]==str(g)+str(v):
                        txt=ids[0].emoji
                        t=1
                if str(g)+str(v)==d:
                    txt=self.donkey
                    t=1
                if t==0:
                    txt=self.button
                buttons.append(types.InlineKeyboardButton(text=txt, callback_data=self.code+' '+str(g)+str(v)))
                v+=1
            self.gamekb.add(*buttons)
            g+=1
        scores=''
        for ids in self.players:
            scores+='['+self.players[ids].emoji+']'+self.players[ids].name+': '+str(self.players[ids].score)+'\n'
        if self.message!=None:
            medit('Угадайте, куда пойдёт осёл.\n\nТекущий ход: '+str(self.turn)+'\nСтадия: '+str(self.stage)+'\nОчки игроков:\n\n'+scores, self.message.chat.id, self.message.message_id, reply_markup=self.gamekb)
        else:
            self.message=bot.send_message(self.id, 'Угадайте, куда пойдёт осёл.\n\nТекущий ход: '+str(self.turn)+'\nСтадия: '+str(self.stage)+'\nОчки игроков:\n\n'+scores, reply_markup=self.gamekb)
        
        
    def movedonkey(self):
        global currentgame
        i=0
        lastpos=self.dplace
        while i<self.dspeed:
            x=[-1, 1]
            x=random.choice(x)
            dg=int(self.dplace[0])
            dv=int(self.dplace[1])
            site=random.choice(['g', 'v'])
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
            dplace=str(dg)+str(dv)
            if dplace!=lastpos:
                i+=1
                self.dplace=dplace
                self.draw()
                time.sleep(1)
            
                
        
        
        
        
        
        
     
class Player:
    
    def __init__(self, user):
        self.id=user.id
        self.name=user.first_name
        self.username=user.username
        self.score=0
        self.choice=None
        self.points=0
        self.percent=0
       
    
    
    
   
@bot.callback_query_handler(func=lambda call:True)
def inline(call): 
    try:
        game=currentgame[0]
        user=call.from_user
        if call.data=='join':
            if game.started==False and len(game.players)<len(game.emojis):
                if user.id not in game.players:
                    game.players.update({user.id:Player(user)})
                    x=random.choice(game.emojis)
                    game.players[user.id].emoji=x
                    game.emojis.remove(x)
                    bot.send_message(call.message.chat.id, user.first_name+' присоединился!')
        elif 'donkey' in call.data:
            if game.stage==1:
                game.players[user.id].choice=call.data.split(' ')[1]
                bot.answer_callback_query(call.id, '✅Точка выбрана!')
            else:
                bot.answer_callback_query(call.id, '❌Ждите стадии 1!')
    except Exception as e:
          print('Ошибка:\n', traceback.format_exc())
          bot.send_message(441399484, traceback.format_exc())
        
def randomgame():
    x=random.randint(60, 3600)
    t=threading.Timer(x, startgame)
    t.start()
    
    
def startgame():
    Donkey()
    
    
startgame()


print('7777')
bot.polling(none_stop=True,timeout=600)


