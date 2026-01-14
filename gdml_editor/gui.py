#!/usr/bin/env python3
"""GUI application for editing GDML geometry files.

Built on the same approach as run_vtkviewer.py, this provides a graphical
interface for:
  1. Opening GDML files
  2. Displaying logical volume structure
  3. Picking volumes and viewing properties
  4. Changing materials
  5. Saving modified geometry
  6. Viewing in VTK viewer

Fixes the same sys.modules issue as run_vtkviewer.py.
"""

import sys
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# FIX: Clear any cached VtkViewer modules that cause the frozen runpy warning
modules_to_clear = [k for k in sys.modules.keys() if 'VtkViewer' in k]
for mod in modules_to_clear:
    del sys.modules[mod]

# Ensure DISPLAY is set for X11
os.environ["DISPLAY"] = ":0"


class UserMaterialDatabase:
    """Database for user-defined materials."""
    
    def __init__(self, db_file="user_materials.json"):
        self.db_file = Path.home() / ".gdml_editor" / db_file
        self.materials = {}
        self.load()
    
    def load(self):
        """Load materials from database file."""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r') as f:
                    self.materials = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load material database: {e}")
                self.materials = {}
        else:
            self.materials = {}
    
    def save(self):
        """Save materials to database file."""
        try:
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_file, 'w') as f:
                json.dump(self.materials, f, indent=2)
        except Exception as e:
            print(f"Error: Could not save material database: {e}")
            raise
    
    def add_material(self, name, material_data):
        """Add or update a material.
        
        Args:
            name: Material name
            material_data: Dictionary with keys:
                - type: 'compound' or 'mixture'
                - density: Density value (float)
                - density_unit: 'g/cm3', 'mg/cm3', 'kg/m3'
                - composition: For compound, molecular formula string (e.g., 'H2O')
                              For mixture, list of dicts with 'element' and 'fraction' keys
                - state: 'solid', 'liquid', 'gas' (optional, default 'solid')
                - temperature: Temperature value (optional)
                - temp_unit: 'K', 'C' (optional)
                - pressure: Pressure value (optional)
                - pressure_unit: 'pascal', 'bar', 'atm' (optional)
        """
        self.materials[name] = material_data
        self.save()
    
    def remove_material(self, name):
        """Remove a material."""
        if name in self.materials:
            del self.materials[name]
            self.save()
            return True
        return False
    
    def get_material(self, name):
        """Get material data by name."""
        return self.materials.get(name)
    
    def list_materials(self):
        """Get list of all material names."""
        return sorted(self.materials.keys())
    
    def get_all_materials(self):
        """Get all materials as dictionary."""
        return self.materials.copy()


class MaterialDefinitionDialog:
    """Dialog for defining a new material or editing existing one."""
    
    # Periodic table elements with symbols
    ELEMENTS = [
        'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
        'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
        'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
        'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
        'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
        'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
        'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
        'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
        'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
        'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
        'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
    ]
    
    # Common elements for quick reference
    COMMON_ELEMENTS = [
        'H', 'C', 'N', 'O', 'F', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl',
        'Ca', 'Ti', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ag', 'Sn',
        'W', 'Pt', 'Au', 'Pb', 'U'
    ]
    
    def __init__(self, parent, user_db, material_name=None):
        self.result = None
        self.user_db = user_db
        self.material_name = material_name
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Define Material" if not material_name else f"Edit Material: {material_name}")
        self.dialog.geometry("700x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Load existing material if editing
        if material_name:
            self.load_material(material_name)
        
    def setup_ui(self):
        """Create the UI for material definition."""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Material Name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Material Name:", width=20).pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=self.material_name or "")
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=40)
        name_entry.pack(side=tk.LEFT, padx=5)
        if self.material_name:
            name_entry.config(state='readonly')
        
        # Material Type
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Material Type:", width=20).pack(side=tk.LEFT)
        self.material_type = tk.StringVar(value="compound")
        ttk.Radiobutton(type_frame, text="Compound (Formula)", variable=self.material_type,
                       value="compound", command=self.update_composition_ui).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Mixture (Elements)", variable=self.material_type,
                       value="mixture", command=self.update_composition_ui).pack(side=tk.LEFT, padx=5)
        
        # Density
        density_frame = ttk.Frame(main_frame)
        density_frame.pack(fill=tk.X, pady=5)
        ttk.Label(density_frame, text="Density:", width=20).pack(side=tk.LEFT)
        self.density_var = tk.StringVar()
        ttk.Entry(density_frame, textvariable=self.density_var, width=15).pack(side=tk.LEFT, padx=5)
        self.density_unit_var = tk.StringVar(value="g/cm3")
        density_unit_combo = ttk.Combobox(density_frame, textvariable=self.density_unit_var,
                                         values=["g/cm3", "mg/cm3", "kg/m3"], state='readonly', width=10)
        density_unit_combo.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Composition Frame (will be updated based on type)
        self.composition_container = ttk.LabelFrame(main_frame, text="Composition", padding=10)
        self.composition_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initialize composition UI
        self.update_composition_ui()
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Advanced Properties (collapsible)
        self.show_advanced = tk.BooleanVar(value=False)
        advanced_check = ttk.Checkbutton(main_frame, text="Show Advanced Properties (State, Temperature, Pressure)",
                                        variable=self.show_advanced, command=self.toggle_advanced)
        advanced_check.pack(fill=tk.X, pady=5)
        
        self.advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Properties", padding=10)
        
        # State
        state_frame = ttk.Frame(self.advanced_frame)
        state_frame.pack(fill=tk.X, pady=5)
        ttk.Label(state_frame, text="State:", width=15).pack(side=tk.LEFT)
        self.state_var = tk.StringVar(value="solid")
        ttk.Combobox(state_frame, textvariable=self.state_var,
                    values=["solid", "liquid", "gas"], state='readonly', width=15).pack(side=tk.LEFT, padx=5)
        
        # Temperature
        temp_frame = ttk.Frame(self.advanced_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        ttk.Label(temp_frame, text="Temperature:", width=15).pack(side=tk.LEFT)
        self.temp_var = tk.StringVar()
        ttk.Entry(temp_frame, textvariable=self.temp_var, width=15).pack(side=tk.LEFT, padx=5)
        self.temp_unit_var = tk.StringVar(value="K")
        ttk.Combobox(temp_frame, textvariable=self.temp_unit_var,
                    values=["K", "C"], state='readonly', width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(temp_frame, text="(optional)").pack(side=tk.LEFT)
        
        # Pressure
        pressure_frame = ttk.Frame(self.advanced_frame)
        pressure_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pressure_frame, text="Pressure:", width=15).pack(side=tk.LEFT)
        self.pressure_var = tk.StringVar()
        ttk.Entry(pressure_frame, textvariable=self.pressure_var, width=15).pack(side=tk.LEFT, padx=5)
        self.pressure_unit_var = tk.StringVar(value="pascal")
        ttk.Combobox(pressure_frame, textvariable=self.pressure_unit_var,
                    values=["pascal", "bar", "atm"], state='readonly', width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(pressure_frame, text="(optional)").pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Save Material", command=self.save_material).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
    def update_composition_ui(self):
        """Update composition UI based on material type."""
        # Clear existing widgets
        for widget in self.composition_container.winfo_children():
            widget.destroy()
        
        if self.material_type.get() == "compound":
            # Compound: molecular formula
            ttk.Label(self.composition_container, 
                     text="Enter molecular formula (e.g., H2O, SiO2, CaCO3):").pack(anchor=tk.W, pady=5)
            
            self.formula_var = tk.StringVar()
            formula_entry = ttk.Entry(self.composition_container, textvariable=self.formula_var, width=50)
            formula_entry.pack(fill=tk.X, pady=5)
            
            ttk.Label(self.composition_container, 
                     text="Examples: H2O, C6H12O6, Al2O3, PbF2, CaCO3",
                     font=('TkDefaultFont', 8, 'italic')).pack(anchor=tk.W, pady=5)
            
        else:
            # Mixture: element fractions
            ttk.Label(self.composition_container,
                     text="Define mixture by mass fraction (fractions must sum to 1.0):").pack(anchor=tk.W, pady=5)
            
            # Element reference hint
            hint_frame = ttk.Frame(self.composition_container)
            hint_frame.pack(fill=tk.X, pady=5)
            ttk.Label(hint_frame, text="💡 Tip:", font=('TkDefaultFont', 8, 'bold')).pack(side=tk.LEFT)
            ttk.Label(hint_frame, 
                     text="Use dropdown to select elements from periodic table. Type to filter (e.g., 'Fe' for Iron).",
                     font=('TkDefaultFont', 8, 'italic')).pack(side=tk.LEFT, padx=5)
            
            # Common elements quick reference
            common_frame = ttk.Frame(self.composition_container)
            common_frame.pack(fill=tk.X, pady=5)
            ttk.Label(common_frame, text="Common elements:", 
                     font=('TkDefaultFont', 8)).pack(side=tk.LEFT)
            ttk.Label(common_frame, 
                     text=" | ".join(self.COMMON_ELEMENTS),
                     font=('TkDefaultFont', 8, 'italic')).pack(side=tk.LEFT, padx=5)
            
            # Scrollable frame for elements
            canvas = tk.Canvas(self.composition_container, height=200)
            scrollbar = ttk.Scrollbar(self.composition_container, orient="vertical", command=canvas.yview)
            self.mixture_frame = ttk.Frame(canvas)
            
            self.mixture_frame.bind("<Configure>", 
                                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            canvas.create_window((0, 0), window=self.mixture_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Element entries list
            self.element_entries = []
            
            # Add initial element row
            self.add_element_row()
            
            # Add button
            ttk.Button(self.composition_container, text="Add Element", 
                      command=self.add_element_row).pack(pady=5)
    
    def add_element_row(self):
        """Add a row for element input with dropdown selection."""
        row_frame = ttk.Frame(self.mixture_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(row_frame, text="Element:", width=10).pack(side=tk.LEFT, padx=2)
        element_var = tk.StringVar()
        # Use Combobox with element list for easy selection
        element_combo = ttk.Combobox(row_frame, textvariable=element_var, 
                                     values=self.ELEMENTS, width=10, state='normal')
        element_combo.pack(side=tk.LEFT, padx=2)
        
        # Add autocomplete behavior - filter as user types
        def on_element_key(event):
            typed = element_var.get().upper()
            if typed:
                # Filter elements that start with typed text
                filtered = [e for e in self.ELEMENTS if e.upper().startswith(typed)]
                element_combo['values'] = filtered if filtered else self.ELEMENTS
            else:
                element_combo['values'] = self.ELEMENTS
        
        element_combo.bind('<KeyRelease>', on_element_key)
        
        ttk.Label(row_frame, text="Mass Fraction:", width=12).pack(side=tk.LEFT, padx=2)
        fraction_var = tk.StringVar()
        fraction_entry = ttk.Entry(row_frame, textvariable=fraction_var, width=10)
        fraction_entry.pack(side=tk.LEFT, padx=2)
        
        # Remove button
        remove_btn = ttk.Button(row_frame, text="Remove", width=8,
                               command=lambda: self.remove_element_row(row_frame))
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        self.element_entries.append({
            'frame': row_frame,
            'element': element_var,
            'fraction': fraction_var
        })
    
    def remove_element_row(self, frame):
        """Remove an element row."""
        if len(self.element_entries) > 1:
            for i, entry in enumerate(self.element_entries):
                if entry['frame'] == frame:
                    frame.destroy()
                    del self.element_entries[i]
                    break
    
    def toggle_advanced(self):
        """Toggle advanced properties visibility."""
        if self.show_advanced.get():
            self.advanced_frame.pack(fill=tk.X, pady=5, before=self.composition_container.master.winfo_children()[-1])
        else:
            self.advanced_frame.pack_forget()
    
    def load_material(self, name):
        """Load existing material data into form."""
        mat_data = self.user_db.get_material(name)
        if not mat_data:
            return
        
        self.material_type.set(mat_data.get('type', 'compound'))
        self.density_var.set(str(mat_data.get('density', '')))
        self.density_unit_var.set(mat_data.get('density_unit', 'g/cm3'))
        
        # Update composition UI first
        self.update_composition_ui()
        
        if mat_data['type'] == 'compound':
            self.formula_var.set(mat_data.get('composition', ''))
        else:
            # Load mixture
            composition = mat_data.get('composition', [])
            # Clear default row
            for entry in self.element_entries[:]:
                entry['frame'].destroy()
            self.element_entries = []
            
            # Add rows for each element
            for comp in composition:
                self.add_element_row()
                self.element_entries[-1]['element'].set(comp.get('element', ''))
                self.element_entries[-1]['fraction'].set(str(comp.get('fraction', '')))
        
        # Advanced properties
        if any(key in mat_data for key in ['state', 'temperature', 'pressure']):
            self.show_advanced.set(True)
            self.toggle_advanced()
            
            self.state_var.set(mat_data.get('state', 'solid'))
            if 'temperature' in mat_data:
                self.temp_var.set(str(mat_data['temperature']))
                self.temp_unit_var.set(mat_data.get('temp_unit', 'K'))
            if 'pressure' in mat_data:
                self.pressure_var.set(str(mat_data['pressure']))
                self.pressure_unit_var.set(mat_data.get('pressure_unit', 'pascal'))
    
    def save_material(self):
        """Validate and save material."""
        # Validate name
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Material name is required")
            return
        
        # Validate density
        try:
            density = float(self.density_var.get())
            if density <= 0:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Density must be a positive number")
            return
        
        # Build material data
        material_data = {
            'type': self.material_type.get(),
            'density': density,
            'density_unit': self.density_unit_var.get(),
        }
        
        # Composition
        if self.material_type.get() == 'compound':
            formula = self.formula_var.get().strip()
            if not formula:
                messagebox.showerror("Error", "Molecular formula is required")
                return
            material_data['composition'] = formula
        else:
            # Validate mixture
            composition = []
            total_fraction = 0.0
            
            for entry in self.element_entries:
                element = entry['element'].get().strip()
                fraction_str = entry['fraction'].get().strip()
                
                if not element and not fraction_str:
                    continue
                    
                if not element or not fraction_str:
                    messagebox.showerror("Error", "All element rows must have both element and fraction")
                    return
                
                try:
                    fraction = float(fraction_str)
                    if fraction <= 0 or fraction > 1:
                        raise ValueError()
                except:
                    messagebox.showerror("Error", f"Invalid fraction for {element}: must be between 0 and 1")
                    return
                
                composition.append({'element': element, 'fraction': fraction})
                total_fraction += fraction
            
            if not composition:
                messagebox.showerror("Error", "At least one element is required for mixture")
                return
            
            if abs(total_fraction - 1.0) > 0.001:
                messagebox.showerror("Error", 
                    f"Mass fractions must sum to 1.0 (current sum: {total_fraction:.4f})")
                return
            
            material_data['composition'] = composition
        
        # Advanced properties
        material_data['state'] = self.state_var.get()
        
        temp = self.temp_var.get().strip()
        if temp:
            try:
                material_data['temperature'] = float(temp)
                material_data['temp_unit'] = self.temp_unit_var.get()
            except:
                messagebox.showerror("Error", "Invalid temperature value")
                return
        
        pressure = self.pressure_var.get().strip()
        if pressure:
            try:
                material_data['pressure'] = float(pressure)
                material_data['pressure_unit'] = self.pressure_unit_var.get()
            except:
                messagebox.showerror("Error", "Invalid pressure value")
                return
        
        # Save to database
        try:
            self.user_db.add_material(name, material_data)
            self.result = name
            messagebox.showinfo("Success", f"Material '{name}' saved successfully")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save material: {e}")


class InsertGDMLDialog:
    """Dialog for inserting volumes from another GDML file."""
    
    def __init__(self, parent, registry, world_lv):
        self.result = None
        self.registry = registry
        self.world_lv = world_lv
        self.ext_registry = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Insert GDML File")
        self.dialog.geometry("600x800")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File Selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_frame, text="GDML File:", width=15).pack(side=tk.LEFT)
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT)
        
        # Volume Selection (Source)
        src_vol_frame = ttk.LabelFrame(main_frame, text="Select Volumes to Import", padding=5)
        src_vol_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview for checklist
        tree_scroll = ttk.Scrollbar(src_vol_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.vol_tree = ttk.Treeview(src_vol_frame, columns=("status",), show="tree headings", 
                                    selectmode="extended", yscrollcommand=tree_scroll.set)
        self.vol_tree.heading("#0", text="Volume Name")
        self.vol_tree.heading("status", text="Status")
        self.vol_tree.column("#0", width=250)
        self.vol_tree.column("status", width=100)
        self.vol_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.vol_tree.yview)
        
        ttk.Label(src_vol_frame, text="Use Shift/Ctrl to select multiple", 
                 font=('TkDefaultFont', 8, 'italic')).pack(side=tk.BOTTOM, anchor=tk.W)

        # Parent Volume
        parent_frame = ttk.Frame(main_frame)
        parent_frame.pack(fill=tk.X, pady=5)
        ttk.Label(parent_frame, text="Parent Volume:", width=15).pack(side=tk.LEFT)
        self.parent_var = tk.StringVar(value=self.world_lv.name)
        volumes = sorted(list(self.registry.logicalVolumeDict.keys()))
        ttk.Combobox(parent_frame, textvariable=self.parent_var, values=volumes, state='readonly', width=30).pack(side=tk.LEFT, padx=5)

        # Name Conflict Resolution
        conflict_frame = ttk.LabelFrame(main_frame, text="Name Conflict Resolution", padding=10)
        conflict_frame.pack(fill=tk.X, pady=5)
        
        self.add_suffix = tk.BooleanVar(value=True)
        ttk.Checkbutton(conflict_frame, text="Auto-rename clashes with suffix (_imported)", 
                        variable=self.add_suffix).pack(anchor=tk.W)
        
        prefix_frame = ttk.Frame(conflict_frame)
        prefix_frame.pack(fill=tk.X, pady=2)
        ttk.Label(prefix_frame, text="OR Add Prefix to clashing volumes:").pack(side=tk.LEFT)
        self.prefix_var = tk.StringVar()
        ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=15).pack(side=tk.LEFT, padx=5)
        
        self.warn_clashes = tk.BooleanVar(value=False)
        ttk.Checkbutton(conflict_frame, text="Warn on clashes", 
                       variable=self.warn_clashes).pack(anchor=tk.W)

        # Merge Options
        opt_frame = ttk.LabelFrame(main_frame, text="Merge Options", padding=10)
        opt_frame.pack(fill=tk.X, pady=5)
        
        self.drop_dup_materials = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, text="Drop duplicate materials (use existing if name matches)", 
                       variable=self.drop_dup_materials).pack(anchor=tk.W)
        
        # Transform
        trans_frame = ttk.LabelFrame(main_frame, text="Transformation (Target PV)", padding=10)
        trans_frame.pack(fill=tk.X, pady=5)

        # Units
        unit_frame = ttk.Frame(trans_frame)
        unit_frame.pack(fill=tk.X, pady=2)
        ttk.Label(unit_frame, text="Length Unit:", width=10).pack(side=tk.LEFT)
        self.length_unit = tk.StringVar(value="mm")
        ttk.Combobox(unit_frame, textvariable=self.length_unit, values=["mm", "cm", "m"], 
                    state="readonly", width=5).pack(side=tk.LEFT)
        
        # Pos
        pos_grid = ttk.Frame(trans_frame)
        pos_grid.pack(fill=tk.X, pady=5)
        ttk.Label(pos_grid, text="Position (X, Y, Z):").pack(side=tk.LEFT, padx=5)
        self.pos_x = tk.StringVar(value="0")
        self.pos_y = tk.StringVar(value="0")
        self.pos_z = tk.StringVar(value="0")
        for v in [self.pos_x, self.pos_y, self.pos_z]:
            ttk.Entry(pos_grid, textvariable=v, width=8).pack(side=tk.LEFT, padx=2)
            
        # Rot
        rot_grid = ttk.Frame(trans_frame)
        rot_grid.pack(fill=tk.X, pady=5)
        ttk.Label(rot_grid, text="Rotation (deg X, Y, Z):").pack(side=tk.LEFT, padx=5)
        self.rot_x = tk.StringVar(value="0")
        self.rot_y = tk.StringVar(value="0")
        self.rot_z = tk.StringVar(value="0")
        for v in [self.rot_x, self.rot_y, self.rot_z]:
            ttk.Entry(rot_grid, textvariable=v, width=8).pack(side=tk.LEFT, padx=2)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Insert Selected", command=self.insert).pack(side=tk.RIGHT, padx=5)

    def browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("GDML Files", "*.gdml"), ("All Files", "*.*")])
        if f: 
            self.file_path.set(f)
            self.load_external_file(f)
            
    def load_external_file(self, path):
        try:
            import pyg4ometry.gdml as gdml
            
            # Load the external registry
            reader = gdml.Reader(path)
            self.ext_registry = reader.getRegistry()
            ext_world = self.ext_registry.getWorldVolume()
            
            # Clear tree
            self.vol_tree.delete(*self.vol_tree.get_children())
            
            # Populate volumes list
            vols = sorted(list(self.ext_registry.logicalVolumeDict.keys()))
            
            to_select = []
            
            for vname in vols:
                status = ""
                tags = ()
                if vname in self.registry.logicalVolumeDict:
                    status = "Clash"
                    tags = ('clash',)
                else:
                    status = "New"
                    to_select.append(vname)
                
                self.vol_tree.insert("", "end", iid=vname, text=vname, values=(status,), tags=tags)
            
            self.vol_tree.tag_configure('clash', foreground='red')
            
            # Select no-clashing volumes by default
            if to_select:
                self.vol_tree.selection_set(to_select)
            
            # Autoscroll to world if possible, or top
            if ext_world and ext_world.name in to_select:
                self.vol_tree.see(ext_world.name)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse GDML file: {e}")
            self.ext_registry = None

    def insert(self):
        path = self.file_path.get()
        if not path or not self.ext_registry:
            messagebox.showerror("Error", "No valid GDML file loaded")
            return
            
        selected_items = self.vol_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select at least one volume to import")
            return
            
        try:
            import pyg4ometry.geant4 as g4
            
            ext_reg = self.ext_registry
            
            # First, transfer all defines from external registry to avoid reference issues
            print("Transferring defines...")
            for define_name, define_obj in ext_reg.defineDict.items():
                if define_name not in self.registry.defineDict:
                    try:
                        # Use transferDefine if available
                        if hasattr(self.registry, 'transferDefine'):
                            self.registry.transferDefine(define_obj)
                        else:
                            # Manual transfer
                            define_obj.registry = self.registry
                            self.registry.defineDict[define_name] = define_obj
                    except Exception as e:
                        print(f"Warning transferring define {define_name}: {e}")
            
            # Get parent for placement
            parent_lv = self.registry.logicalVolumeDict[self.parent_var.get()]
            
            # Transfer parameters
            unit_scale = {'mm': 1.0, 'cm': 10.0, 'm': 1000.0}.get(self.length_unit.get(), 1.0)
            base_pos = [float(self.pos_x.get())*unit_scale, float(self.pos_y.get())*unit_scale, float(self.pos_z.get())*unit_scale]
            base_rot = [float(self.rot_x.get()), float(self.rot_y.get()), float(self.rot_z.get())]
            
            imported_names = []
            
            # Transfer selected volumes
            for vol_name in selected_items:
                if vol_name not in ext_reg.logicalVolumeDict:
                    continue
                
                source_lv = ext_reg.logicalVolumeDict[vol_name]
                
                # Handle name collision by renaming
                final_name = source_lv.name
                if final_name in self.registry.logicalVolumeDict:
                    if self.prefix_var.get().strip():
                        final_name = f"{self.prefix_var.get().strip()}{source_lv.name}"
                    elif self.add_suffix.get():
                        final_name = f"{source_lv.name}_imported"
                    else:
                        # Generate unique name
                        cnt = 1
                        while f"{source_lv.name}_{cnt}" in self.registry.logicalVolumeDict:
                            cnt += 1
                        final_name = f"{source_lv.name}_{cnt}"
                    
                    source_lv.name = final_name
                
                # Use pyg4ometry's addVolumeRecursive
                print(f"Adding volume: {final_name}")
                self.registry.addVolumeRecursive(source_lv)
                
                # Verify it was added
                if final_name not in self.registry.logicalVolumeDict:
                    raise Exception(f"Failed to add volume {final_name} to registry")
                
                imported_lv = self.registry.logicalVolumeDict[final_name]
                imported_names.append(final_name)
                
                # Create physical volume placement
                pv_name = f"{final_name}_pv"
                cnt = 1
                while pv_name in self.registry.physicalVolumeDict:
                    pv_name = f"{final_name}_pv_{cnt}"
                    cnt += 1
                
                print(f"Creating placement: {pv_name}")
                new_pv = g4.PhysicalVolume(base_rot, base_pos, imported_lv, pv_name, parent_lv, self.registry)
                self.registry.physicalVolumeDict[pv_name] = new_pv
                
                if new_pv not in parent_lv.daughterVolumes:
                    parent_lv.daughterVolumes.append(new_pv)
                
                print(f"Successfully imported: {final_name}")
            
            if imported_names:
                self.result = {'name': imported_names[0]}
                messagebox.showinfo("Success", f"Successfully imported {len(imported_names)} volume(s)")
            
            self.dialog.destroy()
            
        except Exception as e:
            error_msg = f"Failed to insert GDML:\n{str(e)}\n\nCheck terminal for details."
            messagebox.showerror("Error", error_msg)
            import traceback
            print("\n=== ERROR DETAILS ===")
            traceback.print_exc()
            print("=====================\n")


class MaterialManagementDialog:
    """Dialog for managing (viewing, editing, deleting) user materials."""
    
    def __init__(self, parent, user_db, app):
        self.user_db = user_db
        self.app = app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manage User Materials")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.refresh_list()
        
    def setup_ui(self):
        """Create the UI."""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="User Material Database", 
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # Material list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox with material names
        self.material_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                          font=('TkDefaultFont', 10))
        self.material_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.material_listbox.yview)
        
        self.material_listbox.bind('<<ListboxSelect>>', self.on_material_select)
        
        # Info panel
        info_frame = ttk.LabelFrame(main_frame, text="Material Details", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        info_scroll = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        self.info_text.config(yscrollcommand=info_scroll.set)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="New Material", 
                  command=self.new_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Selected", 
                  command=self.edit_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
    def refresh_list(self):
        """Refresh the material list."""
        self.material_listbox.delete(0, tk.END)
        for mat_name in self.user_db.list_materials():
            self.material_listbox.insert(tk.END, mat_name)
        
        # Clear info
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def on_material_select(self, event):
        """Handle material selection."""
        selection = self.material_listbox.curselection()
        if not selection:
            return
        
        mat_name = self.material_listbox.get(selection[0])
        mat_data = self.user_db.get_material(mat_name)
        
        if not mat_data:
            return
        
        # Build info string
        info = f"Material: {mat_name}\n\n"
        info += f"Type: {mat_data['type'].capitalize()}\n"
        info += f"Density: {mat_data['density']} {mat_data['density_unit']}\n\n"
        
        if mat_data['type'] == 'compound':
            info += f"Molecular Formula:\n  {mat_data['composition']}\n\n"
        else:
            info += "Composition (by mass fraction):\n"
            for comp in mat_data['composition']:
                info += f"  {comp['element']}: {comp['fraction']:.4f}\n"
            info += "\n"
        
        info += f"State: {mat_data.get('state', 'solid')}\n"
        
        if 'temperature' in mat_data:
            info += f"Temperature: {mat_data['temperature']} {mat_data.get('temp_unit', 'K')}\n"
        if 'pressure' in mat_data:
            info += f"Pressure: {mat_data['pressure']} {mat_data.get('pressure_unit', 'pascal')}\n"
        
        # Update info display
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
    
    def new_material(self):
        """Create a new material."""
        dialog = MaterialDefinitionDialog(self.dialog, self.user_db)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.refresh_list()
            self.app.update_user_material_list()
    
    def edit_material(self):
        """Edit selected material."""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a material to edit")
            return
        
        mat_name = self.material_listbox.get(selection[0])
        dialog = MaterialDefinitionDialog(self.dialog, self.user_db, mat_name)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.refresh_list()
            self.app.update_user_material_list()
    
    def delete_material(self):
        """Delete selected material."""
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a material to delete")
            return
        
        mat_name = self.material_listbox.get(selection[0])
        
        result = messagebox.askyesno("Confirm Delete", 
            f"Are you sure you want to delete material '{mat_name}'?\n\nThis cannot be undone.")
        
        if result:
            self.user_db.remove_material(mat_name)
            # Remove from registry if it exists
            if self.app.registry and mat_name in self.app.registry.materialDict:
                del self.app.registry.materialDict[mat_name]
            self.refresh_list()
            self.app.update_user_material_list()
            messagebox.showinfo("Success", f"Material '{mat_name}' has been deleted")


class InsertVolumeDialog:
    """Dialog for inserting a new volume with CSG shape."""
    
    def __init__(self, parent, registry, world_lv):
        self.result = None
        self.registry = registry
        self.world_lv = world_lv
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Insert New Volume")
        self.dialog.geometry("700x850")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the UI for volume insertion."""
        # Main frame with simple scrolling
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Volume Name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Volume Name:", width=20).pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value="new_volume")
        ttk.Entry(name_frame, textvariable=self.name_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Shape Type
        shape_frame = ttk.Frame(main_frame)
        shape_frame.pack(fill=tk.X, pady=5)
        ttk.Label(shape_frame, text="Shape Type:", width=20).pack(side=tk.LEFT)
        self.shape_type = tk.StringVar(value="Box")
        shape_combo = ttk.Combobox(shape_frame, textvariable=self.shape_type, state='readonly',
                                   values=["Box", "Sphere", "Cylinder", "Cone", "Torus", "Tube", "STEP File", "STL File"],
                                   width=28)
        shape_combo.pack(side=tk.LEFT, padx=5)
        shape_combo.bind('<<ComboboxSelected>>', lambda e: self.update_parameters_ui())
        
        # Length Unit Selection
        unit_frame = ttk.Frame(main_frame)
        unit_frame.pack(fill=tk.X, pady=5)
        ttk.Label(unit_frame, text="Length Unit:", width=20).pack(side=tk.LEFT)
        self.length_unit_var = tk.StringVar(value="mm")
        unit_combo = ttk.Combobox(unit_frame, textvariable=self.length_unit_var, state='readonly',
                                 values=["mm", "cm", "m"], width=10)
        unit_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(unit_frame, text="(for shape and position)", font=('TkDefaultFont', 8, 'italic')).pack(side=tk.LEFT)
        
        # Material Selection - Combined NIST and User materials
        mat_frame = ttk.Frame(main_frame)
        mat_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mat_frame, text="Material:", width=20).pack(side=tk.LEFT)
        self.material_var = tk.StringVar()
        
        # Get all available materials: existing + NIST + user
        materials = self._get_all_available_materials()
        
        self.material_combo = ttk.Combobox(mat_frame, textvariable=self.material_var, 
                                          values=materials, state='readonly', width=28)
        self.material_combo.pack(side=tk.LEFT, padx=5)
        if materials:
            self.material_var.set(materials[0])
        
        # Parent Volume
        parent_frame = ttk.Frame(main_frame)
        parent_frame.pack(fill=tk.X, pady=5)
        ttk.Label(parent_frame, text="Parent Volume:", width=20).pack(side=tk.LEFT)
        self.parent_var = tk.StringVar(value=self.world_lv.name)
        
        # Get available logical volumes
        volumes = list(self.registry.logicalVolumeDict.keys())
        volumes.sort()
        
        ttk.Combobox(parent_frame, textvariable=self.parent_var,
                    values=volumes, state='readonly', width=28).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Parameters Frame (dynamic based on shape)
        self.params_container = ttk.LabelFrame(main_frame, text="Shape Parameters", padding=10)
        self.params_container.pack(fill=tk.X, pady=5)
        
        self.update_parameters_ui()
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Position Frame
        pos_frame = ttk.LabelFrame(main_frame, text="Position (X, Y, Z) - units in mm/cm/m", padding=10)
        pos_frame.pack(fill=tk.X, pady=5)
        
        pos_grid = ttk.Frame(pos_frame)
        pos_grid.pack()
        
        ttk.Label(pos_grid, text="X:").grid(row=0, column=0, padx=5)
        self.pos_x = tk.StringVar(value="0")
        ttk.Entry(pos_grid, textvariable=self.pos_x, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(pos_grid, text="Y:").grid(row=0, column=2, padx=5)
        self.pos_y = tk.StringVar(value="0")
        ttk.Entry(pos_grid, textvariable=self.pos_y, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(pos_grid, text="Z:").grid(row=0, column=4, padx=5)
        self.pos_z = tk.StringVar(value="0")
        ttk.Entry(pos_grid, textvariable=self.pos_z, width=15).grid(row=0, column=5, padx=5)
        
        # Rotation Frame
        rot_frame = ttk.LabelFrame(main_frame, text="Rotation (degrees)", padding=10)
        rot_frame.pack(fill=tk.X, pady=5)
        
        rot_grid = ttk.Frame(rot_frame)
        rot_grid.pack()
        
        ttk.Label(rot_grid, text="X:").grid(row=0, column=0, padx=5)
        self.rot_x = tk.StringVar(value="0")
        ttk.Entry(rot_grid, textvariable=self.rot_x, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(rot_grid, text="Y:").grid(row=0, column=2, padx=5)
        self.rot_y = tk.StringVar(value="0")
        ttk.Entry(rot_grid, textvariable=self.rot_y, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(rot_grid, text="Z:").grid(row=0, column=4, padx=5)
        self.rot_z = tk.StringVar(value="0")
        ttk.Entry(rot_grid, textvariable=self.rot_z, width=15).grid(row=0, column=5, padx=5)
        
        # Buttons at bottom
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Insert Volume", command=self.insert_volume).pack(side=tk.RIGHT, padx=5)
        
        # Force update
        self.dialog.update_idletasks()
    
    def update_parameters_ui(self):
        """Update parameter inputs based on selected shape."""
        # Clear existing widgets
        for widget in self.params_container.winfo_children():
            widget.destroy()
        
        shape = self.shape_type.get()
        self.param_vars = {}
        
        if shape == "Box":
            self.add_param_field("pX (half-width)", "pX", "10")
            self.add_param_field("pY (half-height)", "pY", "10")
            self.add_param_field("pZ (half-depth)", "pZ", "10")
            
        elif shape == "Sphere":
            self.add_param_field("pRMax (outer radius)", "pRMax", "10")
            self.add_param_field("pRMin (inner radius, optional)", "pRMin", "0")
            self.add_param_field("pSPhi (start phi, deg)", "pSPhi", "0")
            self.add_param_field("pDPhi (delta phi, deg)", "pDPhi", "360")
            self.add_param_field("pSTheta (start theta, deg)", "pSTheta", "0")
            self.add_param_field("pDTheta (delta theta, deg)", "pDTheta", "180")
            
        elif shape == "Cylinder":
            self.add_param_field("pRMax (outer radius)", "pRMax", "10")
            self.add_param_field("pRMin (inner radius)", "pRMin", "0")
            self.add_param_field("pDz (half-length)", "pDz", "20")
            self.add_param_field("pSPhi (start phi, deg)", "pSPhi", "0")
            self.add_param_field("pDPhi (delta phi, deg)", "pDPhi", "360")
            
        elif shape == "Cone":
            self.add_param_field("pRMin1 (inner radius at -pDz)", "pRMin1", "0")
            self.add_param_field("pRMax1 (outer radius at -pDz)", "pRMax1", "5")
            self.add_param_field("pRMin2 (inner radius at +pDz)", "pRMin2", "0")
            self.add_param_field("pRMax2 (outer radius at +pDz)", "pRMax2", "10")
            self.add_param_field("pDz (half-length)", "pDz", "20")
            self.add_param_field("pSPhi (start phi, deg)", "pSPhi", "0")
            self.add_param_field("pDPhi (delta phi, deg)", "pDPhi", "360")
            
        elif shape == "Torus":
            self.add_param_field("pRMin (inner radius)", "pRMin", "5")
            self.add_param_field("pRMax (outer radius)", "pRMax", "10")
            self.add_param_field("pRTor (swept radius)", "pRTor", "20")
            self.add_param_field("pSPhi (start phi, deg)", "pSPhi", "0")
            self.add_param_field("pDPhi (delta phi, deg)", "pDPhi", "360")
            
        elif shape == "Tube":
            self.add_param_field("pRMin (inner radius)", "pRMin", "5")
            self.add_param_field("pRMax (outer radius)", "pRMax", "10")
            self.add_param_field("pDz (half-length)", "pDz", "20")
            self.add_param_field("pSPhi (start phi, deg)", "pSPhi", "0")
            self.add_param_field("pDPhi (delta phi, deg)", "pDPhi", "360")
        
        elif shape == "STEP File":
            self.add_file_selector("STEP File (.step, .stp)", "step_file")
            self.add_option_checkbox("Use flat tessellation (single solid)", "use_flat")
            ttk.Label(self.params_container, text="Note: STEP file will preserve hierarchy\nand convert to CSG where possible",
                     font=('TkDefaultFont', 8, 'italic'), foreground='gray').pack(pady=5)
        
        elif shape == "STL File":
            self.add_file_selector("STL File (.stl)", "stl_file")
            self.add_param_field("Linear deflection (mesh quality)", "lin_def", "0.5")
            ttk.Label(self.params_container, text="Note: STL will be converted to tessellated solid",
                     font=('TkDefaultFont', 8, 'italic'), foreground='gray').pack(pady=5)
    
    def _get_all_available_materials(self):
        """Get combined list of existing, NIST, and user-defined materials."""
        materials = []
        
        # Existing materials in registry
        materials.extend(list(self.registry.materialDict.keys()))
        
        # ALL NIST/G4 materials using pyg4ometry's built-in list
        import pyg4ometry.geant4 as g4
        try:
            nist_list = g4.getNistMaterialList()
            for mat in nist_list:
                if mat not in materials:
                    materials.append(mat)
        except Exception as e:
            # Fallback to common materials if getNistMaterialList fails
            print(f"Warning: Could not get full NIST list: {e}")
            nist_materials = [
                'G4_AIR', 'G4_Al', 'G4_Cu', 'G4_Fe', 'G4_Pb', 'G4_W',
                'G4_WATER', 'G4_Galactic', 'G4_CONCRETE', 'G4_PLASTIC_SC_VINYLTOLUENE'
            ]
            for mat in nist_materials:
                if mat not in materials:
                    materials.append(mat)
        
        # User-defined materials from database
        try:
            from pathlib import Path
            db_file = Path.home() / ".gdml_editor" / "user_materials.json"
            if db_file.exists():
                import json
                with open(db_file, 'r') as f:
                    user_mats = json.load(f)
                    for mat_name in user_mats.keys():
                        if mat_name not in materials:
                            materials.append(mat_name)
        except:
            pass
        
        materials.sort()
        return materials
    
    def add_param_field(self, label, param_name, default_value):
        """Add a parameter input field."""
        frame = ttk.Frame(self.params_container)
        frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(frame, text=label + ":", width=30, anchor=tk.W).pack(side=tk.LEFT)
        var = tk.StringVar(value=default_value)
        ttk.Entry(frame, textvariable=var, width=20).pack(side=tk.LEFT, padx=5)
        
        self.param_vars[param_name] = var
    
    def add_file_selector(self, label, param_name):
        """Add a file selector field."""
        frame = ttk.Frame(self.params_container)
        frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(frame, text=label + ":", width=30, anchor=tk.W).pack(side=tk.TOP, anchor=tk.W)
        
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, pady=3)
        
        var = tk.StringVar(value="")
        entry = ttk.Entry(file_frame, textvariable=var, width=40)
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def browse_file():
            if "STEP" in label:
                filetypes = [("STEP Files", "*.step *.stp *.STEP *.STP"), ("All Files", "*.*")]
            else:
                filetypes = [("STL Files", "*.stl *.STL"), ("All Files", "*.*")]
            
            filename = filedialog.askopenfilename(title=f"Select {label}", filetypes=filetypes)
            if filename:
                var.set(filename)
        
        ttk.Button(file_frame, text="Browse...", command=browse_file, width=10).pack(side=tk.LEFT, padx=5)
        
        self.param_vars[param_name] = var
    
    def add_option_checkbox(self, label, param_name):
        """Add a checkbox option."""
        frame = ttk.Frame(self.params_container)
        frame.pack(fill=tk.X, pady=3)
        
        var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text=label, variable=var).pack(side=tk.LEFT, padx=5)
        
        self.param_vars[param_name] = var
    
    def insert_volume(self):
        """Create and insert the volume."""
        try:
            import pyg4ometry.geant4 as g4
            
            
            # Get values
            vol_name = self.name_var.get().strip()
            if not vol_name:
                messagebox.showerror("Error", "Volume name is required")
                return
            
            # Check for name collision
            if vol_name in self.registry.logicalVolumeDict:
                messagebox.showerror("Error", f"Volume '{vol_name}' already exists")
                return
            
            material_name = self.material_var.get()
            if not material_name:
                messagebox.showerror("Error", "Please select a material")
                return
            
            # Get or create material
            if material_name in self.registry.materialDict:
                obj = self.registry.materialDict[material_name]
                # If it's an Element (not Material), we need to create a proper Material
                if isinstance(obj, g4.Element):
                    # This can happen if G4_Si was created as an Element for material composition
                    # Create a proper Material for it
                    if material_name.startswith('G4_'):
                        try:
                            material = g4.MaterialPredefined(material_name, self.registry)
                        except ValueError:
                            messagebox.showerror("Error", f"Failed to create G4 material: {material_name}")
                            return
                    else:
                        messagebox.showerror("Error", f"Material '{material_name}' is an element, not a material")
                        return
                else:
                    material = obj
            elif material_name.startswith('G4_'):
                # Use MaterialPredefined for G4 built-in materials (avoids Material_ prefix)
                try:
                    material = g4.MaterialPredefined(material_name, self.registry)
                except ValueError:
                    messagebox.showerror("Error", f"Failed to create G4 material: {material_name}")
                    return
            else:
                # Try to create from user database
                try:
                    from pathlib import Path
                    import json
                    db_file = Path.home() / ".gdml_editor" / "user_materials.json"
                    with open(db_file, 'r') as f:
                        user_mats = json.load(f)
                    
                    if material_name not in user_mats:
                        messagebox.showerror("Error", f"Material '{material_name}' not found")
                        return
                    
                    mat_data = user_mats[material_name]
                    # Delegate to the centralized creator so constructor differences
                    # are handled in one place
                    try:
                        material = self.create_user_material_in_registry(material_name, mat_data)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to create material: {str(e)}")
                        return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create material: {str(e)}")
                    return
            
            parent_lv = self.registry.logicalVolumeDict[self.parent_var.get()]
            lunit = self.length_unit_var.get()
            
            # Parse parameters
            params = {}
            for name, var in self.param_vars.items():
                if isinstance(var, tk.BooleanVar):
                    params[name] = var.get()
                elif isinstance(var, tk.StringVar):
                    val_str = var.get().strip()
                    if val_str and name not in ['step_file', 'stl_file']:
                        try:
                            params[name] = float(val_str)
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid value for parameter '{name}': {val_str}")
                            return
                    else:
                        params[name] = val_str
            
            # Create solid with selected unit or from CAD file
            shape_type = self.shape_type.get()
            solid_name = f"{vol_name}_solid"
            
            if shape_type == "STEP File":
                # Load STEP file and merge into current registry
                step_file = params.get('step_file', '').strip()
                if not step_file or not Path(step_file).exists():
                    messagebox.showerror("Error", "Please select a valid STEP file")
                    return
                
                use_flat = params.get('use_flat', False)
                lv = self._load_step_as_volume(step_file, vol_name, material, use_flat)
                if not lv:
                    return
                    
            elif shape_type == "STL File":
                # Load STL file and create tessellated solid
                stl_file = params.get('stl_file', '').strip()
                if not stl_file or not Path(stl_file).exists():
                    messagebox.showerror("Error", "Please select a valid STL file")
                    return
                
                lin_def = params.get('lin_def', 0.5)
                lv = self._load_stl_as_volume(stl_file, vol_name, material, lin_def)
                if not lv:
                    return
            
            elif shape_type == "Box":
                solid = g4.solid.Box(solid_name, params['pX'], params['pY'], params['pZ'], 
                                    self.registry, lunit=lunit)
                lv = g4.LogicalVolume(solid, material, vol_name, self.registry)
                
            elif shape_type == "Sphere":
                solid = g4.solid.Sphere(solid_name, params['pRMin'], params['pRMax'],
                                       params['pSPhi'], params['pDPhi'], params['pSTheta'], params['pDTheta'],
                                       self.registry, lunit=lunit, aunit="deg")
                lv = g4.LogicalVolume(solid, material, vol_name, self.registry)
                
            elif shape_type == "Cylinder" or shape_type == "Tube":
                solid = g4.solid.Tubs(solid_name, params['pRMin'], params['pRMax'], params['pDz'],
                                     params['pSPhi'], params['pDPhi'],
                                     self.registry, lunit=lunit, aunit="deg")
                lv = g4.LogicalVolume(solid, material, vol_name, self.registry)
                
            elif shape_type == "Cone":
                solid = g4.solid.Cons(solid_name, params['pRMin1'], params['pRMax1'],
                                     params['pRMin2'], params['pRMax2'], params['pDz'],
                                     params['pSPhi'], params['pDPhi'],
                                     self.registry, lunit=lunit, aunit="deg")
                lv = g4.LogicalVolume(solid, material, vol_name, self.registry)
                
            elif shape_type == "Torus":
                solid = g4.solid.Torus(solid_name, params['pRMin'], params['pRMax'], params['pRTor'],
                                      params['pSPhi'], params['pDPhi'],
                                      self.registry, lunit=lunit, aunit="deg")
                lv = g4.LogicalVolume(solid, material, vol_name, self.registry)
            else:
                messagebox.showerror("Error", f"Unsupported shape type: {shape_type}")
                return
            
            # Parse position and rotation - convert position to mm (internal unit)
            lunit = self.length_unit_var.get()
            unit_to_mm = {'mm': 1.0, 'cm': 10.0, 'm': 1000.0}
            scale = unit_to_mm.get(lunit, 1.0)
            
            pos = [float(self.pos_x.get()) * scale, 
                   float(self.pos_y.get()) * scale, 
                   float(self.pos_z.get()) * scale]
            rot = [float(self.rot_x.get()), float(self.rot_y.get()), float(self.rot_z.get())]
            
            # Create physical volume (position is now in mm)
            pv_name = f"{vol_name}_pv"
            pv = g4.PhysicalVolume(rot, pos, lv, pv_name, parent_lv, self.registry)

            # Some pyg4ometry objects/versions don't consistently back-fill both the parent's
            # `daughterVolumes` and `registry.physicalVolumeDict`. Ensure the placement is
            # discoverable for the hierarchy tree and VTK export.
            try:
                pv_dict = getattr(self.registry, 'physicalVolumeDict', None)
                if isinstance(pv_dict, dict) and pv_name not in pv_dict:
                    pv_dict[pv_name] = pv
            except Exception:
                pass

            try:
                daughters = getattr(parent_lv, 'daughterVolumes', None)
                if isinstance(daughters, list) and pv not in daughters:
                    daughters.append(pv)
            except Exception:
                pass
            
            self.result = {
                'name': vol_name,
                'shape': shape_type,
                'material': material_name
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            # Clean up partially created objects on failure
            try:
                # Remove the logical volume if it was created
                if vol_name in self.registry.logicalVolumeDict:
                    del self.registry.logicalVolumeDict[vol_name]
                
                # Remove the solid if it was created
                solid_name = f"{vol_name}_solid"
                if solid_name in self.registry.solidDict:
                    del self.registry.solidDict[solid_name]
                
                # Remove physical volume if it was created
                pv_name = f"{vol_name}_pv"
                pv_dict = getattr(self.registry, 'physicalVolumeDict', {})
                if pv_name in pv_dict:
                    del pv_dict[pv_name]
            except Exception as cleanup_error:
                print(f"Warning: Cleanup failed: {cleanup_error}")
            
            messagebox.showerror("Error", f"Failed to create volume:\n{str(e)}")
    
    def _convert_density(self, density, unit):
        """Convert density to g/cm³."""
        conversion = {'g/cm3': 1.0, 'mg/cm3': 1e-3, 'kg/m3': 1e-3}
        return density * conversion.get(unit, 1.0)
    
    def _load_step_as_volume(self, step_file, vol_name, material, use_flat):
        """Load STEP file and create logical volume."""
        try:
            import pyg4ometry.geant4 as g4
            import pyg4ometry.pyoce
            
            print(f"Loading STEP file: {step_file}")
            reader = pyg4ometry.pyoce.Reader(step_file)
            
            if use_flat:
                # Flat mode: single tessellated solid
                print("Using flat tessellation mode...")
                oce_shape = reader.getShapeFromRefs()
                tess_solid = g4.solid.TessellatedSolid(f"{vol_name}_tess", self.registry)
                
                # Convert OCC shape to mesh
                mesh = pyg4ometry.geant4.solid.MeshExtractAndReduceToTriangles(oce_shape)
                for triangle in mesh:
                    v1, v2, v3 = triangle
                    tess_solid.addTriangularFacet([v1, v2, v3])
                
                lv = g4.LogicalVolume(tess_solid, material, vol_name, self.registry)
                print(f"✓ Created flat tessellated volume: {vol_name}")
            else:
                # Hierarchy mode: preserve structure
                print("Using hierarchy mode (CSG where possible)...")
                hierarchy_reg = pyg4ometry.pyoce.oce2Geant4(reader)
                
                # Get the top-level logical volume
                world_lv = hierarchy_reg.getWorldVolume()
                
                # Merge all volumes from STEP into current registry
                for lv_name, step_lv in hierarchy_reg.logicalVolumeDict.items():
                    # Rename to avoid conflicts
                    new_lv_name = f"{vol_name}_{lv_name}" if lv_name != world_lv.name else vol_name
                    
                    # Add solid to registry
                    if hasattr(step_lv, 'solid'):
                        solid = step_lv.solid
                        new_solid_name = f"{vol_name}_{solid.name}"
                        solid.name = new_solid_name
                        if new_solid_name not in self.registry.solidDict:
                            self.registry.solidDict[new_solid_name] = solid
                    
                    # Create new logical volume in target registry
                    new_lv = g4.LogicalVolume(step_lv.solid, material, new_lv_name, self.registry)
                    
                    # Copy daughter volumes
                    for pv in step_lv.daughterVolumes:
                        # Recursively rename and add daughters
                        daughter_lv_name = pv.logicalVolume.name
                        new_daughter_name = f"{vol_name}_{daughter_lv_name}"
                        
                        if new_daughter_name in self.registry.logicalVolumeDict:
                            daughter_lv = self.registry.logicalVolumeDict[new_daughter_name]
                        else:
                            continue  # Will be processed in loop
                        
                        # Create physical volume in new registry
                        new_pv_name = f"{vol_name}_{pv.name}"
                        g4.PhysicalVolume(
                            pv.rotation.eval() if hasattr(pv.rotation, 'eval') else [0, 0, 0],
                            pv.position.eval() if hasattr(pv.position, 'eval') else [0, 0, 0],
                            daughter_lv,
                            new_pv_name,
                            new_lv,
                            self.registry
                        )
                
                # Return the top-level volume
                lv = self.registry.logicalVolumeDict.get(vol_name, new_lv)
                print(f"✓ Created hierarchical volume structure: {vol_name}")
            
            return lv
            
        except Exception as e:
            import traceback
            messagebox.showerror("Error", f"Failed to load STEP file:\n{str(e)}\n\n{traceback.format_exc()}")
            return None
    
    def _load_stl_as_volume(self, stl_file, vol_name, material, lin_def):
        """Load STL file and create tessellated solid."""
        try:
            import pyg4ometry.geant4 as g4
            import pyg4ometry.stl as stl
            
            print(f"Loading STL file: {stl_file}")
            reader = stl.Reader(stl_file, registry=self.registry, addRegistry=False)
            
            # Create tessellated solid
            tess_solid = g4.solid.TessellatedSolid(f"{vol_name}_tess", self.registry)
            
            # Get mesh from STL reader
            mesh = reader.getMesh()
            
            # Add triangles to tessellated solid
            for triangle in mesh:
                v1, v2, v3 = triangle
                tess_solid.addTriangularFacet([list(v1), list(v2), list(v3)])
            
            # Create logical volume
            lv = g4.LogicalVolume(tess_solid, material, vol_name, self.registry)
            
            print(f"✓ Created STL tessellated volume: {vol_name} ({len(mesh)} triangles)")
            return lv
            
        except Exception as e:
            import traceback
            messagebox.showerror("Error", f"Failed to load STL file:\n{str(e)}\n\n{traceback.format_exc()}")
            return None


class GDMLEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GDML Geometry Editor")
        self.root.geometry("1200x800")
        
        self.gdml_file = None
        self.registry = None
        self.world_lv = None
        self.modified = False
        
        # VTK viewer tracking
        self.viewer_temp_file = None
        self.viewer_process = None
        
        # Initialize user material database
        self.user_material_db = UserMaterialDatabase()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open GDML...", command=self.open_gdml)
        file_menu.add_command(label="Save", command=self.save_gdml, state=tk.DISABLED)
        file_menu.add_command(label="Save As...", command=self.save_as_gdml, state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="View in VTK", command=self.view_in_vtk, state=tk.DISABLED)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Insert Volume...", command=self.insert_volume, state=tk.DISABLED)
        edit_menu.add_command(label="Insert from GDML...", command=self.insert_gdml, state=tk.DISABLED)
        edit_menu.add_command(label="Delete Volume...", command=self.delete_volume, state=tk.DISABLED)
        
        # Materials menu
        materials_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Materials", menu=materials_menu)
        materials_menu.add_command(label="Define New Material...", command=self.define_new_material)
        materials_menu.add_command(label="Manage User Materials...", command=self.manage_user_materials)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Check Overlaps...", command=self.check_overlaps, state=tk.DISABLED)
        
        self.file_menu = file_menu
        self.view_menu = view_menu
        self.edit_menu = edit_menu
        self.materials_menu = materials_menu
        self.tools_menu = tools_menu
        
        # Main container with paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Volume tree
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Logical Volumes", font=('TkDefaultFont', 10, 'bold')).pack(pady=5)
        
        # Search box
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_volumes)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Volume list with scrollbar
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.volume_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set, 
                                        columns=('Material',), selectmode='browse')
        self.volume_tree.heading('#0', text='Volume Name')
        self.volume_tree.heading('Material', text='Material')
        self.volume_tree.column('Material', width=200)
        self.volume_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.volume_tree.yview)
        
        self.volume_tree.bind('<<TreeviewSelect>>', self.on_volume_select)
        
        # Right panel - Properties
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Volume Properties", font=('TkDefaultFont', 10, 'bold')).pack(pady=5)
        
        # Properties display
        prop_frame = ttk.LabelFrame(right_frame, text="Current Properties", padding=10)
        prop_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Volume name
        name_frame = ttk.Frame(prop_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Volume Name:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.volume_name_var = tk.StringVar(value="")
        self.volume_name_entry = ttk.Entry(name_frame, textvariable=self.volume_name_var)
        self.volume_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.rename_button = ttk.Button(name_frame, text="Rename", command=self.rename_selected_volume, state=tk.DISABLED)
        self.rename_button.pack(side=tk.LEFT)
        
        # Volume type
        type_frame = ttk.Frame(prop_frame)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Type:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.volume_type_label = ttk.Label(type_frame, text="")
        self.volume_type_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Current material
        mat_frame = ttk.Frame(prop_frame)
        mat_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mat_frame, text="Material:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.volume_material_var = tk.StringVar(value="")
        self.volume_material_combo = ttk.Combobox(mat_frame, textvariable=self.volume_material_var, state='readonly')
        self.volume_material_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.apply_material_button = ttk.Button(mat_frame, text="Apply", command=self.apply_selected_material, state=tk.DISABLED)
        self.apply_material_button.pack(side=tk.LEFT)
        
        # Additional info
        info_frame = ttk.LabelFrame(prop_frame, text="Additional Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        info_scroll = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=info_scroll.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Open a GDML file to begin.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize dropdown values (will populate after a GDML is loaded)
        self._cached_nist_materials = None
        
    def update_user_material_list(self):
        """Update the user materials dropdown list."""
        # User material database changed; refresh the combined material dropdown.
        self._update_volume_material_dropdown()
    
    def define_new_material(self):
        """Open dialog to define a new material."""
        dialog = MaterialDefinitionDialog(self.root, self.user_material_db)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            self.update_user_material_list()
            messagebox.showinfo("Success", 
                f"Material '{dialog.result}' has been added to your user material database.")
    
    def manage_user_materials(self):
        """Open dialog to manage user materials."""
        dialog = MaterialManagementDialog(self.root, self.user_material_db, self)
        self.root.wait_window(dialog.dialog)
        self.update_user_material_list()
    
    def create_user_material_in_registry(self, mat_name, mat_data):
        """Create a user-defined material in the pyg4ometry registry using native features.
        
        Args:
            mat_name: Material name
            mat_data: Material data from user database
            
        Returns:
            Created material object
        """
        import pyg4ometry.geant4 as g4
        import inspect

        # Convert density to g/cm3 (pyg4ometry's default)
        density = self._convert_density_to_g_cm3(
            mat_data['density'], 
            mat_data['density_unit']
        )

        # Get optional parameters
        state = mat_data.get('state', 'solid')
        temperature = self._convert_temperature_to_kelvin(mat_data) if 'temperature' in mat_data else None
        pressure = self._convert_pressure_to_pascal(mat_data) if 'pressure' in mat_data else None

        # (No debug logging) Prepare to create materials using available constructors

        # Helper to attempt multiple constructor patterns
        def _try_constructors(ctor, attempts):
            last_exc = None
            for args, kwargs in attempts:
                try:
                    return ctor(*args, **kwargs) if kwargs else ctor(*args)
                except Exception as e:
                    last_exc = e
            # If all attempts failed, raise the last exception
            raise RuntimeError(f"All constructor attempts for {ctor.__name__} failed.") from last_exc

        # Create material based on type with exhaustive fallbacks
        if mat_data['type'] == 'compound':
            # Parse molecular formula (simple parser: ElementSymbol + optional integer)
            formula = mat_data['composition']
            import re
            matches = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
            element_counts = {}
            for sym, count in matches:
                try:
                    n = int(count) if count else 1
                except Exception:
                    n = 1
                element_counts[sym] = element_counts.get(sym, 0) + n

            num_components = len(element_counts) if element_counts else 1

            ctor = getattr(g4, 'MaterialCompound')
            # Prefer kwargs when possible
            try:
                sig = inspect.signature(ctor)
                params = sig.parameters
            except Exception:
                params = {}

            mc_kwargs = {}
            if 'name' in params:
                mc_kwargs['name'] = mat_name
            if 'density' in params:
                mc_kwargs['density'] = density
            if 'number_of_components' in params:
                mc_kwargs['number_of_components'] = num_components
            if 'registry' in params:
                mc_kwargs['registry'] = self.registry
            if 'state' in params:
                mc_kwargs['state'] = state

            attempts = []
            if mc_kwargs:
                attempts.append(((), mc_kwargs))
            # Positional fallbacks using number_of_components
            attempts.extend([
                ((mat_name, density, num_components, self.registry, state), {}),
                ((mat_name, density, num_components, self.registry), {}),
                ((mat_name, num_components, self.registry), {}),
                ((mat_name, self.registry), {}),
            ])

            mat = _try_constructors(ctor, attempts)

            # Add element natoms according to formula
            for sym, natoms in element_counts.items():
                element = self._get_or_create_element(sym)
                try:
                    mat.add_element_natoms(element, natoms)
                except Exception:
                    # ignore element add failures
                    pass
        else:
            # Mixture: create a MaterialCompound with number_of_components and add elements
            ctor = getattr(g4, 'MaterialCompound')
            try:
                sig = inspect.signature(ctor)
                params = sig.parameters
            except Exception:
                params = {}

            accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())

            mc_kwargs = {}
            if accepts_kwargs or 'name' in params:
                mc_kwargs['name'] = mat_name
            if accepts_kwargs or 'density' in params:
                mc_kwargs['density'] = density
            # number_of_components required by some signatures
            num_comp = len(mat_data['composition'])
            if accepts_kwargs or 'number_of_components' in params:
                mc_kwargs['number_of_components'] = num_comp
            if accepts_kwargs or 'registry' in params:
                mc_kwargs['registry'] = self.registry
            if accepts_kwargs or 'state' in params:
                mc_kwargs['state'] = state

            attempts = []
            if mc_kwargs:
                attempts.append(((), mc_kwargs))
            attempts.extend([
                ((mat_name, density, num_comp, self.registry, state), {}),
                ((mat_name, density, num_comp, self.registry), {}),
                ((mat_name, num_comp, self.registry), {}),
                ((mat_name, self.registry), {}),
            ])

            mat = _try_constructors(ctor, attempts)

            # Add elements using pyg4ometry's NIST database
            for comp in mat_data['composition']:
                element = self._get_or_create_element(comp['element'])
                try:
                    mat.add_element_massfraction(element, comp['fraction'])
                except Exception:
                    # ignore element add failures
                    pass

        # Set optional properties using pyg4ometry's attribute system
        if temperature is not None:
            try:
                mat.temperature = temperature
            except Exception:
                pass
        if pressure is not None:
            try:
                mat.pressure = pressure
            except Exception:
                pass

        # Return created material
        # Ensure material is present in the registry for later lookups/usage
        try:
            mat_name_actual = getattr(mat, 'name', None) or mat_name
            if hasattr(self.registry, 'materialDict'):
                self.registry.materialDict[mat_name_actual] = mat
            else:
                try:
                    self.registry.addMaterial(mat)
                except Exception:
                    pass
        except Exception:
            pass

        return mat
    
    def _convert_density_to_g_cm3(self, density, unit):
        """Convert density to g/cm³ (pyg4ometry standard)."""
        conversion = {
            'g/cm3': 1.0,
            'mg/cm3': 1e-3,
            'kg/m3': 1e-3
        }
        return density * conversion.get(unit, 1.0)
    
    def _convert_temperature_to_kelvin(self, mat_data):
        """Convert temperature to Kelvin (pyg4ometry standard)."""
        temp = mat_data['temperature']
        unit = mat_data.get('temp_unit', 'K')
        return temp + 273.15 if unit == 'C' else temp
    
    def _convert_pressure_to_pascal(self, mat_data):
        """Convert pressure to pascal (pyg4ometry standard)."""
        pressure = mat_data['pressure']
        unit = mat_data.get('pressure_unit', 'pascal')
        conversion = {
            'pascal': 1.0,
            'bar': 1e5,
            'atm': 101325.0
        }
        return pressure * conversion.get(unit, 1.0)
    
    # NIST element data (Z, A) for creating simple elements when name conflicts occur
    ELEMENT_DATA = {
        'H': (1, 1.008), 'He': (2, 4.003), 'Li': (3, 6.94), 'Be': (4, 9.012),
        'B': (5, 10.81), 'C': (6, 12.011), 'N': (7, 14.007), 'O': (8, 15.999),
        'F': (9, 18.998), 'Ne': (10, 20.18), 'Na': (11, 22.99), 'Mg': (12, 24.305),
        'Al': (13, 26.982), 'Si': (14, 28.085), 'P': (15, 30.974), 'S': (16, 32.06),
        'Cl': (17, 35.45), 'Ar': (18, 39.95), 'K': (19, 39.098), 'Ca': (20, 40.078),
        'Sc': (21, 44.956), 'Ti': (22, 47.867), 'V': (23, 50.942), 'Cr': (24, 51.996),
        'Mn': (25, 54.938), 'Fe': (26, 55.845), 'Co': (27, 58.933), 'Ni': (28, 58.693),
        'Cu': (29, 63.546), 'Zn': (30, 65.38), 'Ga': (31, 69.723), 'Ge': (32, 72.63),
        'As': (33, 74.922), 'Se': (34, 78.971), 'Br': (35, 79.904), 'Kr': (36, 83.798),
        'Rb': (37, 85.468), 'Sr': (38, 87.62), 'Y': (39, 88.906), 'Zr': (40, 91.224),
        'Nb': (41, 92.906), 'Mo': (42, 95.95), 'Tc': (43, 98), 'Ru': (44, 101.07),
        'Rh': (45, 102.91), 'Pd': (46, 106.42), 'Ag': (47, 107.87), 'Cd': (48, 112.41),
        'In': (49, 114.82), 'Sn': (50, 118.71), 'Sb': (51, 121.76), 'Te': (52, 127.6),
        'I': (53, 126.9), 'Xe': (54, 131.29), 'Cs': (55, 132.91), 'Ba': (56, 137.33),
        'La': (57, 138.91), 'Ce': (58, 140.12), 'Pr': (59, 140.91), 'Nd': (60, 144.24),
        'Pm': (61, 145), 'Sm': (62, 150.36), 'Eu': (63, 151.96), 'Gd': (64, 157.25),
        'Tb': (65, 158.93), 'Dy': (66, 162.5), 'Ho': (67, 164.93), 'Er': (68, 167.26),
        'Tm': (69, 168.93), 'Yb': (70, 173.05), 'Lu': (71, 174.97), 'Hf': (72, 178.49),
        'Ta': (73, 180.95), 'W': (74, 183.84), 'Re': (75, 186.21), 'Os': (76, 190.23),
        'Ir': (77, 192.22), 'Pt': (78, 195.08), 'Au': (79, 196.97), 'Hg': (80, 200.59),
        'Tl': (81, 204.38), 'Pb': (82, 207.2), 'Bi': (83, 208.98), 'Po': (84, 209),
        'At': (85, 210), 'Rn': (86, 222), 'Fr': (87, 223), 'Ra': (88, 226),
        'Ac': (89, 227), 'Th': (90, 232.04), 'Pa': (91, 231.04), 'U': (92, 238.03),
    }

    def _get_or_create_element(self, element_name):
        """Get element from registry or create from NIST database.
        
        Handles the case where G4_X names may exist as Materials (from GDML 
        <materialref ref="G4_Si"/>) but we need them as Elements for composition.
        """
        import pyg4ometry.geant4 as g4
        
        # Normalize common element inputs: accept 'C' or 'G4_C'
        candidates = [element_name]
        if not element_name.startswith('G4_'):
            candidates.insert(0, f'G4_{element_name}')
        
        # Get pure symbol (without G4_ prefix)
        sym = element_name.replace('G4_', '') if element_name.startswith('G4_') else element_name

        # Check if element already exists in registry materials
        # Note: materialDict may contain both Elements and Materials, so verify the type
        mat_dict = getattr(self.registry, 'materialDict', {})
        for cand in candidates:
            if cand in mat_dict:
                obj = mat_dict[cand]
                # Only return if it's actually an Element instance
                if isinstance(obj, g4.Element):
                    return obj
                # If it's a Material, don't use it - we need an Element
        
        # Also check for _elem suffixed versions we may have created earlier
        for cand in candidates:
            alt_name = f'{cand}_elem'
            if alt_name in mat_dict:
                obj = mat_dict[alt_name]
                if isinstance(obj, g4.Element):
                    return obj

        # Try creating from NIST database using pyg4ometry with fallback names
        # If the name conflicts with an existing Material, try alternative naming
        last_exc = None
        for cand in candidates:
            try:
                return g4.nist_element_2geant4Element(cand, self.registry)
            except Exception as e:
                last_exc = e
                # If it's a name conflict (Material already exists with this name),
                # try creating a simple element with a unique suffix
                if 'Identical' in str(e) and 'name' in str(e):
                    alt_name = f'{cand}_elem'
                    if sym in self.ELEMENT_DATA:
                        Z, A = self.ELEMENT_DATA[sym]
                        try:
                            elem = g4.Element(name=alt_name, symbol=sym, Z=Z, A=A, registry=self.registry)
                            return elem
                        except Exception as inner_e:
                            last_exc = inner_e

        raise ValueError(f"Unknown element '{element_name}': {last_exc}")
        
    def open_gdml(self):
        """Open a GDML file using pyg4ometry Reader."""
        filename = filedialog.askopenfilename(
            title="Open GDML File",
            filetypes=[("GDML Files", "*.gdml"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        self._load_gdml_file(filename)
    
    def _load_gdml_file(self, filename):
        """Internal method to load a GDML file."""
        self.status_var.set(f"Loading {filename}...")
        self.root.update()
        
        try:
            import pyg4ometry.gdml as gdml
            import pyg4ometry.geant4 as g4
            
            # Use pyg4ometry's GDML reader
            reader = gdml.Reader(filename)
            self.registry = reader.getRegistry()
            
            # Post-process registry: wrap any Element instances with Material instances
            # This handles GDML files that reference elements directly as materials via <materialref>
            # Uses pyg4ometry's native MaterialPredefined for NIST elements, or MaterialSingleElement as fallback
            elements_to_wrap = {}
            for name, obj in list(self.registry.materialDict.items()):
                if isinstance(obj, g4.Element):
                    elements_to_wrap[name] = obj
            
            for elem_name, element in elements_to_wrap.items():
                # Try MaterialPredefined first (handles NIST element names like G4_H, G4_C, etc.)
                # This provides correct densities and properties from the NIST database
                try:
                    mat = g4.MaterialPredefined(elem_name, self.registry)
                    self.registry.materialDict[elem_name] = mat
                except ValueError:
                    # Fallback to MaterialSingleElement for non-NIST elements
                    # Use a nominal density of 1.0 g/cm³ as placeholder
                    try:
                        mat = g4.MaterialSingleElement(elem_name, 1.0, element, self.registry)
                        self.registry.materialDict[elem_name] = mat
                    except Exception as e:
                        # If both fail, log warning and leave Element as-is
                        print(f"Warning: Could not wrap element {elem_name}: {e}")
            
            self.world_lv = self.registry.getWorldVolume()
            self.gdml_file = filename
            self.modified = False
            
            # Update UI
            self.populate_volume_tree()
            self.update_material_list()
            
            # Enable menu items
            self.file_menu.entryconfig("Save", state=tk.NORMAL)
            self.file_menu.entryconfig("Save As...", state=tk.NORMAL)
            self.view_menu.entryconfig("View in VTK", state=tk.NORMAL)
            self.edit_menu.entryconfig("Insert Volume...", state=tk.NORMAL)
            self.edit_menu.entryconfig("Insert from GDML...", state=tk.NORMAL)
            self.edit_menu.entryconfig("Delete Volume...", state=tk.NORMAL)
            self.tools_menu.entryconfig("Check Overlaps...", state=tk.NORMAL)
            
            self.status_var.set(f"Loaded: {Path(filename).name}")
            messagebox.showinfo("Success", f"Successfully loaded {Path(filename).name}")
            
            # Update viewer if running
            self._update_viewer()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GDML file:\n{str(e)}")
            self.status_var.set("Error loading file")
            
    def populate_volume_tree(self):
        """Populate the volume tree with hierarchical structure."""
        self.volume_tree.delete(*self.volume_tree.get_children())
        
        if not self.registry:
            return

        # Always resolve the world LV name and then use the registry dict as the canonical LV store.
        world_lv = self.registry.getWorldVolume() if hasattr(self.registry, "getWorldVolume") else None
        world_name = getattr(world_lv, "name", None) if world_lv is not None else None
        if not world_name:
            return

        self.world_lv = self.registry.logicalVolumeDict.get(world_name, world_lv)
        if not self.world_lv:
            return

        # Build hierarchy from the registry, but be tolerant:
        # - Some operations update `lv.daughterVolumes` reliably.
        # - Others are only reliably reflected in `registry.physicalVolumeDict`.
        # We merge both sources (by LV names) so the UI refresh always matches the current registry.
        from collections import defaultdict

        children_by_mother: dict[str, set[str]] = defaultdict(set)

        # 1) From physicalVolumeDict
        for pv in getattr(self.registry, "physicalVolumeDict", {}).values():
            mother_obj = getattr(pv, "motherVolume", None)
            if mother_obj is None:
                mother_obj = getattr(pv, "motherLogicalVolume", None)

            if isinstance(mother_obj, str):
                mother = mother_obj
            else:
                mother = getattr(mother_obj, "name", None) if mother_obj is not None else None

            child_obj = getattr(pv, "logicalVolume", None)
            if isinstance(child_obj, str):
                child = child_obj
            else:
                child = getattr(child_obj, "name", None) if child_obj is not None else None

            if mother and child:
                children_by_mother[mother].add(child)

        # 2) From each LV's daughterVolumes
        for mother_name, mother_lv in getattr(self.registry, "logicalVolumeDict", {}).items():
            for pv in getattr(mother_lv, "daughterVolumes", []) or []:
                child_obj = getattr(pv, "logicalVolume", None)
                child = getattr(child_obj, "name", None) if child_obj is not None else None
                if child:
                    children_by_mother[mother_name].add(child)

        def add_lv_by_name(lv_name: str, parent_item: str, visited: set[str]):
            if lv_name in visited:
                return
            visited.add(lv_name)

            lv = self.registry.logicalVolumeDict.get(lv_name)
            if lv and hasattr(lv, "material") and lv.material:
                mat_name = lv.material.name if hasattr(lv.material, "name") else str(lv.material)
            else:
                mat_name = "(Assembly)"

            item_id = self.volume_tree.insert(parent_item, 'end', lv_name, text=lv_name, values=(mat_name,))

            for child_name in sorted(children_by_mother.get(lv_name, set()), key=lambda s: s.lower()):
                add_lv_by_name(child_name, item_id, visited)

        add_lv_by_name(world_name, '', set())
    
    def refresh_volume_tree(self):
        """Alias for populate_volume_tree - refreshes the tree display."""
        self.populate_volume_tree()
    
    def filter_volumes(self, *args):
        """Filter volumes based on search text."""
        if not self.registry or not self.world_lv:
            return
        
        search_text = (self.search_var.get() or "").strip().lower()
        
        if not search_text:
            # No filter - show full hierarchy
            self.populate_volume_tree()
            return
        
        # Filter mode - show flat list of matching volumes
        self.volume_tree.delete(*self.volume_tree.get_children())
        
        for name, lv in sorted(self.registry.logicalVolumeDict.items()):
            if search_text not in name.lower():
                continue
                
            if hasattr(lv, 'material') and lv.material:
                mat_name = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
            else:
                mat_name = "(Assembly)"
            
            self.volume_tree.insert('', 'end', name, text=name, values=(mat_name,))
    
    def update_material_list(self):
        """Update the material dropdown list."""
        if not self.registry:
            return

        self._update_volume_material_dropdown()

    def _get_all_available_materials(self):
        """Return combined list of materials: existing registry + all G4/NIST + user-defined."""
        if not self.registry:
            return []

        materials = set(getattr(self.registry, 'materialDict', {}).keys())

        # Cache the NIST list to avoid recomputing on every selection.
        if self._cached_nist_materials is None:
            try:
                import pyg4ometry.geant4 as g4
                self._cached_nist_materials = list(g4.getNistMaterialList())
            except Exception:
                self._cached_nist_materials = []
        materials.update(self._cached_nist_materials)

        try:
            materials.update(self.user_material_db.list_materials())
        except Exception:
            pass

        return sorted(materials, key=lambda s: s.lower())

    def _update_volume_material_dropdown(self):
        """Refresh the material dropdown used in the Volume Properties panel."""
        if not self.registry:
            return
        values = self._get_all_available_materials()
        self.volume_material_combo['values'] = values

    def _ensure_material_in_registry(self, material_name):
        """Return a material object, creating it if needed."""
        import pyg4ometry.geant4 as g4

        if not self.registry:
            raise ValueError("No registry loaded")

        if material_name in self.registry.materialDict:
            obj = self.registry.materialDict[material_name]
            # If it's an Element (not Material), create a proper Material for it
            if isinstance(obj, g4.Element):
                # This can happen if G4_Si was created as an Element for material composition
                # Create a proper Material for it
                if material_name.startswith('G4_'):
                    try:
                        mat = g4.MaterialPredefined(material_name, self.registry)
                        return mat
                    except ValueError:
                        raise ValueError(f"Material '{material_name}' exists only as Element, cannot use as material")
                else:
                    raise ValueError(f"'{material_name}' is an element, not a material")
            return obj

        if material_name.startswith('G4_'):
            # Use MaterialPredefined for NIST/G4 built-in materials
            # This avoids the Material_ prefix and doesn't define them in GDML
            try:
                mat = g4.MaterialPredefined(material_name, self.registry)
                # MaterialPredefined automatically adds to registry
                return mat
            except ValueError:
                # If MaterialPredefined fails, fall through to user materials
                pass

        mat_data = self.user_material_db.get_material(material_name)
        if mat_data:
            return self.create_user_material_in_registry(material_name, mat_data)

        raise ValueError(f"Unknown material '{material_name}'")

    def apply_selected_material(self):
        """Apply the selected material from the Volume Properties dropdown."""
        selection = self.volume_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a volume first")
            return

        volume_name = selection[0]
        lv = self.registry.logicalVolumeDict.get(volume_name)
        if not lv or not hasattr(lv, 'material'):
            messagebox.showerror("Error", "Selected volume cannot have material changed")
            return

        new_material = (self.volume_material_var.get() or "").strip()
        if not new_material:
            messagebox.showwarning("No Material", "Please select a material")
            return

        try:
            mat = self._ensure_material_in_registry(new_material)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set material '{new_material}':\n{e}")
            return

        old_material = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
        try:
            lv.material = mat
        except Exception as e:
            # Log and attempt safe fallback: ensure material registered and set registry on material
            # Try to ensure material has registry and retry
            try:
                if hasattr(mat, 'set_registry'):
                    try:
                        mat.set_registry(self.registry)
                    except TypeError:
                        try:
                            mat.set_registry(self.registry, dontWarnIfAlreadyAdded=True)
                        except Exception:
                            pass
                if new_material in getattr(self.registry, 'materialDict', {}):
                    lv.material = self.registry.materialDict[new_material]
                    self.modified = True
                    self.status_var.set(f"✓ Changed {volume_name}: {old_material} → {new_material} (fallback)")
                else:
                    raise
            except Exception as e2:
                messagebox.showerror("Error", f"Failed to assign material '{new_material}' to {volume_name}:\n{e2}")
                return

        # Update tree row material column
        if self.volume_tree.exists(volume_name):
            self.volume_tree.item(volume_name, values=(new_material,))

        self.modified = True
        self.status_var.set(f"✓ Changed {volume_name}: {old_material} → {new_material}")
        self._update_viewer()

        # Refresh the info display
        self.on_volume_select(None)

    def rename_selected_volume(self):
        """Rename the selected logical volume."""
        if not self.registry:
            return

        selection = self.volume_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a volume to rename")
            return

        old_name = selection[0]
        new_name = (self.volume_name_var.get() or "").strip()
        if not new_name:
            messagebox.showerror("Error", "New volume name cannot be empty")
            self.volume_name_var.set(old_name)
            return

        if new_name == old_name:
            return

        world_name = getattr(self.registry.getWorldVolume(), 'name', None) if hasattr(self.registry, 'getWorldVolume') else None
        if old_name == world_name:
            messagebox.showerror("Error", "Renaming the world volume is not supported")
            self.volume_name_var.set(old_name)
            return

        if new_name in self.registry.logicalVolumeDict:
            messagebox.showerror("Error", f"A volume named '{new_name}' already exists")
            self.volume_name_var.set(old_name)
            return

        lv = self.registry.logicalVolumeDict.get(old_name)
        if not lv:
            messagebox.showerror("Error", f"Volume '{old_name}' not found")
            return

        # Update registry dict key and LV name
        del self.registry.logicalVolumeDict[old_name]
        lv.name = new_name
        self.registry.logicalVolumeDict[new_name] = lv

        self.modified = True
        self.status_var.set(f"✓ Renamed volume: {old_name} → {new_name}")

        # Refresh UI + select the renamed item
        self.refresh_volume_tree()
        if self.volume_tree.exists(new_name):
            iid = new_name
            while iid:
                self.volume_tree.item(iid, open=True)
                iid = self.volume_tree.parent(iid)
            self.volume_tree.selection_set(new_name)
            self.volume_tree.see(new_name)

        self._update_viewer()

    def _format_solid_parameters(self, solid):
        """Return a human-friendly description of common solid parameters."""
        if solid is None:
            return ""

        solid_type = type(solid).__name__
        lunit = getattr(solid, 'lunit', None)
        aunit = getattr(solid, 'aunit', None)

        def fmt(name):
            val = getattr(solid, name, None)
            if val is None:
                return None
            return f"  {name}: {val}"

        lines = []
        if solid_type == 'Box':
            for k in ('pX', 'pY', 'pZ'):
                v = fmt(k)
                if v:
                    lines.append(v)
        elif solid_type == 'Tubs':
            for k in ('pRMin', 'pRMax', 'pDz', 'pSPhi', 'pDPhi'):
                v = fmt(k)
                if v:
                    lines.append(v)
        elif solid_type == 'Cons':
            for k in ('pRMin1', 'pRMax1', 'pRMin2', 'pRMax2', 'pDz', 'pSPhi', 'pDPhi'):
                v = fmt(k)
                if v:
                    lines.append(v)
        elif solid_type == 'Sphere':
            for k in ('pRMin', 'pRMax', 'pSPhi', 'pDPhi', 'pSTheta', 'pDTheta'):
                v = fmt(k)
                if v:
                    lines.append(v)
        elif solid_type == 'Torus':
            for k in ('pRMin', 'pRMax', 'pRTor', 'pSPhi', 'pDPhi'):
                v = fmt(k)
                if v:
                    lines.append(v)
        elif solid_type == 'TessellatedSolid':
            # Best-effort: not all versions expose facets count.
            for k in ('nFacets', 'numFacets', 'facets'):
                if hasattr(solid, k):
                    try:
                        val = getattr(solid, k)
                        if isinstance(val, int):
                            lines.append(f"  {k}: {val}")
                        elif hasattr(val, '__len__'):
                            lines.append(f"  {k}: {len(val)}")
                    except Exception:
                        pass
                    break

        if not lines:
            return ""

        if lunit:
            lines.append(f"  lunit: {lunit}")
        if aunit:
            lines.append(f"  aunit: {aunit}")
        return "\n".join(lines) + "\n"
        
    def on_volume_select(self, event):
        """Handle volume selection."""
        selection = self.volume_tree.selection()
        if not selection:
            return
        
        volume_name = selection[0]
        lv = self.registry.logicalVolumeDict.get(volume_name)
        
        if not lv:
            return
        
        # Update property display
        self.volume_name_var.set(volume_name)
        
        # Determine type
        if hasattr(lv, 'material'):
            self.volume_type_label.config(text="Logical Volume")
            mat_name = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
            self._update_volume_material_dropdown()
            self.volume_material_var.set(mat_name)
            # Disallow world renaming (keeps registry/world stable)
            world_name = getattr(self.registry.getWorldVolume(), 'name', None) if hasattr(self.registry, 'getWorldVolume') else None
            self.rename_button.config(state=tk.DISABLED if volume_name == world_name else tk.NORMAL)
            self.apply_material_button.config(state=tk.NORMAL)
        else:
            self.volume_type_label.config(text="Assembly Volume")
            self._update_volume_material_dropdown()
            self.volume_material_var.set("")
            world_name = getattr(self.registry.getWorldVolume(), 'name', None) if hasattr(self.registry, 'getWorldVolume') else None
            self.rename_button.config(state=tk.DISABLED if volume_name == world_name else tk.NORMAL)
            self.apply_material_button.config(state=tk.DISABLED)
        
        # Update info text
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = f"Volume: {volume_name}\n\n"
        
        if hasattr(lv, 'solid'):
            solid = lv.solid
            info += f"Solid Type: {type(solid).__name__}\n"
            if hasattr(solid, 'name'):
                info += f"Solid Name: {solid.name}\n"

            params_text = self._format_solid_parameters(solid)
            if params_text:
                info += "\nSolid Parameters:\n"
                info += params_text
        
        if hasattr(lv, 'material') and lv.material:
            mat = lv.material
            info += f"\nMaterial: {mat.name}\n"
            if hasattr(mat, 'density'):
                info += f"Density: {mat.density}\n"
            if hasattr(mat, 'state'):
                info += f"State: {mat.state}\n"
        
        # Placements & daughter count (derived from physicalVolumeDict)
        placements = []
        daughter_count = 0
        for pv_name, pv in getattr(self.registry, 'physicalVolumeDict', {}).items():
            child_lv = getattr(pv, 'logicalVolume', None)
            child_name = getattr(child_lv, 'name', None) if child_lv is not None else None

            mother_obj = getattr(pv, 'motherVolume', None) or getattr(pv, 'motherLogicalVolume', None)
            mother_name = mother_obj if isinstance(mother_obj, str) else getattr(mother_obj, 'name', None)

            if mother_name == lv.name:
                daughter_count += 1

            if child_name == lv.name:
                try:
                    pos = pv.position.eval() if hasattr(pv, 'position') else None
                except Exception:
                    pos = None
                try:
                    rot = pv.rotation.eval() if hasattr(pv, 'rotation') else None
                except Exception:
                    rot = None
                placements.append((pv_name, mother_name, pos, rot))

        info += f"\nDaughter volumes: {daughter_count}\n"
        if placements:
            info += f"Placements: {len(placements)}\n"
            for pv_name, mother_name, pos, rot in placements[:10]:
                info += f"  PV: {pv_name} in {mother_name}\n"
                if pos is not None:
                    info += f"    pos(mm): {pos}\n"
                if rot is not None:
                    info += f"    rot(deg): {rot}\n"
            if len(placements) > 10:
                info += f"  ... ({len(placements) - 10} more)\n"
        
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        
    def save_gdml(self):
        """Save GDML to current file."""
        if not self.gdml_file:
            self.save_as_gdml()
            return
        
        self.save_to_file(self.gdml_file)
    
    def save_as_gdml(self):
        """Save GDML to a new file."""
        filename = filedialog.asksaveasfilename(
            title="Save GDML File As",
            defaultextension=".gdml",
            filetypes=[("GDML Files", "*.gdml"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        self.save_to_file(filename)
        self.gdml_file = filename
    
    def _ensure_element_definitions(self):
        """Ensure all elements referenced by materials are properly defined.
        
        When GDML uses NIST materials like G4_H both as materials (in <materialref>)
        and as element references (in <fraction ref="G4_H">), pyg4ometry may load
        them as Materials. This causes write/read round-trip failures because the
        Writer doesn't output <element> definitions for Materials.
        
        This method ensures that for every material with element components, the
        referenced elements exist as actual Element instances in the registry,
        and updates the material components to reference these Elements.
        """
        import pyg4ometry.geant4 as g4
        
        mat_dict = getattr(self.registry, 'materialDict', {})
        
        # First pass: create Element objects for any Material used as element component
        element_map = {}  # Maps Material name -> Element object
        
        for name, obj in list(mat_dict.items()):
            if not isinstance(obj, g4.Material):
                continue
            
            components = getattr(obj, 'components', None)
            if not components:
                continue
            
            for comp_item in components:
                try:
                    # Handle both tuple/list and direct object references
                    if isinstance(comp_item, (tuple, list)) and len(comp_item) >= 2:
                        comp_obj = comp_item[0]
                    else:
                        continue
                    
                    # If component is a Material (not Element), we need to create an Element
                    if isinstance(comp_obj, g4.Material) and not isinstance(comp_obj, g4.Element):
                        comp_name = getattr(comp_obj, 'name', '')
                        
                        if comp_name in element_map:
                            continue  # Already processed
                        
                        # Extract symbol from name (e.g., G4_Si -> Si)
                        sym = comp_name.replace('G4_', '') if comp_name.startswith('G4_') else comp_name
                        
                        if sym in self.ELEMENT_DATA:
                            Z, A = self.ELEMENT_DATA[sym]
                            elem_name = f'{comp_name}_elem'
                            try:
                                # Check if this element already exists
                                if elem_name in mat_dict and isinstance(mat_dict[elem_name], g4.Element):
                                    element_map[comp_name] = mat_dict[elem_name]
                                else:
                                    elem = g4.Element(name=elem_name, symbol=sym, Z=Z, A=A, registry=self.registry)
                                    element_map[comp_name] = elem
                            except Exception as ex:
                                print(f"Warning: Could not create element for {comp_name}: {ex}")
                except (TypeError, IndexError):
                    continue  # Skip malformed components
        
        # Second pass: replace Material references with Element references in components
        for name, obj in list(mat_dict.items()):
            if not isinstance(obj, g4.Material):
                continue
            
            components = getattr(obj, 'components', None)
            if not components:
                continue
            
            new_components = []
            modified = False
            
            for comp_item in components:
                try:
                    if isinstance(comp_item, (tuple, list)) and len(comp_item) >= 2:
                        comp_obj = comp_item[0]
                        fraction = comp_item[1]
                        # Preserve any additional tuple elements
                        rest = comp_item[2:] if len(comp_item) > 2 else ()
                        
                        # If component is a Material that we've mapped to an Element, replace it
                        comp_name = getattr(comp_obj, 'name', '')
                        if comp_name in element_map:
                            new_comp = (element_map[comp_name], fraction) + tuple(rest)
                            new_components.append(new_comp)
                            modified = True
                        else:
                            new_components.append(comp_item)
                    else:
                        new_components.append(comp_item)
                except (TypeError, IndexError):
                    new_components.append(comp_item)
            
            if modified:
                obj.components = new_components
    
    def save_to_file(self, filename):
        """Save registry to file using pyg4ometry Writer."""
        try:
            import pyg4ometry.gdml as gdml
            
            self.status_var.set(f"Saving to {filename}...")
            self.root.update()
            
            # Ensure all element definitions are present before writing
            self._ensure_element_definitions()
            
            # Use pyg4ometry's GDML writer
            writer = gdml.Writer()
            writer.addDetector(self.registry)
            writer.write(filename)
            
            self.modified = False
            self.status_var.set(f"Saved: {Path(filename).name}")
            messagebox.showinfo("Success", f"Successfully saved to {Path(filename).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
            self.status_var.set("Error saving file")
    
    def insert_volume(self):
        """Insert a new volume with CSG shape."""
        if not self.registry:
            return
        
        dialog = InsertVolumeDialog(self.root, self.registry, self.world_lv)

        # Wait until the dialog is closed (Insert or Cancel). Without this, `dialog.result`
        # is checked before the user clicks Insert, so the tree/viewer won't refresh.
        try:
            self.root.wait_window(dialog.dialog)
        except Exception:
            pass

        if dialog.result:
            self.refresh_volume_tree()

            # Reveal the inserted volume in the hierarchy (expand ancestors, scroll into view).
            inserted_name = dialog.result.get('name')
            if inserted_name and self.volume_tree.exists(inserted_name):
                iid = inserted_name
                while iid:
                    self.volume_tree.item(iid, open=True)
                    iid = self.volume_tree.parent(iid)
                self.volume_tree.selection_set(inserted_name)
                self.volume_tree.see(inserted_name)

            self.volume_tree.update_idletasks()
            self.modified = True
            self.status_var.set(f"✓ Inserted volume: {dialog.result['name']}")
            self._update_viewer()

    def insert_gdml(self):
        """Insert volumes from another GDML file."""
        if not self.registry: return
        
        # Check if sys.modules contains cached VtkViewer which might cause issues
        # (similar to the hack at start of file, but good to be safe)
        
        dialog = InsertGDMLDialog(self.root, self.registry, self.world_lv)
        try:
            self.root.wait_window(dialog.dialog)
        except Exception:
            pass
        
        if dialog.result:
            self.refresh_volume_tree()
            
            # Reveal inserted volume
            iname = dialog.result.get('name')
            if iname and self.volume_tree.exists(iname):
                iid = iname
                while iid:
                    self.volume_tree.item(iid, open=True)
                    iid = self.volume_tree.parent(iid)
                self.volume_tree.selection_set(iname)
                self.volume_tree.see(iname)
                
            self.volume_tree.update_idletasks()
            self.modified = True
            self.status_var.set(f"✓ Inserted GDML volume: {iname}")
            self._update_viewer()
    
    def delete_volume(self):
        """Delete selected volume."""
        if not self.registry:
            return
        
        selected = self.volume_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a volume to delete.")
            return

        selected_iid = selected[0]
        parent_iid = self.volume_tree.parent(selected_iid)
        volume_name = self.volume_tree.item(selected_iid)['text']
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete volume '{volume_name}'?\n\n"
                                   "This will remove the logical volume and all its physical volume placements."):
            return
        
        # Prevent deletion of world volume
        if volume_name == self.world_lv.name:
            messagebox.showerror("Cannot Delete", "Cannot delete the world volume.")
            return
        
        try:
            # Find and remove all physical volumes using this logical volume
            pv_to_remove = []
            for lv_name, lv in self.registry.logicalVolumeDict.items():
                for pv in lv.daughterVolumes:
                    if pv.logicalVolume.name == volume_name:
                        pv_to_remove.append((lv, pv))
            
            # Remove physical volumes from parent's daughter list and from registry
            for parent_lv, pv in pv_to_remove:
                parent_lv.daughterVolumes.remove(pv)
                # Remove from physicalVolumeDict if it exists
                if hasattr(pv, 'name') and pv.name in self.registry.physicalVolumeDict:
                    del self.registry.physicalVolumeDict[pv.name]
            
            # Remove from registry
            if volume_name in self.registry.logicalVolumeDict:
                lv = self.registry.logicalVolumeDict[volume_name]
                
                # Remove all physical volumes that use this logical volume
                pv_names_to_remove = []
                for pv_name, pv in self.registry.physicalVolumeDict.items():
                    if pv.logicalVolume.name == volume_name:
                        pv_names_to_remove.append(pv_name)
                for pv_name in pv_names_to_remove:
                    del self.registry.physicalVolumeDict[pv_name]
                
                # Remove solid if it exists
                if hasattr(lv, 'solid') and lv.solid.name in self.registry.solidDict:
                    del self.registry.solidDict[lv.solid.name]
                
                # Remove logical volume
                del self.registry.logicalVolumeDict[volume_name]
            
            self.refresh_volume_tree()

            # Keep the UI grounded: after delete, select the previous parent if possible.
            if parent_iid and self.volume_tree.exists(parent_iid):
                self.volume_tree.item(parent_iid, open=True)
                self.volume_tree.selection_set(parent_iid)
                self.volume_tree.see(parent_iid)

            self.modified = True
            self.status_var.set(f"✓ Deleted volume: {volume_name}")
            messagebox.showinfo("Success", f"Volume '{volume_name}' has been deleted.")
            self._update_viewer()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete volume:\n{str(e)}")
    
    def check_overlaps(self):
        """Check geometry for overlaps using pyg4ometry's mesh-based overlap detection."""
        if not self.registry:
            messagebox.showerror("Error", "No geometry loaded")
            return
        
        # Create progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Checking Overlaps")
        progress_window.geometry("600x400")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Running overlap check...", 
                 font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        
        # Text widget for results
        result_frame = ttk.Frame(progress_window)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        result_text = tk.Text(result_frame, wrap=tk.WORD, height=15, font=('Courier', 9))
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        result_scroll = ttk.Scrollbar(result_frame, command=result_text.yview)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.config(yscrollcommand=result_scroll.set)
        
        # Close button
        ttk.Button(progress_window, text="Close", command=progress_window.destroy).pack(pady=10)
        
        result_text.insert(tk.END, "Initializing overlap check...\\n")
        result_text.insert(tk.END, "="*60 + "\\n\\n")
        result_text.update()
        
        try:
            import pyg4ometry
            
            # Get world volume
            world_lv = self.registry.worldVolume
            if not world_lv:
                result_text.insert(tk.END, "Error: No world volume found\\n")
                return
            
            # Check if geometry contains tessellated solids
            has_tessellated = False
            total_volumes = 0
            
            def check_for_tessellated(lv):
                nonlocal has_tessellated, total_volumes
                total_volumes += 1
                if hasattr(lv.solid, 'type') and lv.solid.type == 'TessellatedSolid':
                    has_tessellated = True
                    return
                for pv in lv.daughterVolumes:
                    if hasattr(pv, 'logicalVolume'):
                        check_for_tessellated(pv.logicalVolume)
            
            check_for_tessellated(world_lv)
            
            result_text.insert(tk.END, f"World volume: {world_lv.name}\\n")
            result_text.insert(tk.END, f"Total volumes: {total_volumes}\\n")
            result_text.insert(tk.END, f"Daughter volumes: {len(world_lv.daughterVolumes)}\\n\\n")
            
            if has_tessellated:
                result_text.insert(tk.END, "⚠ WARNING: Tessellated Solids Detected\\n")
                result_text.insert(tk.END, "="*60 + "\\n\\n")
                result_text.insert(tk.END, "This geometry contains tessellated solids (STL meshes).\\n\\n")
                result_text.insert(tk.END, "pyg4ometry's mesh-based overlap checking can crash\\n")
                result_text.insert(tk.END, "on complex tessellated geometries due to CGAL library\\n")
                result_text.insert(tk.END, "limitations with high polygon counts.\\n\\n")
                result_text.insert(tk.END, "Recommended alternatives:\\n\\n")
                result_text.insert(tk.END, "1. Visual inspection:\\n")
                result_text.insert(tk.END, "   Use the VTK viewer to visually inspect overlaps\\n\\n")
                result_text.insert(tk.END, "2. Export and check in Geant4:\\n")
                result_text.insert(tk.END, "   a) Save the GDML file\\n")
                result_text.insert(tk.END, "   b) Create a Geant4 macro with:\\n")
                result_text.insert(tk.END, "      /geometry/test/run\\n\\n")
                result_text.insert(tk.END, "3. Simplify STL meshes:\\n")
                result_text.insert(tk.END, "   Reduce polygon count before conversion\\n\\n")
                result_text.update()
                return
            
            result_text.insert(tk.END, f"Checking {len(world_lv.daughterVolumes)} daughter volumes\\n\\n")
            result_text.insert(tk.END, "This uses mesh-based overlap detection.\\n")
            result_text.insert(tk.END, "Checking for:\\n")
            result_text.insert(tk.END, "  • Daughter-daughter overlaps\\n")
            result_text.insert(tk.END, "  • Coplanar surface overlaps\\n")
            result_text.insert(tk.END, "  • Protrusions from mother volume\\n\\n")
            result_text.update()
            
            # Counter for overlaps
            n_overlaps = [0]
            
            # Redirect logging to capture overlap messages
            import logging
            import io
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            handler.setLevel(logging.ERROR)
            logger = logging.getLogger('pyg4ometry.geant4.LogicalVolume')
            old_level = logger.level
            logger.addHandler(handler)
            logger.setLevel(logging.ERROR)
            
            try:
                result_text.insert(tk.END, "Running overlap checks (this may take a while)...\\n")
                result_text.insert(tk.END, "\\nNote: Overlap checking on tessellated/STL geometries\\n")
                result_text.insert(tk.END, "may be slow or unstable due to mesh complexity.\\n\\n")
                result_text.update()
                
                try:
                    # Call checkOverlaps on the world logical volume
                    # This will recursively check all daughter volumes
                    world_lv.checkOverlaps(recursive=True, coplanar=True, printOut=False, nOverlapsDetected=n_overlaps)
                    
                    # Get logged overlap messages
                    log_output = log_capture.getvalue()
                    
                    result_text.insert(tk.END, "\\n" + "="*60 + "\\n")
                    result_text.insert(tk.END, "OVERLAP CHECK RESULTS\\n")
                    result_text.insert(tk.END, "="*60 + "\\n\\n")
                    
                    if n_overlaps[0] > 0:
                        result_text.insert(tk.END, f"⚠ FOUND {n_overlaps[0]} OVERLAP(S)\\n\\n")
                        if log_output:
                            result_text.insert(tk.END, "Details:\\n")
                            result_text.insert(tk.END, "-" * 60 + "\\n")
                            result_text.insert(tk.END, log_output)
                        result_text.insert(tk.END, "\\n" + "-" * 60 + "\\n")
                        result_text.insert(tk.END, "\\nYou can visualize the overlaps by viewing the geometry.\\n")
                        result_text.insert(tk.END, "Overlaps will be highlighted in the VTK viewer.\\n")
                    else:
                        result_text.insert(tk.END, "✓ No overlaps detected\\n\\n")
                        result_text.insert(tk.END, "Geometry appears to be valid!\\n")
                        
                except (MemoryError, SystemError, OSError) as mesh_error:
                    result_text.insert(tk.END, "\\n" + "="*60 + "\\n")
                    result_text.insert(tk.END, "⚠ OVERLAP CHECK FAILED\\n")
                    result_text.insert(tk.END, "="*60 + "\\n\\n")
                    result_text.insert(tk.END, f"Error: {str(mesh_error)}\\n\\n")
                    result_text.insert(tk.END, "The mesh-based overlap checking failed, possibly due to:\\n")
                    result_text.insert(tk.END, "  • Very complex tessellated/STL geometries\\n")
                    result_text.insert(tk.END, "  • High polygon count meshes\\n")
                    result_text.insert(tk.END, "  • Memory constraints\\n\\n")
                    result_text.insert(tk.END, "Consider:\\n")
                    result_text.insert(tk.END, "  • Simplifying STL meshes before conversion\\n")
                    result_text.insert(tk.END, "  • Checking overlaps in Geant4 directly\\n")
                    result_text.insert(tk.END, "  • Using VTK viewer for visual inspection\\n")
                
            finally:
                logger.removeHandler(handler)
                logger.setLevel(old_level)
            
            result_text.see(tk.END)
            
        except Exception as e:
            result_text.insert(tk.END, f"\\nError during overlap check:\\n{str(e)}\\n\\n")
            import traceback
            result_text.insert(tk.END, traceback.format_exc())
    
    def view_in_vtk(self):
        """Launch VTK viewer for current geometry in a separate process with auto-refresh."""
        if not self.registry:
            return
        
        try:
            import tempfile
            import subprocess
            import pyg4ometry.gdml as gdml
            
            self.status_var.set("Launching VTK viewer...")
            self.root.update()
            
            # Create or reuse temporary file
            if not self.viewer_temp_file:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.gdml', delete=False) as tmp:
                    self.viewer_temp_file = tmp.name
            
            # Ensure all element definitions are present before writing
            self._ensure_element_definitions()
            
            # Save current geometry
            writer = gdml.Writer()
            writer.addDetector(self.registry)
            writer.write(self.viewer_temp_file)
            
            # Launch viewer as separate process using run_vtkviewer.py
            viewer_script = Path(__file__).parent / "run_vtkviewer.py"
            if viewer_script.exists():
                # Check if viewer is already running
                if self.viewer_process and self.viewer_process.poll() is None:
                    # Viewer already running, just update the file (auto-refresh will handle it)
                    self.status_var.set("VTK viewer updated (auto-refresh active)")
                    print("✓ Geometry updated - viewer will auto-refresh")
                else:
                    # Launch new viewer with auto-refresh enabled
                    self.viewer_process = subprocess.Popen(
                        [sys.executable, str(viewer_script), self.viewer_temp_file, "--watch"]
                    )
                    self.status_var.set("VTK viewer launched with auto-refresh")
                    print("\n" + "="*60)
                    print("VTK Viewer Controls:")
                    print("  Rotate:   Left mouse button")
                    print("  Zoom:     Right mouse button or scroll wheel")
                    print("  Pan:      Middle mouse button")
                    print("  Clipping: Click and drag the plane widget")
                    print("  Toggle Clipping: Press 'c' key")
                    print("  Quit:     Press 'q' in the viewer window")
                    print("\n  AUTO-REFRESH: Enabled - viewer updates when you edit geometry")
                    print("="*60 + "\n")
            else:
                messagebox.showerror("Error", "VTK viewer script (gdml_editor/run_vtkviewer.py) not found")
                self.status_var.set("Viewer script not found")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch VTK viewer:\n{str(e)}")
            self.status_var.set("Error launching viewer")
    
    def _update_viewer(self):
        """Update viewer if it's running (for auto-refresh)."""
        if not self.viewer_temp_file or not self.registry:
            return
        
        # Check if viewer process is still running
        if self.viewer_process and self.viewer_process.poll() is None:
            try:
                import pyg4ometry.gdml as gdml
                # Ensure element definitions exist before writing
                self._ensure_element_definitions()
                # Save current geometry to the temp file
                writer = gdml.Writer()
                writer.addDetector(self.registry)
                writer.write(self.viewer_temp_file)
                print("✓ Viewer updated - auto-refresh active")
            except Exception as e:
                print(f"Warning: Could not update viewer: {e}")


def main():
    import sys
    root = tk.Tk()
    app = GDMLEditorApp(root)
    
    # Auto-load file if provided as command-line argument
    if len(sys.argv) > 1:
        gdml_file = sys.argv[1]
        if Path(gdml_file).exists():
            root.after(100, lambda: app._load_gdml_file(gdml_file))
        else:
            print(f"Warning: File not found: {gdml_file}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
