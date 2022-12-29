
import cv2 #importing OpenCV
import mouse #importing mouse module
import keyboard #importing keyboard module
import time #importing time module
import pyautogui #importing pyautogui module
import threading #importing threading module
import os #importing os module

#Variables to set the resolution of the projector
PROJECTOR_RESOLUTION_WIDTH = 1920 
PROJECTOR_RESOLUTION_HEIGHT = 1280 

#Variable to set the second monitor 
secondMonitor=0

#Variables to set the offset of the projector
PROJECTOR_X_OFFSET = 0
PROJECTOR_Y_OFFSET = 0 

#Variables to define the camera index and the mappings of the clicks
CAMERA_INDEX = 0
LEFT_CLICK_MAPPING = 'pagedown'
RIGHT_CLICK_MAPPING = 'up'

#Variable to set the drawing state
drawing = False 

#Printing a message when the program is starting
print("Iniciando...")

#Define the calibrate function to set the area of the laser
def calibrate():
    #Define an empty function to be used in the trackbar
    def onThresholdTrackbarChanged(value):
        pass

    #Define the finish function to define the area of the laser
    def finish(dotsX, dotsY):
        #Get the threshold value from the trackbar
        threshold = cv2.getTrackbarPos("Brilho", "calibration")
        #Destroy the window
        cv2.destroyWindow('calibration')

        #Get the minimum and maximum values for X and Y
        lowXpos = min(dotsX)
        lowYpos = min(dotsY)
        highXpos = max(dotsX)
        highYpos = max(dotsY)
        #Return the values of the area
        return lowXpos, lowYpos, highXpos, highYpos, threshold


    #Create a window to set the area
    cv2.namedWindow('calibration')

    #Create a trackbar in the window
    cv2.createTrackbar('Brilho', 'calibration', 255, 255, onThresholdTrackbarChanged)

    #Print a message to the user
    print("Contorne as bordas do projetor e depois aperte F")
    #Create two empty lists to store the values of X and Y
    dotsX = []
    dotsY = []
    #Define the click event to get the values
    def click_event(event, x, y, flags, params):
        global drawing

        #If the left mouse button is pressed
        if event == cv2.EVENT_LBUTTONDOWN:
            #Set the drawing state to true
            drawing = True
            #Set the values of X and Y
            ix,iy = x,y
        #If the mouse is moved and the drawing state is true
        elif event == cv2.EVENT_MOUSEMOVE and drawing == True:
            #Append the values of X and Y to the lists
            dotsX.append(x)
            dotsY.append(y)
        #If the left mouse button is released
        elif event == cv2.EVENT_LBUTTONUP:
            #Set the drawing state to false
            drawing = False
        #If the right mouse button is pressed
        elif event == cv2.EVENT_RBUTTONDOWN:
            #Clear the lists
            dotsX.clear()  
            dotsY.clear() 

    #Create the background subtractor   
    backSub = cv2.createBackgroundSubtractorMOG2( history=25, varThreshold=150, detectShadows=False)
    #Save the time
    restTime = time.time()
    #Get the value of the trackbar
    pastTrackbar =  cv2.getTrackbarPos("Brilho", "calibration")
    #Create a variable to store the new trackbar value
    newTrack =  0
    #While the program is running
    while True:
        #Get the frame from the camera
        ret, frame = cap.read()
        #If there is no frame
        if not ret:
            #Print a message
            print("Can't receive frame (stream end?). Exiting ...")
            #Break the loop
            break
        #Clone the frame
        frameClone = frame
        #Convert the frame to gray
        original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #Convert the cloned frame to gray
        gray = cv2.cvtColor(frameClone, cv2.COLOR_BGR2GRAY)
        #Apply the background subtractor to the 
        mask = backSub.apply(frameClone)      # Apply the mask to the frameClone 
        new_image = cv2.bitwise_and(gray,mask) # Creates a new image using bitwise and 
        thresh = cv2.inRange(new_image, cv2.getTrackbarPos("Brilho", "calibration"), 255) # Sets the range of the image 
        dilated = thresh # Make a copy of the thresh 
        contours = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2] # Find the contours of the image 
        newTrack =  cv2.getTrackbarPos("Brilho", "calibration") # Get the trackbar position

        # If there is more than 10 elements in the dotsX and dotsY arrays
        if(len(dotsX) > 10 and len(dotsY) > 10):
                    # Get the min and max of dotsX and dotsY and creates a Rectangle with those points
                    c1 = min(dotsX), min(dotsY)
                    c2 = max(dotsX), max(dotsY) 
                    cv2.rectangle(dilated, (int(c1[0]), int(c1[1])), (int(c2[0]), int(c2[1])), (255, 0, 0), 2)
                    cv2.rectangle(original, (int(c1[0]), int(c1[1])), (int(c2[0]), int(c2[1])), (0, 0, 0), -1)

        # If the newTrack is different from the pastTrackbar
        if(newTrack != pastTrackbar):
                    pastTrackbar = newTrack
                    dotsX.clear()   # Clear the dotsX array 
                    dotsY.clear()   # Clear the dotsY array 
        finalImg = thresh.copy() # Make a copy of the thresh

        # If the dotsX and dotsY arrays are empty
        if(dotsX == [] or dotsY == []):
                    # Writes in the finalImg
                    cv2.putText(finalImg, "{}".format('Contorne as bordas com o Laser'), (15, 25), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 0, 0), 3)
                    cv2.putText(finalImg, "{}".format('-> use o Botao esquerdo para Selecionar area'), (15, 55), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (255, 0, 0), 3)        
        # If the size of the dotsX and dotsY arrays is greater than 7 
        elif(len(dotsX) > 7 and len(dotsY) > 7):
                    # Writes in the finalImg
                    cv2.putText(finalImg, "{}".format('Pressione F para finalizar'), (15, 25), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 0, 0), 3)
                    cv2.putText(finalImg, "{}".format('-> use o Botao direito para Limpar area'), (15, 55), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (255, 0, 0), 3)
                
        # If the size of the dotsX and dotsY arrays is less than or equal to 7 
        elif(len(dotsX) <= 7 and len(dotsY) <= 7):
                            # Writes in the finalImg
                            cv2.putText(finalImg, "Status: {}".format('Contornando a area: ' + str(int((len(dotsX) * 100) /8)) + " %"), (15, 25), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (255, 0, 0), 3)
        
        # Loop through the contours of the dilated image
        for contour in contours:     
                    # Get the area of the contours
                    area = cv2.contourArea(contour)
                    # If the area is greater than 10
                    if area > 10 :
                        # Get the x, y, w and h of the contours
                        x, y, w, h = cv2.boundingRect(contour)
                        # Append the x and y of the contours to the dotsX and dotsY arrays
                        dotsX.append(x + w / 2)
                        dotsY.append(y + h / 2)
        # Set the callback for mouse events
        cv2.setMouseCallback('calibration', click_event)
        # Create a new image using bitwise or
        new_image = cv2.bitwise_or(original,finalImg)
        # Show the new_image
        cv2.imshow('calibration', new_image)

        # If the key 'f' is pressed
        if cv2.waitKey(1) == ord('f'):
                    # Call the function finish
                    return finish(dotsX, dotsY)

# Open the camera
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
# Set the width and height of the camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# If the camera is not opened, print "Cannot open camera"
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Defines for trackbars
def onOffsetYTrackbarChanged(value):
        global PROJECTOR_Y_OFFSET
        PROJECTOR_Y_OFFSET =int(value)
        pass
def onOffsetXTrackbarChanged(value):
        global PROJECTOR_X_OFFSET
        PROJECTOR_X_OFFSET =int(value)
        pass#Defining the "preview" function 
def preview():
    
    #While loop to keep looping
    while True:
        
        #Reading the video frame
        ret, frame = cap.read()
        
        #If not frame, print message
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
            
        #Writing the text "C - Pressione C para calibrar" in the frame
        cv2.putText(frame, "C - {}".format('Pressione C para calibrar'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 0, 0), 3)
                        
        #Showing the frame
        cv2.imshow('preview', frame)
        
        #If pressing 'c', break loop
        if cv2.waitKey(1) == ord('c'):
            break
    
    #Calling the main function with the calibrate's return
    main(calibrate())

#Defining the "move_mouse" function 
def move_mouse(dotX, dotY, top_left, bottom_right):
    
    #Defining the "get_size" function 
    def get_size(top_left, bottom_right):
        return bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]
    
    #Defining the "offset_laser_pos" function 
    def offset_laser_pos(dotX, dotY):
        return dotX - top_left[0], dotY - top_left[1]
    
    #Defining the "translate_size" function 
    def translate_size(x, y, hsize, vsize, display_width, display_height):
        x = (x * display_width) / hsize
        y = (y * display_height) / vsize
        return x, y
    
    #Getting the size
    hsize, vsize = get_size(top_left, bottom_right)
    
    #Getting the offset laser position
    offsetX, offsetY = offset_laser_pos(dotX, dotY)
    
    #Translating the size
    x, y = translate_size(offsetX, offsetY, hsize, vsize, PROJECTOR_RESOLUTION_WIDTH, PROJECTOR_RESOLUTION_HEIGHT)
    
    #If cursor is inside the limits of the resolution, moving the mouse
    if(x + PROJECTOR_X_OFFSET < PROJECTOR_RESOLUTION_WIDTH and x + PROJECTOR_X_OFFSET> 0 and y + PROJECTOR_Y_OFFSET < PROJECTOR_RESOLUTION_HEIGHT and y> 0):
        mouse.move(x+secondMonitor+PROJECTOR_X_OFFSET, y+PROJECTOR_Y_OFFSET, absolute=True, duration=0.02)

#Defining the "cursor_track" function 
def cursor_track():
    #Time variable to start movement
    timeStartMovement = 0.0
    
    #While loop to keep looping
    while True:
        #Variable to check if the mouse is left pressed
        mouseLeft = False
        
        #If pressing 'pagedown', start the time and press left mouse button
        if keyboard.is_pressed("pagedown"):
            timeStartMovement = time.time()
            if(mouseLeft == False): 
                pyautogui.mouseDown(button='left') 
                mouseLeft = True      
        
        #If the time is more than 0.12 and less than 0.5, release the left mouse button
        elif(float(time.time()) - float(timeStartMovement) > 0.12 and float(time.time()) - float(timeStartMovement) < 0.5 ):
            pyautogui.mouseUp(button='left')  
            mouseLeft = False
            
        #If pressing 'q', break loop
        if cv2.waitKey(1) == ord('q')  : break

#Done variable to finish the main function
done1 = 0

#Defining the "main" function 
def main(calibration):
 
    #Getting the top_left and bottom_right variables from calibration
    top_left = (int(calibration[0]), int(calibration[1]))
    bottom_right = (int(calibration[2]), int(calibration[3]))
    
    #Getting the threshold from calibration
    threshold = calibration[4]

    #Background subtractor
    backSub = cv2.createBackgroundSubtractorMOG2( history=25, varThreshold=150, detectShadows=True)
   
    #Creating the thread
    p1 = threading.Thread(target=cursor_track)
    #Starting the thread
    p1.start() 
    
    #Creating the window
    cv2.namedWindow('MouseViewer')
    
    #Creating the trackbars
    cv2.createTrackbar('DeslocamentoY', 'MouseViewer', 0, 500, onOffsetYTrackbarChanged)
    cv2.setTrackbarMin('DeslocamentoY', 'MouseViewer', -500)
    cv2.createTrackbar('DeslocamentoX', 'MouseViewer', 0, 500, onOffsetXTrackbarChanged)
    cv2.setTrackbarMin('DeslocamentoX', 'MouseViewer', -500)
    
    #Defining the "onThresholdTrackbarChanged" function 
    def onThresholdTrackbarChanged(value):
        pass
    #Creating the trackbar
    cv2.createTrackbar('Brilho', 'MouseViewer', threshold   , 255, onThresholdTrackbarChanged)
    cv2.createTrackbar('BrilhoMax', 'MouseViewer', 255, 255, onThresholdTrackbarChanged)
    
    #While loop to keep looping
    while not (done1):
        #Getting the threshold and brilhoMax from trackbar
        threshold=  cv2.getTrackbarPos("Brilho", "MouseViewer")
        brilhoMax=  cv2.getTrackbarPos("BrilhoMax", "MouseViewer")
        
        #Reading the video frame
        ret, frame = cap.read()
        
        #If not frame, print message
        if not ret:
            print("Can't receive frame. Exiting...")
            break
        
        #Copying the frame
        output = frame.copy()
        
        #Converting to gray
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #Getting the mask
        mask = backSub.apply(frame)
        
        #Applying the bitwise_and
        new_image = cv2.bitwise_and(gray,mask)
        
        #Getting the threshold
        thresh = cv2.inRange(new_image, threshold, brilhoMax)
        
        #Dilating the image
        dilated = thresh
        
        #Creating the dotX and dotY variables
        dotX = []
        dotY = []
        
        #Getting the contours
        contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        
        #For loop for each contour
        for contour in contours:    
            #Getting the area
            area = cv2.contourArea(contour)
            #If area is more than 10
            if area > 10:
                #Getting the x, y, w and h of the contour
                x, y, w, h = cv2.boundingRect(contour)
                #Getting the dotX and dotY
                dotX = [(x + w / 2)]
                dotY = [(y + h / 2)]
                
        #For loop for each point
        for i in range(len(dotX)):
            #Moving the mouse
            move_mouse(dotX[i] , dotY[i], top_left, bottom_right)
        
        #Drawing the rectangle
        output = cv2.rectangle(dilated, top_left, bottom_right, (255,255,255), 2)
        
        #Applying the bitwise_or
        outputmasked = cv2.bitwise_or(output, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        
        #Showing the frame
        cv2.imshow('MouseViewer', outputmasked)
        
        #If pressing 'q', break loop
        if cv2.waitKey(1) == ord('q')  : break

#Calling the preview function
preview()

#Releasing the video capture
cap.release()

#Destroying all windows
cv2.destroyAllWindows()