import cv2 as cv
import config

points = []

def mouse_click(event, x, y, flags, param):

    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print("Klik:", x, y)


def main():

    cap = cv.VideoCapture(config.VIDEO_SOURCE)

    success, frame = cap.read()

    if not success:
        print("Nie mozna odczytac klatki")
        return

    cv.namedWindow("frame")
    cv.setMouseCallback("frame", mouse_click)

    while True:

        display = frame.copy()

        for p in points:
            cv.circle(display, p, 5, (0,0,255), -1)

        if len(points) == 2:

            cv.rectangle(display, points[0], points[1], (255,0,0), 2)

            x1 = min(points[0][0], points[1][0])
            y1 = min(points[0][1], points[1][1])
            x2 = max(points[0][0], points[1][0])
            y2 = max(points[0][1], points[1][1])

            print("\nDodaj do config.py:")
            print(f"ROI_X1 = {x1}")
            print(f"ROI_Y1 = {y1}")
            print(f"ROI_X2 = {x2}")
            print(f"ROI_Y2 = {y2}")

        cv.imshow("frame", display)

        key = cv.waitKey(1)

        if key == ord('q'):
            break

        if key == ord('r'):
            points.clear()

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()