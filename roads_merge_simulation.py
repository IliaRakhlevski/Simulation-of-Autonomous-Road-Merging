
# =================== Import librariests =============================

import pygame
import math
import random 


# =================== Global constants =============================

# colors
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
TEXTCOLOR = (255, 255, 255)

# window size (in pixels)
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Frames per second
FPS = 40

# car size (in pixels)
CAR_WIDTH = 47
CAR_HEIGHT = 23

# main road
Y_START_MAIN_ROAD = 200
WIDTH_MAIN_ROAD = 100

# secondary road
X_WIDTH_SEC_ROAD = 80
X_START_SEC_ROAD = 0
X_END_SEC_ROAD = 500

# roads merging point
X_MERG = X_END_SEC_ROAD + X_WIDTH_SEC_ROAD // 2
Y_MERG = Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD

# traffic cars
TRAFFIC_CAR_MIN_SPEED = 3       # minimal traffic car speed 
TRAFFIC_CAR_MAX_SPEED = 6       # maximal traffic car speed
ADD_NEW_TRAFFIC_CAR_RATE = 40   # rate (in frames) of new traffic car adding

# player's car
PLAYER_CAR_REGULAR_SPEED = 10       # regular speed of the player car
PLAYER_CAR_TURN_SPEED = 3           # speed of the player car during of the turning
PLAYER_CAR_CHECKPOINT_BEFORE_MERGE = 10 # point in which player car must make decision
                                        # if it waits or makes turning
PLAYER_CAR_SLOWDOWN_ACCEL = -1          # slowdown acceleration
PLAYER_CAR_START_UP_ACCEL = 1           # starting up acceleration
PLAYER_CAR_TURN_STEER = -1              # steering angle for the turning


DIST_TO_NEXT_CAR_TO_SLOWDOWN = 100  # min. distance to next car to slowdown

SEC_AREA_UPDATE_VAL = 5             # security area update value

# game states
STATE_START_SEC_ROAD = 0
STATE_SLOWDOWN = 1
STATE_WAIT = 2
STATE_TURN = 3
STATE_SPEED_UP = 4
STATE_REG_SPEED = 5


# =================== Global functions =============================

# angle between vector (x,y) and the x-axis
def get_angle(x, y):
  #  return 10
   return math.degrees(math.atan2(y, x))


# =================== Classes =============================
   
# Class describes the player car
class PlayerCar:
    
    def __init__(self, Env):
        self.player_car_speed = PLAYER_CAR_REGULAR_SPEED    # speed of the player car (pixels per frame)
        self.player_car_angle = 0           # angle of the player car moving, 0 - x-axis
        self.player_car_crash = False       # indicates if a crash process occurs
        self.player_car_crash_counter = 0   # time (in frames) that the crash process lasts
        self.player_car_accel = 0;          # car acceleration
        self.player_car_steer = 0;          # steering angle
        self.dist_till_merge = 0;           # distance till the roads merge - NOT IN USE!
       
        # loading the player car image
        self.playerImage = pygame.image.load('image/car1.png')
        self.playerImage = pygame.transform.scale(self.playerImage, (CAR_WIDTH, CAR_HEIGHT))
        self.playerRect = self.playerImage.get_rect()
        
        # move to start of the secondary road
        self.playerRect.move_ip(X_START_SEC_ROAD + 15 - self.playerRect.left, WINDOW_HEIGHT - CAR_HEIGHT - self.playerRect.top)
        
        # car angle is equal to secondary road angle
        self.player_car_angle = sec_road_angle
        
        # loading the collision image
        self.collision = pygame.image.load('image/collision.png')
        self.collisionRect = self.playerImage.get_rect()
        self.is_collision = False # indicates if a collision occurs
        
        self.env = Env      # environment object
        
        
    # initialize the player car
    def ResetPlayerCar(self):
 
        # move to start of the secondary road
        self.playerRect.move_ip(X_START_SEC_ROAD + 15 - self.playerRect.left, WINDOW_HEIGHT - CAR_HEIGHT - self.playerRect.top)
        # car angle is equal to secondary road angle
        self.player_car_angle = sec_road_angle
        # initialize player car speed by the default speed
        self.player_car_speed = PLAYER_CAR_REGULAR_SPEED
        
        # player car acceleration and steering angle
        self.player_car_accel = 0
        self.player_car_steer = 0
        
        self.env.ResetPlayerCar()
  
      
    # process the player car crash   
    def CrashProcess(self):
        
        # crash process   
        if self.player_car_crash:
            self.player_car_crash_counter -= 1                  # count the crash process
            if self.player_car_crash_counter == (FPS // 2):     # if the crash process passed half second
                                                              
                # return the player car to the start position in the secondary road
                self.ResetPlayerCar()
                self.player_car_speed = 0
                self.is_collision = False
            # end of the crash process
            if self.player_car_crash_counter == 0: 
                self.player_car_speed = PLAYER_CAR_REGULAR_SPEED
                self.player_car_crash = False
 
       
    # update player car position
    def Update(self):
      
        x = 0.0
        y = 0.0
        
        # update the speed according to the acceleration
        self.player_car_speed += self.player_car_accel
        
        # update the angle according to the steering angle
        self.player_car_angle += self.player_car_steer
    
        # calculate new coordinates of the car
        if self.player_car_angle != 0:
            x = round(self.player_car_speed * math.cos((math.pi / 180) * self.player_car_angle))
            y = round(self.player_car_speed * math.sin((math.pi / 180) * self.player_car_angle))
        else: # player_car_angle == 0
            x = self.player_car_speed
        self.playerRect.move_ip(int(x), int(-y))
        
         # if a player car exits the window
        if self.playerRect.left > WINDOW_WIDTH:
            self.ResetPlayerCar() # return it to the start position in the secondary road
         
        # rotate the car image 
        rotated_image = pygame.transform.rotate(self.playerImage, self.player_car_angle)
        
        windowSurface.blit(rotated_image, self.playerRect)
        
        # display the collision image
        if self.is_collision == True:
            windowSurface.blit(self.collision, self.collisionRect)
  

# Class describes the game environment
class Environment:

    def __init__(self):
       
       self.traffic_cars = []           # list of the traffic cars
       self.traffic_car = pygame.image.load('image/car2.png') # traffic car image
       self.trafficCarsAddCounter = 0       # counters of the frames till next adding of a new traffic car
       self.playerCar = PlayerCar(self)     # create the player car
       self.start_slowdown_point = self.get_start_slowdown_point()  # point of start of the slowdown on the secondary road
       self.current_player_car_state = STATE_START_SEC_ROAD         # player car episode state
       self.player_car_state_speed_after_turn = 0   # target speed of the player car after finishing the turn
       self.collided_car_rect = None                # rectangle of the collided car
       
       # borders of collision security area
       self.left_coll_shift = 0
       self.right_coll_shift = 0
       self.tc_speed_factor = 1
       self.top_coll_shift = WINDOW_HEIGHT

       self.num_episodes = 0                        # number of episodes
       self.num_episodes_since_last_crash = 0
       self.num_crashes = 0                         # number of crashes
       self.font = pygame.font.SysFont(None, 30)    # font for text drawing
       
             
    # draw the main and the secondary roads
    def DrawRoads(self):
        
        # main road
        pygame.draw.line(windowSurface, WHITE, [0, Y_START_MAIN_ROAD], [WINDOW_WIDTH, Y_START_MAIN_ROAD], 3)
        
        pygame.draw.line(windowSurface, WHITE, [0, Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD], 
                         [X_END_SEC_ROAD, Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD], 3)
        
        pygame.draw.line(windowSurface, WHITE, [X_END_SEC_ROAD + X_WIDTH_SEC_ROAD, Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD], 
                         [WINDOW_WIDTH, Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD], 3)
                
        # secondary road
        pygame.draw.line(windowSurface, WHITE, [X_START_SEC_ROAD, WINDOW_HEIGHT], 
                         [X_END_SEC_ROAD, Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD], 3)
        
        pygame.draw.line(windowSurface, WHITE, [X_START_SEC_ROAD + X_WIDTH_SEC_ROAD, WINDOW_HEIGHT], 
                         [X_END_SEC_ROAD + X_WIDTH_SEC_ROAD, Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD], 3)
        
     
    # check if player car hit one of the traffic cars
    def playerHasHitTrafficCar(self):
        
        for tc in self.traffic_cars:
            if self.playerCar.playerRect.colliderect(tc['rect']):
                self.collided_car_rect = tc['rect']
                return True
        self.collided_car_rect = None
        return False
    
    
    # if 'tc' car is behind the 'tc1' car
    def is_behind(self, tc, tc1):
        
        if tc.right < tc1.left:
                    
            if (tc.top >= tc1.top and tc.top <= tc1.bottom or
                tc.bottom <= tc1.bottom and tc.bottom >= tc1.top):
                    return True
                
        return False
        
    
    # update traffic cars speeds
    def UpdateTrafficCarsSpeed(self):
        
        # sort the traffic cars according to their right side of the rectangle
        self.traffic_cars.sort(key=lambda x: x['rect'].right, reverse=True)
     
        for tc in self.traffic_cars:            
            for tc1 in self.traffic_cars: 
                
                if tc == tc1 or tc['speed'] <= tc1['speed']:
                    continue
                
                # if there is some car before the checked one and its speed is smaller
                # then the checked car receives the speed of this car
                if (self.is_behind(tc['rect'], tc1['rect']) and tc['speed'] > tc1['speed'] and 
                    tc['rect'].right + DIST_TO_NEXT_CAR_TO_SLOWDOWN >  tc1['rect'].left):
                        tc['speed'] = tc1['speed']
                        
            # check the player car if it is found on the last state (afetr finishing the turn)         
            if self.current_player_car_state == STATE_REG_SPEED:
                
                if (self.is_behind(tc['rect'], self.playerCar.playerRect) and tc['speed'] > self.playerCar.player_car_speed and 
                    tc['rect'].right + DIST_TO_NEXT_CAR_TO_SLOWDOWN >  self.playerCar.playerRect.left):
                        tc['speed'] = self.playerCar.player_car_speed
       
        
    # draw text    
    def drawText(self, text, font, surface, x, y):
        
        textobj = font.render(text, 1, TEXTCOLOR)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)            


    # update the environment

    def Update(self):
         
        self.trafficCarsAddCounter += 1 
        
        # add new traffic car       
        if self.trafficCarsAddCounter == ADD_NEW_TRAFFIC_CAR_RATE:
            self.trafficCarsAddCounter = 0
            
            # define new traffic car parameters
            newTrafficCar = {'rect': pygame.Rect(0, random.randint(Y_START_MAIN_ROAD + 5, Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD - CAR_HEIGHT - 5), 
                                                 CAR_WIDTH, CAR_HEIGHT),
                            'speed': random.randint(TRAFFIC_CAR_MIN_SPEED, TRAFFIC_CAR_MAX_SPEED),
                            'surface': pygame.transform.scale(self.traffic_car, (CAR_WIDTH, CAR_HEIGHT)),
                            }
            self.traffic_cars.append(newTrafficCar) # add the new car into traffic cars list
 
    
        self.UpdateTrafficCarsSpeed()
          
        # update traffic cars   
        for tc in self.traffic_cars:
            tc['rect'].move_ip(tc['speed'], 0)      # update the traffic cars positions
            if tc['rect'].left > WINDOW_WIDTH:      # if a traffic car exits the window
                    self.traffic_cars.remove(tc)    # remove it from the traffic cars list
     
        
        windowSurface.fill(GRAY)    # draw background
        self.DrawRoads()            # draw roads
        
        # draw traffic cars
        for tc in self.traffic_cars:
            windowSurface.blit(tc['surface'], tc['rect'])
         
        # update the player car
        self.playerCar.Update()
        
        # Draw the score and top score.
        self.drawText('Number of episodes: %s' % (self.num_episodes), self.font, windowSurface, 10, 10)
        self.drawText('Number of crashes: %s' % (self.num_crashes), self.font, windowSurface, 10, 30)
        self.drawText('Number of successes: %s' % (self.num_episodes - self.num_crashes), self.font, windowSurface, 10, 50)
        
        self.drawText('Speed: %s' % (self.playerCar.player_car_speed), self.font, windowSurface, 400, 10)
        self.drawText('Acceleration: %s' % (self.playerCar.player_car_accel), self.font, windowSurface, 400, 30)
        self.drawText('Steering Angle: %s' % (self.playerCar.player_car_steer), self.font, windowSurface, 400, 50)

        self.drawText(f'Left Sec-Area : {self.left_coll_shift}' , self.font, windowSurface, 700, 10)
        self.drawText(f'Right Sec-Area : {self.right_coll_shift}' , self.font, windowSurface, 700, 30)
        self.drawText(f'Speed factor: {self.tc_speed_factor}' , self.font, windowSurface, 700, 50)

        # update the display
        pygame.display.update()
        
        
     # distance till the roads merge
    def get_dist_till_merge(self):

        x_dist = self.playerCar.playerRect.right - X_MERG
        y_dist = self.playerCar.playerRect.top - Y_MERG
        dist_till_merge = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if self.playerCar.playerRect.top < Y_MERG:
            dist_till_merge = -dist_till_merge
        return dist_till_merge


    # get the point where the player car start slowdown
    def get_start_slowdown_point(self):

       dist_before_turn_point = 0
      
       # calculate the distance till the merge point
       # where the player car starts slowdown
       sp = PLAYER_CAR_REGULAR_SPEED - 1
       while True:
          dist_before_turn_point += sp
          if sp == PLAYER_CAR_TURN_SPEED:
              break
          sp += PLAYER_CAR_SLOWDOWN_ACCEL
       return PLAYER_CAR_CHECKPOINT_BEFORE_MERGE + dist_before_turn_point


    # re-init the player car
    def ResetPlayerCar(self):
        self.num_episodes += 1 # update number of episodes since game start
        self.num_episodes_since_last_crash += 1 # update number of episodes since last crash

        if self.num_episodes_since_last_crash > 0 and self.num_episodes_since_last_crash % 10 == 0:
            self.tc_speed_factor *= 0.95 # in case of no collisions for a long period of time, decrease speed factor

        self.current_player_car_state = STATE_START_SEC_ROAD # set the initial state

        
    # player car speed after turning
    def get_player_car_speed_after_turn(self):
        
         cur_sel_speed = PLAYER_CAR_REGULAR_SPEED
         
         # check if the traffic car that drives before the player car
         # has the slower speed - the player car get its speed
         for tc in self.traffic_cars:           
            if self.is_behind(self.playerCar.playerRect, tc['rect']):
                if cur_sel_speed > tc['speed']:
                    cur_sel_speed = tc['speed']
                    
         return cur_sel_speed
                
                  
    # check if the turning is allowed
    def if_allow_turn(self):
        # check if the security area is empty
        for tc in self.traffic_cars:
            # the security area is calculated as left_coll_shift * tc_speed * tc_speed_factor
            if (tc['rect'].right > X_MERG - self.left_coll_shift * tc["speed"] * self.tc_speed_factor
                    and tc['rect'].right < X_MERG + self.right_coll_shift * tc["speed"] * self.tc_speed_factor
                    and tc['rect'].bottom > self.top_coll_shift):
                return False # not empty - do not enter
        return True # empty - can enter

    # update collision security area: left and right
    def update_coll_shifts(self):
        
        # trafic car ->> player car
        tr_pl = abs(self.playerCar.playerRect.left - self.collided_car_rect.right)
        # player car ->> traffic car
        pl_tr = abs(self.playerCar.playerRect.right - self.collided_car_rect.left)

        self.tc_speed_factor *= 1.05

        if tr_pl < pl_tr:   # a traffic car hits the player one
            self.left_coll_shift += SEC_AREA_UPDATE_VAL
        else:    # player car hits a traffic one
            self.right_coll_shift += SEC_AREA_UPDATE_VAL
        print(f"Left: {self.left_coll_shift}, Right: {self.right_coll_shift}, TC_speed_factor: {self.tc_speed_factor}")


    # environment step - performing actions in the environment
    def Step(self):

        # the player car start on the secondary road
        if self.current_player_car_state == STATE_START_SEC_ROAD:
            
            merge_dist = self.get_dist_till_merge()
            if merge_dist < self.start_slowdown_point:
                self.current_player_car_state = STATE_SLOWDOWN
                self.playerCar.player_car_accel = PLAYER_CAR_SLOWDOWN_ACCEL
         
        # the player car is slowing down on the secondary road               
        elif self.current_player_car_state == STATE_SLOWDOWN:
            
            merge_dist = self.get_dist_till_merge()
            if merge_dist < PLAYER_CAR_CHECKPOINT_BEFORE_MERGE:
                self.playerCar.player_car_accel = 0
                if self.if_allow_turn():
                    self.current_player_car_state = STATE_TURN
                else:
                    self.current_player_car_state = STATE_WAIT 
        
        # the player car is waiting before the turning to the main road
        elif self.current_player_car_state == STATE_WAIT:
            
            self.playerCar.player_car_accel = 0
            self.playerCar.player_car_speed = 0 
            self.playerCar.player_car_steer = 0
            
            if self.if_allow_turn():           
                self.current_player_car_state = STATE_TURN
                self.playerCar.player_car_accel = PLAYER_CAR_START_UP_ACCEL
         
        # the player car is turning to the main road
        elif self.current_player_car_state == STATE_TURN:
            
            self.playerCar.player_car_steer = PLAYER_CAR_TURN_STEER
            if self.playerCar.player_car_speed >= PLAYER_CAR_TURN_SPEED:
                self.playerCar.player_car_accel = 0
                self.playerCar.player_car_speed == 0
            
            # if it is the first episode 
            if self.num_episodes == 0:
                # update top value of the security area with maximal value
                # of the top value of the player car rectangle 
                if self.playerCar.playerRect.top < self.top_coll_shift:
                    self.top_coll_shift = self.playerCar.playerRect.top
            
            if self.playerCar.player_car_angle <= 0:
                self.playerCar.player_car_angle = 0
                self.playerCar.player_car_steer = 0
                self.player_car_state_speed_after_turn = self.get_player_car_speed_after_turn()
                self.current_player_car_state = STATE_SPEED_UP
        
        # the player car is speeding up on the main road
        elif self.current_player_car_state == STATE_SPEED_UP:
              
            self.playerCar.player_car_accel = PLAYER_CAR_START_UP_ACCEL
            if self.playerCar.player_car_speed >= self.player_car_state_speed_after_turn:
                self.playerCar.player_car_speed = self.player_car_state_speed_after_turn
                self.playerCar.player_car_accel = 0
                self.current_player_car_state = STATE_REG_SPEED

        # the player car returns to regulat speed
        elif self.current_player_car_state == STATE_REG_SPEED:

            self.playerCar.player_car_accel = 0
            
        # check if the collision occurs
        if not self.playerCar.player_car_crash and self.playerHasHitTrafficCar():
            # start crash process
            self.playerCar.player_car_crash = True
            # stop the player car
            self.playerCar.player_car_speed = 0    
            self.playerCar.player_car_accel = 0
            self.playerCar.player_car_steer = 0
            self.playerCar.player_car_crash_counter = FPS      # duration of the crash process
            
            # start of the collision process - display the collision image
            self.playerCar.collisionRect.left = self.playerCar.playerRect.left
            self.playerCar.collisionRect.top = self.playerCar.playerRect.top
            self.playerCar.is_collision = True
            
            self.update_coll_shifts()
            self.ResetPlayerCar()
            self.num_crashes += 1
            self.num_episodes_since_last_crash = 0

        # process the player car crash if it exists
        self.playerCar.CrashProcess()



# ============== Initialize the game ==============

# Initialize pygame library
pygame.init()

# clock object to control number of frames per second
mainClock = pygame.time.Clock()

# window display surface
windowSurface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# wundow caption
pygame.display.set_caption('Roads Merge')

# get the angle between the main and the secondary roads
sec_road_angle = get_angle(X_END_SEC_ROAD - X_START_SEC_ROAD, WINDOW_HEIGHT - (Y_START_MAIN_ROAD + WIDTH_MAIN_ROAD))

# create environment
env = Environment()


# =================== main loop =============================

carryOn = True
while carryOn:
    
    # events process
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            carryOn = False # Flag that we are done so we exit this loop
    
    env.Step()
    env.Update()
                     
    mainClock.tick(FPS)        

            
pygame.quit()

