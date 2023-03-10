# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
from PIL import Image
import numpy as np
import pyautogui
import scipy
import scipy.ndimage
import typing as t

def get_cross_kernel(size: int, cross: int) -> np.ndarray:
  """Returns a kernel of given size with a origin symmetric cross shape.

  Args:
      size (int): The width and height of the kernel.
      cross (int): The width of the cross.

  Returns:
      np.ndarray: The kernel as a numpy array of the shape (size, size).
  """
  kernel = np.zeros((size, size), np.uint8)
  # cross shaped kernel
  size_2 = size // 2
  cross_2 = cross // 2
  kernel[size_2 - cross_2:size_2 + cross_2 + 1, size_2] = 1
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
  img = scipy.ndimage.morphology.binary_dilation(img, structure=kernel, iterations=3).astype(img.dtype)
  img = scipy.ndimage.morphology.binary_erosion(img, structure=kernel, iterations=3).astype(img.dtype)
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

def measure_bright_box(mask: np.ndarray) -> t.List[tuple]:
  """Measure the area of the largest shape in the given mask.

  Args:
      mask (np.ndarray): The processed monochrome image

  Returns:
      int: The area of the boundary box of largest shape in the given mask
      t.List[tuple]: The boundary boxes of all the shapes in the given mask
  """
  labels, n = scipy.ndimage.measurements.label(mask, np.ones((3, 3)))
  # get the bounding boxes of the bright boxes
  bboxes: t.List[tuple] = scipy.ndimage.measurements.find_objects(labels)
  bboxes.sort(key=lambda bbox: boundary_box_area(bbox), reverse=True)
  # return the area of the largest bounding box
  return bboxes

def largest_bbox(bboxes: t.List[tuple]) -> float:
  return pow(boundary_box_area(bboxes[0]),.5) if bboxes is not None and len(bboxes) > 0.0 else 0.0

def render_bboxes(img: np.ndarray, bboxes: t.List[tuple], primary_color: t.Tuple[int, int, int] = (0, 255, 0), secondary_color: t.Tuple[int, int, int] = (0,110,135), background_color: t.Tuple[int, int, int] = None) -> np.ndarray:
  """Renders bounding boxes to a mono-channel image.

  Args:
      img (np.ndarray): A openCV image with 1 channel and (floating-point) values between 0 and 1
      bboxes (t.List[tuple]): The bounding boxes to render

  Returns:
      np.ndarray: The RGB image with the bounding boxes rendered in the shape (height, width, 3)
  """
  # we need to convert it to a PIL image with 3 channels and values between 0 and 255m
  img = np.multiply(img, 255).astype(np.uint8)
  img = np.dstack((img,) * 3)
  # add the background color 0-255 to the image 0-255 and normalize it to 0-255
  if background_color is not None:
    img = np.add(img, background_color)
    img = np.divide(img, 2).astype(np.uint8)

  # render bounding boxes to the image
  if len(bboxes) > 0:
    # first box in green
    y,x = bboxes[0]
    img[(y.start,y.stop-1),x]=primary_color
    img[y,(x.start,x.stop-1)]=primary_color
    for y,x in bboxes[1:]:
      # other boxes in teal
      img[(y.start,y.stop-1),x]=secondary_color
      img[y,(x.start,x.stop-1)]=secondary_color
  return img

def smart_resize(img: Image, height: int = None, width: int = None) -> Image:
  """Resize the given image to the given dimensions while keeping the aspect ratio, if only width or height is defined

  Args:
      img (PIL.Image): The image to resize
      dims (object): The dimensions to resize to, in the form (width, height) where either width or height can be None

  Returns:
      PIL.Image: The resized image
  """
  dims = (img.height, img.width)
  if width is not None and height is not None:
    dims = (width, height)
  elif width is not None:
    dims = (width, int(width * img.height / img.width))
  elif height is not None:
    dims = (int(height * img.width / img.height), height)
  return img.resize(dims, Image.ANTIALIAS)
