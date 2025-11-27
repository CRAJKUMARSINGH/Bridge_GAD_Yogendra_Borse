"""
Show only main elevation and plan views - exclude section views
"""

import ezdxf
import tkinter as tk

def show_main_views_only(dxf_file):
    """Display only elevation and plan views, excluding sections."""
    
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()
    
    # Collect entities, excluding sections (X > 50000 or Y > 20000)
    main_entities = []
    
    for entity in msp:
        include = True
        
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            # Exclude if X > 50000 or Y > 20000
            if max(start[0], end[0]) > 50000 or max(start[1], end[1]) > 20000:
                include = False
            if include:
                main_entities.append(('LINE', start, end))
                
        elif entity.dxftype() == 'LWPOLYLINE':
            points = list(entity.get_points('xy'))
            if points:
                max_x = max(p[0] for p in points)
                max_y = max(p[1] for p in points)
                # Exclude if X > 50000 or Y > 20000
                if max_x > 50000 or max_y > 20000:
                    include = False
                if include:
                    main_entities.append(('POLYLINE', points))
                    
        elif entity.dxftype() == 'TEXT':
            insert = entity.dxf.insert
            text = entity.dxf.text
            # Exclude if X > 50000 or Y > 20000
            if insert[0] > 50000 or insert[1] > 20000:
                include = False
            if include:
                main_entities.append(('TEXT', insert, text))
    
    print(f"\nFiltered to {len(main_entities)} main view entities")
    
    # Calculate bounds
    xs, ys = [], []
    for entity in main_entities:
        if entity[0] == 'LINE':
            xs.extend([entity[1][0], entity[2][0]])
            ys.extend([entity[1][1], entity[2][1]])
        elif entity[0] == 'POLYLINE':
            for p in entity[1]:
                xs.append(p[0])
                ys.append(p[1])
        elif entity[0] == 'TEXT':
            xs.append(entity[1][0])
            ys.append(entity[1][1])
    
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    print(f"\nMain views bounds:")
    print(f"  X: {min_x:.0f} to {max_x:.0f} (width: {max_x - min_x:.0f})")
    print(f"  Y: {min_y:.0f} to {max_y:.0f} (height: {max_y - min_y:.0f})")
    
    # Create fullscreen window
    root = tk.Tk()
    root.title("Bridge GAD - Main Views (Elevation + Plan)")
    root.state('zoomed')
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    canvas = tk.Canvas(root, bg='white')
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Calculate scale
    margin = 80
    canvas_width = screen_width - 2 * margin
    canvas_height = screen_height - 2 * margin
    
    scale_x = canvas_width / (max_x - min_x)
    scale_y = canvas_height / (max_y - min_y)
    scale = min(scale_x, scale_y) * 0.95
    
    # Center drawing
    drawing_width = (max_x - min_x) * scale
    drawing_height = (max_y - min_y) * scale
    offset_x = margin + (canvas_width - drawing_width) / 2
    offset_y = margin + canvas_height - (canvas_height - drawing_height) / 2
    
    print(f"\nDisplay scale: 1:{1/scale:.0f}")
    
    # Title
    canvas.create_text(screen_width // 2, 30,
                      text="BRIDGE GENERAL ARRANGEMENT DRAWING",
                      font=('Arial', 20, 'bold'), fill='black')
    
    # Draw entities
    for entity in main_entities:
        if entity[0] == 'LINE':
            _, start, end = entity
            x1 = (start[0] - min_x) * scale + offset_x
            y1 = offset_y - (start[1] - min_y) * scale
            x2 = (end[0] - min_x) * scale + offset_x
            y2 = offset_y - (end[1] - min_y) * scale
            canvas.create_line(x1, y1, x2, y2, fill='blue', width=1)
            
        elif entity[0] == 'POLYLINE':
            _, points = entity
            if len(points) > 1:
                coords = []
                for p in points:
                    x = (p[0] - min_x) * scale + offset_x
                    y = offset_y - (p[1] - min_y) * scale
                    coords.extend([x, y])
                
                # Color based on Y position
                avg_y = sum(p[1] for p in points) / len(points)
                if avg_y < -20000:  # Plan view
                    canvas.create_polygon(coords, outline='red', fill='pink', width=2)
                else:  # Elevation
                    canvas.create_line(coords, fill='blue', width=1)
        
        elif entity[0] == 'TEXT':
            _, insert, text = entity
            x = (insert[0] - min_x) * scale + offset_x
            y = offset_y - (insert[1] - min_y) * scale
            
            # Font size and color based on position
            if insert[1] < -20000:  # Plan view
                font_size = max(10, int(12 * scale * 100))
                color = 'darkred'
                weight = 'bold'
            else:  # Elevation
                font_size = max(8, int(10 * scale * 100))
                color = 'blue'
                weight = 'normal'
            
            canvas.create_text(x, y, text=text, 
                             font=('Arial', font_size, weight), fill=color)
    
    # Info
    info = f"Elevation + Plan Views | Scale: 1:{1/scale:.0f} | Entities: {len(main_entities)}"
    canvas.create_text(screen_width // 2, screen_height - 30,
                      text=info, font=('Arial', 10), fill='black')
    
    # Close button
    close_btn = tk.Button(root, text="Close (ESC)", command=root.destroy,
                         font=('Arial', 12), bg='lightgray', padx=20, pady=10)
    close_btn.place(x=screen_width - 150, y=screen_height - 70)
    
    root.bind('<Escape>', lambda e: root.destroy())
    
    print(f"\n✓ Main views displayed properly scaled!")
    print(f"  Press ESC to close\n")
    
    root.mainloop()

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    dxf_file = "complete_gad_test_sample_input.dxf"
    
    if not Path(dxf_file).exists():
        print(f"Error: {dxf_file} not found!")
        sys.exit(1)
    
    print(f"Loading: {dxf_file}")
    show_main_views_only(dxf_file)
