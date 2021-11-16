import cv2
import mediapipe as mp
import math

mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

FINGER = {
    "THUMB": {"p1": 0, "p2": 2, "p3": 4, "max_close_angle": 140, "min_open_angle": 150},
    "INDEX": {"p1": 0, "p2": 6, "p3": 8, "max_close_angle": 45, "min_open_angle": 100},
    "MIDDLE": {"p1": 0, "p2": 10, "p3": 12, "max_close_angle": 45, "min_open_angle": 100},
    "RING": {"p1": 0, "p2": 14, "p3": 16, "max_close_angle": 40, "min_open_angle": 80},
    "PINKY": {"p1": 0, "p2": 18, "p3": 20, "max_close_angle": 40, "min_open_angle": 80},
}

class Vector3:
    x = 0
    y = 0
    z = 0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class JankenCam:
    cap = None
    play = -1
    debugMode = False

    # opens cam
    def __init__(self, src=0, debugMode=False):
        self.cap = cv2.VideoCapture(src)
        self.debugMode = debugMode

    # capture current frame for hand identification
    def capture(self, do_process_hand):
        with mp_hands.Hands(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1,
        ) as hands:
            if self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    print("Video input reading FAILED!")

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(img)

                if do_process_hand:
                    self.process_hand(results.multi_hand_landmarks, img)

                img.flags.writeable = self.debugMode
                if self.debugMode: #debug mode stuff
                    img = self.draw_hand_annotations(img, results)

                    # display flipped image (w/ annotations)
                    cv2.imshow('Janken Debug - Hand Annotations', cv2.flip(img, 1))
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        return


    def __del__(self):
        self.cap.release()

    # process playing hand for janken
    def process_hand(self, hands, img):
        if hands:
            h, w, _ = img.shape

            fingers = []
            for x in FINGER:
                isOpen = self.is_finger_open(FINGER[x], hands[0], h, w)
                fingers.append(isOpen)
            
            if None in fingers:
                print("Cannot read playing hand. Please try again.")
            else:
                self.play = self.get_janken_hand(fingers[0], fingers[1], fingers[2], fingers[3], fingers[4])


    # draw annotations for debug mode
    def draw_hand_annotations(self, img, results):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    img,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style()
                )
        return img


    # returns janken hand as integer
    def get_janken_hand(self, t, i, m, r, p):
        print(t, i, m, r, p)
        if t and i and m and r and p:
            return 1 #rock
        elif not (t or i or m or r or p):
            return 0 #paper
        elif i and m and not (t or r or p):
            return 2 #scissors
        
        return -1 # invalid if not matching any of the preset hands
    

    # uses finger metadata to see if finger is open
    def is_finger_open(self, finger, landmarks, img_height, img_width):
        theta = self.get_finger_angle(finger, landmarks, img_height, img_width)
        
        if theta <= finger["max_close_angle"]:
            return False
        elif theta >= finger["min_open_angle"]:
            return True
        else:
            print(theta)
            return None    # invalid if between close angle and open angle thresholds


    # calculates angle of a finger based on landmarks
    def get_finger_angle(self, finger, landmarks, img_height, img_width):
        p1 = landmarks.landmark[finger["p1"]]
        p2 = landmarks.landmark[finger["p2"]]
        p3 = landmarks.landmark[finger["p3"]]

        a = Vector3(p1.x, p1.y, p1.z)
        b = Vector3(p2.x, p2.y, p2.z)
        c = Vector3(p3.x, p3.y, p3.z)

        a.x *= img_width
        b.x *= img_width
        c.x *= img_width

        a.y *= img_height
        b.y *= img_height
        c.y *= img_height

        a.z *= img_width
        b.z *= img_width
        c.z *= img_width

        # angle of 3 points in 3d space formula
        ab = Vector3(a.x-b.x, a.y-b.y, a.z-b.z)
        bc = Vector3(c.x-b.x, c.y-b.y, c.z-b.z)

        abmag = math.sqrt(ab.x **2 + ab.y**2 + ab.z**2)
        abnorm = Vector3(ab.x/abmag, ab.y/abmag, ab.z/abmag)

        bcmag = math.sqrt(bc.x **2 + bc.y**2 + bc.z**2)
        bcnorm = Vector3(bc.x/bcmag, bc.y/bcmag, bc.z/bcmag)

        dot = abnorm.x*bcnorm.x + abnorm.y*bcnorm.y + abnorm.z*bcnorm.z
        theta = math.degrees(math.acos(dot))

        return theta