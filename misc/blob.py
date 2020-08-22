#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------
import array
import math
from micropython import const

# pylint: disable=bad-whitespace
BLOB_ERRC_OK       = const(0)
BLOB_ERRC_MEMORY   = const(-1)

MAX_BLOBS          = const(5)
MAX_BLOB_FIELDS    = const(5)
FILTER_SIZE        = const(3)
MAX_FILTERS        = const(2)

filterSet          = [[[1,  1, 1], [ 1, 1,  1], [1,  1, 1]],
                      [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]]

xoffs              = [-1, 1,  0, 0]
yoffs              = [ 0, 0, -1, 1]
# pylint: enable=bad-whitespace

class blob_struct(object):
  def __init__(self, area=0, ID=0, prob=0, x=0, y=0):
    self.area = area
    self.ID = ID
    self.prob = prob
    self.x = x
    self.y = y

  @property
  def as_list(self):
    return [self.area, self.ID, self.prob, self.x, self.y]

  def copy(self, b):
    self.area = b.area
    self.ID = b.ID
    self.prob = b.prob
    self.x = b.x
    self.y = b.y


class pos_struct(object):
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

# ---------------------------------------------------------------------
def filter(dx, dy, pImg, mode):
  """
  """
  n = dx*dy
  pTmp = None
  #int r, dxf, dyf, x, y, j, nf, m, ix, iy;

  # Check parameters
  if mode <= 0 or mode > MAX_FILTERS:
    # No filter requested or invalid filter mode
    return

  # Calculate average for edge pixels
  sum = 0
  avg = 0
  for j in range(n):
    sum += pImg[j]
  avg = sum /n

  # Make a larger image copy for the filtering
  r = int((FILTER_SIZE -1) /2)
  dxf = dx +r*2
  dyf = dy +r*2
  nf = dxf*dyf

  '''
  pTmp = malloc(nf*sizeof(*pTmp));
  for(j=0; j<nf; j++)
    pTmp[j] = avg;
  for(x=0; x<dx; x++) {
    for(y=0; y<dy; y++) {
      pTmp[x+r +(y+r)*dx] = pImg[x +y*dx];
    }
  }
  // Apply filter ...
  for(x=0; x<dxf; x++) {
    for(y=0; y<dyf; y++) {
      if((y >= r) && (y < dyf-r) && (x >= r) && (x < dxf-r)) {
        sum = 0;
        m = 0;
        for(iy=-r; iy<r; iy++) {
          for(ix=-r; ix<r; ix++) {
            sum += pTmp[x+ix +(y+iy)*dxf] *filterSet[mode-1][ix+r][iy+r];
            if(filterSet[mode-1][ix+r][iy+r] != 0)
              m++;
          }
        }
        pImg[x-r +(y-r)*dx] = sum/m;
      }
    }
  }
  free(pTmp);
  '''

# ---------------------------------------------------------------------
def detect(img, dxy, params):
  """
  """
  blobs = []
  for i in range(MAX_BLOBS):
    blobs.append(blob_struct())
  nBlobs = 0
  posList = []

  # Extract the parameters from the micropython input objects
  dx = dxy[0]
  dy = dxy[1]
  mode = params[0]
  nsd = params[1]
  n = dx*dy
  pImg = array.array("f", [0]*n)
  pMsk = array.array("B", [0]*n)
  pPrb = array.array("f", [0]*n)

  # Copy image data into a float array
  for i in range(n):
    pImg[i] = img[i]
    pMsk[i] = 0

  # Apply filter, if requested
  if mode > 0:
    filter(dx, dy, pImg, mode)

  # Mean and sd across (filtered) image
  avg = sum(pImg) /n
  _sum = 0
  for i in range(n):
    _sum += math.pow(pImg[i] -avg, 2)
  sd = math.sqrt(_sum /(n-1))

  # Mark all pixels above a threshold
  nThres = 0
  for i in range(n):
    if pImg[i] >= avg +sd *nsd:
      pMsk[i] = 255
      pPrb[i] = (pImg[i] -avg) /sd
      nThres += 1

  # Find blobs
  nLeft = nThres
  #iBlob = 1
  iBlob = 0
  #while nLeft > 0:
  while nLeft > 0 and iBlob < MAX_BLOBS:
    # As long as unassigned mask pixels are left, continue going over the image
    for y in range(dy):
      for x in range(dx):
        #print("mask({0:.0d})={1:.0d}".format(x +y*dx, pMsk[x +y*dx]))

        if pMsk[x +y*dx] == 255:
          # Unassigned pixel found ...
          posList.append(pos_struct(x, y))
          pMsk[x +y*dx] = iBlob
          nFound = 1
          bx = float(x)
          by = float(y)
          bp = pPrb[x +y*dx]

          # Find all unassigned pixels in the neighborhood of this seed pixel
          while len(posList) > 0:
            p0 = posList.pop()
            for k in range(4):
              p1 = pos_struct(p0.x +xoffs[k], p0.y +yoffs[k])
              if((p1.x >= 0) and (p1.x < dx) and
                 (p1.y >= 0) and (p1.y < dy) and
                 (pMsk[p1.x +p1.y*dx] == 255)):
                # Add new position from which to explore
                posList.append(pos_struct(p1.x, p1.y))
                pMsk[p1.x +p1.y*dx] = iBlob
                nFound += 1
                bx += float(p1.x)
                by += float(p1.y)
                bp += pPrb[p1.x +p1.y*dx]
          # Update number of unassigned pixels
          nLeft -= nFound

          # Store blob size and center of gravity position
          k = 0
          try:
            #if iBlob > 1:
            if iBlob > 0:
              while (k < iBlob) and (blobs[k].area > nFound):
                k += 1
              if k < iBlob:
                #for m in range(iBlob-1, k, -1):
                #  blobs[m].copy(blobs[m-1])
                for m in range(iBlob-1, k, -1):
                  blobs[m].copy(blobs[m-1])
          except IndexError:
            print("INDEX ERROR: k, iBlob, m, len(blobs)", k, iBlob, m, len(blobs))

          blobs[k].ID   = iBlob
          blobs[k].area = nFound
          blobs[k].x    = by /nFound
          blobs[k].y    = bx /nFound
          blobs[k].prob = bp /nFound
          iBlob += 1
  nBlobs = iBlob

  # Copy blobs into list as function result
  tempL = []
  try:
    for i in range(nBlobs):
      if blobs[i].area > 0:
        tempL.append(blobs[i].as_list)
  except IndexError:
    print("INDEX ERROR: i, nBlobs, len(blobs)", i, nBlobs, len(blobs))


  # Return list of blobs, otherwise empty list
  return tempL

# ---------------------------------------------------------------------
