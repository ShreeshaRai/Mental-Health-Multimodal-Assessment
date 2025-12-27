import cv2
import dlib
from fer import FER


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


emotion_detector = FER(mtcnn=True)


def draw_landmarks(frame, rect):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    landmarks = predictor(gray, rect)

    for n in range(68):
        x = landmarks.part(n).x
        y = landmarks.part(n).y
        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)


def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    
    results = emotion_detector.detect_emotions(frame)

    
    for face in faces:
        draw_landmarks(frame, face)

    
    for data in results:
        x, y, w, h = data["box"]
        emotions = data["emotions"]

        dominant_emotion = max(emotions, key=emotions.get)
        confidence = emotions[dominant_emotion]

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 200, 0), 2)
        cv2.putText(
            frame,
            f"{dominant_emotion}: {confidence:.2f}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

    return frame


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = process_frame(frame)
        cv2.imshow("Facial Emotion & Landmark Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:  
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
