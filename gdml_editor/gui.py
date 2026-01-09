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
            self.refresh_list()
            self.app.update_user_material_list()
            messagebox.showinfo("Success", f"Material '{mat_name}' has been deleted")


class GDMLEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GDML Geometry Editor")
        self.root.geometry("1200x800")
        
        self.gdml_file = None
        self.registry = None
        self.world_lv = None
        self.modified = False
        
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
        
        # Materials menu
        materials_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Materials", menu=materials_menu)
        materials_menu.add_command(label="Define New Material...", command=self.define_new_material)
        materials_menu.add_command(label="Manage User Materials...", command=self.manage_user_materials)
        
        self.file_menu = file_menu
        self.view_menu = view_menu
        self.materials_menu = materials_menu
        
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
        self.volume_name_label = ttk.Label(name_frame, text="", font=('TkDefaultFont', 9, 'bold'))
        self.volume_name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Volume type
        type_frame = ttk.Frame(prop_frame)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Type:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.volume_type_label = ttk.Label(type_frame, text="")
        self.volume_type_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Current material
        mat_frame = ttk.Frame(prop_frame)
        mat_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mat_frame, text="Current Material:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.current_material_label = ttk.Label(mat_frame, text="")
        self.current_material_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Separator
        ttk.Separator(prop_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Material editor
        edit_frame = ttk.LabelFrame(prop_frame, text="Change Material", padding=10)
        edit_frame.pack(fill=tk.X, pady=5)
        
        # Material source selection
        source_frame = ttk.Frame(edit_frame)
        source_frame.pack(fill=tk.X, pady=5)
        ttk.Label(source_frame, text="Material Source:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        
        self.material_source = tk.StringVar(value="existing")
        ttk.Radiobutton(source_frame, text="Existing", variable=self.material_source, 
                       value="existing", command=self.update_material_controls).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(source_frame, text="NIST/G4", variable=self.material_source, 
                       value="nist", command=self.update_material_controls).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(source_frame, text="User Defined", variable=self.material_source,
                       value="user", command=self.update_material_controls).pack(side=tk.LEFT, padx=5)
        
        # Existing materials dropdown
        self.existing_mat_frame = ttk.Frame(edit_frame)
        self.existing_mat_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.existing_mat_frame, text="Select Material:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        
        self.material_var = tk.StringVar()
        self.material_combo = ttk.Combobox(self.existing_mat_frame, textvariable=self.material_var, state='readonly')
        self.material_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # NIST/G4 materials dropdown
        self.nist_mat_frame = ttk.Frame(edit_frame)
        ttk.Label(self.nist_mat_frame, text="G4 Material:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.nist_material_var = tk.StringVar()
        self.nist_material_combo = ttk.Combobox(self.nist_mat_frame, textvariable=self.nist_material_var, 
                                                state='readonly', width=30)
        self.nist_material_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Populate G4 materials list
        self.populate_g4_materials()
        
        # Search box for NIST materials
        search_nist_frame = ttk.Frame(self.nist_mat_frame)
        search_nist_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(search_nist_frame, text="Filter:").pack(side=tk.LEFT)
        self.nist_search_var = tk.StringVar()
        self.nist_search_var.trace('w', self.filter_nist_materials)
        ttk.Entry(search_nist_frame, textvariable=self.nist_search_var, width=15).pack(side=tk.LEFT, padx=2)
        
        # User materials dropdown
        self.user_mat_frame = ttk.Frame(edit_frame)
        ttk.Label(self.user_mat_frame, text="User Material:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.user_material_var = tk.StringVar()
        self.user_material_combo = ttk.Combobox(self.user_mat_frame, textvariable=self.user_material_var,
                                                state='readonly', width=30)
        self.user_material_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.update_user_material_list()
        
        # Info button for user materials
        ttk.Button(self.user_mat_frame, text="Info", width=6,
                  command=self.show_user_material_info).pack(side=tk.LEFT, padx=2)
        
        # Apply button
        self.apply_button = ttk.Button(edit_frame, text="Apply Material Change", 
                                       command=self.apply_material_change, state=tk.DISABLED)
        self.apply_button.pack(pady=10)
        
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
        
        # Initialize material controls visibility
        self.update_material_controls()
        
    def populate_g4_materials(self):
        """Populate the list of common G4/NIST materials."""
        # Comprehensive list of NIST and built-in Geant4 materials
        self.g4_materials = [
            # Elements
            "G4_H", "G4_He", "G4_Li", "G4_Be", "G4_B", "G4_C", "G4_N", "G4_O", "G4_F", "G4_Ne",
            "G4_Na", "G4_Mg", "G4_Al", "G4_Si", "G4_P", "G4_S", "G4_Cl", "G4_Ar", "G4_K", "G4_Ca",
            "G4_Sc", "G4_Ti", "G4_V", "G4_Cr", "G4_Mn", "G4_Fe", "G4_Co", "G4_Ni", "G4_Cu", "G4_Zn",
            "G4_Ga", "G4_Ge", "G4_As", "G4_Se", "G4_Br", "G4_Kr", "G4_Rb", "G4_Sr", "G4_Y", "G4_Zr",
            "G4_Nb", "G4_Mo", "G4_Tc", "G4_Ru", "G4_Rh", "G4_Pd", "G4_Ag", "G4_Cd", "G4_In", "G4_Sn",
            "G4_Sb", "G4_Te", "G4_I", "G4_Xe", "G4_Cs", "G4_Ba", "G4_La", "G4_Ce", "G4_Pr", "G4_Nd",
            "G4_Pm", "G4_Sm", "G4_Eu", "G4_Gd", "G4_Tb", "G4_Dy", "G4_Ho", "G4_Er", "G4_Tm", "G4_Yb",
            "G4_Lu", "G4_Hf", "G4_Ta", "G4_W", "G4_Re", "G4_Os", "G4_Ir", "G4_Pt", "G4_Au", "G4_Hg",
            "G4_Tl", "G4_Pb", "G4_Bi", "G4_Po", "G4_At", "G4_Rn", "G4_Fr", "G4_Ra", "G4_Ac", "G4_Th",
            "G4_Pa", "G4_U", "G4_Np", "G4_Pu", "G4_Am", "G4_Cm", "G4_Bk", "G4_Cf",
            
            # Common compounds and materials
            "G4_WATER", "G4_WATER_VAPOR", "G4_AIR", "G4_VACUUM", "G4_Galactic",
            "G4_CONCRETE", "G4_GLASS_PLATE", "G4_GLASS_LEAD", "G4_PYREX_GLASS",
            "G4_LUCITE", "G4_PLEXIGLASS", "G4_POLYETHYLENE", "G4_POLYPROPYLENE", "G4_POLYSTYRENE",
            "G4_TEFLON", "G4_MYLAR", "G4_KAPTON", "G4_NYLON-6-6", "G4_NYLON-6-10",
            "G4_BAKELITE", "G4_POLYCARBONATE", "G4_PHOTO_EMULSION",
            
            # Scintillators and crystals
            "G4_SODIUM_IODIDE", "G4_CESIUM_IODIDE", "G4_BGO", "G4_LSO", "G4_LYSO", "G4_GSO",
            "G4_PLASTIC_SC_VINYLTOLUENE", "G4_PbWO4", "G4_PbF2",
            "G4_CADMIUM_TUNGSTATE", "G4_BISMUTH_GERMANIUM_OXIDE",
            "G4_CALCIUM_FLUORIDE", "G4_BARIUM_FLUORIDE", "G4_LITHIUM_FLUORIDE",
            "G4_SODIUM_CHLORIDE", "G4_POTASSIUM_IODIDE",
            
            # Biological materials - ICRP
            "G4_TISSUE_SOFT_ICRP", "G4_TISSUE_SOFT_ICRU-4", "G4_TISSUE-METHANE_ICRP", "G4_TISSUE-PROPANE_ICRP",
            "G4_BONE_COMPACT_ICRU", "G4_BONE_CORTICAL_ICRP", "G4_BRAIN_ICRP", "G4_BLOOD_ICRP",
            "G4_MUSCLE_SKELETAL_ICRP", "G4_MUSCLE_STRIATED_ICRU", "G4_MUSCLE_WITH_SUCROSE", "G4_MUSCLE_WITHOUT_SUCROSE",
            "G4_LUNG_ICRP", "G4_ADIPOSE_TISSUE_ICRP", "G4_BREAST_TISSUE_ICRP",
            "G4_SKIN_ICRP", "G4_EYE_LENS_ICRP", "G4_TESTIS_ICRP", "G4_OVARY_ICRP",
            
            # Additional biological
            "G4_A-150_TISSUE", "G4_B-100_BONE", "G4_MS20_TISSUE", "G4_SKELETAL_MUSCLE",
            "G4_DNA_ADENINE", "G4_DNA_GUANINE", "G4_DNA_CYTOSINE", "G4_DNA_THYMINE", "G4_DNA_URACIL",
            
            # Shielding and structural materials
            "G4_STAINLESS-STEEL", "G4_GRAPHITE", "G4_SILICON_DIOXIDE", "G4_BORON_CARBIDE", "G4_BORON_OXIDE",
            "G4_ALUMINUM_OXIDE", "G4_BERYLLIUM_OXIDE", "G4_LITHIUM_OXIDE", "G4_MAGNESIUM_OXIDE",
            "G4_LITHIUM_TETRABORATE", "G4_LITHIUM_CARBONATE", "G4_LITHIUM_HYDRIDE",
            "G4_FERROUS_OXIDE", "G4_FERROUS_SULFATE", "G4_LEAD_OXIDE",
            
            # Gases
            "G4_He", "G4_Ar", "G4_Kr", "G4_Xe", "G4_H", "G4_N", "G4_O", "G4_Ne",
            "G4_METHANE", "G4_ETHANE", "G4_PROPANE", "G4_BUTANE", "G4_ISOBUTANE",
            "G4_CARBON_DIOXIDE", "G4_NITROGEN_GAS", "G4_OXYGEN_GAS", "G4_ARGON_GAS",
            "G4_XENON_GAS", "G4_KRYPTON_GAS", "G4_HELIUM_GAS",
            "G4_CARBON_TETRACHLORIDE", "G4_FREON-12", "G4_FREON-12B2", "G4_FREON-13", "G4_FREON-13B1", "G4_FREON-13I1",
            
            # Electronics and detector materials
            "G4_SILICON", "G4_GERMANIUM", "G4_CADMIUM_TELLURIDE", "G4_MERCURIC_IODIDE",
            "G4_GALLIUM_ARSENIDE", "G4_CESIUM_FLUORIDE", "G4_SODIUM_CARBONATE",
            
            # Aerogels and foams
            "G4_AEROGEL", "G4_STYROFOAM", "G4_DACRON",
            
            # Graphite and carbons
            "G4_GRAPHITE", "G4_C", "G4_CARBON_DIOXIDE", "G4_PARAFFIN",
            
            # Medical and pharmaceutical
            "G4_CELLULOSE_CELLOPHANE", "G4_CELLULOSE_BUTYRATE", "G4_CELLULOSE_NITRATE",
            "G4_NEOPRENE", "G4_POLYOXYMETHYLENE", "G4_POLYTETRAFLUOROETHYLENE",
            "G4_POLYTRIFLUOROCHLOROETHYLENE", "G4_POLYVINYL_ACETATE", "G4_POLYVINYL_ALCOHOL",
            "G4_POLYVINYL_BUTYRAL", "G4_POLYVINYL_CHLORIDE", "G4_POLYVINYLIDENE_CHLORIDE",
            "G4_POLYVINYLIDENE_FLUORIDE", "G4_POLYVINYL_PYRROLIDONE",
            
            # Oils and organic
            "G4_PARAFFIN", "G4_TERPHENYL", "G4_TOLUENE", "G4_BENZENE", "G4_ANTHRACENE",
            "G4_NAPHTHALENE", "G4_STILBENE", "G4_n-PENTANE", "G4_n-HEPTANE", "G4_n-HEXANE",
            
            # Insulators and ceramics
            "G4_AMBER", "G4_KEROSENE", "G4_RUBBER_BUTYL", "G4_RUBBER_NATURAL", "G4_RUBBER_NEOPRENE",
            
            # Liquids
            "G4_WATER_LIQUID", "G4_lH2", "G4_lN2", "G4_lO2", "G4_lAr", "G4_lKr", "G4_lXe",
            
            # Pressurized gases  
            "G4_PH2", "G4_PN2", "G4_PO2", "G4_PAr", "G4_PKr", "G4_PXe",
            
            # Miscellaneous compounds
            "G4_CALCIUM_CARBONATE", "G4_CALCIUM_SULFATE", "G4_CALCIUM_TUNGSTATE",
            "G4_METHYL_ISOBUTYL_KETONE", "G4_ACETONE", "G4_ACETYLENE",
            "G4_UREA", "G4_CELLULOSE_NITRATE", "G4_SUCROSE",
            
            # Rare and special materials
            "G4_NYLON-8062", "G4_NYLON-11_RILSAN", "G4_CR39", "G4_KEVLAR",
            "G4_LECITHIN", "G4_GLUCOSE", "G4_DICHLOROBENZENE",
            
            # HEP materials
            "G4_SILVER_BROMIDE", "G4_SILVER_CHLORIDE", "G4_SILVER_HALIDES", "G4_SILVER_IODIDE",
            
            # Additional tissues
            "G4_TISSUE_LUNG_ICRP", "G4_TISSUE_COLON_ICRP", "G4_TISSUE_STOMACH_ICRP",
            "G4_TISSUE_THYROID_ICRP", "G4_TISSUE_PANCREAS_ICRP", "G4_TISSUE_KIDNEY_ICRP",
        ]
        
        # Store full list
        self.g4_materials_full = sorted(set(self.g4_materials))
        self.nist_material_combo['values'] = self.g4_materials_full
    
    def filter_nist_materials(self, *args):
        """Filter NIST materials based on search text."""
        search_text = self.nist_search_var.get().lower()
        if not search_text:
            self.nist_material_combo['values'] = self.g4_materials_full
        else:
            filtered = [m for m in self.g4_materials_full if search_text in m.lower()]
            self.nist_material_combo['values'] = filtered
    
    def update_user_material_list(self):
        """Update the user materials dropdown list."""
        user_materials = self.user_material_db.list_materials()
        self.user_material_combo['values'] = user_materials
    
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
    
    def show_user_material_info(self):
        """Show information about selected user material."""
        mat_name = self.user_material_var.get()
        if not mat_name:
            messagebox.showinfo("Info", "Please select a user material first")
            return
        
        mat_data = self.user_material_db.get_material(mat_name)
        if not mat_data:
            messagebox.showerror("Error", f"Material '{mat_name}' not found")
            return
        
        # Build info string
        info = f"Material: {mat_name}\n\n"
        info += f"Type: {mat_data['type'].capitalize()}\n"
        info += f"Density: {mat_data['density']} {mat_data['density_unit']}\n"
        
        if mat_data['type'] == 'compound':
            info += f"Formula: {mat_data['composition']}\n"
        else:
            info += "Composition (by mass fraction):\n"
            for comp in mat_data['composition']:
                info += f"  {comp['element']}: {comp['fraction']}\n"
        
        info += f"State: {mat_data.get('state', 'solid')}\n"
        
        if 'temperature' in mat_data:
            info += f"Temperature: {mat_data['temperature']} {mat_data.get('temp_unit', 'K')}\n"
        if 'pressure' in mat_data:
            info += f"Pressure: {mat_data['pressure']} {mat_data.get('pressure_unit', 'pascal')}\n"
        
        messagebox.showinfo(f"Material Info: {mat_name}", info)
    
    def create_user_material_in_registry(self, mat_name, mat_data):
        """Create a user-defined material in the pyg4ometry registry using native features.
        
        Args:
            mat_name: Material name
            mat_data: Material data from user database
            
        Returns:
            Created material object
        """
        import pyg4ometry.geant4 as g4
        
        # Convert density to g/cm3 (pyg4ometry's default)
        density = self._convert_density_to_g_cm3(
            mat_data['density'], 
            mat_data['density_unit']
        )
        
        # Get optional parameters
        state = mat_data.get('state', 'solid')
        temperature = self._convert_temperature_to_kelvin(mat_data) if 'temperature' in mat_data else None
        pressure = self._convert_pressure_to_pascal(mat_data) if 'pressure' in mat_data else None
        
        # Create material based on type
        if mat_data['type'] == 'compound':
            # Use MaterialCompound - pyg4ometry parses the formula automatically
            mat = g4.MaterialCompound(
                mat_name,
                density,
                mat_data['composition'],  # Molecular formula
                self.registry,
                state=state
            )
        else:
            # Use Material with element composition
            composition = mat_data['composition']
            mat = g4.Material(
                mat_name,
                density,
                len(composition),
                self.registry,
                state=state
            )
            
            # Add elements using pyg4ometry's NIST database
            for comp in composition:
                element = self._get_or_create_element(comp['element'])
                mat.add_element_massfraction(element, comp['fraction'])
        
        # Set optional properties using pyg4ometry's attribute system
        if temperature is not None:
            mat.temperature = temperature
        if pressure is not None:
            mat.pressure = pressure
        
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
    
    def _get_or_create_element(self, element_name):
        """Get element from registry or create from NIST database."""
        import pyg4ometry.geant4 as g4
        
        # Check if element already exists in registry
        if element_name in self.registry.defineDict:
            return self.registry.defineDict[element_name]
        
        # Create from NIST database using pyg4ometry
        try:
            return g4.nist_element_2geant4Element(element_name, self.registry)
        except Exception as e:
            raise ValueError(f"Unknown element '{element_name}': {e}")
    
    def _create_material_from_source(self, material_name):
        """Create material from selected source using pyg4ometry.
        
        Args:
            material_name: Name of material to create
            
        Returns:
            Material object or None if creation failed
        """
        import pyg4ometry.geant4 as g4
        
        source = self.material_source.get()
        
        try:
            if source == "nist":
                # Use pyg4ometry's NIST material database
                return g4.nist_material_2geant4Material(material_name, self.registry)
                
            elif source == "user":
                # Create from user database
                mat_data = self.user_material_db.get_material(material_name)
                if not mat_data:
                    messagebox.showerror("Error", 
                        f"User material '{material_name}' not found in database")
                    return None
                return self.create_user_material_in_registry(material_name, mat_data)
                
            else:
                messagebox.showerror("Error", 
                    f"Material '{material_name}' not found in registry")
                return None
                
        except Exception as e:
            messagebox.showerror("Error", 
                f"Failed to create material '{material_name}':\n{str(e)}")
            return None
    
    def update_material_controls(self):
        """Update visibility of material selection controls based on radio button."""
        if self.material_source.get() == "existing":
            self.existing_mat_frame.pack(fill=tk.X, pady=5)
            self.nist_mat_frame.pack_forget()
            self.user_mat_frame.pack_forget()
        elif self.material_source.get() == "nist":
            self.existing_mat_frame.pack_forget()
            self.nist_mat_frame.pack(fill=tk.X, pady=5)
            self.user_mat_frame.pack_forget()
        else:  # user
            self.existing_mat_frame.pack_forget()
            self.nist_mat_frame.pack_forget()
            self.user_mat_frame.pack(fill=tk.X, pady=5)
        
    def open_gdml(self):
        """Open a GDML file using pyg4ometry Reader."""
        filename = filedialog.askopenfilename(
            title="Open GDML File",
            filetypes=[("GDML Files", "*.gdml"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        self.status_var.set(f"Loading {filename}...")
        self.root.update()
        
        try:
            import pyg4ometry.gdml as gdml
            
            # Use pyg4ometry's GDML reader
            reader = gdml.Reader(filename)
            self.registry = reader.getRegistry()
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
            
            self.status_var.set(f"Loaded: {Path(filename).name}")
            messagebox.showinfo("Success", f"Successfully loaded {Path(filename).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GDML file:\n{str(e)}")
            self.status_var.set("Error loading file")
            
    def populate_volume_tree(self):
        """Populate the volume tree with logical volumes."""
        self.volume_tree.delete(*self.volume_tree.get_children())
        
        if not self.registry:
            return
        
        for name, lv in sorted(self.registry.logicalVolumeDict.items()):
            if hasattr(lv, 'material'):
                mat_name = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
            else:
                mat_name = "(Assembly)"
            
            self.volume_tree.insert('', 'end', name, text=name, values=(mat_name,))
    
    def filter_volumes(self, *args):
        """Filter volumes based on search text."""
        if not self.registry:
            return
        
        search_text = self.search_var.get().lower()
        self.volume_tree.delete(*self.volume_tree.get_children())
        
        for name, lv in sorted(self.registry.logicalVolumeDict.items()):
            if search_text and search_text not in name.lower():
                continue
                
            if hasattr(lv, 'material'):
                mat_name = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
            else:
                mat_name = "(Assembly)"
            
            self.volume_tree.insert('', 'end', name, text=name, values=(mat_name,))
    
    def update_material_list(self):
        """Update the material dropdown list."""
        if not self.registry:
            return
        
        materials = sorted(self.registry.materialDict.keys())
        self.material_combo['values'] = materials
        
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
        self.volume_name_label.config(text=volume_name)
        
        # Determine type
        if hasattr(lv, 'material'):
            self.volume_type_label.config(text="Logical Volume")
            mat_name = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
            self.current_material_label.config(text=mat_name)
            self.apply_button.config(state=tk.NORMAL)
        else:
            self.volume_type_label.config(text="Assembly Volume")
            self.current_material_label.config(text="(No material - assembly)")
            self.apply_button.config(state=tk.DISABLED)
        
        # Update info text
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = f"Volume: {volume_name}\n\n"
        
        if hasattr(lv, 'solid'):
            solid = lv.solid
            info += f"Solid Type: {type(solid).__name__}\n"
            if hasattr(solid, 'name'):
                info += f"Solid Name: {solid.name}\n"
        
        if hasattr(lv, 'material') and lv.material:
            mat = lv.material
            info += f"\nMaterial: {mat.name}\n"
            if hasattr(mat, 'density'):
                info += f"Density: {mat.density}\n"
            if hasattr(mat, 'state'):
                info += f"State: {mat.state}\n"
        
        # Count daughters
        daughter_count = 0
        for pv_name, pv in self.registry.physicalVolumeDict.items():
            if hasattr(pv, 'motherVolume') and pv.motherVolume == lv:
                daughter_count += 1
        
        info += f"\nDaughter volumes: {daughter_count}\n"
        
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        
    def apply_material_change(self):
        """Apply material change to selected volume using pyg4ometry."""
        selection = self.volume_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a volume first")
            return
        
        volume_name = selection[0]
        lv = self.registry.logicalVolumeDict.get(volume_name)
        
        if not lv or not hasattr(lv, 'material'):
            messagebox.showerror("Error", "Selected volume cannot have material changed")
            return
        
        # Get new material name based on selected source
        source = self.material_source.get()
        if source == "existing":
            new_material = self.material_var.get()
        elif source == "nist":
            new_material = self.nist_material_var.get()
        else:  # user
            new_material = self.user_material_var.get()
            
        if not new_material:
            messagebox.showwarning("No Material", "Please select a material")
            return
        
        try:
            # Check if material exists in registry, create if needed
            if new_material not in self.registry.materialDict:
                mat = self._create_material_from_source(new_material)
                if mat is None:
                    return
                # Update material list after creation
                self.update_material_list()
                self.material_combo['values'] = sorted(self.registry.materialDict.keys())
            
            # Apply material change using pyg4ometry
            old_material = lv.material.name if hasattr(lv.material, 'name') else str(lv.material)
            lv.material = self.registry.materialDict[new_material]
            
            # Update UI elements
            self.volume_tree.item(volume_name, values=(new_material,))
            self.volume_tree.selection_remove(volume_name)
            self.root.update_idletasks()
            self.volume_tree.selection_set(volume_name)
            
            self.current_material_label.config(text=new_material)
            
            # Update info text
            self.info_text.config(state=tk.NORMAL)
            current_info = self.info_text.get(1.0, tk.END)
            updated_info = current_info.replace(f"Material: {old_material}", f"Material: {new_material}")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, updated_info)
            self.info_text.config(state=tk.DISABLED)
            
            # Clear material selection
            if source == "nist":
                self.nist_material_var.set("")
            elif source == "user":
                self.user_material_var.set("")
            
            self.modified = True
            self.status_var.set(f"✓ Changed {volume_name}: {old_material} → {new_material}")
            
            messagebox.showinfo("Success", 
                f"Material changed successfully:\n\n{volume_name}\n{old_material} → {new_material}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change material:\n{str(e)}")
    
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
    
    def save_to_file(self, filename):
        """Save registry to file using pyg4ometry Writer."""
        try:
            import pyg4ometry.gdml as gdml
            
            self.status_var.set(f"Saving to {filename}...")
            self.root.update()
            
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
    
    def view_in_vtk(self):
        """Launch VTK viewer for current geometry using pyg4ometry."""
        if not self.registry:
            return
        
        try:
            import pyg4ometry.visualisation as vis
            
            self.status_var.set("Launching VTK viewer...")
            self.root.update()
            
            # Create viewer using pyg4ometry's VtkViewer
            viewer = vis.VtkViewer()
            viewer.addLogicalVolume(self.world_lv)
            
            # Configure viewer window
            viewer.renWin.SetSize(1024, 768)
            viewer.renWin.SetWindowName(f"pyg4ometry Viewer - {Path(self.gdml_file).name if self.gdml_file else 'Untitled'}")
            viewer.ren.ResetCamera()
            
            # Start interactive rendering
            viewer.renWin.Render()
            viewer.iren.Initialize()
            
            self.status_var.set("VTK viewer running (close viewer window to continue)")
            viewer.iren.Start()
            
            self.status_var.set(f"Loaded: {Path(self.gdml_file).name if self.gdml_file else 'Untitled'}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch VTK viewer:\n{str(e)}")
            self.status_var.set("Error launching viewer")


def main():
    root = tk.Tk()
    app = GDMLEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
