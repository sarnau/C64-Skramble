#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import struct
import binascii
from PIL import Image, ImageDraw, ImageShow, ImageFont

font12 = ImageFont.truetype('FiraCode-Regular.ttf', 12)
font8 = ImageFont.truetype('FiraCode-Regular.ttf', 8)

PIXEL_SET = '█︎'
PIXEL_CLEAR = ' '

data = bytearray(0x801) + bytearray(open('./SKRAMBLE.TAP_ANIROG TAPE_BLOCK_5.PRG','rb').read()[2:])


class bcolors:
	BLACK = '\033[38;5;0m'
	WHITE = '\033[38;5;15m'
	RED = '\033[38;5;1m'
	CYAN = '\033[38;5;13m'
	PURPLE = '\033[38;5;5m'
	GREEN = '\033[38;5;2m'
	BLUE = '\033[38;5;4m'
	YELLOW = '\033[38;5;11m'

	ORANGE = '\033[38;5;220m'
	BROWN = '\033[38;5;88m'
	LIGHT_RED = '\033[38;5;9m'
	DARK_GREY = '\033[38;5;238m'
	GREY = '\033[38;5;244m'
	LIGHT_GREEN = '\033[38;5;10m'
	LIGHT_BLUE = '\033[38;5;12m'
	LIGHT_GREY = '\033[38;5;252m'
	
	DEFAULT = '\033[1;39m'

c64_colors = (
			bcolors.BLACK,
			bcolors.RED,
			bcolors.YELLOW,
			bcolors.BLUE,
			)

c64_rgb_colors = (
			(0x00,0x00,0x00,0xFF), (0xFF,0xFF,0xFF,0xFF), (0x88,0x00,0x00,0xFF), (0xAA,0xFF,0xEE,0xFF),
			(0xCC,0x44,0xCC,0xFF), (0x00,0xCC,0x55,0xFF), (0x00,0x00,0xAA,0xFF), (0xEE,0xEE,0x77,0xFF),
			(0xDD,0x88,0x55,0xFF), (0x66,0x44,0x00,0xFF), (0xFF,0x77,0x77,0xFF), (0x33,0x33,0x33,0xFF),
			(0x77,0x77,0x77,0xFF), (0xAA,0xFF,0x66,0xFF), (0x00,0x88,0xFF,0xFF), (0xBB,0xBB,0xBB,0xFF),
			)

def drawFont(addr,firstChar=0x00,lastChar=0x40,isColor=False):
	print('Font $%04x $%02x-$%02x' % (addr,firstChar,lastChar))
	print('=====================')
	if isColor:
		width = 4
		lineLen = 16
	else:
		width = 8
		lineLen = 8
	gap = 0
	chheight = 8
	for cindex in range(firstChar,lastChar+1,lineLen):
		s = ''
		for o in range(0,lineLen):
			st = '$%02x' % (cindex + o)
			s += (st + ' ' * 30)[:width+gap] + ' '
		print(s)
		for row in range(0,chheight):
			s = ''
			for o in range(0,lineLen):
				bstr = '{:08b}'.format(data[addr + (chheight * (cindex + o)) + row])
				st = ''
				if isColor:
					for i in range(0,len(bstr),2):
						val = int(bstr[i:i+2],2)
						st += c64_colors[val]+PIXEL_SET
					st += bcolors.DEFAULT
				else:
					st = bstr.replace('1',PIXEL_SET).replace('0',PIXEL_CLEAR)
				s += st + ' ' + ' ' * gap
			print(s)
	print()

def drawSprites(addr,count=1,baseAddr=0x00,isColor=False):
	print('Sprites $%04x' % (addr))
	print('==============')
	if isColor:
		width = 4
	else:
		width = 8
	for sindex in range(0,count):
		print('Sprite #%d / $%02x' % (sindex, (sindex * 64 + baseAddr) >> 6))
		for row in range(0,21):
			s = ''
			for o in range(0,3):
				bstr = '{:08b}'.format(data[addr + sindex * 64 + (row * 3) + o])
				st = ''
				if isColor:
					for i in range(0,len(bstr),2):
						val = int(bstr[i:i+2],2)
						st += c64_colors[val]+PIXEL_SET
					st += bcolors.DEFAULT
				else:
					st = bstr.replace('1',PIXEL_SET).replace('0',PIXEL_CLEAR)
				s += st
			print(s)
	print()

def drawLevels():
	global c64_rgb_colors
	LOWER_SECTOR_DATA = 0x4000
	UPPER_SECTOR_DATA = 0x6000
	SECTOR_COUNT = 1176
	SCREEN_HEIGHT = 20
	SCREEN_WIDTH = 40
	CH_WIDTH = 8
	CH_HEIGHT = 8

	IMAGE_WIDTH = (SCREEN_WIDTH + SECTOR_COUNT + SCREEN_WIDTH) * CH_WIDTH
	IMAGE_HEIGHT = SCREEN_HEIGHT * CH_HEIGHT

	def drawChar(xoffset,yoffset,ch,sector,color=None):
		if yoffset < 0:
			return
		for y in range(0,CH_HEIGHT):
			fontOffset = 0x3800 + ch * CH_HEIGHT + y
			if not color:
				for x in range(0,CH_WIDTH):
					col = (data[fontOffset] >> (8 - x // 2 * 2 - 2)) & 3
					if col == 0:
						col = 0 # BLACK
					elif col == 1:
						SECTOR_COLORS = (2,6,9,14,4,5)
						col = SECTOR_COLORS[sector]
					elif col == 2:
						col = 7 # YELLOW
					elif col == 3:
						col = 0 # UNUSED (BLACK)
					draw.point([(xoffset * CH_WIDTH + x, yoffset * CH_HEIGHT + y)], c64_rgb_colors[col])
			else:
				for x in range(0,CH_WIDTH):
					if (data[fontOffset] >> (7 - x)) & 1:
						draw.point([(xoffset * CH_WIDTH + x, yoffset * CH_HEIGHT + y)], color)

	img = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), color = 'black')
	draw = ImageDraw.Draw(img)

	# screen before sector 0 begins
	for columnOffset in range(0,SCREEN_WIDTH):
		drawChar(columnOffset,17,0x3B,0)
		drawChar(columnOffset,18,0x3C,0)
		drawChar(columnOffset,19,0x3C,0)

	# the sectors are following each other directly
	for columnOffset in range(0,SECTOR_COUNT):
		def drawColumn(columnOffset,columnCharOffset):
			if columnOffset > 1100:
				sector = 5
			elif columnOffset > 939:
				sector = 4
			elif columnOffset > 691:
				sector = 3
			elif columnOffset > 496:
				sector = 2
			elif columnOffset > 244:
				sector = 1
			else:
				sector = 0
			uoffset = UPPER_SECTOR_DATA + columnOffset * 2
			loffset = LOWER_SECTOR_DATA + columnOffset * 6

			if sector < 3:
				SECTOR_FILL_CHAR = 0x3C
			else:
				SECTOR_FILL_CHAR = 0x40

			# upper part of a column downwards
			for row in range(0,data[uoffset]):
				drawChar(columnCharOffset,row - 1,SECTOR_FILL_CHAR,sector)
			drawChar(columnCharOffset,data[uoffset] - 1,data[uoffset+1],sector)

			# lower part of a column upwards
			drawChar(columnCharOffset,SCREEN_HEIGHT - 1,SECTOR_FILL_CHAR,sector)
			for row in range(0,data[loffset]):
				drawChar(columnCharOffset,SCREEN_HEIGHT - 2 - row,SECTOR_FILL_CHAR,sector)
			drawChar(columnCharOffset,SCREEN_HEIGHT - 2 - data[loffset],data[loffset+1],sector)
			drawChar(columnCharOffset,SCREEN_HEIGHT - 2 - data[loffset] - 1,data[loffset+2],sector,c64_rgb_colors[data[loffset+3] & 0xF])
			drawChar(columnCharOffset,SCREEN_HEIGHT - 2 - data[loffset] - 2,data[loffset+4],sector,c64_rgb_colors[data[loffset+5] & 0xF])
		drawColumn(columnOffset,SCREEN_WIDTH + columnOffset)

	# after the end the last sector repeats before it restarts with sector 0
	REPEAT_END_CITY_OFFSET = 1101
	for columnOffset in range(REPEAT_END_CITY_OFFSET,SECTOR_COUNT):
		drawColumn(columnOffset,SCREEN_WIDTH + SECTOR_COUNT + columnOffset - REPEAT_END_CITY_OFFSET)

	img.save('sectors.png')

if False:
	drawSprites(0x3000,32,0x3000,True)
	drawSprites(0x8000,13,0x3000,True)

if False:
	drawFont(0x3800,0x00,0xbf,True)

if True:
	drawLevels()
