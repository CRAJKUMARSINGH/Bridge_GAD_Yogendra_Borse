; ==============================================================================
; Common Lisp Code for Plotting Bridge Layout and Components in AutoCAD
; ==============================================================================
; This code defines functions to read data, set up plotting parameters, and draw
; bridge components (axes, cross-sections, piers, abutments) in AutoCAD.
; All measurements are in meters unless specified, converted to millimeters for plotting.
; ==============================================================================

; ------------------------------------------------------------------------------
; 1.0 File Handling
; ------------------------------------------------------------------------------
(defun opn ()
  "Opens the input file for reading data."
  (setq f (open "D:\\gad.txt" "r"))
  ; (setq h (open "E:\\program files\\AutoCAD 2004\\h.txt" "w")) ; Commented out
)

; ------------------------------------------------------------------------------
; 2.0 Reading Layout Data
; ------------------------------------------------------------------------------
(defun reed ()
  "Reads parameters for layout and calculates derived variables."
  (setq scale1 (atof (read-line f)))       ; Scale for plan and elevation
  (setq scale2 (atof (read-line f)))       ; Scale for sections
  (setq skew (atof (read-line f)))         ; Skew angle (degrees)
  (setq datum (atoi (read-line f)))        ; Datum level
  (setq toprl (atoi (read-line f)))        ; Top level on Y-axis
  (setq left (atof (read-line f)))         ; Start chainage of X-axis
  (setq right (atof (read-line f)))        ; End chainage of X-axis
  (setq xincr (atof (read-line f)))        ; Interval of distances on X-axis (m)
  (setq yincr (atof (read-line f)))        ; Interval of levels on Y-axis (m)
  (setq noch (atoi (read-line f)))         ; Total number of chainages

  ; Set drawing scale (1 unit = 1 mm on screen)
  (setq hs 1)
  (setq vs 1)
  (setq vvs (/ 1000.0 vs))                ; Convert meters to millimeters
  (setq hhs (/ 1000.0 hs))                ; Convert meters to millimeters
  (setq skew1 (* skew 0.0174532))         ; Convert skew angle to radians
  (setq s (sin skew1))                    ; Sine of skew angle
  (setq c (cos skew1))                    ; Cosine of skew angle
  (setq tn (/ s c))                       ; Tangent of skew angle
  (setq sc (/ scale1 scale2))             ; Scale ratio for sections
)

; ------------------------------------------------------------------------------
; 3.0 Coordinate Conversion Functions
; ------------------------------------------------------------------------------
(defun vpos (a)
  "Converts vertical level to plot position (millimeters)."
  (setq a (* vvs (- a datum)))            ; Convert level difference to mm
  (setq a (+ datum a))                    ; Adjust relative to datum
)

(defun hpos (a)
  "Converts horizontal chainage to plot position (millimeters)."
  (setq a (* hhs (- a left)))             ; Convert chainage difference to mm
  (setq a (+ left a))                     ; Adjust relative to left
)

(defun v2pos (a)
  "Converts vertical level for sections with scale adjustment."
  (setq a (* vvs (- a datum)))            ; Convert level difference to mm
  (setq a (* sc a))                       ; Apply scale ratio
  (setq a (+ datum a))                    ; Adjust relative to datum
)

(defun h2pos (a)
  "Converts horizontal chainage for sections with scale adjustment."
  (setq a (* hhs (- a left)))             ; Convert chainage difference to mm
  (setq a (* sc a))                       ; Apply scale ratio
  (setq a (+ left a))                     ; Adjust relative to left
)

(defun pt (a b z)
  "Converts point (a, b) to graph coordinates and returns as list."
  (setq aa (hpos a))                      ; Convert x-coordinate
  (setq bb (vpos b))                      ; Convert y-coordinate
  (list aa bb)                            ; Return as (x, y) list
)

(defun p2t (a b z)
  "Converts point (a, b) to graph coordinates for sections."
  (setq aa (h2pos a))                     ; Convert x-coordinate with scale
  (setq bb (v2pos b))                     ; Convert y-coordinate with scale
  (list aa bb)                            ; Return as (x, y) list
)

; ------------------------------------------------------------------------------
; 4.0 AutoCAD Dimension Style Setup
; ------------------------------------------------------------------------------
(defun st ()
  "Sets up AutoCAD dimension style for consistent appearance."
  (command "-style" "Arial" "Arial" "" "" "" "" "") ; Set text style
  (command "DIMASZ" "150")                        ; Arrow size
  (command "DIMDEC" "0")                          ; No decimal places
  (command "DIMEXE" "400")                        ; Dimension line extension
  (command "DIMEXO" "400")                        ; Dimension line offset
  (command "DIMLFAC" "1")                         ; Scale factor
  (command "DIMTXSTY" "Arial")                    ; Text style for dimensions
  (command "DIMTXT" "400")                        ; Text height
  (command "DIMTAD" "0")                          ; Center text alignment
  (command "DIMTIH" "1")                          ; Dimension line on top
  (command "-dimstyle" "save" "pmb100" "y")       ; Save dimension style
)

; ------------------------------------------------------------------------------
; 5.0 Plotting Layout (X and Y Axes)
; ------------------------------------------------------------------------------
(defun layout ()
  "Draws X and Y axes with labels and gridlines for elevation plot."
  (setq os (getvar "OSMODE"))                    ; Save OSNAP mode
  (setvar "OSMODE" 0)                            ; Turn off OSNAP
  (setq left (- left (rem left 1.0)))            ; Round left to integer
  (setq d1 20)                                   ; Distance between parallel lines (mm)
  
  ; Define points for axes
  (setq pta1 (list left datum))
  (setq ptb1 (list left (- datum (* d1 scale1))))
  (setq pta2 (list (hpos right) datum))
  (setq ptb2 (list (hpos right) (- datum (* d1 scale1))))
  (setq ptc1 (list left (- datum (* d1 scale1 2))))
  (setq ptc2 (list (hpos right) (- datum (* d1 scale1 2))))
  (setq ptd1 (list left (vpos toprl)))

  ; Draw axes
  (command "line" pta1 pta2 "")                 ; X-axis
  (command "line" ptb1 ptb2 "")                 ; Line 20mm below X-axis
  (command "line" ptc1 ptc2 "")                 ; Line 40mm below X-axis
  (command "line" ptc1 ptd1 "")                 ; Y-axis

  ; Add labels
  (setq ptb3 (list (- left (* 25 scale1)) (- datum (* d1 0.5 scale1))))
  (command "text" ptb3 (* 2.5 scale1) 0 "BED LEVEL")
  (setq ptb3 (list (- left (* 25 scale1)) (- datum (* d1 1.5 scale1))))
  (command "text" ptb3 (* 2.5 scale1) 0 "CHAINAGE")

  ; Draw small lines on Y-axis
  (setq d2 2.5)                                 ; Half-length of small lines (mm)
  (setq pta1 (list (- left (* d2 scale1)) datum))
  (setq pta2 (list (+ left (* d2 scale1)) datum))
  (command "color" 7)
  (command "line" pta1 pta2 "")
  (setq e1 (entlast))
  (setq nov (fix (- toprl datum)))
  (command "array" e1 "" "R" (+ nov 1) 1 vvs)   ; Array small lines on Y-axis

  ; Write levels on Y-axis
  (setq a 0)
  (setq n (fix (/ nov yincr)))
  (while (< a (+ n 1))
    (setq lvl (+ datum (* a yincr)))
    (setq b1 (rtos lvl 2 3))                    ; Format level to 3 decimals
    (setq pta1 (list (- left (* 13 scale1)) (- (vpos lvl) (* 1.0 scale1))))
    (command "text" pta1 (* 2.0 scale1) 0 b1)   ; Write level
    (setq a (+ a 1))
  )

  ; Write chainages on X-axis
  (setq a 1)
  (setq noh (- right left))
  (setq n (fix (/ noh xincr)))
  (while (< a (+ n 1))
    (setq ch (+ left (* a xincr)))
    (setq b1 (rtos ch 2 3))                     ; Format chainage to 3 decimals
    (setq d4 (* 2 d1))
    (setq d5 (- d4 2.0))
    (setq d6 (+ d1 2.0))
    (setq d7 (- d1 2.0))
    (setq d8 (- d4 4.0))
    (setq d9 (- d1 4.0))
    (setq pta1 (list (+ scale1 (hpos ch)) (- datum (* d8 scale1))))
    (command "text" pta1 (* 2.0 scale1) 90 b1)  ; Write chainage
    (setq pta1 (list (hpos ch) (- datum (* d4 scale1))))
    (setq pta2 (list (hpos ch) (- datum (* d5 scale1))))
    (setq pta3 (list (hpos ch) (- datum (* d6 scale1))))
    (setq pta4 (list (hpos ch) (- datum (* d7 scale1))))
    (command "color" 7)
    (command "line" pta1 pta2 "")               ; Small line on X-axis
    (command "line" pta3 pta4 "")               ; Small line on X-axis
    (setq a (+ a 1))
  )
)

; ------------------------------------------------------------------------------
; 6.0 Plotting River Cross-Section
; ------------------------------------------------------------------------------
(defun cs ()
  "Plots river cross-section and writes chainages."
  (setq a 1)
  (while (< a (+ noch 1))
    (setq x (atof (read-line f)))               ; Read chainage
    (setq y (atof (read-line f)))               ; Read RL
    (setq b1 (rtos x 2 3))                     ; Format chainage
    (setq b2 (rtos y 2 3))                     ; Format RL
    (setq xx (hpos x))
    (setq pta1 (list (+ xx (* 0.9 scale1)) (- datum (* d8 scale1))))
    (setq pta2 (list (+ xx (* 0.9 scale1)) (- datum (* d9 scale1))))
    (command "text" pta2 (* 2 scale1) 90 b2)    ; Write RL
    (setq b (rem (- x left) xincr))            ; Check if chainage is on increment
    (if (/= b 0.0)
      (command "text" pta1 (* 1.8 scale1) 90 b1)) ; Write chainage if not on increment
    (setq pta1 (list xx (- datum (* d4 scale1))))
    (setq pta2 (list xx (- datum (* d5 scale1))))
    (setq pta3 (list xx (- datum (* d6 scale1))))
    (setq pta4 (list xx (- datum (* d7 scale1))))
    (if (/= b 0.0)
      (progn
        (command "line" pta1 pta2 "")           ; Small line on X-axis
        (command "line" pta3 pta4 "")           ; Small line on X-axis
      )
    )
    (setq pta5 (list xx (- datum (* 2 scale1))))
    (setq pta6 (list xx datum))
    (command "line" pta5 pta6 "")               ; Vertical line
    (setq ptb4 (list xx (vpos y)))              ; Point on cross-section
    (if (/= a 1)
      (command "line" ptb3 ptb4 ""))            ; Connect points
    (setq ptb3 ptb4)
    (setq a (+ a 1))
  )
)

; ------------------------------------------------------------------------------
; 7.0 Plotting Piers
; ------------------------------------------------------------------------------
(defun pier ()
  "Plots piers in elevation, plan, and cross-section."
  ; Read pier data
  (setq nspan (atoi (read-line f)))           ; Number of spans
  (setq lbridge (atof (read-line f)))         ; Bridge length
  (setq abtl (atof (read-line f)))            ; Left abutment chainage
  (setq RTL (atof (read-line f)))             ; Right top level
  (setq rtl2 (- RTL (* 30 sc)))               ; Adjusted top level for section
  (setq Sofl (atof (read-line f)))            ; Soffit level
  (setq kerbw (atof (read-line f)))           ; Kerb width
  (setq kerbd (atof (read-line f)))           ; Kerb depth
  (setq ccbr (atof (read-line f)))            ; Clear carriageway width
  (setq slbthc (atof (read-line f)))          ; Slab thickness at center
  (setq slbthe (atof (read-line f)))          ; Slab thickness at edge
  (setq slbtht (atof (read-line f)))          ; Slab thickness at tip
  (setq capt (atof (read-line f)))            ; Pier cap top RL
  (setq capb (atof (read-line f)))            ; Pier cap bottom RL
  (setq capw (atof (read-line f)))            ; Pier cap width
  (setq piertw (atof (read-line f)))          ; Pier top width
  (setq battr (atof (read-line f)))           ; Pier batter
  (setq pierst (atof (read-line f)))          ; Pier straight length
  (setq piern (atoi (read-line f)))           ; Pier number for cross-section

  ; Draw piers
  (setq spans abtl)
  (setq a 1)
  (while (<= a nspan)
    (setq span1 (atof (read-line f)))         ; Span length
    (setq futrl (atof (read-line f)))         ; Founding RL
    (setq futd (atof (read-line f)))          ; Footing depth
    (setq futw (atof (read-line f)))          ; Footing width
    (setq futl (atof (read-line f)))          ; Footing length
    (setq spane (+ spans span1))              ; End chainage of span

    ; Draw superstructure in elevation
    (setq x1 (hpos spans))
    (setq y1 (vpos RTL))
    (setq x2 (hpos spane))
    (setq y2 (vpos sofl))
    (setq pta1 (list (+ x1 25.0) y1))         ; Expansion gap
    (setq pta2 (list (- x2 25.0) y2))
    (command "rectangle" pta1 pta2)           ; Draw superstructure
    (setq pta1 (list x1 y1))
    (setq pta2 (list x2 y1))
    (setq ptaa1 (list (+ x1 50) (+ y1 2000)))
    (command "DIMLINEAR" pta1 pta2 ptaa1)     ; Dimension superstructure

    ; Draw pier cap
    (setq capwsq (/ capw c))                  ; Skew-adjusted cap width
    (setq x1 (- spane (/ capwsq 2)))
    (setq x2 (+ x1 capwsq))
    (setq x1 (hpos x1))
    (setq x2 (hpos x2))
    (setq y1 (vpos capt))
    (setq y2 (vpos capb))
    (setq pta1 (list x1 y1))
    (setq pta2 (list x2 y2))
    (command "rectangle" pta1 pta2)           ; Draw pier cap
    (setq ptaa1 (list (+ x1 50) (- y2 400)))
    (command "DIMEXE" "300")
    (command "DIMEXO" "200")
    (command "DIMLINEAR" (list x1 y2) pta2 ptaa1) ; Dimension cap width

    ; Draw pier
    (setq piertwsq (/ piertw c))
    (setq x1 (- spane (/ piertwsq 2)))
    (setq x3 (+ x1 piertwsq))
    (setq y2 (+ futrl futd))
    (setq ofset (/ (- capb y2) battr))
    (setq ofsetsq (/ ofset c))
    (setq x2 (- x1 ofsetsq))
    (setq x4 (+ x3 ofsetsq))
    (setq y4 y2)
    (setq pta1 (pt x1 capb pta1))
    (setq pta2 (pt x2 y2 pta2))
    (setq pta3 (pt x3 capb pta3))
    (setq pta4 (pt x4 y4 pta4))
    (command "line" pta1 pta2 "")             ; Draw pier sides
    (command "line" pta3 pta4 "")
    (setq ptaa1 (list (+ (hpos x2) 50) (- (vpos y2) 300)))
    (command "DIMEXE" "200")
    (command "DIMEXO" "100")
    (command "DIMLINEAR" pta2 pta4 ptaa1)     ; Dimension pier base

    ; Draw footing
    (setq futwsq (/ futw c))
    (setq x5 (- spane (/ futwsq 2)))
    (setq x6 (+ x5 futwsq))
    (setq y6 futrl)
    (setq y5 y4)
    (setq pta5 (pt x5 y5 pta5))
    (setq pta6 (pt x6 y6 pta6))
    (command "rectangle" pta5 pta6)           ; Draw footing
    (setq pt1 (list (hpos x5) (vpos y6)))
    (setq pt2 pta6)
    (setq pt3 (list (+ (hpos x5) 100) (- (vpos y6) 600)))
    (command "DIMEXE" "200")
    (command "DIMEXO" "400")
    (command "DIMLINEAR" pt1 pt2 pt3)         ; Dimension footing width
    (setq pt2 pt1)
    (setq pt1 pta5)
    (setq pt3 (list (- (hpos x5) 700) (- (vpos y5) 100)))
    (command "DIMEXE" "400")
    (command "DIMEXO" "500")
    (command "DIMLINEAR" pt1 pt2 pt3)         ; Dimension footing depth

    ; Draw footing in plan
    (setq x7 (- spane (/ futw 2)))
    (setq x8 (+ x7 futw))
    (setq yc (- datum 30.0))
    (setq y7 (+ yc (/ futl 2)))
    (setq y8 (- y7 futl))
    (setq pta7 (pt x7 y7 pta7))
    (setq pta8 (pt x8 y8 pta8))
    (command "rectangle" pta7 pta8)           ; Draw footing
    (setq g2 (entlast))
    (setq pt1 (list (hpos x7) (vpos y8)))
    (setq pt2 pta8)
    (setq pt3 (list (+ (hpos x7) 100) (- (vpos y8) 600)))
    (command "DIMEXE" "200")
    (command "DIMEXO" "400")
    (command "DIMLINEAR" pt1 pt2 pt3)         ; Dimension footing length
    (setq g3 (entlast))
    (setq pt1 (list (hpos x8) (vpos y7)))
    (setq pt2 pta8)
    (setq pt3 (list (+ (hpos x8) 700) (- (vpos y7) 100)))
    (command "DIMEXE" "200")
    (command "DIMEXO" "500")
    (command "DIMLINEAR" pt1 pt2 pt3)         ; Dimension footing width
    (setq g4 (entlast))
    (setq ptc (pt spane yc ptc))
    (command "rotate" g2 g3 g4 "" ptc skew)   ; Rotate footing to skew angle

    ; Draw pier in plan
    (setq pierstsq (+ (/ pierst c) (abs (* piertw tn))))
    (setq x1 (- spane (/ piertw 2)))
    (setq x3 (+ x1 piertw))
    (setq x2 (- x1 ofset))
    (setq x4 (+ x3 ofset))
    (setq y9 (+ yc (/ pierstsq 2)))
    (setq y10 (- y9 pierstsq))
    (setq pta9 (pt x2 y9 pta9))
    (setq pta10 (pt x2 y10 pta10))
    (setq pta11 (pt x1 y9 pta11))
    (setq pta12 (pt x1 y10 pta12))
    (setq pta13 (pt x3 y9 pta13))
    (setq pta14 (pt x3 y10 pta14))
    (setq pta15 (pt x4 y9 pta15))
    (setq pta16 (pt x4 y10 pta16))
    (command "line" pta9 pta10 "")            ; Draw pier sides
    (setq g1 (entlast))
    (command "line" pta11 pta12 "")
    (setq g2 (entlast))
    (command "line" pta13 pta14 "")
    (setq g3 (entlast))
    (command "line" pta15 pta16 "")
    (setq g4 (entlast))
    (setq y17 (+ y9 (/ piertw 2)))
    (setq y18 (+ y17 ofset))
    (setq y19 (- y10 (/ piertw 2)))
    (setq y20 (- y19 ofset))
    (setq pta17 (pt spane y17 pta17))
    (setq pta18 (pt spane y18 pta18))
    (setq pta19 (pt spane y19 pta19))
    (setq pta20 (pt spane y20 pta20))
    (command "arc" pta9 pta18 pta15)          ; Draw pier arcs
    (setq g5 (entlast))
    (command "arc" pta11 pta17 pta13)
    (setq g6 (entlast))
    (command "arc" pta12 pta19 pta14)
    (setq g7 (entlast))
    (command "arc" pta10 pta20 pta16)
    (setq g8 (entlast))
    (command "DIMEXE" "200")
    (command "DIMEXO" "500")
    (setq pt3 (list (+ (hpos x4) 700) (- (vpos y9) 100)))
    (command "DIMLINEAR" pta15 pta16 pt3)     ; Dimension pier
    (setq g9 (entlast))
    (setq pt3 (list (+ (hpos x1) 100) (+ (vpos y9) 700)))
    (command "DIMLINEAR" pta11 pta13 pt3)
    (setq g10 (entlast))
    (setq pt3 (list (+ (hpos x2) 100) (+ (vpos y9) 1000)))
    (command "DIMLINEAR" pta9 pta15 pt3)
    (setq g11 (entlast))
    (command "rotate" g1 g2 g3 g4 g5 g6 g7 g8 g9 g10 g11 "" ptc skew) ; Rotate pier

    ; Store data for deepest pier
    (setq n a)
    (while (= n piern)
      (setq futprl futrl)
      (setq futpd futd)
      (setq futpw futw)
      (setq futpl futl)
      (setq n (+ n 1))
    )

    (setq a (+ a 1))
    (setq spans spane)
  )

  ; Draw last span superstructure
  (setq x1 (hpos spane))
  (setq y1 (vpos RTL))
  (setq x2 (hpos (+ abtl lbridge)))
  (setq y2 (vpos sofl))
  (setq pta1 (list (+ x1 25.0) y1))
  (setq pta2 (list (- x2 25.0) y2))
  (command "rectangle" pta1 pta2)             ; Draw last span
  (setq pta1 (list x1 y1))
  (setq pta2 (list x2 y1))
  (setq ptaa1 (list (+ x1 50) (+ y1 2000)))
  (command "DIMLINEAR" pta1 pta2 ptaa1)       ; Dimension last span

  ; Draw pier cross-section (YY)
  (setq xp (+ left 55))
  (setq yp rtl2)
  (setq ppt16 (p2t xp yp ppt16))
  (setq ccbrsq (/ ccbr c))
  (setq ppt1 (p2t (+ xp (/ ccbrsq 2)) yp ppt1))
  (setq ppt2 (p2t (+ xp ccbrsq) yp ppt2))
  (setq kerbwsq (/ kerbw c))
  (setq ppt3 (p2t (+ xp ccbrsq kerbwsq) (+ yp (- slbthe slbtht)) ppt3))
  (setq ppt4 (p2t (+ xp ccbrsq kerbwsq) (+ yp slbthe) ppt4))
  (setq ppt5 (p2t (+ xp ccbrsq kerbwsq) (+ yp slbthe kerbd) ppt5))
  (setq k1 (/ 0.05 c))
  (setq k2 (/ 0.025 c))
  (setq ppt6 (p2t (+ xp ccbrsq k1) (+ yp slbthe kerbd) ppt6))
  (setq ppt7 (p2t (+ xp ccbrsq k2) (+ yp slbthe kerbd (- 0 0.025)) ppt7))
  (setq ppt8 (p2t (+ xp ccbrsq) (+ yp slbthe) ppt8))
  (setq ppt9 (p2t (+ xp (/ ccbrsq 2)) (+ yp slbthc) ppt9))
  (setq ppt10 (p2t xp (+ yp slbthe) ppt10))
  (setq ppt11 (p2t (- xp k2) (+ yp slbthe kerbd (- 0 0.025)) ppt11))
  (setq ppt12 (p2t (- xp k1) (+ yp slbthe kerbd) ppt12))
  (setq ppt13 (p2t (- xp kerbwsq) (+ yp slbthe kerbd) ppt13))
  (setq ppt14 (list (car ppt13) (cadr ppt4)))
  (setq ppt15 (list (car ppt13) (cadr ppt3)))
  (command "line" ppt16 ppt1 ppt2 ppt3 ppt4 ppt5 ppt6 ppt7 ppt8 ppt9 ppt10 ppt11 ppt12 ppt13 ppt14 ppt15 ppt16 "") ; Draw slab section
  (command "line" ppt14 ppt10 "")             ; Draw kerb lines
  (command "line" ppt8 ppt4 "")

  ; Draw pier cap in section
  (setq diff (/ (- pierstsq ccbrsq) 2))
  (setq xp (- xp diff))
  (setq pedstl (- sofl capt))
  (setq yp (- yp pedstl))
  (setq ppt16 (p2t xp yp ppt16))
  (setq capd (- capt capb))
  (setq ppt17 (p2t (- xp (/ capw 2)) yp ppt17))
  (setq ppt18 (p2t (+ xp pierstsq (/ capw 2)) yp ppt18))
  (setq ppt19 (p2t (- xp (/ capw 2)) (- yp capd) ppt19))
  (setq ppt20 (p2t (+ xp pierstsq (/ capw 2)) (- yp capd) ppt20))
  (command "line" ppt17 ppt18 ppt20 ppt19 ppt17 "") ; Draw pier cap

  ; Draw pier and footing in section
  (setq ppt21 (p2t (- xp (/ piertw 2)) (- yp capd) ppt21))
  (setq ppt22 (p2t xp (- yp capd) ppt22))
  (setq ppt23 (p2t (+ xp pierstsq) (- yp capd) ppt23))
  (setq ppt24 (p2t (+ xp pierstsq (/ piertw 2)) (- yp capd) ppt24))
  (setq xpc (+ xp (/ pierstsq 2)))
  (setq pierht (- capb futprl futpd))
  (setq pierbw (+ piertw (* 2 (/ pierht battr))))
  (setq h1 (- yp pierht capd))
  (setq ppt25 (p2t (- xpc (/ futpl 2)) h1 ppt25))
  (setq ppt26 (p2t (- xp (/ pierbw 2)) h1 ppt26))
  (setq ppt27 (p2t xp h1 ppt27))
  (setq ppt28 (p2t (+ xp pierstsq) h1 ppt28))
  (setq ppt29 (p2t (+ xp pierstsq (/ pierbw 2)) h1 ppt29))
  (setq ppt30 (p2t (+ xpc (/ futpl 2)) h1 ppt30))
  (setq h2 (- h1 futpd))
  (setq ppt31 (p2t (- xpc (/ futpl 2)) h2 ppt31))
  (setq ppt32 (p2t xpc h2 ppt32))
  (setq ppt33 (p2t (+ xpc (/ futpl 2)) h2 ppt33))
  (setq ppt2 (p2t (+ xp ccbrsq diff diff) yp ppt2))
  (command "line" ppt21 ppt26 "")             ; Draw pier sides
  (command "line" ppt16 ppt27 "")
  (command "line" ppt2 ppt28 "")
  (command "line" ppt24 ppt29 "")
  (command "line" ppt25 ppt30 ppt33 ppt31 ppt25 "") ; Draw footing
  (command "line" ppt9 ppt32 "")              ; Connect slab to footing
)

; ------------------------------------------------------------------------------
; 8.0 Left Abutment
; ------------------------------------------------------------------------------
(defun abt1 ()
  "Draws left abutment in elevation and plan views."
  ; Read abutment data
  (setq dwth (atof (read-line f)))            ; Dirtwall thickness
  (setq alcw (atof (read-line f)))            ; Abutment left cap width
  (setq alcd (atof (read-line f)))            ; Abutment left cap depth
  (setq alfb (atof (read-line f)))            ; Front batter
  (setq alfbl (atof (read-line f)))           ; Front batter RL
  (setq altb (atof (read-line f)))            ; Toe batter
  (setq altbl (atof (read-line f)))           ; Toe batter level
  (setq alfo (atof (read-line f)))            ; Front offset to footing
  (setq alfd (atof (read-line f)))            ; Footing depth
  (setq albb (atof (read-line f)))            ; Back batter
  (setq albbl (atof (read-line f)))           ; Back batter RL

  ; Calculate coordinates
  (setq abtlen (+ ccbrsq kerbwsq kerbwsq))    ; Abutment length
  (setq x1 abtl)
  (setq alcwsq (/ alcw 1))                    ; No skew adjustment
  (setq x3 (+ x1 alcwsq))
  (setq capb (- capt alcd))
  (setq p1 (/ (- capb alfbl) alfb))
  (setq p1sq (/ p1 1))
  (setq x5 (+ x3 p1sq))
  (setq p2 (/ (- alfbl altbl) altb))
  (setq p2sq (/ p2 1))
  (setq x6 (+ x5 p2sq))
  (setq alfosq (/ alfo 1))
  (setq x7 (+ x6 alfosq))
  (setq y8 (- altbl alfd))
  (setq dwthsq (/ dwth 1))
  (setq x14 (- x1 dwthsq))
  (setq p3 (/ (- capb albbl) albb))
  (setq p3sq (/ p3 1))
  (setq x12 (- x14 p3sq))
  (setq rt1s x12)
  (setq x10 (- x12 alfosq))

  ; Draw elevation
  (setq pt1 (pt x1 rtl pt1))
  (setq pt2 (pt x1 capt pt2))
  (setq pt3 (pt x3 capt pt3))
  (setq pt4 (pt x3 capb pt4))
  (setq pt5 (pt x5 alfbl pt5))
  (setq pt6 (pt x6 altbl pt6))
  (setq pt7 (pt x7 altbl pt7))
  (setq pt8 (pt x7 y8 pt8))
  (setq pt9 (pt x10 y8 pt9))
  (setq pt10 (pt x10 altbl pt10))
  (setq pt11 (pt x12 altbl pt11))
  (setq pt12 (pt x12 albbl pt12))
  (setq pt13 (pt x14 capb pt13))
  (setq pt14 (pt x14 rtl pt14))
  (setq pt15 (pt x12 rtl pt15))
  (command "line" pt1 pt2 pt3 pt4 pt5 pt6 pt7 pt8 pt9 pt10 pt11 pt12 pt13 pt14 pt1 "") ; Draw abutment
  (command "line" pt13 pt4 "")                ; Additional lines
  (command "line" pt10 pt7 "")
  (command "line" pt12 pt15 pt14 "")

  ; Draw plan view
  (setq y20 (+ yc (/ abtlen 2)))              ; Y-ordinate on downstream side
  (setq y21 (- y20 abtlen))                   ; Y-ordinate on upstream side
  (setq y16 (+ y20 0.15))                     ; Footing downstream
  (setq y17 (- y21 0.15))                     ; Footing upstream
  (setq footl (/ (- y16 y17) 2))
  (setq x (* footl s))
  (setq y (* footl (- 1 c)))
  (setq pt16 (pt (- x10 x) (- y16 y) pt16))
  (setq pt17 (pt (+ x10 x) (+ y17 y) pt17))
  (setq pt18 (pt (- x7 x) (- y16 y) pt18))
  (setq pt19 (pt (+ x7 x) (+ y17 y) pt19))
  (setq pt14 (pt x14 rtl pta14))
  (setq pt15 (pt x12 rtl pta15))
  (command "line" pt16 pt17 pt19 pt18 pt16 "") ; Draw footing

  ; Adjust for skew
  (setq xx (/ abtlen 2))
  (setq x (* xx s))
  (setq y (* xx (- 1 c)))
  (setq y20 (- y20 y))
  (setq y21 (+ y21 y))
  (setq pt20 (pt (- x12 x) y20 pt20))
  (setq pt21 (pt (+ x12 x) y21 pt21))
  (setq pt22 (pt (- x14 x) y20 pt22))
  (setq pt23 (pt (+ x14 x) y21 pt23))
  (setq pt24 (pt (- x1 x) y20 pt24))
  (setq pt25 (pt (+ x1 x) y21 pt25))
  (setq pt26 (pt (- x3 x) y20 pt26))
  (setq pt27 (pt (+ x3 x) y21 pt27))
  (setq pt28 (pt (- x5 x) y20 pt28))
  (setq pt29 (pt (+ x5 x) y21 pt29))
  (setq pt30 (pt (- x6 x) y20 pt30))
  (setq pt31 (pt (+ x6 x) y21 pt31))
  (command "line" pt20 pt21 "")               ; Draw abutment plan
  (command "line" pt22 pt23 "")
  (command "line" pt24 pt25 "")
  (command "line" pt26 pt27 "")
  (command "line" pt28 pt29 "")
  (command "line" pt30 pt31 "")
  (command "line" pt21 pt31 "")
  (command "line" pt20 pt30 "")
)

; ==============================================================================
; End of Code
; ==============================================================================