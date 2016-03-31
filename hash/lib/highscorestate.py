##############################################################################
# highscorestate.py
##############################################################################
# This state is used to check if the score achieved is a new high score and
# prompt the user for their name if so.
##############################################################################
# 03/13 - GoshDarnGames
##############################################################################

import os
import pygame

from gui import *

from engine.model import State
from engine.systemevents import *

from gameoverstate import GameOverState
from gui import *

##############################################################################
# CONSTANTS
##############################################################################

HIGH_SCORE_FILE = os.path.join("data","high_score.txt")
SCORE_DELIMITER = "|"
BLANK_SCORE = ("nobody",0)

TITLE_Y = 50
PROMPT_Y = 200
TB_INITIAL_TEXT = "Type your name here"
TEXT_BOX_Y = 250
ACCEPT_BUTTON_SIZE = (150,60)
ACCEPT_FONT_SIZE = 20
ACCEPT_BUTTON_Y = 330

##############################################################################
# HIGH SCORE STATE
##############################################################################

class HighScoreState(State,GUIEventListener,SystemEventListener):

   def __init__(self,model,score):
      """
      model - reference to the model
      score - the score that was achieved
      """
      
      State.__init__(self,model)
      
      self.new_score = score
      self.old_high_score = self._read_high_score()
         
      GUIEventListener.__init__(self)
      SystemEventListener.__init__(self)
         
      self.title = Text((0,0),"!!!NEW HIGH SCORE!!!",(255,0,0),50)
      self.title.rect.center = (320,TITLE_Y)
         
         
      self.prompt = Text((0,0),"Enter your name:",(255,255,255),25)
      self.prompt.rect.center = (320,PROMPT_Y)
      
      self.text_box = TextInputBox((0,0),400,TB_INITIAL_TEXT,
                                   (255,255,255),(0,0,0),20)
      self.text_box.rect.center = (320,TEXT_BOX_Y)
      
      self.accept_button = self._create_accept_button()
      self.accept_button.rect.center = (320,ACCEPT_BUTTON_Y)  
                                 
                                   
      
   #--------------------------------------------------------------------------
   
   def notify(self,event):
      
      if isinstance(event,TickEvent):
      
         #HACK ALERT - This functionality used to be in the __init__ method
         #             but python didn't like me breaking from the init
         #             when there wasn't a new high score
         if self.new_score <= int(self.old_high_score[1]):
            self.model.change_state(
                  GameOverState(self.model,("",self.new_score),
                                self.old_high_score))
            return
      
         visible_objects = []
         visible_objects.append(self.title)
         visible_objects.append(self.prompt)
         visible_objects.append(self.text_box)
         visible_objects.append(self.accept_button)
         
         SystemEventManager.post(ModelUpdatedEvent(visible_objects,[]))
         
      if isinstance(event,ButtonClickedEvent) and \
         event.button is self.accept_button:
         
         if self.text_box.text is TB_INITIAL_TEXT or \
            len(self.text_box.text) is 0:
            return
            
         else:
            new_high_score = (self.text_box.text,self.new_score)
            self._save_high_score(new_high_score)
            self.model.change_state(GameOverState(self.model,new_high_score,
                                                  self.old_high_score))
         
      
   #--------------------------------------------------------------------------     
      
   def _read_high_score(self):
      """
      Reads the high score file, returning a tuple ("name",score)
      """
      
      high_score = None
      high_score_file = None
      
      try: 
         high_score_file = open(HIGH_SCORE_FILE,'r')
      except IOError:
         return BLANK_SCORE
         
      try:
         for line in high_score_file:
            high_score = tuple(line.split(SCORE_DELIMITER))
      except ValueError:
         pass
         
      return high_score
      
   #--------------------------------------------------------------------------
   
   def _save_high_score(self,new_high_score):
      
      high_score_text = new_high_score[0]+"|"+str(new_high_score[1])
      high_score_file = None
      
      try:
         high_score_file = open(HIGH_SCORE_FILE,'w')
         high_score_file.write(high_score_text)
         high_score_file.close()
      except IOError:
         print "COULDN'T WRITE HIGH SCORE FILE!!!"
         
   
   #--------------------------------------------------------------------------
   
   def _create_accept_button(self):
   
      text = Text((0,0),"Accept",(0,0,0),ACCEPT_FONT_SIZE)
   
      normal_surf = pygame.Surface(ACCEPT_BUTTON_SIZE)
      normal_surf.fill((0,255,0))
      text.rect.center = normal_surf.get_rect().center
      normal_surf.blit(text.surf,text.rect)
      
      mo_surf = pygame.Surface(ACCEPT_BUTTON_SIZE)
      mo_surf.fill((0,255,255))
      mo_surf.blit(text.surf,text.rect)
      
      return Button(normal_surf.get_rect(),normal_surf,mo_surf)
      