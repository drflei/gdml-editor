
import pyg4ometry.geant4 as g4
import pyg4ometry.gdml as gdml

def create_simple_world():
    # Create Registry
    reg = g4.Registry()
    
    # Create Material (Air)
    # Trying NIST lookup first
    try:
        air = g4.nist_material_2geant4Material("G4_AIR", reg)
    except Exception as e:
        print(f"NIST lookup failed ({e}), creating Air manually")
        # Elements
        n = g4.Element("Nitrogen", "N", 7, 14.01, reg)
        o = g4.Element("Oxygen",   "O", 8, 16.00, reg)
        # Material
        air = g4.Material("G4_AIR", 1.29e-3, 2, reg) # density g/cm3
        air.add_element_massfraction(n, 0.7)
        air.add_element_massfraction(o, 0.3)

    # World Volume Dimensions
    # 5m x 5m x 5m
    # Geant4 Box takes half-lengths in internal units (mm)
    # 5m = 5000mm -> half-length = 2500mm
    world_dx = 2500.0
    world_dy = 2500.0
    world_dz = 2500.0
    
    # Solid
    world_solid = g4.solid.Box("WorldSolid", world_dx, world_dy, world_dz, reg)
    
    # Logical Volume
    world_lv = g4.LogicalVolume(world_solid, air, "World", reg)
    
    # Set Registry World
    reg.setWorld(world_lv)
    
    # Write to GDML
    output_file = "simple_world_5m.gdml"
    writer = gdml.Writer()
    writer.addDetector(reg)
    writer.write(output_file)
    print(f"Successfully created {output_file}")

if __name__ == "__main__":
    create_simple_world()
