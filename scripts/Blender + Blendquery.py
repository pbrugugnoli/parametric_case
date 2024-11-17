# GM328A Case
from build123d import *
import math as math

#*******************
# SUPPORT FUNCTIONS 
#*******************
# Function to create a polyline from a shape
def shape_to_ordered_path(shape):
    """
    Convert a Shape into a Polyline (for sweep purposes, for example).

    Parameters:
    shape (Shape): the Shape object to be converted.

    Returns:
    Curve: a Curve create from the edges of the input Shape.
    """        
    # get edges from shape
    edges = shape.edges()
    
    # Start with the first edge
    ordered_edges = [edges.pop(0)]
    
    # While there are remaining edges to order
    while edges:
        last_edge = ordered_edges[-1]
        last_point = last_edge.end_point()

        # Find the next edge whose start point matches the last edge's end point
        for i, edge in enumerate(edges):
            if edge.start_point() == last_point:
                ordered_edges.append(edge)
                edges.pop(i)  # Remove the used edge from the list
                break
            elif edge.end_point() == last_point:  # Handle reversed edge
                # If the next edge is reversed, reverse its direction
                #ordered_edges.append(bd.Line(edge.end_point(), edge.start_point()))
                ordered_edges.append(edge.reversed())
                edges.pop(i)  # Remove the used edge from the list
                break
               
    curve = bd.Curve() + ordered_edges
    return curve


#*******************
# CLASSES 
#*******************

class board():
    # class properties
    d = bd.Vector(78.7, 63.8, 1.52)          # PCB dimensions
    solder = 4.0 #3.48                       # height of the solder leads (bottom of the PCB)
    hole_radius = 1.55
    hole_pos = hole_radius + 1.3
    dxy = bd.Vector(-78.7/2+hole_pos, -63.8/2+hole_pos, 1.52/2)
    dXy = bd.Vector(+78.7/2-hole_pos, -63.8/2+hole_pos, 1.52/2)
    dxY = bd.Vector(-78.7/2+hole_pos, +63.8/2-hole_pos, 1.52/2)
    dXY = bd.Vector(+78.7/2-hole_pos, +63.8/2-hole_pos, 1.52/2)

    def __init__(self):
        # instance properties
        return None

    def solid(self):
        solid = bd.Box(self.d.X, self.d.Y, self.d.Z)
        
        # fillets
        z_edges = solid.edges().filter_by(bd.Axis.Z)
        solid = bd.fillet(z_edges, radius=2.35)
        
        # holes       
        solid -= bd.Pos(self.dxy) * bd.Hole(radius=self.hole_radius, depth=self.d.Z)
        solid -= bd.Pos(self.dXy) * bd.Hole(radius=self.hole_radius, depth=self.d.Z)
        solid -= bd.Pos(self.dxY) * bd.Hole(radius=self.hole_radius, depth=self.d.Z)
        solid -= bd.Pos(self.dXY) * bd.Hole(radius=self.hole_radius, depth=self.d.Z)

        return solid

class lcd():
    # class properties
    d = bd.Vector(34.0 + 2.20, 43.8 + 2.33, 4.0)

    def __init__(self, pos, clearance):
        # instance properties
        self.p = pos
        self.clearance = clearance
        return None
    
    def sketch(self):
        slcd = bd.Pos(self.p + bd.Vector(self.d.X/2, self.d.Y/2, 0)) * bd.Rectangle(self.d.X + self.clearance.X, self.d.Y + self.clearance.Y)
        return slcd
    
    def solid_hole_upwards(self):
        slcd = self.sketch()
        solid_hole = bd.extrude(slcd, amount=20) 
        return solid_hole
    
class encoder():
    # class properties
    d = bd.Vector(13.8, 11.9, 0)
    radius = 10/2

    def __init__(self, pos):
        # instance properties
        self.p = pos
        return None
    
    def sketch(self):
        senc = bd.Pos(self.p + bd.Vector(-self.d.X/2, self.d.Y/2, 0)) * bd.Circle(self.radius)
        return senc
    
    def solid_hole_upwards(self):
        senc = self.sketch()
        solid_hole = bd.extrude(senc, amount=20) 
        return solid_hole

class led():
    # class properties
    radius = 3/2

    def __init__(self, pos):
        # instance properties
        self.p = pos
        return None
    
    def sketch(self):
        sled = bd.Pos(self.p + bd.Vector( self.radius, self.radius, 0)) * bd.Circle(self.radius)
        return sled

    def solid_hole_upwards(self):
        sled = self.sketch()
        solid_hole = bd.extrude(sled, amount=20) 
        return solid_hole

class mkdsn():
    # class properties  
    d = bd.Vector(5, 10, 1000)
    dxy = bd.Vector(10, 10, 5.2)

    def __init__(self, board, clearance_xy):
        # instance properties
        self.p1 = bd.Vector(board.d.X/2 - 3.55, board.d.Y/2 - self.d.Y/2 - 8.5)
        self.p2 = bd.Vector(board.d.X/2 - 3.55, (board.d.Y+clearance_xy)/2 - self.d.Y/2 - 8.5 - self.d.Y - 6.7)
        self.p3 = bd.Vector( -(board.d.X+clearance_xy)/2 + self.d.X/2, (board.d.Y+clearance_xy)/2 - self.d.Y/2 - 10.2)
        return None

    def sketch(self):  
        _slot_face =  bd.Rot(0, 0, 90) * bd.SlotOverall(self.d.Y, self.d.X, mode=bd.Mode.PRIVATE)
        smkdsn =  bd.Pos(self.p1.X, self.p1.Y) * _slot_face
        smkdsn += bd.Pos(self.p2.X, self.p2.Y) * _slot_face
        smkdsn += bd.Pos(self.p3.X, self.p3.Y) * _slot_face
        return smkdsn
    
    def solid_hole_outwards(self, box):
        xy_hole =  bd.Pos(box.board.d.X/2, self.p1.Y, box.dim_bottom.Z + box.clearance.Z + box.board.solder + box.board.d.Z + self.dxy.Z/2)  * \
                   bd.Box(self.dxy.X, self.dxy.Y, self.dxy.Z)
        xy_hole += bd.Pos(box.board.d.X/2, self.p2.Y, box.dim_bottom.Z + box.clearance.Z + box.board.solder + box.board.d.Z + self.dxy.Z/2)  * \
                   bd.Box(self.dxy.X, self.dxy.Y, self.dxy.Z)
        xy_hole += bd.Pos(-box.board.d.X/2, self.p3.Y, box.dim_bottom.Z + box.clearance.Z + box.board.solder + box.board.d.Z + self.dxy.Z/2)  * \
                   bd.Box(self.dxy.X, self.dxy.Y, self.dxy.Z)
        return xy_hole

    def solid_hole_upwards(self):
        smkdsn = self.sketch()
        solid_hole = bd.extrude(smkdsn, amount=20, both=True) 
        return solid_hole

class zif():
    # class properties
    d1 = bd.Vector(17, 47.4, 1000)
    d2 = bd.Vector(18, 22, 1000)
    d3 = bd.Vector(20, 12, 1000)
    d4 = bd.Vector(21, 27, 1000)

    def __init__(self, pos, edge):
        # instance properties
        #self.d1 += bd.Vector(0, box.clearance_xy, 0)    ### PEB Why this in the original one?     
        self.p = pos
        self.edge = edge
        return None
    
    def sketch(self):
        szif =  bd.Pos(self.p.X - self.d1.X/2 + 1, (self.p.Y + self.edge) - 0.5 - (self.d1.Y+self.edge)/2) * bd.Rectangle(self.d1.X, (self.d1.Y+self.edge))
        szif += bd.Pos(self.p.X - self.d2.X/2 + 1, (self.p.Y + self.edge) - 0.5 - self.d2.Y/2)             * bd.Rectangle(self.d2.X, self.d2.Y)
        szif += bd.Pos(self.p.X - self.d3.X/2 + 2, (self.p.Y + self.edge) - 0.5 - self.d3.Y/2)             * bd.Rectangle(self.d3.X, self.d3.Y)
        szif += bd.Pos(self.p.X - self.d4.X/2 + 2, (self.p.Y + self.edge) - 4.0 + (self.d4.Y-7)/2)   * bd.Rectangle(self.d4.X, self.d4.Y)              
        return szif
    
    def solid_hole_outwards(self, amount = 50):
        szif = self.sketch()
        hole = bd.Pos(0, 0, self.p.Z) * bd.extrude(szif, amount)
        return hole
        
class plug():
    d = bd.Vector(9, 15.3, 11)
    
    def __init__(self, pos):
        self.p = pos
        return None
    
    def solid_hole_outwards(self):
        plug_hole = bd.Pos(self.p) * bd.Box(self.d.X, 10, self.d.Z, align=[bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN])        
        return plug_hole

class battery():
    d = bd.Vector(26, 52, 17)
    
    def __init__(self):
        return None
    
    def solid(self):
        solid = bd.Box(self.d.X, self.d.Y, self.d.Z)
        solid = bd.fillet(solid.edges(), 1)
        return solid

class connector():
    radius = 4/2
    length = 2.5
    clearance = 0.2
    length_reinf = length + 3*clearance
    length_empty = length + clearance
        
    def __init__(self):
        return None
    
    def _sketch(self, radius):
        sketch = bd.RegularPolygon(radius=radius, side_count=6)
        return sketch
    
    def solid(self):
        sketch = self._sketch(self.radius)
        solid = bd.Rot(0,-90,0) * bd.extrude(sketch, self.length)
        return solid
    
    def hole_reinforcement(self):
        sketch = self._sketch(self.radius+3*self.clearance)
        solid = bd.Rot(0, -90, 0) * bd.extrude(sketch, self.length_reinf)
        return solid

    def hole_empty(self):
        sketch = self._sketch(self.radius+self.clearance)
        solid = bd.Rot(0,-90,0) * bd.extrude(sketch, self.length_empty)
        return solid
    
class magneto():
    global math
    radius = 5*math.sqrt(2)/2
    length = 2
    clearance = 0.2
    length_reinf = length + 3*clearance
    length_empty = length + clearance
        
    def __init__(self):
        return None
    
    def _sketch(self, radius):
        sketch = bd.RegularPolygon(radius=radius, side_count=4)
        # sketch = bd.Rectangle(5,5)
        return sketch
    
    def solid(self):
        sketch = self._sketch(self.radius)
        solid = bd.Rot(0,-90,0) * bd.extrude(sketch, self.length)
        return solid
    
    def hole_reinforcement(self):
        sketch = self._sketch(self.radius+3*self.clearance)
        solid = bd.Rot(0, -90, 0) * bd.extrude(sketch, self.length_reinf)
        return solid

    def hole_empty(self):
        sketch = self._sketch(self.radius+self.clearance)
        solid = bd.Rot(0,-90,0) * bd.extrude(sketch, self.length_empty)
        
        # cable hole
        sketch =  bd.Pos(self.radius - 0.5/2, 0) * bd.RegularPolygon(radius=0.5, side_count=4)
        solid += bd.Rot(0,-90,0) * bd.extrude(sketch, -3*self.length_empty)
        solid += bd.Rot(0,-90,0) * bd.extrude(sketch,  3*self.length_empty)
        return solid    

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------

class parametric_fillet():  
    global shape_to_ordered_path                        # for blendquery compability
    def __init__(self, fillet_type, fillet_side, box):
        shell_xy = box.dim_wall.X
        shell_z = box.dim_top.Z
        self.box = box
        self.fillet_type = fillet_type 
        self.fillet_side = fillet_side # 0 = bottom, 1 = lid
        match fillet_type:
            case 0: # fillet snapped     
                self.pts_fillet_profile = [
                    (+shell_xy*0.000, +shell_z*1.000),
                    (+shell_xy*0.000, +shell_z*0.750),
                    (-shell_xy*0.750, +shell_z*0.000),
                    (-shell_xy*1.000, +shell_z*0.000), 
                    (-shell_xy*1.000, +shell_z*0.375),
                    (-shell_xy*1.125, +shell_z*0.500),
                    (-shell_xy*1.000, +shell_z*0.625),
                    (-shell_xy*1.000, +shell_z*1.000),
                    (+shell_xy*0.000, +shell_z*1.000)]   
            case 1: # lid/base locks the fillet in place
                self.pts_fillet_profile = [
                    (+shell_xy*0.500, -shell_z*0.500),
                    (+shell_xy*0.500, +shell_z*0.000),
                    (+shell_xy*0.000, +shell_z*0.000),
                    (+shell_xy*0.000, +shell_z*0.500), 
                    (-shell_xy*0.250, +shell_z*0.500),
                    (-shell_xy*1.000, -shell_z*0.250),
                    (-shell_xy*1.000, -shell_z*0.500),
                    (-shell_xy*0.500, -shell_z*0.500),
                    (-shell_xy*0.375, -shell_z*0.375),
                    (-shell_xy*0.250, -shell_z*0.500),
                    (+shell_xy*0.500, -shell_z*0.500)]                   
        return None

    def path(self):
        match self.fillet_side:
            case 0: # bottom
                _sketch = self.box._bottom_sketch()
            case 1: # top
                _sketch = self.box._top_sketch()
       
        # adjust for clearance
        if (self.box.clearance.X != 0):
            _sketch = bd.offset(_sketch, amount=self.box.clearance.X)

        # convert to ordered path

        _path = shape_to_ordered_path(_sketch)        
        
        return _path 

    def sketch(self):
        # create profile
        _sketch =  bd.Polyline(self.pts_fillet_profile)
            
        return _sketch
         
    def solid(self):
        # retrieve fillet path and profile
        _path = self.path()                
        _sketch = self.sketch()
        
        # correct position and rotation
         
        rot = bd.Vector([[[90, 0, 180], [90, 180, 180]],
                         [[90, 0,   0], [90, 10,   0]] ][self.fillet_side][self.fillet_type])
        pos = bd.Vector([[[0, 0, 0], [0, 0, self.box.dim_bottom.Z/2]],
                         [[0, 0, self.box.height], [0, 0, self.box.height-self.box.dim_top.Z/2]]][self.fillet_side][self.fillet_type])
        _sketch = bd.Pos(pos) * bd.Pos(_path.edges()[0] @ 0) * bd.Rot(rot) * _sketch

        # create fillet section
        _sfillet_sections = [bd.Face.make_surface(_sketch)]

        # create fillet
        special_fillet = bd.sweep(_sfillet_sections, _path, transition=bd.Transition.RIGHT)
        
        # position fillet
        
        return special_fillet, _sfillet_sections
  
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------

class parametric_box():
    global parametric_fillet                             # for blendquery compability
    global board, lcd, encoder, led, zif, mkdsn, plug    # for blendquery compability
    def __init__(self,
                # box dimensions and clearances
                dim_top,                                    # external top dimension with Z as the top shell width/height
                dim_bottom,                                 # external bottom dimension with Z as the bottom shell width/height
                dim_wall,                                   # x = y = wall shell width, z = height
                clearance,                                  # reduces wall height and top/bottom external dimension                        
                pos_top = bd.Vector(0,0,0),
                pos_bottom = bd.Vector(0,0,0),
                # box type
                base_type = 1,                              # 0 = base + wall fused, 1 = dettachable base
                edge_top = bd.Vector(1, 1, 1),              # defines the edge width(x=y) and height(z) that goes on top of the fillet     
                edge_bottom = bd.Vector(1, 1, 1),           # only used for base_type = 1
                # corner / z edges
                corners_type = 1,                           # Corners type: 0 straight, 1 fillet, 2 chamfer
                corners_size = 3.5,                         # Fillet radius/chamfer size for corners (z edges)
                # fillet/chamfer definition for top and bottom
                fillet_type_top = 4,                        # type of fillet/chamfer at top: 0 = none, 1 integrated fillet, 2 as an independent fillet part, 3 integrated chamfer, 4 as an independent chamfer part
                fillet_dim_top = bd.Vector(2, 2, 2),        # x = y = width and z = height
                fillet_size_top = 1.5,                      # fillet radius/chamfer size
                fillet_snap_top = False,                     # add snap between fillet and wall
                fillet_type_bottom = 4,                     # type of fillet/chamfer at bottom: 0 = none, 1 integrated fillet, 2 as an independent fillet part, 3 integrated chamfer, 4 as an independent chamfer part
                fillet_dim_bottom = bd.Vector(2, 2, 2),     # x = width, y = fillet radius/chamfer size, z = height
                fillet_size_bottom = 1.5,                   # fillet radius/chamfer size
                fillet_snap_bottom = False,                    # add snap between fillet and wall                
                # flange for dettachable top/bottom
                flange_width_top = 2,                       # applied to the lid
                flange_height_top = 4,
                flange_width_bottom = 2,                    # applied to the base when dettachable
                flange_height_bottom = 4,
                # lid/base snap     
                snap_top = 1,                                # 0 = no lid snap, 1 lid_snap shorter side, 2 lid_snap longer side, 3 lid snap both sides
                snap_bottom = 1                              # 0 = no base snap, 1 base_snap shorter side, 2 base_snap longer side, 3 base snap both sides
                ):
        """
        Initializes the box with the specified parameters.

        Parameters:
            dim_top: float
                External top dimension with Z as the top shell width/height.
            dim_bottom: float
                External bottom dimension with Z as the bottom shell width/height.
            dim_wall: float
                Wall shell width (x=y) and height (z).
            clearance: float
                Clearance applied to reduce wall height and top/bottom external dimensions.
            pos_top: bd.Vector, optional
                Position vector for the top shell (default is bd.Vector(0, 0, 0)).
            pos_bottom: bd.Vector, optional
                Position vector for the bottom shell (default is bd.Vector(0, 0, 0)).
            base_type: int, optional
                Box type: 0 for base and wall fused, 1 for detachable base (default is 1).
            edge_top: bd.Vector, optional
                Vector defining edge width (x=y) and height (z) for the top (default is bd.Vector(1, 1, 1)).
            edge_bottom: bd.Vector, optional
                Vector defining edge width (x=y) and height (z) for the bottom (used only if base_type=1).
            corners_type: int, optional
                Corners type: 0 for straight edges, 1 for fillet, 2 for chamfer (default is 1).
            corners_size: float, optional
                Fillet radius or chamfer size for corners in the Z direction (default is 3.5).
            fillet_type_top: int, optional
                Fillet/chamfer type at the top:
                0 = none, 1 = integrated fillet, 2 = independent fillet, 3 = integrated chamfer, 4 = independent chamfer (default is 2).
            fillet_dim_top: bd.Vector, optional
                Dimensions for the top fillet or chamfer (x=y for width, z for height) (default is bd.Vector(2, 2, 2)).
            fillet_size_top: float, optional
                Fillet radius or chamfer size at the top (default is 1.5).
            fillet_snap_top = Boolean, optional  (default is True) 
                Flag to add snap between top fillet and wall                
            fillet_type_bottom: int, optional
                Fillet/chamfer type at the bottom:
                0 = none, 1 = integrated fillet, 2 = independent fillet, 3 = integrated chamfer, 4 = independent chamfer (default is 2).
            fillet_dim_bottom: bd.Vector, optional
                Dimensions for the bottom fillet or chamfer (x for width, y for radius/size, z for height) (default is bd.Vector(2, 2, 2)).
            fillet_size_bottom: float, optional
                Fillet radius or chamfer size at the bottom (default is 1.5).
            fillet_snap_bottom = Boolean, optional (default is False) 
                Flag to add snap between bottom fillet and wall                
            flange_width_top: float, optional
                Width of the flange applied to the top lid (default is 2).
            flange_height_top: float, optional
                Height of the flange applied to the top lid (default is 4).
            flange_width_bottom: float, optional
                Width of the flange applied to the base (default is 2).
            flange_height_bottom: float, optional
                Height of the flange applied to the base (default is 4).
            snap_top = float, optional (default is 1).
                0 = no lid snap, 1 = lid snap shorter side, 2 = lid snap longer side, 3 = lid snap both sides
            snap_bottom: float, optional (default is 1).
                0 = no base snap, 1 = base snap shorter side, 2 = base snap longer side, 3 = base snap both sides
        """

        # validate inputs
        if (edge_top.Z < clearance.Z):
            raise ValueError(f"Edge height ({edge_top.Z}) has to be greatter than clearance at z direction ({clearance.Z})")
        if (base_type == 0 and fillet_type_bottom == 2):
            raise ValueError("Fillet as an independent part are not consistent with fused wall + base")
        if (base_type == 0 and fillet_type_bottom == 4):
            raise ValueError("Fillet as an independent part are not consistent with fused wall + base")
        if (base_type == 0 and edge_bottom != bd.Vector(0, 0, 0)):
            raise ValueError("For fused wall + base, the edge_bottom must be (0,0,0)")
        if (dim_top.X != dim_bottom.X or dim_top.Y != dim_bottom.Y):
            raise ValueError("")


        # box dimensions and clearances
        self.dim_top = dim_top
        self.dim_bottom = dim_bottom
        self.dim_wall = dim_wall
        self.clearance = clearance
        self.pos_top = pos_top
        self.pos_bottom = pos_bottom
        # box type
        self.base_type = base_type
        self.edge_top = edge_top
        self.edge_bottom = edge_bottom
        # corner / z edges
        self.corners_type = corners_type
        self.corners_size = corners_size
        # fillet/chamfer definition for top and bottom
        self.fillet_type_top = fillet_type_top
        self.fillet_dim_top = fillet_dim_top
        self.fillet_size_top = fillet_size_top
        self.fillet_snap_top = fillet_snap_top
        self.fillet_type_bottom = fillet_type_bottom
        self.fillet_dim_bottom = fillet_dim_bottom
        self.fillet_size_bottom = fillet_size_bottom
        self.fillet_snap_bottom = fillet_snap_bottom
        # flange for dettachable top/bottom
        self.flange_width_top = flange_width_top
        self.flange_height_top = flange_height_top
        self.flange_width_bottom = flange_width_bottom
        self.flange_height_bottom = flange_height_bottom
        # snaps
        self.snap_top = snap_top
        self.snap_bottom = snap_bottom
        
        # calculate some additional properties
        self.height = self.dim_bottom.Z + self.dim_wall.Z + self.dim_top.Z + 2 * self.clearance.Z                

        # fillet profiles definition
        shell_xy = dim_wall.X
        shell_z = dim_top.Z
        self.pts_fillet_profiles = [
            [
            (+shell_xy*0.000, +shell_z*1.000),
            (+shell_xy*0.000, +shell_z*0.750),
            (-shell_xy*0.750, +shell_z*0.000),
            (-shell_xy*1.000, +shell_z*0.000), 
            (-shell_xy*1.000, +shell_z*0.375),
            (-shell_xy*1.125, +shell_z*0.500),
            (-shell_xy*1.000, +shell_z*0.625),
            (-shell_xy*1.000, +shell_z*1.000),
            (+shell_xy*0.000, +shell_z*1.000)
            ], [   
            (+shell_xy*0.500, -shell_z*0.500),
            (+shell_xy*0.500, +shell_z*0.000),
            (+shell_xy*0.000, +shell_z*0.000),
            (+shell_xy*0.000, +shell_z*0.500), 
            (-shell_xy*0.250, +shell_z*0.500),
            (-shell_xy*1.000, -shell_z*0.250),
            (-shell_xy*1.000, -shell_z*0.500),
            (-shell_xy*0.500, -shell_z*0.500),
            (-shell_xy*0.375, -shell_z*0.375),
            (-shell_xy*0.250, -shell_z*0.500),
            (+shell_xy*0.500, -shell_z*0.500)
            ]]                   

        return None

    def _snap_top_sketch(self):
        # select small side for snap  (PEB: for while top and bottom are equal)
        if self.snap_top == 1 and self.dim_top.X < self.dim_top.Y:
            sketch1 = bd.Rectangle(self.dim_top.X/2, self.flange_height_top/4)
            sketch2 = bd.Rectangle(self.dim_top.X/2 - self.flange_height_top/8, 0.01)            
        else:
            sketch1 = bd.Rectangle(self.dim_top.Y/2, self.flange_height_top/4)            
            sketch2 = bd.Rectangle(self.dim_top.Y/2 - self.flange_height_top/8, 0.01)            
        
        return sketch1, sketch2
    
    def _snap_top_solid(self):
        sketch1, sketch2 = self._snap_top_sketch()
        faces = bd.Sketch() + [
            bd.Plane.XY * sketch1,
            bd.Plane.XY.offset(self.flange_height_top/8) * sketch2
        ]
        solid = bd.loft(faces)
        return solid

    def _snap_bottom_sketch(self):
        # select small side for snap  (PEB: for while top and bottom are equal)
        if self.snap_bottom == 1 and self.dim_bottom.X < self.dim_bottom.Y:
            sketch1 = bd.Rectangle(self.dim_bottom.X/2, self.flange_height_bottom/4)
            sketch2 = bd.Rectangle(self.dim_bottom.X/2 - self.flange_height_bottom/8, 0.01)            
        else:
            sketch1 = bd.Rectangle(self.dim_bottom.Y/2, self.flange_height_bottom/4)            
            sketch2 = bd.Rectangle(self.dim_bottom.Y/2 - self.flange_height_bottom/8, 0.01)            
        
        return sketch1, sketch2
    
    def _snap_bottom_solid(self):
        sketch1, sketch2 = self._snap_bottom_sketch()
        faces = bd.Sketch() + [
            bd.Plane.XY * sketch1,
            bd.Plane.XY.offset(self.flange_height_bottom/8) * sketch2
        ]
        solid = bd.loft(faces)
        return solid    

    def _top_sketch(self):
        # lid border
        match self.fillet_type_top:
            case 0 | 1 | 3:
                sketch = bd.Rectangle(self.dim_top.X, self.dim_top.Y)
            case 2 | 4:
                sketch = bd.Rectangle(self.dim_top.X - 2 * (self.fillet_dim_top.X + self.clearance.X), 
                                      self.dim_top.Y - 2 * (self.fillet_dim_top.Y + self.clearance.Y)
                                      )
    
        # lid fillet/chamfer
        match self.corners_type:
            case 1:
                sketch = bd.fillet(sketch.vertices(), self.corners_size)      
            case 2:
                sketch = bd.chamfer(sketch.vertices(), self.corners_size)                            
                                  
        return sketch

    def _top_flange_sketch(self):
        sketch1 = bd.offset(self._top_sketch(), amount=-self.edge_top.X)
        sketch2 = bd.offset(sketch1, amount=-self.flange_width_top)
        sketch = sketch1 - sketch2
        return sketch, sketch1
        
    def _top_flange_solid(self):
        sketch, outer_sketch = self._top_flange_sketch()
        solid = bd.Pos(0,0, (self.height - self.dim_top.Z + self.clearance.Z) - self.flange_height_top) * \
            bd.extrude(sketch, amount=self.flange_height_top)
                      
        # add snap
        if (self.snap_top != 0):
            if ((self.snap_top == 1 and self.dim_top.X < self.dim_top.Y) or (self.snap_top == 2 and self.dim_top.X > self.dim_top.Y)):
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(0,1,0)))==1).sort_by(bd.Axis.Y)
                p1 = bd.Vector(0, outer_sketch.vertices().sort_by(bd.Axis.Y) [0].Y, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
                p2 = bd.Vector(0, outer_sketch.vertices().sort_by(bd.Axis.Y)[-1].Y, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
            else:
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(1,0,0)))==1).sort_by(bd.Axis.X)
                p1 = bd.Vector(outer_sketch.vertices().sort_by(bd.Axis.X)[ 0].X, 0, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
                p2 = bd.Vector(outer_sketch.vertices().sort_by(bd.Axis.X)[-1].X, 0, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
                
            # snapshot = solid.edges()   
            plane = bd.Plane(sorted_faces[0]).shift_origin(p1).reverse()
            solid -= plane * self._snap_top_solid()
            # last_edges = solid.edges() - snapshot
            # solid = bd.chamfer(last_edges.group_by(bd.Axis.Z)[0], self.flange_height_top/64)
            
            # snapshot = solid.edges()   
            plane = bd.Plane(sorted_faces[-1]).shift_origin(p2).reverse()
            solid -= plane * self._snap_top_solid()  
            # last_edges = solid.edges() - snapshot
            # solid = bd.chamfer(last_edges.group_by(bd.Axis.Z)[0], self.flange_height_top/64)
                      
        return solid       

    def top_solid(self):
        # create (and position) first layer of the top with edge
        sketch = bd.Pos(self.pos_top) * self._top_sketch()
        solid = bd.Pos(0, 0, self.height - (self.edge_top.Z - self.clearance.Z))  * \
            bd.extrude(sketch, self.edge_top.Z - self.clearance.Z)  

        # create (and position) second layer of the top without edge, just below the first layer
        sketch = bd.offset(sketch, amount=-self.edge_top.X)
        solid += bd.Pos(0, 0, self.height - self.dim_top.Z) * \
            bd.extrude(sketch, self.dim_top.Z - (self.edge_top.Z - self.clearance.Z))      
    
        # apply fillet/chamfer when necessary
        match self.fillet_type_top:
            case 1: # integrated fillet
                solid = bd.fillet(solid.edges().group_by()[-1], radius=self.fillet_size_top)  
            case 3: # integrate chamfer
                solid = bd.chamfer(solid.edges().group_by()[-1], lenght=self.fillet_size_top) 
    
        # add external flange
        solid += self._top_flange_solid()
    
        return solid

    def _bottom_sketch(self):
        if self.base_type == 0: 
            # sketch for base + wall fused
                sketch = bd.Rectangle(self.dim_bottom.X, self.dim_bottom.Y)
        else:        
            # sketch for dettached base
            match self.fillet_type_top:
                case 0 | 1 | 3:
                    sketch = bd.Rectangle(self.dim_bottom.X, self.dim_bottom.Y)
                case 2 | 4:
                    sketch = bd.Rectangle(self.dim_bottom.X - 2 * (self.fillet_dim_bottom.X + self.clearance.X), 
                                          self.dim_bottom.Y - 2 * (self.fillet_dim_bottom.Y + self.clearance.Y)
                                          )                       
        
        match self.corners_type:
            case 1:
                sketch = bd.fillet(sketch.vertices(), self.corners_size)      
            case 2:
                sketch = bd.chamfer(sketch.vertices(), self.corners_size)        
               
        return sketch

    def _bottom_flange_sketch(self):
        sketch1 = bd.offset(self._bottom_sketch(), amount=-self.edge_top.X)
        sketch2 = bd.offset(sketch1, amount=-self.flange_width_top)
        sketch = sketch1 - sketch2
        return sketch, sketch1
        
    def _bottom_flange_solid(self):
        sketch, outer_sketch = self._bottom_flange_sketch()
        solid = bd.Pos(0,0, self.dim_bottom.Z- self.clearance.Z) * bd.extrude(sketch, amount=self.flange_height_bottom)
        
        # add snap
        if (self.snap_bottom != 0):
            if ((self.snap_bottom == 1 and self.dim_top.X < self.dim_top.Y) or (self.snap_bottom == 2 and self.dim_top.X > self.dim_top.Y)):
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(0,1,0)))==1).sort_by(bd.Axis.Y)
                p1 = bd.Vector(0, outer_sketch.vertices().sort_by(bd.Axis.Y)[ 0].Y, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
                p2 = bd.Vector(0, outer_sketch.vertices().sort_by(bd.Axis.Y)[-1].Y, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
            else:
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(1,0,0)))==1).sort_by(bd.Axis.X)
                p1 = bd.Vector(outer_sketch.vertices().sort_by(bd.Axis.X)[ 0].X, 0, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
                p2 = bd.Vector(outer_sketch.vertices().sort_by(bd.Axis.X)[-1].X, 0, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
                
            plane = bd.Plane(sorted_faces[0]).shift_origin(p1).reverse()
            solid -= plane * self._snap_bottom_solid()
            plane = bd.Plane(sorted_faces[-1]).shift_origin(p2).reverse()
            solid -= plane * self._snap_bottom_solid()                 
        return solid    
    
    def bottom_solid(self):
        # create (and position) first layer of the bottom with edge
        sketch = bd.Pos(self.pos_top) * self._bottom_sketch()
        solid = bd.Pos(0, 0, 0)  * bd.extrude(sketch, self.edge_bottom.Z - self.clearance.Z)  

        # create (and position) second layer of the top without edge, just aboxe the first layer
        sketch = bd.offset(sketch, amount=-self.edge_top.X)
        solid += bd.Pos(0, 0, self.edge_bottom.Z - self.clearance.Z) * bd.extrude(sketch, self.dim_bottom.Z - (self.edge_bottom.Z - self.clearance.Z))  
 
        # apply fillet/chamfer when necessary for fused 
        match self.fillet_type_bottom:
            case 1: # integrated fillet
                solid = bd.fillet(solid.edges().group_by()[0], radius=self.fillet_size_bottom)      
            case 3: # integrate chamfer
                solid = bd.chamfer(solid.edges().group_by()[0], lenght=self.fillet_size_bottom)      

        match self.base_type:
            case 0:
                solid += wall_solid()
            case 1:
                solid += self._bottom_flange_solid()
                            
        return solid        
  
    def _wall_sketch(self):
        perimeter_external = bd.Rectangle(self.dim_bottom.X, self.dim_bottom.Y)
        
        match self.corners_type:
            case 1:
                perimeter_external = bd.fillet(perimeter_external.vertices(), self.corners_size + self.dim_wall.X)      
            case 2:
                perimeter_external = bd.chamfer(perimeter_external.vertices(), self.corners_size  + self.dim_wall.X)   
                        
        perimeter_internal         = bd.offset(perimeter_external, amount=-self.dim_wall.X, mode=bd.Mode.INTERSECT)
        perimeter_internal_top     = bd.offset(perimeter_external, amount=-(self.dim_wall.X + self.edge_top.X), mode=bd.Mode.INTERSECT)
        perimeter_internal_bottom  = bd.offset(perimeter_external, amount=-(self.dim_wall.X + self.edge_top.X), mode=bd.Mode.INTERSECT)
        
        wall        = perimeter_external - perimeter_internal
        wall_top    = perimeter_external - perimeter_internal_top
        wall_bottom = perimeter_external - perimeter_internal_bottom
        
        return wall, wall_top, wall_bottom,  perimeter_internal,  perimeter_internal_top,  perimeter_internal_bottom, perimeter_external

    def _fillet_snap_sketch(self):
        _, _, _, _, _, _, sketch = self._wall_sketch()
        sketch = bd.offset(sketch, amount=-self.dim_wall.X/2) - \
                 bd.offset(sketch, amount=-self.dim_wall.X/2-self.dim_wall.X/4)
        return sketch

    def _fillet_snap_solid(self):
        sketch = self._fillet_snap_sketch()
        solid = bd.extrude(sketch, amount=self.dim_wall.X/8, taper=45)
        return solid
     
    def wall_solid(self, wider_top=True, wider_bottom=True):
        wall, wall_top, wall_bottom,  perimeter_internal,  perimeter_internal_top,  perimeter_internal_bottom, _ = self._wall_sketch()

        (sbase, ibase, cbase) = [(wall, perimeter_internal, 0), (wall_bottom, perimeter_internal_bottom, self.clearance.Z)][wider_bottom]
        (stop, itop, ctop)    = [(wall, perimeter_internal, 0), (wall_top,    perimeter_internal_top,    self.clearance.Z)][wider_top]
    
        # bottom layer
        solid = bd.Pos(0, 0, self.dim_bottom.Z + cbase) * bd.extrude(sbase, amount=2*self.dim_bottom.Z)  # PEB IMPROVE HEIGHT
        
        # interface bottom - body 
        plane = bd.Plane(solid.faces().sort_by().last)
        solid += (bd.loft([plane * sbase, plane.offset(self.dim_bottom.Z/2) * wall]) - 
                 bd.loft([plane * ibase, plane.offset(self.dim_bottom.Z/2) * perimeter_internal]) )

        # body layer
        plane = bd.Plane(solid.faces().sort_by().last)
        solid += plane * bd.extrude(wall, amount=self.height - 2 * (1 + 2 + 0.5)*self.dim_bottom.Z - cbase - ctop)

        # interface body - top
        plane = bd.Plane(solid.faces().sort_by().last)
        solid += (bd.loft([plane * wall, plane.offset(self.dim_top.Z/2) * stop]) - 
                 bd.loft([plane * perimeter_internal, plane.offset(self.dim_top.Z/2) * itop]) )
        
        # top layer
        plane = bd.Plane(solid.faces().sort_by().last)
        solid += plane * bd.extrude(stop, amount=2*self.dim_top.Z)

        #add top fillet snap
        if (self.fillet_snap_top):        
            plane = bd.Plane(solid.faces().sort_by().last)
            solid += plane * self._fillet_snap_solid()
        
        #add bottom fillet snap
        if (self.fillet_snap_bottom):        
            plane = bd.Plane(solid.faces().sort_by().first).reverse()
            solid += plane * bd.mirror(self._fillet_snap_solid(), about=bd.Plane.XY)
            
        # add lid snap
        if (self.snap_top != 0):
            if ((self.snap_top == 1 and self.dim_top.X < self.dim_top.Y) or (self.snap_top == 2 and self.dim_top.X > self.dim_top.Y)):
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(0,1,0)))==1).sort_by(bd.Axis.Y)
                p1 = bd.Vector(0, perimeter_internal_top.vertices().sort_by(bd.Axis.Y) [0].Y, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
                p2 = bd.Vector(0, perimeter_internal_top.vertices().sort_by(bd.Axis.Y)[-1].Y, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
            else:
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(1,0,0)))==1).sort_by(bd.Axis.X)
                p1 = bd.Vector(perimeter_internal_top.vertices().sort_by(bd.Axis.X)[ 0].X, 0, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
                p2 = bd.Vector(perimeter_internal_top.vertices().sort_by(bd.Axis.X)[-1].X, 0, self.height -(self.dim_top.Z+self.flange_height_top-self.clearance.Z-self.flange_height_top/8))
                
            plane = bd.Plane(sorted_faces[2]).shift_origin(p1)
            solid += plane * self._snap_top_solid()
            plane = bd.Plane(sorted_faces[-3]).shift_origin(p2)
            solid += plane * self._snap_top_solid()
            
        # add base snap
        if (self.snap_bottom != 0):
            pts = [(0, 0), (2.75, 0), (4.45, 1.7), (-4.45, 1.7), (-2.75, 0), (0, 0)]
            ln = bd.Polyline(pts)

            if ((self.snap_bottom & 1 and self.dim_top.X < self.dim_top.Y) or (self.snap_bottom & 2 and self.dim_top.X > self.dim_top.Y)):
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(0,1,0)))==1).sort_by(bd.Axis.Y)
                p1 = bd.Vector(0, perimeter_internal_bottom.vertices().sort_by(bd.Axis.Y)[ 0].Y, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
                p2 = bd.Vector(0, perimeter_internal_bottom.vertices().sort_by(bd.Axis.Y)[-1].Y, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
                sketch = bd.Pos(0, 0, sorted_faces[-1].width/2-0.85) * bd.make_face(bd.Plane(sorted_faces[-1]).reverse() * ln)
                amount = self.dim_wall.X*2
            else:
                sorted_faces = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(1,0,0)))==1).sort_by(bd.Axis.X)
                p1 = bd.Vector(perimeter_internal_bottom.vertices().sort_by(bd.Axis.X)[ 0].X, 0, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
                p2 = bd.Vector(perimeter_internal_bottom.vertices().sort_by(bd.Axis.X)[-1].X, 0, self.dim_bottom.Z+self.flange_height_bottom-self.clearance.Z-self.flange_height_bottom/8)
                sketch = bd.Pos(0, 0, sorted_faces[-1].width/2-0.85) * bd.make_face(bd.Plane(sorted_faces[-1]) * ln)
                amount = -self.dim_wall.X*2
            
            plane = bd.Plane(sorted_faces[2]).shift_origin(p1)
            solid += plane * self._snap_bottom_solid()
            plane = bd.Plane(sorted_faces[-3]).shift_origin(p2)
            solid += plane * self._snap_bottom_solid()     
            
            solid -= bd.extrude(sketch, amount=amount)
            
        # hole for the screw driver
        

        return solid
 
    def _fillet_path(self, bottom_top):
        match bottom_top:
            case 0: # bottom
                _sketch = self._bottom_sketch()
            case 1: # top
                _sketch = self._top_sketch()
       
        # adjust for clearance
        if (self.clearance.X != 0):
            _sketch = bd.offset(_sketch, amount=self.clearance.X)

        # convert to ordered path
        _path = shape_to_ordered_path(_sketch)        
        
        return _path 

    def _fillet_sketch(self, _fillet_type):
        # create profile
        _sketch =  bd.Polyline(self.pts_fillet_profiles[_fillet_type])
        
        return _sketch
         
    def _fillet_solid(self, _bottom_top, _type):
        # retrieve fillet path and profile
        _path = self._fillet_path(_bottom_top)                
        _sketch = self._fillet_sketch(_type)
        
        # correct position and rotation
         
        rot = bd.Vector([[[90, 0, 180], [90, 180, 180]],
                         [[90, 0,   0], [90, 10,   0]] ][_bottom_top][_type])
        pos = bd.Vector([[[0, 0, 0], [0, 0, self.dim_bottom.Z/2]],
                         [[0, 0, self.height], [0, 0, self.height-self.dim_top.Z/2]]][_bottom_top][_type])
        _sketch = bd.Pos(pos) * bd.Pos(_path.edges()[0] @ 0) * bd.Rot(rot) * _sketch

        # create fillet section
        _sfillet_sections = [bd.Face.make_surface(_sketch)]

        # create fillet
        solid = bd.sweep(_sfillet_sections, _path, transition=bd.Transition.RIGHT)
        
        # position fillet
        
        return solid
    
    def top_fillet_solid(self):
        solid = self._fillet_solid(_bottom_top=1, _type=1)
        
        return solid 
  
    def bottom_fillet_solid(self):
        solid = self._fillet_solid(_bottom_top=0, _type=1)
        
        return solid 
  
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
  
class gm328A_case(parametric_box):
    global parametric_box, parametric_fillet             # for blendquery compability
    global board, lcd, encoder, led, zif, mkdsn, plug    # for blendquery compability
    global connector, magneto    
    def __init__(self,
                # box dimensions and clearances
                dim_top,                                    # external top dimension with Z as the top shell width/height
                dim_bottom,                                 # external bottom dimension with Z as the bottom shell width/height
                dim_wall,                                   # x = y = wall shell width, z = height
                clearance,                                  # reduces wall height and top/bottom external dimension      
                pos_top = bd.Vector(0,0,0),
                pos_bottom = bd.Vector(0,0,0),
                # box type
                base_type = 1,                              # 0 = base + wall fused, 1 = dettachable base
                edge_top = bd.Vector(1, 1, 1),              # defines the edge width(x=y) and height(z) that goes on top of the fillet     
                edge_bottom = bd.Vector(1, 1, 1),           # only used for base_type = 1
                # corner / z edges
                corners_type = 1,                           # Corners type: 0 straight, 1 fillet, 2 chamfer
                corners_size = 3.5,                         # Fillet radius/chamfer size for corners (z edges)
                # fillet/chamfer definition for top and bottom
                fillet_type_top = 2,                        # type of fillet/chamfer at top: 0 = none, 1 integrated fillet, 2 as an independent fillet part, 3 integrated chamfer, 4 as an independent chamfer part
                fillet_dim_top = bd.Vector(2, 2, 2),        # x = y = width and z = height
                fillet_size_top = 1.5,                      # fillet radius/chamfer size
                fillet_type_bottom = 2,                     # type of fillet/chamfer at bottom: 0 = none, 1 integrated fillet, 2 as an independent fillet part, 3 integrated chamfer, 4 as an independent chamfer part
                fillet_dim_bottom = bd.Vector(2, 2, 2),     # x = width, y = fillet radius/chamfer size, z = height
                fillet_size_bottom = 1.5,                   # fillet radius/chamfer size
                # flange for dettachable top/bottom
                flange_width_top = 2,                       # applied to the lid
                flange_height_top = 4,
                flange_width_bottom = 2,                    # applied to the base when dettachable
                flange_height_bottom = 4,
                # lid/base snap     
                snap_top = 1,                                # 0 = no lid snap, 1 lid_snap shorter side, 2 lid_snap longer side, 3 lid snap both sides
                snap_bottom = 1                              # 0 = no base snap, 1 base_snap shorter side, 2 base_snap longer side, 3 base snap both sides
                
                ):
        super().__init__(dim_top, dim_bottom,  dim_wall, clearance, pos_top, pos_bottom)

        # specific properties
        self.board = board()
        self.zif = zif(pos=bd.Vector(self.board.d.X/2 - 14.5, 
                                      self.board.d.Y/2 + clearance.Y, 
                                      self.dim_bottom.Z + self.clearance.Z + self.board.solder + self.board.d.Z),
                        edge = self.edge_top.Y
                        )
        self.internal_flange_height = 10
        return None
        
    def _internal_flange_sketch(self):
        szif = self.zif.sketch()
        sinternal_flange = bd.offset(szif, amount=self.flange_width_top/2) - szif 
        plane = bd.Plane.XZ.offset(-self.board.d.Y/2)
        sinternal_flange = bd.split(sinternal_flange, bisect_by=plane)
        return sinternal_flange

    def _internal_flange_solid(self):
        _s = self._internal_flange_sketch()
        internal_flange = bd.Pos(0,0, (self.height  - self.dim_top.Z + self.clearance.Z) - self.internal_flange_height) * bd.extrude(_s, amount=self.internal_flange_height)
        return internal_flange

    def top_solid(self):
        solid = parametric_box.top_solid(self)
        
        # add internal flange
        solid += self._internal_flange_solid()
        
        # remove LCD
        lcd_position = bd.Vector(-self.board.d.X/2 + 6.9,  -self.board.d.Y/2 + 8.95, self.height - self.dim_top.Z)
        solid -= lcd(pos=lcd_position, clearance=self.clearance).solid_hole_upwards()
        
        # remove encoder
        enc_position = bd.Vector(self.board.d.X/2 - 2.5, -self.board.d.Y/2 + 3.50, self.height - self.dim_top.Z)
        solid -= encoder(pos=enc_position).solid_hole_upwards()
        
        # remove led
        led_position = bd.Vector(-self.board.d.X/2 + 3, -self.board.d.Y/2 + 6.5, self.height - self.dim_top.Z)
        solid -= led(pos=led_position).solid_hole_upwards()
        
        # remove mkdns
        solid -= bd.Pos(0, 0, self.height - self.dim_top.Z) * mkdsn(self.board, self.clearance.X).solid_hole_upwards()
        
        # remove zif
        solid -= self.zif.solid_hole_outwards()
        
        # remove plug
        plug_position = bd.Vector(8.15, -self.board.d.Y/2, self.dim_bottom.Z + self.board.solder + self.board.d.Z)
        solid -= plug(plug_position).solid_hole_outwards()   
        
        return solid

    def bottom_solid(self):
        solid = parametric_box.bottom_solid(self)
        solid_aux = parametric_box.wall_solid(self)
                
        # add connector
        leftmost = solid_aux.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(1,0,0)))==1).sort_by(bd.Axis.X)[0]
        height, width = leftmost.width, leftmost.length      
        center_aux = leftmost.center_location.position
        
        bottommost = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(0,0,1)))==1).sort_by(bd.Axis.Z)[0]
        center = bottommost.center_location.position
        center.X = bottommost.vertices().sort_by(bd.Axis.X)[0].X + height/2        
        
        hr = [loc * bd.Rot(0, -90, 0) * connector().hole_reinforcement()
              for loc in bd.Locations((center.X+height/6, center.Y-width/2+5, center.Z+connector().length_reinf),
                                      (center.X-height/8, center.Y+0,         center.Z+connector().length_reinf),
                                      (center.X+height/6, center.Y+width/2-5, center.Z+connector().length_reinf),)] 
        he = [loc * bd.Rot(0, -90, 0) * connector().hole_empty()
             for loc in bd.Locations((center.X+height/6, center.Y-width/2+5, center.Z+connector().length_empty),
                                     (center.X-height/8, center.Y+0,         center.Z+connector().length_empty),
                                     (center.X+height/6, center.Y+width/2-5, center.Z+connector().length_empty))]                
        mr = [loc * bd.Rot(0, -90, 0) * magneto().hole_reinforcement()
              for loc in bd.Locations((center.X-height*0, center.Y-width/10, center.Z+magneto().length_reinf),
                                      (center.X-height*0, center.Y+width/10, center.Z+magneto().length_reinf))]                
        me = [loc * bd.Rot(0, -90, 0) * magneto().hole_empty()
              for loc in bd.Locations((center.X-height*0, center.Y-width/10, center.Z+magneto().length_empty),
                                      (center.X-height*0, center.Y+width/10, center.Z+magneto().length_empty))]                
        solid += hr
        solid -= he   
        solid += mr
        solid -= me           
        
        
        # add board fixers
        locations = bd.Locations((self.board.dxy.X, self.board.dxy.Y, self.dim_bottom.Z-self.clearance.Z),
                                 (self.board.dxY.X, self.board.dxY.Y, self.dim_bottom.Z-self.clearance.Z),
                                 (self.board.dXy.X, self.board.dXy.Y, self.dim_bottom.Z-self.clearance.Z),
                                 (self.board.dXY.X, self.board.dXY.Y, self.dim_bottom.Z-self.clearance.Z))            
        hr = [loc * bd.Cylinder(radius=self.board.hole_pos-0.2, height=self.flange_height_bottom, align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
              for loc in locations]    
        he = [loc * bd.Cylinder(radius=3/2, height=self.flange_height_bottom, align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
              for loc in locations]
        solid += hr
        solid -= he  
        
        return solid 

    def wall_solid(self):
        solid = parametric_box.wall_solid(self)
        
        # add connector
        leftmost = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(1,0,0)))==1).sort_by(bd.Axis.X)[0]
        height, width = leftmost.width, leftmost.length
        center = leftmost.center_location.position
        hr = [loc * connector().hole_reinforcement()
              for loc in bd.Locations((center.X+connector().length_reinf, center.Y-width/2+5, center.Z-height/6),
                                      (center.X+connector().length_reinf, center.Y+0,         center.Z+height/8),
                                      (center.X+connector().length_reinf, center.Y+width/2-5, center.Z-height/6),)] 
        he = [loc * connector().hole_empty()
             for loc in bd.Locations((center.X+connector().length_empty, center.Y-width/2+5, center.Z-height/6),
                                     (center.X+connector().length_empty, center.Y+0,         center.Z+height/8),
                                     (center.X+connector().length_empty, center.Y+width/2-5, center.Z-height/6))]                
        mr = [loc * magneto().hole_reinforcement()
              for loc in bd.Locations((center.X+magneto().length_reinf, center.Y-width/10, center.Z+height*0),
                                      (center.X+magneto().length_reinf, center.Y+width/10, center.Z+height*0))]                
        me = [loc * magneto().hole_empty()
              for loc in bd.Locations((center.X+magneto().length_empty, center.Y-width/10, center.Z+height*0),
                                      (center.X+magneto().length_empty, center.Y+width/10, center.Z+height*0))]                
        solid += hr
        solid -= he   
        solid += mr
        solid -= me       
                    
        # remove zif open
        solid -= self.zif.solid_hole_outwards()
        
        # remove plug
        plug_position = bd.Vector(8.15, -self.board.d.Y/2, self.dim_bottom.Z + self.board.solder + self.board.d.Z)
        solid -= plug(plug_position).solid_hole_outwards()   
        
        # remove mkdsn (PEB - THIS IS HORRIBLE)
        solid -= bd.Pos(0, 0, 0) * mkdsn(self.board, self.clearance.X).solid_hole_outwards(self)
        
        return solid
   
    def top_fillet_solid(self):
        solid = parametric_box.top_fillet_solid(self)

        # remove zif open
        solid -= self.zif.solid_hole_outwards()
        
        return solid 
    
    def board_solid(self):
        solid = self.board.solid()
        solid = bd.Pos(0, 0, self.dim_wall.X + self.board.solder + self.board.d.Z/2) * solid
        
        return solid
               
class gm328A_battery(parametric_box):
    global parametric_box, parametric_fillet             # for blendquery compability
    global board, lcd, encoder, led, zif, mkdsn, plug    # for blendquery compability
    global connector, magneto    
    def __init__(self,
                # box dimensions and clearances
                dim_top,                                    # external top dimension with Z as the top shell width/height
                dim_bottom,                                 # external bottom dimension with Z as the bottom shell width/height
                dim_wall,                                   # x = y = wall shell width, z = height
                clearance,                                  # reduces wall height and top/bottom external dimension      
                pos_top = bd.Vector(0,0,0),
                pos_bottom = bd.Vector(0,0,0),
                # box type
                base_type = 1,                              # 0 = base + wall fused, 1 = dettachable base
                edge_top = bd.Vector(1, 1, 1),              # defines the edge width(x=y) and height(z) that goes on top of the fillet     
                edge_bottom = bd.Vector(1, 1, 1),           # only used for base_type = 1
                # corner / z edges
                corners_type = 1,                           # Corners type: 0 straight, 1 fillet, 2 chamfer
                corners_size = 3.5,                         # Fillet radius/chamfer size for corners (z edges)
                # fillet/chamfer definition for top and bottom
                fillet_type_top = 2,                        # type of fillet/chamfer at top: 0 = none, 1 integrated fillet, 2 as an independent fillet part, 3 integrated chamfer, 4 as an independent chamfer part
                fillet_dim_top = bd.Vector(2, 2, 2),        # x = y = width and z = height
                fillet_size_top = 1.5,                      # fillet radius/chamfer size
                fillet_type_bottom = 2,                     # type of fillet/chamfer at bottom: 0 = none, 1 integrated fillet, 2 as an independent fillet part, 3 integrated chamfer, 4 as an independent chamfer part
                fillet_dim_bottom = bd.Vector(2, 2, 2),     # x = width, y = fillet radius/chamfer size, z = height
                fillet_size_bottom = 1.5,                   # fillet radius/chamfer size
                # flange for dettachable top/bottom
                flange_width_top = 2,                       # applied to the lid
                flange_height_top = 4,
                flange_width_bottom = 2,                    # applied to the base when dettachable
                flange_height_bottom = 4,
                # lid/base snap     
                snap_top = 1,                                # 0 = no lid snap, 1 lid_snap shorter side, 2 lid_snap longer side, 3 lid snap both sides
                snap_bottom = 1                              # 0 = no base snap, 1 base_snap shorter side, 2 base_snap longer side, 3 base snap both sides                
                ):
        super().__init__(dim_top, dim_bottom,  dim_wall, clearance, pos_top, pos_bottom, snap_top=snap_top, snap_bottom=snap_bottom)

        return None   
        
    def wall_solid(self):
        solid = parametric_box.wall_solid(self)
        
        # add connector
        rightmost = solid.faces().filter_by(lambda f: abs(f.normal_at().dot(bd.Vector(1,0,0)))==1).sort_by(bd.Axis.X)[-1]
        height, width = rightmost.width, rightmost.length
        center = rightmost.center_location.position
        cs = [loc * connector().solid()
             for loc in bd.Locations((center.X+connector().length, center.Y-width/2+5, center.Z-height/6),
                                     (center.X+connector().length, center.Y+0,         center.Z+height/8),
                                     (center.X+connector().length, center.Y+width/2-5, center.Z-height/6))]                
        mr = [loc * magneto().hole_reinforcement()
              for loc in bd.Locations((center.X, center.Y-width/10, center.Z+height*0),
                                      (center.X, center.Y+width/10, center.Z+height*0))]                
        me = [loc * magneto().hole_empty()
              for loc in bd.Locations((center.X, center.Y-width/10, center.Z+height*0),
                                      (center.X, center.Y+width/10, center.Z+height*0))]                
        solid += cs
        solid += mr
        solid -= me     
        
        return solid
        
# #-----------------------------------------------------------------------------------------------------------------------
# #-----------------------------------------------------------------------------------------------------------------------


#*******************
# SOLIDS 
#*******************
clearance_xy   = 0.2
clearance_z    = 0.2
shell=2
dx, dy, dz = 78.7, 63.8, (1.52+15.1+4+2)
b_dx, b_dy, b_dz = 26, 52, 17

_y = gm328A_case(
        dim_top    = bd.Vector(dx+2*(shell+clearance_xy)+shell, dy+2*(shell+clearance_xy)+shell, shell),
        dim_bottom = bd.Vector(dx+2*(shell+clearance_xy)+shell, dy+2*(shell+clearance_xy)+shell, shell),
        dim_wall   = bd.Vector(shell, shell, dz - 2*shell - 2*clearance_z),
        clearance  = bd.Vector(clearance_xy, clearance_xy, clearance_z))
        

case_lid = _y.top_solid()
case_base = _y.bottom_solid()
case_top_fillet = _y.top_fillet_solid()
case_bottom_fillet = _y.bottom_fillet_solid()
case_wall = _y.wall_solid()

case_lid.material = "PLA Branco"
case_base.material = "PLA Branco"
case_top_fillet.material = "PLA Neon"
case_bottom_fillet.material = "PLA Neon"
case_wall.material = "PLA Branco"

_x = gm328A_battery(
        dim_top    = bd.Vector(b_dx+4*(shell+clearance_xy)+shell+2*clearance_xy, dy+2*(shell+clearance_xy)+shell, shell),
        dim_bottom = bd.Vector(b_dx+4*(shell+clearance_xy)+shell+2*clearance_xy, dy+2*(shell+clearance_xy)+shell, shell),
        dim_wall   = bd.Vector(shell, shell, dz - 2*shell - 2*clearance_z),
        clearance  = bd.Vector(clearance_xy, clearance_xy, clearance_z))         

px = bd.Vector(-(78.7/2+26/2 + 20), 0, 0)
battery_lid = bd.Pos(px) * _x.top_solid()
battery_base = bd.Pos(px) *  _x.bottom_solid()
battery_top_fillet = bd.Pos(px) * _x.top_fillet_solid()
battery_bottom_fillet = bd.Pos(px) * _x.bottom_fillet_solid()
battery_wall = bd.Pos(px) * _x.wall_solid()

battery_lid.material = "PLA Branco"
battery_base.material = "PLA Branco"
battery_top_fillet.material = "PLA Neon"
battery_bottom_fillet.material = "PLA Neon"
battery_wall.material = "PLA Branco"
