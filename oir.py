# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
import typing as t
import pyautogui
import scipy.ndimage
import scipy
from itertools import product
import numpy as np

def get_cross_kernel(size: int) -> np.ndarray:
  """Returns a kernel of given size with a origin symmetric cross shape.

  Args:
      size (int): The width and height of the kernel.

  Returns:
      np.ndarray: The kernel as a numpy array of the shape (size, size).
  """
  kernel = np.zeros((size, size), np.uint8)
  # cross shaped kernel
  half = size // 2
  for x,y in product(range(size), range(size)):
      if x == half or y == half:
          kernel[x,y] = 1
  return kernel

def masked_screenshot(region: tuple, kernel: np.ndarray) -> np.ndarray:
  """Take a screenshot of the given region and apply some processing to it.
  Args:
      region (tuple): The region from top-left in the form (x1, y1, x2, y2)
      kernel (np.ndarray): The kernel used for dilation and erosion
  Returns:
      np.ndarray: The monochrome screenshot taken from the given region
  """
  img = pyautogui.screenshot(region=region)
  # convert the image to a grayscale numpy array
  img = np.array(img.convert('L'))
  # apply thresholding
  # the dark box will turn bright if its a match, so we ought to remove the dark, but keep the bright over the thresholdm
  # the theshold is around 180, so anything below 180 will be set to 0, anything above that will be set to 255
  # now the dark box will be 0, and the bright box will be 255, which can easily be detected using the scipy.ndimage.morphology
  img = (img > 180) * 255
  # finally apply dilation and erosion to complete possible holes in the bright box border
  img = scipy.ndimage.morphology.binary_dilation(img, structure=kernel).astype(img.dtype)
  img = scipy.ndimage.morphology.binary_erosion(img, structure=kernel).astype(img.dtype)
  # save image
  return img

def boundary_box_area(bbox: t.Tuple[object, object]) -> int:
  """Calculate the area of a boundary box.

  Args:
      bbox (t.Tuple[object, object]): The scipy boundary box

  Returns:
      int: The area of the boundary box
  """
  return abs(bbox[0].stop - bbox[0].start) * abs(bbox[1].stop - bbox[1].start)

def rect_area(rect: t.Tuple[int, int, int, int]) -> int:
  """Calculate the area of a rectangle.

  Args:
      rect (t.Tuple[int, int, int, int]): The rectangle in the form (x1, y1, x2, y2)

  Returns:
      int: The area of the rectangle
  """
  return abs(rect[2] - rect[0]) * abs(rect[3] - rect[1])

def measure_bright_box(mask: np.ndarray) -> int:
  """Measure the area of the largest shape in the given mask.

  Args:
      mask (np.ndarray): The processed monochrome image

  Returns:
      int: The area of the boundary box of largest shape in the given mask
      np.ndarray: The
  """
  labels, n = scipy.ndimage.measurements.label(mask, np.ones((3, 3)))
  # get the bounding boxes of the bright boxes
  bboxes: list = scipy.ndimage.measurements.find_objects(labels)
  if len(bboxes) == 0:
    return 0
  # get the largest bounding box
  largest_bbox = max(bboxes, key=lambda bbox: boundary_box_area(bbox))
  largest_bbox_area = boundary_box_area(largest_bbox)
  # return the area of the largest bounding box
  return largest_bbox_area
