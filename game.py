import cv2
import mediapipe as mp
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize OpenCV Video Capture
cap = cv2.VideoCapture(0)

# Game variables
screen_width, screen_height = 640, 480
player_radius = 20
enemy_radius = 15
enemies = []
score = 0
game_over = False

# Function to generate new enemies
def generate_enemy():
    x = random.randint(enemy_radius, screen_width - enemy_radius)
    y = 0
    return (x, y)

# Generate initial enemies
for _ in range(5):
    enemies.append(generate_enemy())

while cap.isOpened() and not game_over:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Resize the frame to match the game screen dimensions
    frame = cv2.resize(frame, (screen_width, screen_height))

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    results = hands.process(rgb_frame)

    # Draw player and update position
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get the position of the index finger tip
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            player_x = int(index_finger_tip.x * screen_width)
            player_y = int(index_finger_tip.y * screen_height)

            # Draw the player
            cv2.circle(frame, (player_x, player_y), player_radius, (0, 255, 0), -1)

            # Collision detection
            for enemy in enemies:
                ex, ey = enemy
                distance = ((player_x - ex)**2 + (player_y - ey)**2)**0.5
                if distance < player_radius + enemy_radius:
                    game_over = True

    # Update enemy positions
    new_enemies = []
    for enemy in enemies:
        ex, ey = enemy
        ey += 5  # Move the enemy downward
        if ey < screen_height:
            new_enemies.append((ex, ey))
            cv2.circle(frame, (ex, ey), enemy_radius, (0, 0, 255), -1)

    # Remove off-screen enemies and generate new ones
    enemies = new_enemies
    while len(enemies) < 5:
        enemies.append(generate_enemy())

    # Display score
    cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    score += 1

    # Display the frame
    cv2.imshow("Enemy Dodging Game", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

if game_over:
    print("Game Over! Your score:", score)