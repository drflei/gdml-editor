#!/usr/bin/env python3
"""Simple GDML viewer using pyg4ometry - exports to various formats."""

import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="View a GDML file using pyg4ometry")
    parser.add_argument("gdml_file", help="Path to the GDML file to visualize")
    parser.add_argument("--format", choices=["wrl", "obj", "stl", "vtk"], default="wrl",
                        help="Export format (default: wrl for VRML)")
    parser.add_argument("--output", help="Output file name (default: based on input GDML name)")
    parser.add_argument("--interactive", action="store_true",
                        help="Try interactive VTK viewer (may crash on WSL/headless)")
    args = parser.parse_args()

    gdml_path = Path(args.gdml_file)
    if not gdml_path.exists():
        print(f"Error: GDML file not found: {gdml_path}", file=sys.stderr)
        return 1

    # Set output filename
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = gdml_path.with_suffix(f".{args.format}")

    try:
        # Block Intel graphics drivers that cause LLVM conflicts in WSL
        os.environ["__GLX_VENDOR_LIBRARY_NAME"] = "mesa"
        os.environ["LIBGL_ALWAYS_SOFTWARE"] = "true"  
        os.environ["GALLIUM_DRIVER"] = "llvmpipe"
        # Completely disable D3D12 drivers
        os.environ["MESA_D3D12_DEFAULT_ADAPTER_NAME"] = "llvmpipe"
        os.environ["LD_PRELOAD"] = ""  # Clear any preloads
        
        import pyg4ometry
        import vtk
        
        # Read GDML file
        print(f"Reading GDML: {gdml_path}")
        reader = pyg4ometry.gdml.Reader(str(gdml_path))
        reg = reader.getRegistry()
        world_lv = reg.getWorldVolume()
        
        if args.interactive:
            print("Launching VTK viewer with pure software rendering...")
            
            # Create viewer - this builds all the VTK pipeline internally
            viewer = pyg4ometry.visualisation.VtkViewer()
            viewer.addLogicalVolume(world_lv)
            
            # Try to use OSMesa render window (pure software, no hardware drivers)
            try:
                from vtk import vtkOSOpenGLRenderWindow
                render_window = vtkOSOpenGLRenderWindow()
                print("Using OSMesa (software-only) render window")
            except (ImportError, AttributeError):
                # Create a new offscreen window
                import vtk
                render_window = vtk.vtkRenderWindow()
                render_window.SetOffScreenRendering(1)
                print("Using offscreen render window")
            
            # Set up renderer
            import vtk
            renderer = vtk.vtkRenderer()
            render_window.AddRenderer(renderer)
            renderer.SetBackground(0.1, 0.1, 0.1)
            
            # Add all actors from the viewer
            for actor in viewer.actors:
                renderer.AddActor(actor)
            
            # Set up camera
            renderer.ResetCamera()
            
            # Set window size
            render_window.SetSize(1920, 1080)
            
            # Render
            print("Rendering scene...")
            render_window.Render()
            
            # Save screenshot
            output_img = gdml_path.with_suffix('.png')
            print(f"Saving image to: {output_img}")
            
            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(render_window)
            w2if.Update()
            
            writer = vtk.vtkPNGWriter()
            writer.SetFileName(str(output_img))
            writer.SetInputConnection(w2if.GetOutputPort())
            writer.Write()
            
            print(f"\n✓ Successfully rendered to: {output_img}")
            print("Open the PNG file to view the geometry.")
        else:
            # Export to file format
            print(f"Exporting to {args.format.upper()}: {output_path}")
            
            if args.format == "wrl":
                # VRML export
                viewer = pyg4ometry.visualisation.VtkViewer()
                viewer.addLogicalVolume(world_lv)
                viewer.exportVRMLScene(str(output_path))
            elif args.format == "obj":
                # OBJ export
                from pyg4ometry.visualisation import MeshWriter
                mesh_writer = MeshWriter.MeshWriter()
                mesh_writer.addLogicalVolume(world_lv)
                mesh_writer.write(str(output_path.with_suffix("")))
            elif args.format == "stl":
                # STL export
                viewer = pyg4ometry.visualisation.VtkViewer()
                viewer.addLogicalVolume(world_lv)
                viewer.exportSTLFile(str(output_path))
            elif args.format == "vtk":
                # VTK export
                viewer = pyg4ometry.visualisation.VtkViewer()
                viewer.addLogicalVolume(world_lv)
                viewer.exportVTKFile(str(output_path))
            
            print(f"Successfully exported to: {output_path}")
        
        return 0
    except Exception as e:
        print(f"Error processing GDML: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
