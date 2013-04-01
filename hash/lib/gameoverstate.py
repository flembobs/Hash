##############################################################################
# gameoverstate.py
##############################################################################
# This state is used to display the score achieved with the old high score
# and allow the user to start a new game.
##############################################################################
# 03/13 Flembobs
##############################################################################

import pygame

from engine.model import State
from engine.systemevents import *

from gui import Text

##############################################################################
# CONSTANTS
##############################################################################

GAME_OVER_Y = 30
YOUR_SCORE_Y = 150
HIGH_SCORE_Y = 300
PRESS_ANY_Y = 420

##############################################################################
# GAME OVER STATE
##############################################################################

class GameOverState(State,SystemEventListener):
   
   def __init__(self,model,new_score,old_high_score):
   
      State.__init__(self,model)
      SystemEventListener.__init__(self)
      
      self.text_objects = []
      
      game_over = Text((0,0),"GAME OVER",(255,0,0),50)
      game_over.rect.center = (320,GAME_OVER_Y)
      self.text_objects.append(game_over)
      
      your_score = Text((0,0),"You scored: "+str(new_score[1]),
                        (255,255,255),30)
      your_score.rect.center = (320,YOUR_SCORE_Y)
      self.text_objects.append(your_score)
      
      high_score_str = ""
      
      if int(new_score[1]) > int(old_high_score[1]):
         high_score_str = "Old High Score: "+str(old_high_score[1])+" ("+ \
                          old_high_score[0]+")"
      else:
         high_score_str = "High Score: "+str(old_high_score[1])+" ("+ \
                          old_high_score[0]+")"
                          
      high_score = Text((0,0),high_score_str,(255,255,0),30)
      high_score.rect.center = (320,HIGH_SCORE_Y)
      self.text_objects.append(high_score)
      
      press_any = Text((0,0),"Press any key to play again",(0,255,0),20)
      press_any.rect.center = (320,PRESS_ANY_Y)
      self.text_objects.append(press_any)
      
   #--------------------------------------------------------------------------   
      
   def notify(self,event):
      
      if isinstance(event,TickEvent):         
         SystemEventManager.post(ModelUpdatedEvent(self.text_objects,[]))
         
      if isinstance(event,KeyboardEvent):
         from gamestate import GameState
         self.model.change_state(GameState(self.model))
      
      