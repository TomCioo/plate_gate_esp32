import cv2 as cv

def is_valid_plate_size(width,height,min_plate_width,min_plate_height):
    return width >= min_plate_width and height >= min_plate_height


def crop_plate(bbox,pad,frame):
    x1p = max(0, bbox[0]-pad)
    y1p = max(0, bbox[1]-pad)
    x2p = min(frame.shape[1], bbox[2]+pad)
    y2p = min(frame.shape[0], bbox[3]+pad)

    return frame[y1p:y2p, x1p:x2p]


def draw_plate_overlay(confirmed_plate,frame,bbox,track_id):
    display_text = confirmed_plate if confirmed_plate is not None else "?"
    cv.rectangle(frame,(bbox[0],bbox[1]),(bbox[2],bbox[3]),(0,0,255),2)
    cv.putText(frame,f'ID:{track_id} {display_text}',(bbox[0],bbox[1] - 10),cv.FONT_HERSHEY_PLAIN,1,(0,255,0),2)
