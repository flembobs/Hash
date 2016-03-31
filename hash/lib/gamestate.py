##############################################################################
# gamestate.py
##############################################################################
# Classes related to the game play state.
##############################################################################
# 03/13 GoshDarnGames
##############################################################################

import pygame
import random
from weakref import WeakKeyDictionary       
       
from engine.model import *
from engine.events import *
from engine.systemevents import *

from gui import *
from highscorestate import HighScoreState

##############################################################################
# CONSTANTS
##############################################################################

BG_COLOR = (0,0,0)

#BOX CONSTANTS
BOX_NORMAL_COLOR = (0,255,0)
BOX_MO_COLOR = (255,0,255)
BOX_FONT_COLOR = (255,255,255)
BOX_BORDER_SIZE = 6
NUM_FONTSIZE = 78

#PROGRESS BAR CONSTANTS
PROGRESS_RECT = pygame.Rect((30,90),(580,300))
PROGRESS_BG_COLOR = (100,100,100)
PROGRESS_BAR_COLOR = (100,255,100)
PROGRESS_BAR_TL = (60,200)
PROGRESS_TEXT_Y = 120
PROGRESS_FONT_SIZE = 60

#OP-CODES
INSERT = 1
REMOVE = 2

#number of frames for an operation (i.e. frames = num_data * operation_time)
OPERATION_TIME = 30

#INSTRUCTION QUEUE CONSTANTS
MAX_INSTRUCTIONS = 7
INITIAL_DELAY = 900
DELAY_DECAY = 10
MIN_DELAY = 180

#DATA CONSTANTS
DATA_COLORS = ((255,0,0),(255,0,255),(255,255,0),
               (0,255,255),(0,0,255),(0,255,0))               
INITIAL_MIN_DATA_IN_BOXES = 8

#ERROR MSG CONSTANTS
ERROR_RECT = pygame.Rect((30,90),(580,300))
ERROR_TITLE_Y = 120
ERROR_TEXT_Y = 240
ERROR_TITLE_FONTSIZE = 60
ERROR_TEXT_FONTSIZE = 30
ERROR_BG_COLOR = (255,0,0)
ERROR_TITLE = "ERROR"
ERROR_TEXT = "Data not found in this box."
ERROR_TIME = 120

##############################################################################
# GAME EVENTS
##############################################################################

class GameTick(Event):
   """
   Generated by the game state so that objects can process ticks before the
   ModelUpdated event is posted.
   """
   pass
   
class ProgressComplete(Event):
   """
   Posted by the progress bar when its action is complete.  Contains the
   reference number of the box that was being processed.
   """
   
   def __init__(self,box_num):
      """
      box_num - the box that the operation pending was in relation to.
      """
      self.box_num = box_num
   
class InstructionAdded(Event):
   """
   Posted by the game state when a new instruction is added to the queue.
   """
   
   def __init__(self,instruction):
      self.instruction = instruction
      
class InstructionSuccessful(Event):
   """
   Posted by the game state class when the player successfully completes the
   first instruction on the queue
   """
   pass
   
class ErrorComplete(Event):
   """
   Posted by the error message class when its time has elapsed, allowing the
   game state to remove the dialogue
   """
   pass
      
##############################################################################
# GAME EVENTS - MANAGER AND LISTENER CLASSES
##############################################################################

class GameEventManager(EventManager):
   listeners = WeakKeyDictionary()

class GameEventListener(Listener):
   
   def __init__(self):
      Listener.__init__(self,GameEventManager)

##############################################################################
# GAME OBJECTS - BOX
##############################################################################     

class Box(Button):
   
   def __init__(self,num,rect):
   
      self.num = num
   
      normal_surf = self._draw_box(BOX_NORMAL_COLOR,rect)
      mo_surf = self._draw_box(BOX_MO_COLOR,rect)
      
      Button.__init__(self,rect,normal_surf,mo_surf)
   
   def _draw_box(self,color,rect):
      
      #fill in fg color
      box_surf = pygame.Surface((rect.width,rect.height))
      
      #rect relative to the box surf
      box_rect = pygame.Rect(0,0,rect.width,rect.height)
      
      box_surf.fill(color)
      
      #paint background over center to make box hollow
      bg_rect = box_rect.inflate(-1*BOX_BORDER_SIZE,-1*BOX_BORDER_SIZE)
      box_surf.fill(BG_COLOR,bg_rect)
      
      #add the number to the center
      num_surf = pygame.font.SysFont("courier",NUM_FONTSIZE,True).\
                                             render(str(self.num),True,color)
      num_rect = pygame.Rect(0,0,num_surf.get_width(),num_surf.get_height())
      num_rect.center = box_rect.center
      
      box_surf.blit(num_surf,num_rect)
      
      return box_surf
      
##############################################################################
# GAME OBJECTS - PROGRESS BAR
##############################################################################

class ProgressBar(GameObject,GameEventListener,GUIEventListener):

   def __init__(self,frames,box_num):
   
      GameEventListener.__init__(self)
      GUIEventListener.__init__(self)
   
      self.frames = frames
      self.initial_frames = frames
      self.box_num = box_num
      
   #--------------------------------------------------------------------------
      
   def notify(self,event):
   
      if isinstance(event,GameTick):
         self.frames -= 1
         
         if self.frames <= 0:
            GameEventManager.post(ProgressComplete(self.box_num))
            
   #--------------------------------------------------------------------------
            
   def render(self,screen):
   
      #draw background
      screen.fill(PROGRESS_BG_COLOR,PROGRESS_RECT)
      
      #draw progress bar
      max_width = 640 - PROGRESS_BAR_TL[0]*2
      width = (float(max_width) / self.initial_frames)*  \
              (self.initial_frames-self.frames)
      
      height = (240 - PROGRESS_BAR_TL[1])*2
      
      progress_bar_rect = pygame.Rect(PROGRESS_BAR_TL,(width,height))
      
      screen.fill(PROGRESS_BAR_COLOR,progress_bar_rect)
      
      #draw text
      text_surf = pygame.font.SysFont("courier",PROGRESS_FONT_SIZE,True).\
                                      render("PROGRESS:",True,(0,0,0))
                                      
      text_rect = text_surf.get_rect()
      text_rect.center = PROGRESS_RECT.center
      text_rect.top = PROGRESS_TEXT_Y
      
      screen.blit(text_surf,text_rect)
      
##############################################################################
# GAME OBJECTS -  ERROR MESSAGE
##############################################################################

class ErrorMessage(GameObject, GameEventListener):
   
   def __init__(self):
   
      GameEventListener.__init__(self)
      
      self.frames_left = ERROR_TIME
      
   def notify(self,event):
   
      if isinstance(event,GameTick):
         self.frames_left -= 1
         
         if self.frames_left <= 0:
            GameEventManager.post(ErrorComplete())
            
   def render(self,screen):
   
      #draw background
      screen.fill(ERROR_BG_COLOR,ERROR_RECT)
      
      #draw title
      title_surf = pygame.font.SysFont("courier",ERROR_TITLE_FONTSIZE,True).\
                                 render(ERROR_TITLE,True,(0,0,0))
      title_rect = title_surf.get_rect()
      title_rect.center = ERROR_RECT.center
      title_rect.top = ERROR_TITLE_Y
      
      screen.blit(title_surf,title_rect)
      
      #draw message
      text_surf = pygame.font.SysFont("courier",ERROR_TEXT_FONTSIZE,True).\
                                     render(ERROR_TEXT,True,(0,0,0))
      text_rect = text_surf.get_rect()
      text_rect.center = ERROR_RECT.center
      text_rect.top = ERROR_TEXT_Y
      
      screen.blit(text_surf,text_rect)
                                       
##############################################################################
# GAME OBJECTS - INSTRUCTION QUEUE
##############################################################################
      
class InstructionQueue(GameObject,GameEventListener):

   def __init__(self):
      
      GameEventListener.__init__(self)
      
      self.queue = []
      
   #--------------------------------------------------------------------------
      
   def notify(self,event):
      
      if isinstance(event,InstructionAdded):
         self.queue.append(event.instruction)
         
      if isinstance(event,InstructionSuccessful):
         del self.queue[0]
         
   #--------------------------------------------------------------------------      
         
   def render(self,screen):
      
      for idx,instruction in enumerate(self.queue):
         self._draw_instruction(400-idx*80,instruction,screen)
         
   #--------------------------------------------------------------------------
   
   def get_next_instruction(self):
      """
      Returns the instruction at the bottom of the queue.
      """
      
      if len(self.queue) is 0:
         return None
         
      return self.queue[0]
         
   #--------------------------------------------------------------------------
         
   def _draw_instruction(self,y,instruction,screen):
      
      #draw data
      data_surf = self._create_data_surf(instruction.data)
      data_rect = pygame.Rect((580,y+15),(50,50))
      screen.blit(data_surf,data_rect)
      
      #draw arrow
      
      #actual position on screen to draw
      pointlist = []
      
      #relative points of the arrow
      rel_pointlist = []
      
      arrow_color = None
      
      #set the relative points for an insert arrow
      if instruction.opcode is INSERT:

         arrow_color = (0,0,255)
         
         rel_pointlist = [(0,0), (20,20),(20,10),(60,10),
                          (60,-10),(20,-10),(20,-20),(0,0)]
                             
      #set the relative points for a remove arrow
      if instruction.opcode == REMOVE:
         arrow_color = (255,0,0)
         
         rel_pointlist = [(0,0),(0,10),(40,10),(40,20),(60,0),
                          (40,-20),(40,-10),(0,-10),(0,0)]
                             
      #convert the relative points into screen coordinates                    
      arrow_x = 500
      arrow_y = y+40
      for point in rel_pointlist:
         pointlist.append((point[0]+arrow_x,point[1]+arrow_y))
         
      pygame.draw.polygon(screen,arrow_color,pointlist)
      
   #--------------------------------------------------------------------------
      
   def _create_data_surf(self,data):
   
      data_surf = pygame.Surface((50,50))
      
      for i in range(len(data)):
         
         #create local rect for data element
         rect = pygame.Rect(((i%2)*25,(i/2)*25),(25,25))
         
         #blit colour onto surf
         data_surf.fill(data[i],rect)
         
      return data_surf
                 
         
class Instruction:
   
   def __init__(self,opcode,data):
      self.opcode = opcode
      self.data = data     
   

##############################################################################
# GAME STATE CLASS
##############################################################################

class GameState(State,SystemEventListener,GUIEventListener,GameEventListener):

   def __init__(self, model):
   
      SystemEventListener.__init__(self)
      GUIEventListener.__init__(self)
      GameEventListener.__init__(self)
      State.__init__(self,model)
      
      self.boxes = []
      self.dialogue = None
      self.score = 0
      self.min_data_in_boxes = INITIAL_MIN_DATA_IN_BOXES
      
      #data held in boxes { box_num : [data] }
      self.box_data = dict()
      
      #create the boxes
      for i in range(9):
         
         #NB - doesn't support multiple resolutions
         box_topleft = (i%3)*(480/3)
         box_topright = (i/3)*(480/3)
         box_size = 480/3
         
         box_rect = pygame.Rect(box_topleft,box_topright,box_size,box_size)
         
         self.boxes.append(Box(i+1,box_rect))
         self.box_data[i+1] = []
         
      self.instruction_queue = InstructionQueue()
         
      #delay until next instruction
      self.delay = INITIAL_DELAY
      
      #last delay (used to calculate next delay)
      self.last_delay = INITIAL_DELAY
      
      #add the first instruction
      self._add_new_instruction()
      
         
      
      
   #--------------------------------------------------------------------------
   
   def notify(self,event):
   
      if isinstance(event,TickEvent):
      
         #post game tick
         GameEventManager.post(GameTick())
         
         #check if new instruction needs to be added
         self.delay -= 1
         
         #check if instruction queue is empty
         if len(self.instruction_queue.queue) is 0:
            self.delay = 0
         
         if self.delay <= 0:
            self._add_new_instruction()
            self.delay = self.last_delay - DELAY_DECAY
            self.last_delay = self.delay
            
            if self.delay < MIN_DELAY:
               self.delay = MIN_DELAY
               
         if len(self.instruction_queue.queue) >= MAX_INSTRUCTIONS:
            self.model.change_state(HighScoreState(self.model,self.score))
            return       
         
         #create visible objects list         
         visible_objects = []
         
         visible_objects += self.boxes
         
         visible_objects.append(self.instruction_queue)
         
         if self.dialogue is not None:
            visible_objects.append(self.dialogue)
      
         SystemEventManager.post(ModelUpdatedEvent(visible_objects,
                                                   self.game_objects))
                               
                                              
      if isinstance(event,ButtonClickedEvent):
      
         #box click
         if isinstance(event.button, Box):
            
            #start the operation
            if self.dialogue is None:
               box_num = event.button.num
               operation_time = OPERATION_TIME * len(self.box_data[box_num])
               self.dialogue = ProgressBar(operation_time,box_num)
      
      #after progress complete, check if operation was successful
      if isinstance(event,ProgressComplete):
         self.dialogue = None
         
         box_num = event.box_num
         instruction = self.instruction_queue.get_next_instruction()
         
         if instruction is None:
            return
            
         if instruction.opcode is INSERT:
            
            self.box_data[box_num].append(instruction.data)
            
         if instruction.opcode is REMOVE:
         
            #check data is in box and remove if so
            if instruction.data in self.box_data[box_num]:
               self.box_data[box_num].remove(instruction.data)
               
            else:
               self.dialogue = ErrorMessage()
               return                
         
         self.score += 1   
         GameEventManager.post(InstructionSuccessful())
         
      #clear the dialogue on error complete
      if isinstance(event,ErrorComplete):
         self.dialogue = None
         
   #--------------------------------------------------------------------------
   
   def _data_exists(self, data):
      """
      Returns True if the data exists in one of the boxes or the instruction
      queue.
      """
      
      #check if data is in box data      
      for box_num in self.box_data.keys():
         if data in self.box_data[box_num]:
            return True
            
      #check if data is in instruction queue data
      for instruction in self.instruction_queue.queue:
         if data == instruction.data:
            return True
            
      return False
      
   #--------------------------------------------------------------------------
   
   def _new_data(self):
      """
      Creates a data item that does not already exist in the instuction
      queue or boxes.
      """
   
      data = None
       
      while True:
         
         data = (random.choice(DATA_COLORS),random.choice(DATA_COLORS),
                random.choice(DATA_COLORS),random.choice(DATA_COLORS))
                
         if not self._data_exists(data):
            break
            
      return data
      
   #--------------------------------------------------------------------------
   
   def _all_box_data(self):
      """
      Returns a list holding all data items held in the boxes.
      """
      
      all_data = []
      
      for box_num in self.box_data.keys():
         all_data += self.box_data[box_num]
         
      return all_data
      
   #--------------------------------------------------------------------------
   
   def _add_new_instruction(self):
      """
      Adds a new instruction to the instruction queue.
      """ 
      
      all_data = self._all_box_data()
      
      opcode = None
      
      #decide if we want an insert or remove instruction      
      if len(all_data) < self.min_data_in_boxes:
         opcode = INSERT
      else:
         opcode = random.choice((INSERT,REMOVE))     
      
            
      data = None
      
      #if insert op - create new data
      if opcode is INSERT:
         data = self._new_data()
      
      #if remove op - select existing data
      if opcode is REMOVE:
      
         while True:
         
            data = random.choice(all_data)
            
            #check that data is not already in instruction queue
            for instruction in self.instruction_queue.queue:
               if data == instruction.data:
                  continue
            break
            
       
      instruction = Instruction(opcode,data)  
      GameEventManager.post(InstructionAdded(instruction))
         
               
   