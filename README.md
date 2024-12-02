# 3D Printed Parametric Case

## Project Overview
This project explores the capabilities of **Build123d** as a modeling tool, with the aim of creating a parametric box featuring multi-color fillets and chamfers. The design takes inspiration from Perinski's creations on [MyMiniFactory](https://www.myminifactory.com/users/Perinski). Additionally, the project includes modeling an assembled circuit board (GM328A Test Kit) using the Printed Circuit Board FreeCAD add-on.

## Key Objectives
1. Explore **Build123d** as a 3D modeling tool.
2. Create a parametric case with customizable fillets and chamfers in various colors.
3. Model an assembled GM328A circuit board using the FreeCAD Printed Circuit Board add-on.

## Features of Build123d
**Build123d** is a powerful tool for Boundary Representation (BREP) modeling with several notable features:
- **Alternative to OpenSCAD**: Unlike mesh-based modeling, Build123d uses BREP modeling, providing more detailed and versatile structures.
- **Python Library**: Build123d can be integrated with other Python libraries, making it suitable for scientific explorations such as FEM analysis and optimization.
- **FreeCAD Integration**: Build123d shares the same OpenCascade (OCCT) engine as FreeCAD, allowing for seamless transition and further refinement in FreeCAD.

For more information, refer to the [Build123d documentation](https://build123d.readthedocs.io/en/latest/introduction.html).

## Integration with FreeCAD
- **FreeCAD 1.0** was installed in a Miniconda environment.
- The latest versions of **CadQuery** and **Build123d** were installed within the same environment.
- The **FreeCAD CadQuery Add-on** was installed manually (not using the Add-on Manager).
- A final step is necessary in the code to convert Build123d objects into CadQuery objects.
- The **Printed Circuit Board Add-on** was used for circuit board modeling.

## Integration with Blender (BlendQuery)
- The **BlendQuery add-on** was installed in **Blender 4.0**.
- Although some bugs were encountered (requiring the declaration of libraries as global), the integration proved functional.

## Proof of Concept: GM328A Electronic Tester Case
### Design Details
Two new classes were derived from the base parametric box class (parametric_box class to model:
1. The main case (gm328A_case class).
2. A detachable battery case (gm328A_battery class), which can be connected horizontally and vertically to the main case (see pictures of final product) 

### Scripts
- **Python in VSCode** with the **OCP extension**: [python script](https://github.com/pbrugugnoli/parametric_case/blob/main/scripts/GM328A%20Case%20-%20VSCode%20%2B%20OCP.py)
- **FreeCAD** with the **CadQuery add-on**: [python script](https://github.com/pbrugugnoli/parametric_case/blob/main/scripts/GM328A%20Case%20-%20Freecad%20%2B%20Cadquery%20Add-on.py)
- **Blender** with the **BlendQuery add-on**: [python script](https://github.com/pbrugugnoli/parametric_case/blob/main/scripts/Blender%20%2B%20Blendquery.py)

### Outputs
- **Rendered Images in Blender**:
  - Battery connected horizontally
  <img src="https://github.com/pbrugugnoli/parametric_case/blob/main/rendered%20images/GM328A%20%2B%20Battery%20cases%20-%20storage%20assembly.jpg" width="600" />
  
  - Battery connected vertically
  <img src="https://github.com/pbrugugnoli/parametric_case/blob/main/rendered%20images/GM328A%20%2B%20Battery%20cases%20-%20working%20assembly.jpg" width="600" />
  
- **Final Product Images**:
  - Battery connected horizontally
  <img src="https://github.com/pbrugugnoli/parametric_case/blob/main/Final%20Product/Case%20GM328A_01.jpg" width="600" />
  
  - Battery connected vertically
  <img src="https://github.com/pbrugugnoli/parametric_case/blob/main/Final%20Product/Case%20GM328A_02.jpg" width="600" />

## Conclusions
- It is feasible to create general parametric object classes that can be further specialized in derived classes and methods.
- While **Build123d** is more complex than **OpenSCAD**, it provides an organized, class-based approach to modeling.
- Modeling can be done using basic geometric volumes similar to OpenSCAD, or more advanced CAD techniques involving sketches and extrusions.
- FreeCAD or Blender with the **Cad Sketcher** add-on can model the same object faster, but Build123d offers greater flexibility and integration potential.

---
Feel free to explore the project, experiment with the scripts, and adapt them for your own 3D modeling and printing needs!
Note that this is just a documentation repository and I am not intend to evolve or support these scripts

