IDEAL
MODEL small
STACK 200h
DATASEG
	currentSize dw 10 
	selectedTool dw 0 ;0 - Draw, 1 - Erase, 2 - Sample, 3 - Fill      
	drawColour dw 0
	bgColour dw 0  
	selectedShape dw 0 ;0 - Square, 1 - Circle 
	mouseDriverErrorMsg db 'Error: mouse driver not found.',10,10,10,13,'Press any key to exit the programme...$'
	helpMenuFileName db 'helpmenu.bmp',0
	toolsFileName db 'tools1.bmp',0
	coloursFileName db 'colours1.bmp',0
	savingFileName db 'saving1.bmp',0
	menuFileName db 'menu.bmp',0 
	bgFileName db 'bg.bmp',0
	fileHandle dw ?
	fileHeader db 54 dup (0)
	palette db 256*4 dup (0)
	screenLine db 320 dup (0)
	errorMsg db 'Error: could not open the file', 13, 10,'$'
	saveFileNameBuffer db 1 dup ('e', 'x', 'p', 'o', 'r', 't', 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	promptSaveName db 'Enter a name (max 8): $'
	imgNotSavedMsg db 'Save failed or aborted...$'
	imgSavedMsg db 'File saved$'
	savedImagesHeaderTemplate db 1 dup (42h, 4dh, 0b6h, 0d8h, 0, 0, 0, 0, 0, 0, 36h, 4, 0, 0, 28h, 0, 0, 0, 40h, 1, 0, 0, 0aah, 0, 0, 0, 1, 0, 8, 0, 0, 0, 0, 0, 80h, 0d4h, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	highlightColour dw 0 
	normalToolColour dw 0 
	bottomLeftScreenMask db 320 * 9 dup (0)

	stdCursorOffset dw -1 				 ;Standard cursor hotspot offset 
					dw 15 
	stdBrushMask   dw 1111111111111100b  ;Screen mask 
				   dw 1111111111111000b
				   dw 1111111111110000b
				   dw 1111111111100001b
				   dw 1111111111000011b  
				   dw 1111111110000111b   
				   dw 1111111100001111b    
				   dw 1111111000011111b     
				   dw 1111110000111111b      
				   dw 1110000001111111b       
				   dw 1000000011111111b         
				   dw 1000000011111111b        
				   dw 0000000011111111b        
				   dw 0000000111111111b         
				   dw 0000000111111111b         
				   dw 0000001111111111b 
				   ;------------------;
				   dw 0000000000000000b  ;Mouse mask
				   dw 0000000000000010b   
				   dw 0000000000000110b    
				   dw 0000000000001100b
				   dw 0000000000011000b
				   dw 0000000000110000b
				   dw 0000000001100000b
				   dw 0000000011000000b
				   dw 0000000110000000b
				   dw 0000001100000000b
				   dw 0001111000000000b
				   dw 0011111000000000b
				   dw 0111111000000000b
				   dw 0111110000000000b
				   dw 0111100000000000b
				   dw 0000000000000000b
	ersToolMask dw 1111111111001111b		;Screen mask 
				dw 1111111110000111b
				dw 1111111100000011b
				dw 1111111000000001b
				dw 1111110000000000b
				dw 1111100000000000b
				dw 1111000000000000b
				dw 1110000000000001b
				dw 1100000000000011b
				dw 1000000000000111b
				dw 0000000000001111b
				dw 0000000000011111b
				dw 0000000000111111b
				dw 1000000001111111b
				dw 1100000011111111b
				dw 1110000111111111b
				;-----------------;
				dw 0000000000000000b		;Mouse mask 
				dw 0000000000000000b
				dw 0000000000000000b
				dw 0000000000000000b
				dw 0000000000000000b
				dw 0000000000000000b
				dw 0000000000000000b
				dw 0000000000000000b
				dw 0000000000000000b
				dw 0011100000000000b
				dw 0111110000000000b
				dw 0111111000000000b
				dw 0011111100000000b
				dw 0001111100000000b
				dw 0000111000000000b
				dw 0000000000000000b
	ersToolHotOffset dw 5 
					 dw 15 
	colourSampMask dw 1111111111110000b		;Screen mask 
				   dw 1111111111100000b
				   dw 1111111111000000b
				   dw 1111111110000000b
				   dw 1111111100000001b
				   dw 1111111000000011b
				   dw 1111110000000111b
				   dw 1111100000001111b
				   dw 1111000000011111b
				   dw 1111000000111111b
				   dw 1110000001111111b
				   dw 1100000011111111b
				   dw 1100001111111111b
				   dw 1000011111111111b
				   dw 0001111111111111b
				   dw 0011111111111111b
				   ;------------------;
				   dw 0000000000000000b		;Mouse mask 
				   dw 0000000000001110b
				   dw 0000000000011110b
				   dw 0000000000011110b
				   dw 0000000001001100b
				   dw 0000000011100000b
				   dw 0000000111110000b
				   dw 0000000011100000b
				   dw 0000011001000000b
				   dw 0000011100000000b
				   dw 0000111100000000b
				   dw 0001110000000000b
				   dw 0001100000000000b
				   dw 0010000000000000b
				   dw 0100000000000000b
				   dw 0000000000000000b
	fillToolMask dw 1111111100111111b		;Screen mask 
				 dw 1111111000011111b
				 dw 1111110000001111b
				 dw 1111100000000111b
				 dw 1111000000000011b
				 dw 1000000000000001b
				 dw 0000000000000000b
				 dw 0000000000000000b
				 dw 0000000000000000b
				 dw 0000000000000000b
				 dw 0000000000000000b
				 dw 0000100000000001b
				 dw 0001110000000011b
				 dw 1001111000000111b
				 dw 1111111100001111b
				 dw 1111111110011111b
				 ;------------------;
				 dw 0000000000000000b		;Mouse mask 
		       	 dw 0000000000000000b
				 dw 0000000011000000b
				 dw 0000000111100000b
				 dw 0000001111110000b
				 dw 0000011111111000b
				 dw 0000111111111100b
				 dw 0000111111111110b
				 dw 0000111111111110b
				 dw 0000011111111110b
				 dw 0000001111111100b
				 dw 0000000111111000b
				 dw 0000000011110000b
				 dw 0000000001100000b
				 dw 0000000000000000b
				 dw 0000000000000000b
	fillToolHotOffset dw 0
					  dw 13 
CODESEG  
proc DisplayImage
	;Displays an image on the entire screen (320 x 200 images only)
	;Order of parameters
	push bp 
	mov bp, sp 
	refFileName equ [bp + 14]
	refFileHandle equ [bp + 12]
	refFileHeader equ [bp + 10]
	refPalette equ [bp + 8] 
	refScreenLine equ [bp + 6]
	refErrorMsg equ [bp + 4]
	;Opens the file 
	push refFileName
	push refFileHandle
	push refErrorMsg
	call OpenFile
	;Reads the header 
	push refFileHandle
	push refFileHeader
	call ReadHeader
	;Reads the palette 
	push refPalette
	call ReadPalette
	;Copies the palette 
	push refPalette
	call CopyPal
	;Copies the bitmap 
	push refScreenLine
	push refFileHandle
	call CopyBitmap
	pop bp 
	ret 12 
endp DisplayImage
proc OpenFile
	;Opens the file and saves the handle 
	;Order of parameters: offset fileName, offset fileHandle, offset errorMessage
	push bp 
	mov bp, sp 
	fileNameParmRef equ [bp + 8] 
	fileHandleParmRef equ [bp + 6]
	errorMsgParmRef equ [bp + 4]
	mov ah, 3Dh
	xor al, al
	mov dx, fileNameParmRef
	int 21h
	jc openerror
	mov bx, fileHandleParmRef
	mov [word ptr bx], ax
	pop bp 
	ret 6 
	openerror:
	mov dx, errorMsgParmRef
	mov ah, 9h
	int 21h
	pop bp 
	ret 6 
endp OpenFile
proc ReadHeader
	;Reads the BMP file header 
	;Order of parameters: offset fileHandle, offset fileHeader 
	push bp 
	mov bp, sp 
	fileHandleParmRef equ [bp + 6]
	fileHeaderParmRef equ [bp + 4]  
	mov ah, 3fh
	mov bx, fileHandleParmRef
	mov bx, [word ptr bx]  
	mov cx, 54
	mov dx, fileHeaderParmRef
	int 21h
	pop bp 
	ret 4 
endp ReadHeader
proc ReadPalette
	;Reads the BMP file colour palette and saves it 
	;Order of parameters: offset palette
	push bp 
	mov bp, sp 
	paletteParmRef equ [bp + 4] 
	mov ah, 3fh
	mov cx, 400h
	mov dx, paletteParmRef
	int 21h
	pop bp 
	ret 2 
endp ReadPalette
proc CopyPal
	;Copies the colour palette to the memory of the graphics card 
	;Order of parameters: offset palette
	push bp 
	mov bp, sp 
	paletteParmRef equ [bp + 4]
	mov si, paletteParmRef
	mov cx, 256
	mov dx, 3C8h
	mov al, 0
	out dx, al
	inc dx
	PalLoop:
		mov al, [si+2]
		shr al, 2
		out dx, al 
		mov al, [si+1]
		shr al, 2
		out dx, al 
		mov al, [si] 
		shr al, 2
		out dx, al 
		add si, 4 
		loop PalLoop
	pop bp 
	ret 2 
endp CopyPal
proc CopyBitmap
	;Displays the image
	push bp 
	mov bp, sp 
	screenLineParmRef equ [bp + 6]
	fileHandleParmRef equ [bp + 4]  
	mov ax, 0A000h
	mov es, ax
	mov cx, 200
	PrintBMPLoop:
		push cx
		mov di, cx
		shl cx, 6
		shl di, 8
		add di, cx
		mov ah, 3fh
		mov cx, 320
		mov dx, screenLineParmRef
		int 21h
		cld 
		mov cx, 320
		mov si, screenLineParmRef
		rep movsb 
		pop cx
		loop PrintBMPLoop
	mov ah,3Eh
	mov bx, fileHandleParmRef
	mov bx, [word ptr bx] 
	int 21h
	pop bp 
	ret 4 
endp CopyBitmap
proc InitMouse
	push bp 
	mov bp, sp 
	doMaskParm equ [bp + 14] 
	setMouseXParm equ [bp + 12]
	setMouseYParm equ [bp + 10]
	mouseDriverErrorMsgParm equ [bp + 8]
	mouseMaskParm equ [bp + 6]
	mouseOffsetParm equ [bp + 4]
	;Resets the mouse 
	call ResetMouse
	;Sets the colour of the mouse 
	push 15 
	push 63 
	push 63   
	push 63 
	call SetColourAt
	;Checks if the mouse driver is missing 
	cmp ax, 0 
	je MouseDriverMissing
	mov ax, doMaskParm
	cmp ax, 1
	jne ConinueInitMouse
		;Sets the mask 
		push mouseOffsetParm
		push mouseMaskParm
		call SetMouseMask
	ConinueInitMouse:
		;Sets the mouse position 
		push setMouseXParm
		push setMouseYParm
		call SetMousePosition
		;Displays the mouse 
		call DisplayMouse
		pop bp 
		ret 12 
	MouseDriverMissing:
		call MouseDriverError
		pop bp 
		ret 12 
endp InitMouse 
proc ResetMouse
	;Resets the mouse 
	mov ax, 0 
	int 33h
	ret 
endp ResetMouse
proc SetColourAt
	;Sets the colour of the mouse 
	push bp 
	mov bp, sp 
	colourIndex equ [bp + 10] 
	rParm equ [bp + 8]
	gParm equ [bp + 6]
	bParm equ [bp + 4]
	mov dx, 3C8h
	mov ax, colourIndex
	out dx, al 
	inc dx 
	mov ax, rParm
	out dx, al
	mov ax, gParm
	out dx, al 
	mov ax, bParm
	out dx, al 
	pop bp 
	ret 8 
endp SetColourAt
proc MouseDriverError
	;Displays an error message and terminates the programme 
	push bp 
	mov bp, sp 
	mouseDriverErrorMsgParm equ [bp + 4] 
	mov dx, mouseDriverErrorMsgParm
	mov ah, 9 
	int 21h 
	mov ah, 1 
	int 21h 
	mov ax, 4c00h
	int 21h
	pop bp 
	ret 2  
endp MouseDriverError
proc SetMouseMask
	;Sets the mouse mask 
	push bp 
	mov bp, sp 
	mouseOffsetParm equ [bp + 6]
	mouseMaskParm equ [bp + 4]
	;Sets the mouse mask 
	mov bx, mouseOffsetParm
	mov cx, [bx + 2] 
	mov bx, [word ptr bx] 
	mov ax, ds 
	mov es, ax 
	mov ax, 9
    mov dx, mouseMaskParm
    int 33h
	pop bp 
	ret 4 
endp SetMouseMask
proc SetMousePosition 
	;Sets the position of the mouse 
	push bp 
	mov bp, sp 
	mouseSetX equ [bp + 6]
	mouseSetY equ [bp + 4]
	mov ax, 4 
	mov cx, mouseSetX
	mov dx, mouseSetY 
	int 33h 
	pop bp 
	ret 4 
endp SetMousePosition
proc DisplayMouse
	;Displays the mouse 
	mov ax, 1 
	int 33h 
	ret 
endp DisplayMouse
proc HideMouse
	;Hides the mouse 
	mov ax, 2 
	int 33h 
	ret 
endp HideMouse
proc MainProgramme
	;Waits for an input and acts accordingly 
	push bp 
	mov bp, sp 
	highlightColourParm equ [bp + 38]
	normalToolColourParm equ [bp + 36]
	imgPaletteParm equ [bp + 34] 
	savedImagesHeaderParm equ [bp + 32]
	bottomLeftScreenMaskSaveParm equ [bp + 30]
	imgSavedParm equ [bp + 28]
	selectedShapeParm equ [bp + 26]
	fillToolMaskParm equ [bp + 24]
	fillToolHotOffsetParm equ [bp + 22] 
	colourSampMaskParm equ [bp + 20]
	ersMaskParm equ [bp + 18]
	ersHotOffsetParm equ [bp + 16] 
	stdMaskParm equ [bp + 14] 
	stdHotOffsetParm equ [bp + 12] 
	currentSizeParm equ [bp + 10]  
	bgColourParm equ [bp + 8]
	drawColourParm equ [bp + 6]
	currentSelectedToolParm equ [bp + 4] 
	;Sets the draw colour 
	xor ax, ax 
	mov bx, drawColourParm
	mov [word ptr bx], ax 
	;Sets the tool 
	mov bx, currentSelectedToolParm
	mov [word ptr bx], ax 
	;Sets the shape 
	mov bx, selectedShapeParm
	mov [word ptr bx], ax 
	;Sets the size
	mov ax, 10
	mov bx, currentSizeParm
	mov [word ptr bx], ax 
	;Sets the bg colour
	push 1
	push 40
	push bgColourParm
	call ChangeColour
	;Sets the highlight and normal colours for tool buttons outline 
	push 131 
	push 6
	push highlightColourParm
	call ChangeColour
	push 151 
	push 6
	push normalToolColourParm
	call ChangeColour 
	call WaitForButtonRelease 
	WaitForInputLoop:
		mov ax, 3
		int 33h 
		;Checks if the left mouse button is clicked (+ otherwise, no mouse button was clicked, wait for an input)
		cmp bx, 1 
		jne WaitForInputLoop
		shr cx, 1 
		push highlightColourParm
		push normalToolColourParm
		push imgPaletteParm
		push savedImagesHeaderParm
		push bottomLeftScreenMaskSaveParm
		push imgSavedParm
		push selectedShapeParm
		push fillToolMaskParm
		push fillToolHotOffsetParm 
		push colourSampMaskParm
		push ersMaskParm
		push ersHotOffsetParm
		push stdMaskParm
		push stdHotOffsetParm 
		push currentSizeParm
		push cx ;Pushes the X
		push dx ;Pushes the Y
		push bgColourParm
		push drawColourParm
		push currentSelectedToolParm
		call Use 
		cmp ax, 1 
		je ExitMainProgramme
		jmp WaitForInputLoop
	ExitMainProgramme:
		pop bp 
		ret 36 
endp MainProgramme
proc Use 
	;Checks what the user has clicked on 
	push bp 
	mov bp, sp 
	highlightToolColourParm equ [bp + 42]
	normalToolColourParm equ [bp + 40] 
	paletteParm equ [bp + 38]
	savedImagesHeaderTemplateParm equ [bp + 36]
	bottomLeftScreenMaskParm equ [bp + 34]
	savedImgParm equ [bp + 32]
	currentShapeParm equ [bp + 30]
	bucketFillToolMaskParm equ [bp + 28] 
	bucketFillToolHotOffsetParm equ [bp + 26] 
	colourSampleMaskParm equ [bp + 24] 
    ersToolMaskParm equ [bp + 22]
	ersToolHotOffsetParm equ [bp + 20] 
	stdBrushMaskParm equ [bp + 18] 
	stdCursorHotOffsetParm equ [bp + 16]
	currSizeParm equ [bp + 14] 
	clickXParm equ [bp + 12]
	clickYParm equ [bp + 10]
	bgColParm equ [bp + 8]
	drawColParm equ [bp + 6] 
	currentToolParm equ [bp + 4] 
	mov cx, clickXParm 
	mov dx, clickYParm
	cmp dx, 29 ;Checks if the user has clicked on the GUI or not  
	jb OnGUI 
	mov bx, currentToolParm
	mov ax, [word ptr bx] 
	cmp ax, 2 
	je UsingSampleTool
	;If the user has not clicked on the GUI, draw 
	push currentShapeParm
	push clickXParm
	push clickYParm
	push currSizeParm
	push drawColParm
	push bgColParm
	push currentToolParm
	call Draw
	jmp ExitUseProc
	UsingSampleTool:	
		push clickXParm
		push clickYParm
		push drawColParm
		call ChangeColour
		push drawColParm
		call UpdateBucket
	ExitUseProc:
		xor ax, ax 
		pop bp 
		ret 40
	OnGUI: ;User has clicked on the GUI  
		push bgColParm
		push highlightToolColourParm
		push normalToolColourParm
		push paletteParm 
		push savedImagesHeaderTemplateParm
		push bottomLeftScreenMaskParm
		push savedImgParm
		push currentShapeParm
		push bucketFillToolMaskParm
		push bucketFillToolHotOffsetParm
		push colourSampleMaskParm
		push currentToolParm
		push ersToolMaskParm
		push ersToolHotOffsetParm
		push stdBrushMaskParm
		push stdCursorHotOffsetParm
		push clickXParm
		push clickYParm
		push currSizeParm
		push drawColParm
		call GUI 
		pop bp 
		ret 40 
endp Use  
proc Draw
	;Draws a square according to the current tool and colour 
	push bp 
	mov bp, sp 
	currentShapeParm equ [bp + 16] 
	clickXParm equ [bp + 14]
	clickYParm equ [bp + 12]
	currSizeParm equ [bp + 10]
	drawColParm equ [bp + 8]
	bgColParm equ [bp + 6]
	currentToolParm equ [bp + 4] 
	mov bx, currentToolParm
	mov ax, [word ptr bx] 
	cmp ax, 3 
	je UsingBucketFillTool1
	mov bx, currentToolParm
	mov ax, [word ptr bx]
	cmp ax, 0
	je UsingStdBrush 
	;Checks which shape is selected 
	mov bx, currentShapeParm
	mov ax, [word ptr bx] 
	cmp ax, 0 
	je UsingEraserSquare
	push 1 
	mov bx, bgColParm
	push [word ptr bx]
	push clickXParm
	push clickYParm
	mov bx, currSizeParm
	push [word ptr bx] 
	call CircleProc
	push 1
	call WaitTicks
	pop bp 
	ret 14
	UsingEraserSquare:
		push clickXParm
		push clickYParm
		mov bx, currSizeParm
		push [word ptr bx]
		mov bx, bgColParm
		mov ax, [word ptr bx] 
		push ax 
		call DrawSquare
		pop bp 
		ret 14 
	UsingBucketFillTool1:
		jmp UsingBucketFillTool
	UsingStdBrush:	
		;Checks which shape is selected 
		mov bx, currentShapeParm
		mov ax, [word ptr bx] 
		cmp ax, 0 
		je UsingStdBrushSquare
		;Using the circle 
		push 1 
		mov bx, drawColParm
		push [word ptr bx] 
		push clickXParm
		push clickYParm
		mov bx, currSizeParm
		push [word ptr bx] 
		call CircleProc
		push 1
		call WaitTicks
		pop bp 
		ret 14
		UsingStdBrushSquare:
			push clickXParm
			push clickYParm
			mov bx, currSizeParm
			push [word ptr bx]
			mov bx, drawColParm
			mov ax, [word ptr bx] 
			push ax 
			call DrawSquare
			pop bp 
			ret 14 
	UsingBucketFillTool:
		mov ax, clickYParm
		cmp ax, 29 
		je ExitDrawProc
		push bgColParm
		mov bx, currSizeParm
		push [word ptr bx]  
		push clickXParm
		push clickYParm
		mov bx, drawColParm
		push [word ptr bx] 
		call BucketFill
		ExitDrawProc:
			pop bp 
			ret 14
endp Draw
proc WaitTicks
	;Waits a certain amount of ticks 
	push bp 
	mov bp, sp
	amountToWait equ [bp + 4] 
	Clock equ es:6Ch
	mov ax, 40h 
	mov es, ax 
	mov ax, [Clock]
	mov cx, amountToWait
	WaitTicksLoop:
		cmp ax, [Clock]
		je WaitTicksLoop
		mov ax, [Clock] 
		loop WaitTicksLoop
	pop bp 
	ret 2
endp WaitTicks 
proc DrawSquare
	;Draws a square at the location of the mouse 
	push bp 
	mov bp, sp 
	sub sp, 2 
	clickXParm equ [bp + 10]
	clickYParm equ [bp + 8]
	sideSizeParm equ [bp + 6]
	drawColourParm equ [bp + 4]
	localClickXParm equ [bp - 2]
	mov cx, clickYParm
	inc cx 
	mov clickYParm, cx 
	mov cx, sideSizeParm
	DrawSquareLoop:
		push cx 
		mov cx, clickXParm
		mov localClickXParm, cx 
		mov cx, sideSizeParm
		DrawLineLoop:
			push cx 
			mov ax, drawColourParm 
			mov ah, 0Ch 
			mov bh, 0 
			mov cx, localClickXParm
			mov dx, clickYParm
			int 10h 
			inc cx
			mov localClickXParm, cx 
			cmp cx, 319  
			ja SquareEndOfLine
			jmp ContinueSquareLineLoop
			SquareEndOfLine:
				pop cx 
				jmp ExitDrawSquareLineLoop
			ContinueSquareLineLoop:
				pop cx 
				loop DrawLineLoop
		ExitDrawSquareLineLoop:
			mov cx, clickYParm
			inc cx 
			cmp cx, 199 
			ja QuitDrawSquareLoop
			mov clickYParm, cx 
			pop cx 
			loop DrawSquareLoop
		add sp, 2 
		pop bp 
		ret 8 
	QuitDrawSquareLoop:
		add sp, 4 
		pop bp 
		ret 8
endp DrawSquare
proc GUI 
	;Checks which part of the GUI was clicked 
	push bp 
	mov bp, sp 
	bgColParm equ [bp + 42] 
	highlightToolColourParm equ [bp + 40] 
	normalToolColourParm equ [bp + 38]
	paletteParm equ [bp + 36]
	savedImagesHeaderTemplateParm equ [bp + 34]
	bottomLeftScreenMaskParm equ [bp + 32]
	savedImgParm equ [bp + 30]
	currentShapeParm equ [bp + 28] 
	bucketFillToolMaskParm equ [bp + 26]
	bucketFillToolHotOffsetParm equ [bp + 24]
	colourSampleMaskParm equ [bp + 22]
	selectedToolParm equ [bp + 20]
    ersToolMaskParm equ [bp + 18]
	ersToolHotOffsetParm equ [bp + 16] 
	stdBrushMaskParm equ [bp + 14] 
	stdCursorHotOffsetParm equ [bp + 12] 
	clickXParm equ [bp + 10]
	clickYParm equ [bp + 8]
	currSizeParm equ [bp + 6] 
	drawColParm equ [bp + 4] 
	mov cx, clickXParm 
	cmp cx, 128   
	ja NotColourPicker 
	mov dx, clickYParm
	cmp dx, 24  
	ja NotColourPicker
	mov bx, selectedToolParm
	push [word ptr bx] 
	push clickXParm
	push clickYParm
	push drawColParm
	call ColourPicker  
	xor ax, ax 
	jmp ExitGUIProc1
	NotColourPicker:
		cmp cx, 289  
		jb CheckSave 
		push 290
		push 1 
		call GetColourAt
		push ax 
		push clickXParm
		push clickYParm
		call GetColourAt
		mov cx, ax 
		pop ax 
		cmp ax, cx 
		je ExitGUIProc1
		mov ax, 1  
		ExitGUIProc1:
			pop bp 
			ret 40
		CheckSave:
			cmp cx, 256
			jb OnTools
			push 257 
			push 1 
			call GetColourAt
			push ax 
			push clickXParm
			push clickYParm
			call GetColourAt
			mov cx, ax 
			pop ax 
			cmp ax, cx 
			je ExitGUIProc
			;Saves the image 
			push bottomLeftScreenMaskParm
			push savedImagesHeaderTemplateParm 
			push savedImgParm
			push paletteParm
			call SaveImage  
			jmp ExitGUIProc
		OnTools:
			push drawColParm
			push bgColParm
			push highlightToolColourParm
			push normalToolColourParm
			push currentShapeParm
			push bucketFillToolMaskParm
			push bucketFillToolHotOffsetParm
			push colourSampleMaskParm
			push selectedToolParm   
			push ersToolMaskParm 
			push ersToolHotOffsetParm   
			push stdBrushMaskParm
			push stdCursorHotOffsetParm 
			push clickXParm
			push clickYParm
			push currSizeParm
			call Tools 
	ExitGUIProc:
		xor ax, ax 
		pop bp 
		ret 40 
endp GUI 
proc ColourPicker
	;Allows the user to switch between colours and get a visual representation 
	push bp
	mov bp, sp 
	currentToolParm equ [bp + 10] 
	clickXParm equ [bp + 8]
	clickYParm equ [bp + 6]
	drawColParm equ [bp + 4]
	;Checks if actually on a colour 
	mov cx, clickXParm
	cmp cx, 112
	ja ExitColourPickerProc
	cmp cx, 2 
	jb ExitColourPickerProc
	mov dx, clickYParm 
	cmp dx, 2 
	jb ExitColourPickerProc
	;Checks if on borders 
	push clickXParm
	push clickYParm
	call GetColourAt
	cmp al, 0 
	je CheckCoordinates 
	push clickXParm
	push clickYParm
	push drawColParm
	call ChangeColour
	mov ax, currentToolParm
	cmp ax, 1
	je ExitColourPickerProc 
	jmp ContinueColourPickerProc
	CheckCoordinates:
		cmp cx, 12
		ja ExitColourPickerProc
		cmp cx, 3 
		jb ExitColourPickerProc
		cmp dx, 15 
		jb ExitColourPickerProc
		cmp dx, 24 
		ja ExitColourPickerProc
		push clickXParm
		push clickYParm
		push drawColParm
		call ChangeColour
		mov ax, currentToolParm
		cmp ax, 1
		je ExitColourPickerProc 
	ContinueColourPickerProc:
		;Updates the bucket to the now chosen colour  
		mov cx, clickXParm
		cmp cx, 100 
		jb ContniueColourPicker 
		call HideMouse
		push drawColParm
		call UpdateBucket
		call DisplayMouse
		jmp ExitColourPickerProc
		ContniueColourPicker:
			push drawColParm
			call UpdateBucket
		ExitColourPickerProc:
			pop bp 
			ret 8
endp ColourPicker 
proc UpdateBucket
	;Updates the bucket to display the current colour 
	push bp 
	mov bp, sp 
	sub sp, 6 
	bucketColourParm equ [bp + 4] 
	currentLocalX equ [bp - 2]
	currentLocalY equ [bp - 4]
	bucketColourLocal equ [bp - 6]
	;Gets the colour of the bucket 
	push 117
	push 12
	call GetColourAt
	xor ah, ah 
	mov bucketColourLocal, ax 
	;Sets the initial Y value  
	mov ax, 12  
	mov currentLocalY, ax 
	mov cx, 8 
	OuterUpdateBucketLoop:
		push cx 
		mov ax, 117 
		mov currentLocalX, ax 
		mov cx, 8 
		InnerUpdateBucketLoop:
			push cx 
			;Checks if on bucket or paint 
			push currentLocalX
			push currentLocalY
			call GetColourAt
			mov bx, bucketColourLocal
			cmp al, bl 
			je NotPaintPixel
			;On paint pixel, colour it 
			mov bx, bucketColourParm
			push [word ptr bx]
			push currentLocalX
			push currentLocalY 
			call PaintPixelAt
			NotPaintPixel:
				mov ax, currentLocalX
				inc ax 
				mov currentLocalX, ax 
				pop cx 
				loop InnerUpdateBucketLoop
		mov ax, currentLocalY
		inc ax 
		mov currentLocalY, ax 
		pop cx 
		loop OuterUpdateBucketLoop
	add sp, 6
	pop bp 
	ret 2
endp UpdateBucket
proc Tools
	;Checks which button was pressed 
	push bp 
	mov bp, sp 
	drawColParm equ [bp + 34]
	bgColParm equ [bp + 32]
	highlightToolColourParm equ [bp + 30]
	normalToolColourParm equ [bp + 28]
	currentShapeParm equ [bp + 26] 
	bucketFillToolMaskParm equ [bp + 24]
	bucketFillToolHotOffsetParm equ [bp + 22]
	colourSampleMaskParm equ [bp + 20]
    selectedToolParm equ [bp + 18] 
    ersToolMaskParm equ [bp + 16] 
	ersToolHotOffsetParm equ [bp + 14]  
	stdBrushMaskParm equ [bp + 12] 
	stdCursorHotOffsetParm equ [bp + 10] 
	clickXParm equ [bp + 8]
	clickYParm equ [bp + 6] 
	currSizeParm equ [bp + 4] 
	mov cx, clickXParm
	cmp cx, 242 
	ja OnScaleButtons 
	cmp cx, 227  
	ja ExitToolsProc
	cmp cx, 213
	ja OnShapeButtons
	;Checks which tool was pressed 
	push drawColParm
	push bgColParm
	push highlightToolColourParm
	push normalToolColourParm
	push bucketFillToolMaskParm
	push bucketFillToolHotOffsetParm
	push colourSampleMaskParm 
	push clickXParm
	push clickYParm
	push selectedToolParm 
	push ersToolMaskParm 
	push ersToolHotOffsetParm
	push stdBrushMaskParm 
	push stdCursorHotOffsetParm 
	call SelectTool 
	jmp ExitToolsProc
	OnShapeButtons:
		;On the shape button 
		push highlightToolColourParm
		push normalToolColourParm
		push currentShapeParm
		push clickYParm
		call SelectShape
		jmp ExitToolsProc
	OnScaleButtons:
		;On the scale buttons 
		cmp cx, 256
		ja ExitToolsProc
		push clickYParm
		push currSizeParm
		call ScaleButtons
	ExitToolsProc:
		pop bp 
		ret 32  
endp Tools
proc SelectShape 
	;Selects a shape according to the position at which the user has clicked 
	push bp 
	mov bp, sp 
	highlightToolColourParm equ [bp + 10]
	normalToolColourParm equ [bp + 8]
	currentShapeParm equ [bp + 6]
	clickYParm equ [bp + 4]
	call HideMouse
	mov ax, clickYParm
	cmp ax, 13 
	ja OnCircleButton
	;On square button 
	xor ax, ax 
	mov bx, currentShapeParm
	mov [word ptr bx], ax
	;Deselects the circle 
	push 0 
	mov bx, normalToolColourParm
	push [word ptr bx]
	push 215
	push 15 
	push 5 
	call CircleProc
	;Selects the square 
	push 4
	push 11
	mov bx, highlightToolColourParm
	push [word ptr bx]
	call DrawHollowSquare
	call DisplayMouse
	pop bp 
	ret 8
	OnCircleButton:
		;On circle button 
		mov ax, 1 
		mov bx, currentShapeParm
		mov [word ptr bx], ax 
		;Deselect the square 
		push 4
		push 11
		mov bx, normalToolColourParm
		push [word ptr bx]
		call DrawHollowSquare
		;Selects the circle 
		push 0 
		mov bx, highlightToolColourParm
		push [word ptr bx] 
		push 215
		push 15 
		push 5 
		call CircleProc
		call DisplayMouse
		pop bp 
		ret 8
endp SelectShape	
proc SelectTool
	push bp 
	mov bp, sp 
	drawColParm equ [bp + 30]
	bgColParm equ [bp + 28]
	highlightToolColourParm equ [bp + 26]
	normalToolColourParm equ [bp + 24]
	bucketFillToolMaskParm equ [bp + 22] 
	bucketFillToolHotOffsetParm equ [bp + 20]  
	colourSampleMaskParm equ [bp + 18]
	clickXParm equ [bp + 16]
	clickYParm equ [bp + 14]
	selectedToolParm equ [bp + 12] 
	ersToolMaskParm equ [bp + 10]
	ersToolHotOffsetParm equ [bp + 8] 
	stdBrushMaskParm equ [bp + 6]
	stdCursorHotOffsetParm equ [bp + 4]
	mov dx, clickYParm
	cmp dx, 5 
	jb ExitSelecToolProc1
	cmp dx, 22
	ja ExitSelecToolProc1
			mov cx, clickXParm
		cmp cx, 208 
		ja ExitSelecToolProc1
		cmp cx, 130   
		jb ExitSelecToolProc1
	jmp ContinueCheckTools 
	ExitSelecToolProc1:
		pop bp 
		ret 28
	ContinueCheckTools:
		mov bx, selectedToolParm
		mov ax, [word ptr bx] 
		;Checks which button was pressed 
		cmp cx, 148
		jb OnBrushToolButton 
		cmp cx, 190
		ja OnFillToolButton
		cmp cx, 188 
		ja ExitSelecToolProc1
		cmp cx, 170
		ja OnSampleToolButton
		cmp cx, 168 
		ja ExitSelecToolProc1
		cmp cx, 150 
		jb ExitSelecToolProc1
		;On ersToolButton
		cmp ax, 1
		je ExitSelecToolProc1
		push bgColParm
		call UpdateBucket
		push 1 
		push ersToolMaskParm
		push ersToolHotOffsetParm
		jmp ChangeToolLabel
		OnFillToolButton:
			;On fillToolButton 
			cmp ax, 3 
			je ExitSelecToolProc
			push drawColParm
			call UpdateBucket
			push 3 
			push bucketFillToolMaskParm
			push bucketFillToolHotOffsetParm
			jmp changeToolLabel
		OnBrushToolButton:
			;On stdBrushToolButton 
			cmp ax, 0 
			je ExitSelecToolProc
			push drawColParm
			call UpdateBucket
			push 0 
			push stdBrushMaskParm
			push stdCursorHotOffsetParm
			jmp ChangeToolLabel
		OnSampleToolButton: 	
			;On sampleToolButton  
			cmp ax, 2   
			je ExitSelecToolProc
			push 2 
			push colourSampleMaskParm
			push stdCursorHotOffsetParm 
		ChangeToolLabel:
			push selectedToolParm
			push clickXParm
			push clickYParm
			push highlightToolColourParm
			push normalToolColourParm
			call ChangeTool
		ExitSelecToolProc:
			pop bp 
			ret 28
endp SelectTool
proc ChangeTool  
	;Changes the tool 
	push bp 
	mov bp, sp 
	toolNumberParm equ [bp + 18]
	toolMaskParm equ [bp + 16]
	toolHotOffsetParm equ [bp + 14]
	selectedToolParm equ [bp + 12]
	mouseX equ [bp + 10]
	mouseY equ [bp + 8]
	highlightToolColourParm equ [bp + 6] 
	normalToolColourParm equ [bp + 4]
	call HideMouse
	;Colours the previous tool outline 
	mov bx, selectedToolParm
	push [word ptr bx] 
	push 18
	mov bx, normalToolColourParm
	push [word ptr bx] 
	call DrawHollowSquare
	;Updates the tool 
	mov bx, selectedToolParm
	mov ax, toolNumberParm
	mov [word ptr bx], ax 
	;Colours the tool button outline 
	push toolNumberParm
	push 18 
	mov bx, highlightToolColourParm
	push  [word ptr bx]
	call DrawHollowSquare
	;Updates the mouse mask 
	push 1 
	mov ax, mouseX
	shl ax, 1 
	push ax 
	push mouseY
	push offset mouseDriverErrorMsg
	push toolMaskParm
	push toolHotOffsetParm
	call InitMouse
	pop bp 
	ret 16 
endp ChangeTool 
proc ScaleButtons
	push bp 
	mov bp, sp
	clickYParm equ [bp + 6] 
	currSizeParm equ [bp + 4] 
	mov bx, currSizeParm
	mov ax, [word ptr bx] 
	mov cx, clickYParm
	cmp cx, 15 
	ja DecScale
	cmp ax, 20 
	jae ExitScaleButtons
	inc ax 	
	mov [word ptr bx], ax 
	push currSizeParm
	call UpdateScaleBar
	jmp ExitScaleButtons
	DecScale:
		cmp ax, 1 
		jbe ExitScaleButtons
		dec ax 		
		mov [word ptr bx], ax 
		push currSizeParm
		call UpdateScaleBar
	ExitScaleButtons:
		push 3 
		call WaitTicks
		pop bp 
		ret 4 
endp ScaleButtons
proc UpdateScaleBar
	push bp 
	mov bp, sp 
	sub sp, 4 
	currSizeParm equ [bp + 4] 
	localCurrentX equ [bp - 2] 
	localCurerntY equ [bp - 4]
	call HideMouse
	mov bx, currSizeParm
	mov cx, [word ptr bx] 
	mov ax, 23 
	mov localCurerntY, ax 
	ColourScaleBarLoop:
		push cx 
		mov ax, 236 
		mov localCurrentX, ax 
		mov cx, 5 
		ScaleBarLineLoop:
			push cx 
			push localCurrentX
			push localCurerntY
			push 1 
			push 'r'
			call DrawSquare
			mov ax, localCurrentX 
			inc ax 
			mov localCurrentX, ax 
			pop cx 
			loop ScaleBarLineLoop
		mov ax, localCurerntY
		dec ax 
		mov localCurerntY, ax 
		pop cx 
		loop ColourScaleBarLoop
	mov bx, currSizeParm
	mov cx, 20 
	mov ax, [word ptr bx] 
	sub cx, ax 
	cmp cx, 0 
	je ExitUpdateBarProc
	ClearScaleBarLoop:
		push cx 
		mov ax, 236 
		mov localCurrentX, ax 
		mov cx, 5 
		ScaleBarClearLoop:
			push cx 
			push localCurrentX
			push localCurerntY
			push 1 
			push 0
			call DrawSquare
			mov ax, localCurrentX 
			inc ax 
			mov localCurrentX, ax 
			pop cx 
			loop ScaleBarClearLoop
		mov ax, localCurerntY
		dec ax 
		mov localCurerntY, ax 
		pop cx 
		loop ClearScaleBarLoop
	ExitUpdateBarProc:
		call DisplayMouse
		add sp, 4 
		pop bp 
		ret 2 
endp UpdateScaleBar
proc ChangeColour
	;Changes the colour to the colour the mouse is hovering over 
	push bp 
	mov bp, sp
	clickXParm equ [bp + 8] 
	clickYParm equ [bp + 6] 
	changeColourParm equ [bp + 4] 
	mov cx, clickXParm 
	mov dx, clickYParm
	mov bh, 0h
	mov ah, 0Dh
	int 10h
	xor ah, ah 
	mov bx, changeColourParm
	mov [word ptr bx], ax 
	pop bp 
	ret 6 
endp ChangeColour
proc ColourEntireCanvas
	;Colours the entire canvas with a single colour 
	push bp 
	mov bp, sp 
	sub sp, 4 
	colourParm equ [bp + 4] 
	currentXLocal equ [bp - 2]
	currentYLocal equ [bp - 4]
	mov ax, 30 
	mov currentYLocal, ax 
	mov cx, 170 
	OuterColourCanvasLoop:
		push cx 
		mov ax, 0 
		mov currentXLocal, ax 
		mov cx, 320 
		InnerColourCanvasLoop:
			push cx 
			;Colours the pixel 
			mov cx, currentXLocal
			mov dx, currentYLocal
			mov ax, colourParm
			mov ah, 0Ch 
			mov bh, 0 
			int 10h 
			mov ax, currentXLocal
			inc ax 
			mov currentXLocal, ax 
			pop cx 
			loop InnerColourCanvasLoop
		mov ax, currentYLocal
		inc ax 
		mov currentYLocal, ax 
		pop cx 
		loop OuterColourCanvasLoop
	add sp, 4 
	pop bp 
	ret 2
endp ColourEntireCanvas 
proc BucketFill 
	;Colours the entire screen with one colour 
	push bp 
	mov bp, sp 
	sub sp, 2
	bgColParm equ [bp + 12]
	currentToolSizeParm equ [bp + 10] 
	mouseX equ [bp + 8]
	mouseY equ [bp + 6]
	colourParm equ [bp + 4] 
	colourToReplace equ [bp - 2]
	;Checks if already on colour 
	push mouseX 
	push mouseY
	call GetColourAt
	mov bx, colourParm
	cmp bl, al 
	jne ContinueBucketFillProc 
	add sp, 2
	pop bp 
	ret 10
	ContinueBucketFillProc:
		call HideMouse
		;Checks if using maximum tool size 
		mov ax, currentToolSizeParm
		cmp ax, 20 
		jne NotMaximumToolSize 
		;Using the maximum tool size, colour the entire screen 
		mov bx, bgColParm
		mov ax, colourParm
		mov [word ptr bx], ax 
		push colourParm 
		call ColourEntireCanvas
		jmp ReInitMouse
		NotMaximumToolSize:
			;Gets the colour at the pixel the user has pressed 
			push mouseX
			push mouseY
			call GetColourAt
			xor ah, ah 
			mov colourToReplace, ax 
			;Marks the original pixel 
			push mouseX
			push mouseY
			call MarkPixel
			MarkSelection:
				push colourToReplace
				call CheckFromTopLeft
				push colourToReplace
				call CheckFromBottomRight
				cmp ax, 1
				je MarkSelection
			;Changes to the actual colour 
			push 0 
			push 30 
			push 320 
			push 170 
			push colourParm
			call ColourMarkedArea
		ReInitMouse:
			call DisplayMouse
			add sp, 2
			pop bp 
			ret 10
endp BucketFill 
proc ColourMarkedArea 
	;Colours all the marked pixels 
	push bp 
	mov bp, sp 
	sub sp, 2
	startXParm equ [bp + 12]
	startYParm equ [bp + 10]
	amountXParm equ [bp + 8]
	amountYParm equ [bp + 6]
	finalColourParm equ [bp + 4] 
	currentXLocal equ [bp - 2]
	mov cx, amountYParm
	OuterColourAreaLoop:
		push cx 
		mov ax, startXParm 
		mov currentXLocal, ax 
		mov cx, amountXParm
		InnerColourAreaLoop:
			push cx 
			push currentXLocal
			push startYParm
			call GetColourAt
			cmp al, 125 
			jne NotSpecialColour
			mov ax, finalColourParm
			mov ah, 0Ch 
			mov bh, 0 
			mov cx, currentXLocal
			mov dx, startYParm
			int 10h
			NotSpecialColour:
				mov ax, currentXLocal
				inc ax 
				mov currentXLocal, ax 
				pop cx 
				loop InnerColourAreaLoop
		mov ax, startYParm
		inc ax 
		mov startYParm, ax 
		pop cx 
		loop OuterColourAreaLoop
	add sp, 2
	pop bp 
	ret 10 
endp ColourMarkedArea
proc CheckFromTopLeft 
	;Checks the canvas from left to right, top to bottom to see if any pixel is next to any pixel of the "special" colour
	push bp 
	mov bp, sp
	sub sp, 4
	originalColour equ [bp + 4]
	currentLocalX equ [bp - 2]
	currentLocalY equ [bp - 4]
	;Sets the initial X and Y coordinates 
	mov ax, 0 
	mov currentLocalX, ax 
	mov ax, 30 
	mov currentLocalY, ax 
	mov cx, 170 
	OuterLeftToRightLoop:
		push cx 
		mov ax, 0 
		mov currentLocalX, ax 
		mov cx, 320 
		InnerLeftToRightLoop:
			push cx 
			;Checks if already pointing to "special" colour
			push currentLocalX
			push currentLocalY
			call GetColourAt
			mov bx, originalColour
			cmp al, bl
			jne NoNearSpecialFound1
			cmp al, 125 
			je NoNearSpecialFound1
			;Checks to the left 
			mov cx, currentLocalX
			cmp cx, 0 
			je CheckAbovePixel
			dec cx 
			push cx 
			push currentLocalY
			call GetColourAt
			cmp al, 125 
			je FoundSpecialPixel1
			CheckAbovePixel:
				;Checks above 
				mov dx, localCurerntY
				cmp cx, 30 
				je NoNearSpecialFound1
				push localCurrentX
				dec dx 
				push dx 
				call GetColourAt
				cmp al, 125 
				jne NoNearSpecialFound1
			FoundSpecialPixel1:
				;Found a special pixel 
				push localCurrentX
				push localCurerntY
				call MarkPixel 
			NoNearSpecialFound1:
				mov ax, currentLocalX
				inc ax 
				mov currentLocalX, ax 
				pop cx 
				loop InnerLeftToRightLoop
		mov ax, currentLocalY
		inc ax 
		mov currentLocalY, ax 
		pop cx 
		loop OuterLeftToRightLoop
	add sp, 4 
	pop bp 
	ret 2
endp CheckFromTopLeft
proc CheckFromBottomRight 
	;Checks the canvas from right to left, bottom to top to see if any pixel is next to any pixel of the "special" colour
	push bp 
	mov bp, sp 
	sub sp, 6 
	originalColour equ [bp + 4]
	currentLocalX equ [bp - 2]
	currentLocalY equ [bp - 4]
	changesMade equ [bp - 6]
	mov ax, 0 
	mov changesMade, ax 
	;Sets the initial X and Y coordinates 
	mov ax, 319
	mov currentLocalX, ax 
	mov ax, 199 
	mov currentLocalY, ax 
	mov cx, 170 
	OuterRightToLeftLoop:
		push cx 
		mov ax, 319
		mov currentLocalX, ax 
		mov cx, 320 
		InnerRightToLeftLoop:
		push cx 
			;Checks if already pointing to "special" colour
			push currentLocalX
			push currentLocalY
			call GetColourAt
			mov bx, originalColour
			cmp al, bl
			jne NoNearSpecialFound2
			cmp al, 125 
			je NoNearSpecialFound2
			;Checks to the right
			mov cx, currentLocalX
			cmp cx, 319  
			je CheckBelowPixel
			inc cx 
			push cx 
			push currentLocalY
			call GetColourAt
			cmp al, 125 
			je FoundSpecialPixel2
			CheckBelowPixel:
				;Checks below
				mov dx, localCurerntY
				cmp cx, 199 
				je NoNearSpecialFound2
				push localCurrentX
				inc dx 
				push dx 
				call GetColourAt
				cmp al, 125 
				jne NoNearSpecialFound2
			FoundSpecialPixel2:
				;Found a special pixel 
				push localCurrentX
				push localCurerntY
				call MarkPixel 
				mov ax, 1 
				mov changesMade, ax 
			NoNearSpecialFound2:
				mov ax, currentLocalX
				dec ax 
				mov currentLocalX, ax 
				pop cx 
				loop InnerRightToLeftLoop
		mov ax, currentLocalY
		dec ax 
		mov currentLocalY, ax 
		pop cx 
		loop OuterRightToLeftLoop
	mov ax, changesMade
	add sp, 6
	pop bp 
	ret 2
endp CheckFromBottomRight
proc MarkPixel
	;Marks the pixel with the "special" colour 
	push bp 
	mov bp, sp 
	xParm equ [bp + 6]
	yParm equ [bp + 4]
	mov al, 125
	mov ah, 0Ch 
	mov bh, 0 
	mov cx, xParm
	mov dx, yParm
	int 10h
	mov ax, 1 
	pop bp 
	ret 4 
endp MarkPixel
proc GetColourAt
	;Gets the colour at a certain coordinate 
	push bp 
	mov bp, sp 
	xCoordinate equ [bp + 6]
	yCoordinate equ [bp + 4]
	mov cx, xCoordinate
	mov dx, yCoordinate
	mov bh, 0
	mov ah, 0Dh
	int 10h
	pop bp 
	ret 4 
endp GetColourAt
proc Compare
	;Compares 3 points to see which is closest to being on the circle 
	push bp 
	mov bp, sp
	sub sp, 6 
	radiusParm equ [bp + 16]
	x1Parm equ [bp + 14]
	y1Parm equ [bp + 12]
	x2Parm equ [bp + 10]
	y2Parm equ [bp + 8]
	x3Parm equ [bp + 6]
	y3Parm equ [bp + 4]
	distance1 equ [bp - 2] 
	distance2 equ [bp - 4]
	distance3 equ [bp - 6]
	;Calculates the distance of the first point 
	push radiusParm
	push x1Parm
	push y1Parm
	call CalcDistance
	mov distance1, cx 
	;Calculates the distance of the second point 
	push radiusParm
	push x2Parm
	push y2Parm
	call CalcDistance
	mov distance2, cx 
	;Calculates the distance of the third point 
	push radiusParm
	push x3Parm
	push y3Parm
	call CalcDistance
	mov distance3, cx 
	;Checks which is the closest to the circle 
	mov ax, distance1
	mov bx, distance2
	mov cx, distance3
	cmp ax, bx 
	jb d1Smaller
	cmp bx, cx 
	jb d2Smallest
	jmp d3Smallest
	d1Smaller:
		cmp ax, cx 
		jb d1Smallest 
	d3Smallest:
		mov ax, x3Parm
		mov bx, y3Parm
		jmp ExitCompareProc
	d1Smallest:
		mov ax, x1Parm
		mov bx, y1Parm
		jmp ExitCompareProc
	d2Smallest:
		mov ax, x2Parm
		mov bx, y2Parm
	ExitCompareProc:
		add sp, 6 
		pop bp 
		ret 14 
endp Compare 
proc CalcDistance
	;Calculates the distance from the circle 
	push bp 
	mov bp, sp 
	rParm equ [bp + 8]
	xParm equ [bp + 6]
	yParm equ [bp + 4]
	push xParm
	push 2 
	call Power
	mov cx, ax 
	push yParm
	push 2 
	call Power
	add cx, ax 
	push rParm
	push 2
	call Power
	cmp ax, cx 
	ja RadiusBigger 
	sub cx, ax 
	pop bp 
	ret 6 
	RadiusBigger:
		sub ax, cx 
		mov cx, ax 
		pop bp 
		ret 6
endp CalcDistance
proc Power 
	;Raises a number to a certain power 
	push bp 
	mov bp, sp
	baseParm equ [bp + 6]
	extenderParm equ [bp + 4]
	push cx 
	push bx 
	mov cx, extenderParm
	mov ax, 1
	mov bx, baseParm
	PowerLoop:
		mul bx 
		loop PowerLoop
	pop bx 
	pop cx 
	pop bp 
	ret 4 
endp Power 
proc CircleProc 
	;Calculates all the points for a quarter of a circle 
	push bp 
	mov bp, sp 
	sub sp, 4 
	boolFillCircle equ [bp + 12] 
	colourParm equ [bp + 10] 
	xOffsetParm equ [bp + 8] 
	yOffsetParm equ [bp + 6]
	circleRariusParm equ [bp + 4]
	currentXLocal equ [bp - 2]
	currentYLocal equ [bp - 4]
	;Sets the offsets 
	mov ax, xOffsetParm
	add ax, circleRariusParm
	mov xOffsetParm, ax 
	mov ax, yOffsetParm
	add ax, circleRariusParm
	inc ax 
	mov yOffsetParm, ax 
	;Sets the initial X and Y 
	xor ax, ax 
	mov currentXLocal, ax 
	mov ax, circleRariusParm
	mov currentYLocal, ax 
	;Points the two "stubborn" pixels 
	push 125
	mov ax, currentXLocal
	add ax, xOffsetParm
	push ax 
	mov ax, currentYLocal
	add ax, yOffsetParm
	push ax 
	call PaintPixelAt
	push 125
	mov ax, currentXLocal
	add ax, xOffsetParm
	push ax 
	mov ax, currentYLocal
	add ax, yOffsetParm
	sub ax, circleRariusParm
	sub ax, circleRariusParm
	push ax 
	call PaintPixelAt
	;Calculates the points 
	CalculatePoints: 
		mov ax, currentXLocal
		mov bx, currentYLocal
		push circleRariusParm
		inc ax 
		push ax 
		push bx 
		push ax 
		dec bx 
		push bx 
		dec ax 
		push ax 
		push bx 
		call Compare
		push 125
		mov currentXLocal, ax 
		mov currentYLocal, bx 
		push xOffsetParm
		push yOffsetParm
		push circleRariusParm
		push ax 
		push bx 
		call PaintCircleOutline
		mov ax, currentYLocal
		cmp ax, 0
		jne CalculatePoints	
	mov ax, boolFillCircle
	cmp ax, 0 
	je DoNotFillCircle
	push colourParm
	push xOffsetParm
	push circleRariusParm
	xor ax, ax 
	add ax, xOffsetParm
	sub ax, circleRariusParm
	push ax 
	xor ax, ax 
	add ax, yOffsetParm
	sub ax, circleRariusParm
	push ax 
	call FillCircle 
	add sp, 4 
	pop bp 
	ret 10 
	DoNotFillCircle:
		mov ax, xOffsetParm
		sub ax, circleRariusParm
		push ax 
		mov ax, yOffsetParm
		sub ax, circleRariusParm
		push ax 
		mov ax, circleRariusParm
		shl ax, 1 
		add ax, 1 
		push ax 
		push ax 
		push colourParm
		call ColourMarkedArea
		add sp, 4 
		pop bp 
		ret 10 
endp CircleProc
proc FillCircle
	;Fills the circle 
	push bp 
	mov bp, sp 
	sub sp, 4 
	colParm equ [bp + 12]
	offsetXParm equ [bp + 10]
	rParm equ [bp + 8]
	xParm equ [bp + 6]
	yParm equ [bp + 4]
	currentXLocal equ [bp - 2]
	currentYLocal equ [bp - 4] 
	mov ax, yParm
	mov currentYLocal, ax 
	mov cx, rParm
	shl cx, 1 
	inc cx 
	FillCircleLoop:
		push cx 
		mov ax, xParm
		mov currentXLocal, ax
		mov cx, rParm
		shl cx, 1 
		InnerFillCircleLoop:
			push cx 
			push currentXLocal
			push currentYLocal
			call GetColourAt
			cmp al, 125 
			jne NotSpecialColour1
			;Special colour, colour the row 
			push colParm
			push currentXLocal
			mov ax, offsetXParm
			sub ax, currentXLocal
			add ax, offsetXParm
			inc ax 
			push ax 
			push currentYLocal
			call ColourFromTo
			pop cx 
			jmp ExitInnerFillCircleLoop
			NotSpecialColour1:
				mov ax, currentXLocal
				inc ax 
				mov currentXLocal, ax 
				pop cx 
				loop InnerFillCircleLoop
		ExitInnerFillCircleLoop:
			mov ax, currentYLocal
			inc ax 
			mov currentYLocal, ax 
			pop cx 
			loop FillCircleLoop
	add sp, 4 
	pop bp 
	ret 10 
endp FillCircle
proc ColourFromTo
	;Colours from a certain coordinate to a certain coordinate on the same row
	push bp 
	mov bp, sp 
	colParm equ [bp + 10]
	startX equ [bp + 8] 
	endX equ [bp + 6] 
	yCoordinate equ [bp + 4] 
	ColourPixel:
		push colParm
		push startX
		push yCoordinate
		call PaintPixelAt
		mov ax, startX
		inc ax 
		cmp ax, endX
		je ExitColourFromToProc
		mov startX, ax 
		jmp ColourPixel
	ExitColourFromToProc:
		pop bp 
		ret 8 
endp ColourFromTo 
proc PaintCircleOutline
	;Paints the outline of the circle 
	push bp 
	mov bp, sp 
	colParm equ [bp + 14] 
	offsetXParm equ [bp + 12]
	offsetYParm equ [bp + 10]
	rParm equ [bp + 8]
	xParm equ [bp + 6]
	yParm equ [bp + 4]
	;Paints the bottom right quarter 
	push colParm
	mov ax, xParm
	add ax, offsetXParm
	push ax 
	mov ax, yParm
	add ax, offsetYParm
	push ax 
	call PaintPixelAt
	;Paints the bottom left quarter 
	push colParm
	mov ax, offsetXParm
	sub ax, xParm
	push ax 
	mov ax, yParm
	add ax, offsetYParm 
	push ax 
	call PaintPixelAt
	;Paints the top right quarter 
	push colParm
	mov ax, xParm
	add ax, offsetXParm
	push ax 
	mov ax, offsetYParm
	sub ax, yParm
	push ax 
	call PaintPixelAt
	;Paints the top left quarter
	push colParm
	mov ax, offsetXParm
	sub ax, xParm
	push ax 
	mov ax, offsetYParm
	sub ax, yParm
	push ax 
	call PaintPixelAt	
	pop bp 
	ret 12 
endp PaintCircleOutline
proc PaintPixelAt
	;Paints a single pixel at a given coordinate 
	push bp 
	mov bp, sp 
	paintColourParm equ [bp + 8]
	pixelXParm equ [bp + 6]
	pixelYParm equ [bp + 4]
	mov ax, paintColourParm
	mov ah, 0Ch
	mov bl, 0 
	mov cx, pixelXParm
	cmp cx, 319 
	ja OutOfRange
	mov dx, pixelYParm 
	cmp dx, 199 
	ja OutOfRange
	cmp dx, 0 
	jb OutOfRange
	int 10h 
	OutOfRange:
		pop bp 
		ret 6
endp PaintPixelAt
proc SaveImage
	;Saves the canvas to a .BMP file 
	push bp 
	mov bp, sp 
	sub sp, 2
	blScreenMaskParm equ [bp + 10]
	headerParm equ [bp + 8]
	saveFileNameParm equ [bp + 6]
	paletteParm equ [bp + 4]
	dataSegmentLocal equ [bp - 2] 
	call HideMouse
	;Saves the area into the mask 
	push blScreenMaskParm
	call SaveBottomLeftMask
	call ClearBottomTextRow
	;Asks for a name to use for the file 
	push 1 
	push 1 
	push offset promptSaveName
	call DisplayMessage
	mov bx, saveFileNameParm
	add bx, 6 
	push bx 
	call GetFileName
	;Checks if the user wants to abort the save image procedure 
	mov bx, saveFileNameParm
	add bx, 8 
	mov al, [byte ptr bx] 
	cmp al, '.'
	je ExitSaveImageProc
	;Creates the file 
	mov ah, 3Ch
	mov cx, 0 
	mov dx, saveFileNameParm
	int 21h 
	jnc ContinueSaveImageProc
	ExitSaveImageProc:
		;Displays that the file was not saved 
		call ClearBottomTextRow
		push 1
		push 60   
		push offset imgNotSavedMsg		
		call DisplayMessage
		push 11 
		mov bx, saveFileNameParm
		add bx, 6 
		push 9 
		push bx 
		call ClearBuffer
		push blScreenMaskParm
		call PrintMask 
		call DisplayMouse
		add sp, 2 
		pop bp 
		ret 8
	ContinueSaveImageProc:
		;Writes the header to the file  
		mov bx, ax 
		mov ah, 40h 
		mov cx, 54 
		mov dx, headerParm
		int 21h 
		;Writes the palette 
		mov ah, 40h 
		mov cx, 1024 
		mov dx, paletteParm
		int 21h 
		;Restores the original pixels
		push bx 
		push blScreenMaskParm
		call PrintMask 
		pop bx 
		;Writes the bitmap 
		mov ax, ds 
		mov dataSegmentLocal, ax 
		mov dx, 63680 
		mov ax, 0A000h
		mov ds, ax 
		mov cx, 170 
		SaveBitmapLoop:	
			push cx 
			mov ah, 40h 
			mov cx, 320  
			int 21h 
			sub dx, 320 
			pop cx 
			loop SaveBitmapLoop
		mov ax, dataSegmentLocal
		mov ds, ax 
		;Closes the file 
		mov ah, 3Eh 
		int 21h
		call DisplayMouse
		;Clears the buffer 
		push 11 
		mov bx, saveFileNameParm
		add bx, 6 
		push 9 
		push bx 
		call ClearBuffer
		;DisplayMessage
		call ClearBottomTextRow
		push 1
		push 40  
		push offset imgSavedMsg
		call DisplayMessage
		;Restores the original pixels
		push blScreenMaskParm
		call PrintMask 
		call DisplayMouse
		add sp, 2
		pop bp 
		ret 8 
endp SaveImage 
proc ClearBuffer 
	;Clears the buffer 
	push bp 
	mov bp, sp 
	lengthParm equ [bp + 8]
	amountFor1stCell equ [bp + 6] 
	bufferToClearParm equ [bp + 4]
	mov bx, bufferToClearParm
	mov ax, amountFor1stCell
	mov [byte ptr bx], al 
	mov cx, lengthParm
	dec cx 
	xor al, al 
	ClearBufferLoop:
		inc bx 
		mov [byte ptr bx], al 
		loop ClearBufferLoop
	pop bp 
	ret 6
endp ClearBuffer
proc GetFileName
	;Gets a name for the file 
	push bp 
	mov bp, sp 
	fileNameSaveParm equ [bp + 4]
	mov dx, fileNameSaveParm
	mov ah, 0Ah
	int 21h 
	mov bx, fileNameSaveParm
	mov al, 's'
	mov [byte ptr bx], al 
	mov al, [byte ptr bx + 1]
	xor ah, ah 
	add bx, ax 
	add bx, 2 
	mov ah, '.'
	mov [byte ptr bx], ah 
	inc bx 
	mov ah, 'b'
	mov [byte ptr bx], ah 
	inc bx
	mov ah, 'm'
	mov [byte ptr bx], ah 
	inc bx 
	mov ah, 'p'
	mov [byte ptr bx], ah 
	inc bx 
	mov al, 0
	mov [byte ptr bx], al 
	mov al, '/'
	mov bx, fileNameSaveParm
	mov [byte ptr bx + 1], al  
	pop bp 
	ret 2 
endp GetFileName
proc ClearBottomTextRow
	;Colours the bottom text row with black 
	push bp 
	mov bp, sp 
	sub sp, 2 
	currentLocalY equ [bp - 2] 
	mov ax, 191 
	mov currentLocalY, ax 
	mov cx, 9 
	ClearBottomTextRowLoop:
		push cx 
		push 0 
		push 0 
		push 320  
		push currentLocalY 
		call ColourFromTo
		mov ax, currentLocalY
		inc ax 
		mov currentLocalY, ax 
		pop cx 
		loop ClearBottomTextRowLoop
	add sp, 2 
	pop bp 
	ret 
endp ClearBottomTextRow
proc DisplayMessage
	;Displays a message at the bottom of the screen 
	push bp 
	mov bp, sp 
	boolPosition equ [bp + 8]
	amountOfTicksParm equ [bp + 6]
	msgToDisplayParm equ [bp + 4] 
	mov ax, boolPosition
	cmp ax, 0
	je ContinueDisplayMessageProc
	mov  dl, 0
    mov  dh, 24
    mov  ah, 2     
    mov  bh, 0     
    int  10h 
	ContinueDisplayMessageProc:
		;Displays the message 
		mov dx, msgToDisplayParm
		mov ah, 9 
		int 21h
		;Waits 40 ticks 
		push amountOfTicksParm
		call WaitTicks
		pop bp 
		ret 6
endp DisplayMessage 
proc SaveBottomLeftMask
	;Saves the bottom left area of the screen on which the message will be shown 
	push bp 
	mov bp, sp 
	sub sp, 4 
	bottomLeftScreenMaskParm equ [bp + 4] 
	currentLocalX equ [bp - 2]
	currentLocalY equ [bp - 4]
	;Sets the initial values 
	mov ax, 191 
	mov currentLocalY, ax 
	mov cx, 9 
	OuterSaveBLMaskLoop:
		push cx 
		xor ax, ax 
		mov currentLocalX, ax 
		mov cx, 320 
		InnerSaveBLMaskLoop:
			push cx 
			push currentLocalX
			push currentLocalY
			call GetColourAt
			mov bx, bottomLeftScreenMaskParm 
			add bx, currentLocalX
			mov cx, currentLocalY
			sub cx, 191
			cmp cx, 0 
			je OnFirstRow1
			CalcBLMask1:
				add bx, 320 
				loop CalcBLMask1
			OnFirstRow1:
				mov [byte ptr bx], al 
				mov ax, currentLocalX
				inc ax 
				mov currentLocalX, ax 
				pop cx 
				loop InnerSaveBLMaskLoop
		mov ax, currentLocalY
		inc ax 
		mov currentLocalY, ax 
		pop cx 
		loop OuterSaveBLMaskLoop
	add sp, 4 
	pop bp 
	ret 2 
endp SaveBottomLeftMask
proc PrintMask
	;Clears a mask 
	push bp 
	mov bp, sp 
	sub sp, 4 
	bottomLeftScreenMaskParm equ [bp + 4] 
	currentLocalX equ [bp - 2]
	currentLocalY equ [bp - 4]
	;Sets the initial values  
	mov ax, 191
	mov currentLocalY, ax 
	mov cx, 9 
	OuterPrintMaskLoop:
		push cx 
		xor ax, ax 
		mov currentLocalX, ax 
		mov cx, 320 
		InnerPrintMaskLoop:
			push cx 
			mov bx, bottomLeftScreenMaskParm 
			add bx, currentLocalX
			mov cx, currentLocalY
			sub cx, 191
			cmp cx, 0 
			je OnFirstRow2
			CalcBLMask2:
				add bx, 320 
				loop CalcBLMask2
			OnFirstRow2:
				push [word ptr bx] 
				push currentLocalX
				push currentLocalY
				call PaintPixelAt
				mov ax, currentLocalX
				inc ax 
				mov currentLocalX, ax
				pop cx 
				loop InnerPrintMaskLoop
		mov ax, currentLocalY
		inc ax 
		mov currentLocalY, ax 
		pop cx 
		loop OuterPrintMaskLoop
	add sp, 4 
	pop bp 
	ret 2
endp PrintMask
proc DrawHollowSquare
	;Draws a hollow square 
	push bp 
	mov bp, sp 
	sub sp, 4 
	toolNumParm equ [bp + 8]
	sideLengthParm equ [bp + 6]
	squareColourParm equ [bp + 4]
	topLeftXParm equ [bp - 2] 
	topLeftYParm equ [bp - 4]
	mov ax, 6 
	mov topLeftYParm, ax 
	mov ax, toolNumParm
	cmp ax, 0 
	je stdBrushButton
	cmp ax, 1 
	je eraserButton
	cmp ax, 2 
	je sampleButton
	cmp ax, 3 
	je bucketButton
	jmp squareButton 
	stdBrushButton:
		mov ax, 131
		jmp ContinueColourOutline
	eraserButton:
		mov ax, 151 
		jmp ContinueColourOutline 
	sampleButton:
		mov ax, 171  
		jmp ContinueColourOutline
	bucketButton: 
		mov ax, 191 
		jmp ContinueColourOutline
	squareButton:
		mov ax, 3
		mov topLeftYParm, ax 
		mov ax, 215
	ContinueColourOutline:
		mov topLeftXParm, ax 
		;Colours the top Row 
		push squareColourParm
		push topLeftXParm
		mov ax, topLeftXParm
		add ax, sideLengthParm
		push ax 
		push topLeftYParm
		call ColourFromTo
		;Colours the bottom row 
		push squareColourParm
		push topLeftXParm
		mov ax, topLeftXParm
		add ax, sideLengthParm
		push ax 
		mov ax, topLeftYParm
		add ax, sideLengthParm
		dec ax 
		push ax 
		call ColourFromTo
		;Colours the left and right borders 
		mov cx, sideLengthParm
		ColourSidesHollowSquare:
			push cx 
			push squareColourParm
			push topLeftXParm
			push topLeftYParm 
			call PaintPixelAt
			push squareColourParm
			mov ax, topLeftXParm
			add ax, sideLengthParm
			dec ax 
			push ax 
			push topLeftYParm 
			call PaintPixelAt
			mov ax, topLeftYParm
			inc ax 
			mov topLeftYParm, ax 
			pop cx 
			loop ColourSidesHollowSquare
		add sp, 4 
		pop bp 
		ret 6 
endp DrawHollowSquare
proc Menu
	;Displays the menu and lets the user interact with it 
	push bp 
	mov bp, sp 
	toolsInfoFilesNamesParm equ [bp + 22]
	colorusInfoFilesNamesParm equ [bp + 20]
	savingInfoFilesNamesParm equ [bp + 18]
	helpMenuFileNameParm equ [bp + 16] 
	menuFileNameParm equ [bp + 14]
	fileHandleParm equ [bp + 12]
	fileHeaderParm equ [bp + 10] 
	paletteParm equ [bp + 8]
	screenLineParm equ [bp + 6]
	errorMsgParm equ [bp + 4]
	mov cx, 320 
	mov dx, 100 
	InitMenu:
		push cx 
		push dx 
		call HideMouse
		;Displays the menu 
		push menuFileNameParm
		push fileHandleParm
		push fileHeaderParm
		push paletteParm
		push screenLineParm
		push errorMsgParm
		call DisplayImage
		;Initializes the mouse 
		pop dx 
		pop cx
		push 0  
		push cx  
		push dx  
		push offset mouseDriverErrorMsg
		push 0
		push 0
		call InitMouse	
		MenuInputLoop:
			mov ax, 3 
			int 33h 
			cmp bx, 1 
			jne MenuInputLoop
			shr cx, 1 
			cmp cx, 44
			ja NotOnQuit
			cmp dx, 154 
			jb NotOnQuit
			call ExitProgramme
			NotOnQuit:
				cmp cx, 49 
				jb MenuInputLoop
				cmp cx, 89 
				ja NotOnInst
				cmp dx, 154 
				jb MenuInputLoop
				push toolsInfoFilesNamesParm
				push colorusInfoFilesNamesParm
				push savingInfoFilesNamesParm
				push helpMenuFileNameParm
				push fileHandleParm
				push fileHeaderParm
				push paletteParm
				push screenLineParm
				push errorMsgParm
				call Instructions 
				jmp InitMenu
				NotOnInst:
					cmp cx, 133 
					jb MenuInputLoop
					cmp cx, 189 
					ja MenuInputLoop
					cmp dx, 102
					jb MenuInputLoop
					cmp dx, 128 
					jb ExitMenuProc
					jmp MenuInputLoop
		ExitMenuProc:
			call HideMouse
			pop bp 
			ret 20 
endp Menu 
proc Instructions
	push bp 
	mov bp, sp 
	toolsInfoNamesParm equ [bp + 20]
	colorusInfoNamesParm equ [bp + 18]
	savingInfoNamesParm equ [bp + 16]
	helpFileNameParm equ [bp + 14]
	imageHandleParm equ [bp + 12]
	imageHeaderParm equ [bp + 10] 
	helpPaletteParm equ [bp + 8]
	scrLineParm equ [bp + 6]
	imageErrorMsgParm equ [bp + 4]
	InitInstructions:
		call HideMouse
		;Displays the instructions menu 
		push helpFileNameParm
		push imageHandleParm
		push imageHeaderParm
		push helpPaletteParm
		push scrLineParm
		push imageErrorMsgParm
		call DisplayImage
		push 15 
		push 63
		push 63
		push 63 
		call SetColourAt
		call DisplayMouse
		InstructionsInputLoop:
			mov ax, 3 
			int 33h 
			and bx, 1 
			cmp bx, 1 
			jne InstructionsInputLoop
			shr cx, 1 
			cmp cx, 44
			ja NotOnBack
			cmp dx, 154 
			jb NotOnBack
			jmp ExitInstructionsProc
			NotOnBack:
				cmp dx, 72 
				jb InstructionsInputLoop
				cmp dx, 159  
				ja InstructionsInputLoop
				cmp cx, 96
				jb InstructionsInputLoop
				cmp cx, 224 
				ja InstructionsInputLoop
				cmp dx, 103 
				jb CheckToolsInfoButton  
				cmp dx, 129 
				ja CheckSavingInfoButton 
				;On colours info button 
				push 2
				push colorusInfoNamesParm
				jmp DisplayHelpImages
				CheckToolsInfoButton:
					cmp dx, 98 
					ja InstructionsInputLoop
					cmp cx, 114 
					jb InstructionsInputLoop
					cmp cx, 205 
					ja InstructionsInputLoop
					;On tools info button 
					push 9
					push toolsInfoNamesParm
					jmp DisplayHelpImages
				CheckSavingInfoButton:
					cmp dx, 133 
					jb InstructionsInputLoop
					cmp cx, 104 
					jb InstructionsInputLoop
					cmp cx, 216
					ja InstructionsInputLoop
					;On saving info button 
					push 5
					push savingInfoNamesParm
				DisplayHelpImages:
					push imageHandleParm
					push imageHeaderParm
					push helpPaletteParm
					push scrLineParm
					push imageErrorMsgParm
					call DisplayImages
					jmp InitInstructions 
	ExitInstructionsProc:
		mov ax, 3 
		int 33h  
		WaitForClickRelease:
			mov ax, 3 
			int 33h 
			and bx, 1 
			cmp bx, 0 
			jne WaitForClickRelease 
		pop bp 
		ret 18
endp Instructions
proc DisplayImages 
	;Displays a group of images 
	push bp 
	mov bp, sp 
	sub sp, 2 
	imagesMaxValueParm equ [bp + 16] 
	imagesNameParm equ [bp + 14] 
	imagesHandleParm equ [bp + 12]
	imagesHeaderParm equ [bp + 10] 
	imagesPaletteParm equ [bp + 8]
	imagesScreenLineParm equ [bp + 6]
	imagesErrorMsgParm equ [bp + 4]
	numberOffsetLocal equ [bp - 2] 
	;Finds the offset of the '.' from the start of the file name 
	push '.'
	push imagesNameParm
	call FindValueByte 
	dec ax 
	mov numberOffsetLocal, ax 
	DisplayCurrentImage:
		call HideMouse
		push imagesNameParm
		push imagesHandleParm
		push imagesHeaderParm
		push imagesPaletteParm
		push imagesScreenLineParm
		push imagesErrorMsgParm
		call DisplayImage
		push 15 
		push 63 
		push 63 
		push 63 
		call SetColourAt
		call DisplayMouse
		ImagesInputLoop:
			mov ax, 3 
			int 33h 
			and bx, 1 
			cmp bx, 1 
			jne ImagesInputLoop
			shr cx, 1 
			cmp dx, 154
			jb ImagesInputLoop
			cmp cx, 44 
			ja NotOnReturn
			;On left button 
			mov bx, imagesNameParm
			mov ax, numberOffsetLocal
			add bx, ax 
			mov al, [byte ptr bx] 
			cmp al, '1'
			je ExitDisplayImagesProc
			dec al 
			mov [byte ptr bx], al 
			call WaitForButtonRelease
			jmp DisplayCurrentImage 
			NotOnReturn:
				cmp cx, 275 
				jb ImagesInputLoop
				;On right button 
				mov bx, imagesNameParm
				mov ax, numberOffsetLocal
				add bx, ax 
				mov al, [byte ptr bx] 
				mov dx, imagesMaxValueParm
				add dl, '0' 
				cmp al, dl 
				je ExitDisplayImagesProc
				inc al 
				mov [byte ptr bx], al 
				call WaitForButtonRelease
				jmp DisplayCurrentImage
	ExitDisplayImagesProc:
		mov bx, imagesNameParm
		mov ax, numberOffsetLocal
		add bx, ax 
		mov al, '1'
		mov [byte ptr bx], al 
		call WaitForButtonRelease
		add sp, 2 
		pop bp 
		ret 14 
endp DisplayImages
proc WaitForButtonRelease
	;Waits until the left mouse button is released 
	WaitForButtonReleaseLoop:
		mov ax, 3 
		int 33h 
		and bx, 1 
		cmp bx, 0 
		jne WaitForButtonReleaseLoop 
	ret 
endp WaitForButtonRelease
proc FindValueByte
	;Finds a certain value and returns its offset from a given starting point on ax 
	push bp 
	mov bp, sp 
	valueToFindParm equ [bp + 6]
	startingPointParm equ [bp + 4]
	xor ax, ax 
	mov dx, valueToFindParm
	xor dh, dh 
	mov bx, startingPointParm
	CheckCurrentByte:	
		cmp [byte ptr bx], dl 
		je FoundOffsetOfValue
		inc ax
		inc bx 
		jmp CheckCurrentByte
	FoundOffsetOfValue:
		pop bp 
		ret 4 
endp FindValueByte 
proc ExitProgramme
	;Exits the programme 
	mov ax, 2 
	int 10h
	mov ax, 4c00h
	int 21h
	ret 
endp ExitProgramme
start:
	mov ax, @data
	mov ds, ax
	;Switches to graphics mode 
	mov ax, 13h
	int 10h
	;Initializes the menu 
	push offset toolsFileName
	push offset coloursFileName
	push offset savingFileName
	push offset helpMenuFileName
	push offset menuFileName
	push offset fileHandle
	push offset fileHeader
	push offset palette
	push offset screenLine
	push offset errorMsg
	call Menu
	push cx 
	push dx 
	;Displays the background and GUI 
	push offset bgFileName 
	push offset fileHandle
	push offset fileHeader
	push offset palette
	push offset screenLine 
	push offset errorMsg 
	call DisplayImage
	;Initializes the mouse 
	pop dx
	pop cx 
	push 1 
	shl cx, 1 
	push cx   
	push dx 
	push offset mouseDriverErrorMsg
	push offset stdBrushMask
	push offset stdCursorOffset
	call InitMouse
	;Main Programme
	push offset highlightColour
	push offset normalToolColour
	push offset palette
	push offset savedImagesHeaderTemplate
	push offset bottomLeftScreenMask 
	push offset saveFileNameBuffer
	push offset selectedShape
	push offset fillToolMask
	push offset fillToolHotOffset
	push offset colourSampMask
	push offset ersToolMask
	push offset ersToolHotOffset
	push offset stdBrushMask
	push offset stdCursorOffset
	push offset currentSize
	push offset bgColour
	push offset drawColour
	push offset selectedTool
	call MainProgramme 
	jmp start
exit:
	mov ax, 4c00h
	int 21h
END start