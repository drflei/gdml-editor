# Element Dropdown Feature - User Guide

## Overview

The material definition dialog now includes a **dropdown element selector** with autocomplete filtering, making it easier to define mixture materials without typing errors.

## What's New

### 1. Element Dropdown Selection

Instead of manually typing element symbols, you can now:
- **Click the dropdown** to see all 118 elements from the periodic table
- **Select from list** with mouse click
- **Type to filter** - list updates dynamically as you type
- **No more typos** - ensures valid element symbols

### 2. Type-Ahead Filtering

As you type, the dropdown automatically filters elements:

```
Type: "F"  → Shows: F, Fe, Fm, Fr, Fl
Type: "Fe" → Shows: Fe
Type: "C"  → Shows: C, Ca, Cd, Ce, Cf, Cl, Cm, Cn, Co, Cr, Cs, Cu
Type: "Cu" → Shows: Cu, Cm
```

### 3. Common Elements Reference

A quick reference bar shows frequently used elements:
```
Common elements: H | C | N | O | F | Na | Mg | Al | Si | P | S | Cl | Ca | Ti | Cr | Mn | Fe | Co | Ni | Cu | Zn | Ag | Sn | W | Pt | Au | Pb | U
```

## How to Use

### Creating a Mixture Material

**Example: Stainless Steel 316**

1. Open GDML Editor → **Materials** → **Define New Material**

2. Fill in basic information:
   - Name: `StainlessSteel316`
   - Type: Select **"Mixture (Elements)"**
   - Density: `8.0`
   - Unit: `g/cm3`

3. Define composition:
   - Click **"Add Element"** button
   - **Row 1:**
     - Click Element dropdown
     - Type "Fe" or scroll to find Iron
     - Select **Fe**
     - Enter mass fraction: `0.68`
   
   - Click **"Add Element"** again
   - **Row 2:**
     - Element: **Cr** (Chromium)
     - Fraction: `0.17`
   
   - **Row 3:**
     - Element: **Ni** (Nickel)
     - Fraction: `0.12`
   
   - **Row 4:**
     - Element: **Mo** (Molybdenum)
     - Fraction: `0.03`

4. Verify fractions sum to 1.0
5. Click **"Save Material"**

### Using the Dropdown

**Three Ways to Select Elements:**

1. **Click and Select:**
   - Click the dropdown arrow
   - Scroll through list
   - Click element name

2. **Type Complete Symbol:**
   - Click in element field
   - Type "Fe" (case insensitive)
   - Press Enter or Tab

3. **Type and Filter:**
   - Click in element field
   - Start typing "F"
   - List shows: F, Fe, Fm, Fr, Fl
   - Continue typing "e"
   - List narrows to: Fe
   - Press Enter or click to select

## Features

### ✓ Complete Periodic Table

All 118 elements included:
- **Natural Elements:** H through U (1-92)
- **Synthetic Elements:** Np through Og (93-118)
- **Standard Symbols:** IUPAC standard element symbols

### ✓ Smart Filtering

- **Case Insensitive:** Type "fe", "Fe", or "FE"
- **Prefix Matching:** "C" shows C, Ca, Cd, Ce, Cf, Cl, etc.
- **Instant Update:** List updates as you type each character
- **Fallback:** Shows full list if no matches

### ✓ Error Prevention

The dropdown helps prevent common errors:

| ❌ Before (Manual Entry) | ✓ After (Dropdown) |
|-------------------------|-------------------|
| "fe" (lowercase) | "Fe" (from list) |
| "iron" (full name) | "Fe" (standard symbol) |
| "FE" (all caps) | "Fe" (correct case) |
| "CR" (wrong case) | "Cr" (from list) |

### ✓ Still Flexible

- Dropdown is **editable** - you can still type if you prefer
- **Tab/Enter** to move to next field
- **Arrow keys** to navigate dropdown list
- **Backspace** to clear and start over

## Available Elements

### Full Periodic Table

**Period 1:** H, He  
**Period 2:** Li, Be, B, C, N, O, F, Ne  
**Period 3:** Na, Mg, Al, Si, P, S, Cl, Ar  
**Period 4:** K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr  
**Period 5:** Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe  
**Period 6:** Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn  
**Period 7:** Fr, Ra, Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr, Rf, Db, Sg, Bh, Hs, Mt, Ds, Rg, Cn, Nh, Fl, Mc, Lv, Ts, Og

### Common Elements Highlighted

Most frequently used in detector materials:
- **Light Elements:** H, C, N, O, F
- **Alkali/Alkaline:** Na, Mg, Ca
- **Common Metals:** Al, Si, Ti, Cr, Mn, Fe, Co, Ni, Cu, Zn
- **Noble Metals:** Ag, Pt, Au
- **Heavy Elements:** Sn, W, Pb
- **Special:** U (uranium for shielding)

## Integration with pyg4ometry

The element dropdown integrates seamlessly with pyg4ometry:

1. **NIST Database:** Selected elements are created using `nist_element_2geant4Element()`
2. **Registry Caching:** Elements are stored in registry to avoid duplication
3. **Validation:** pyg4ometry validates element existence
4. **Geant4 Compatible:** All symbols match Geant4 conventions

## Tips for Best Results

### 1. Use Type-Ahead for Speed
Instead of scrolling through 118 elements:
- Type first letter(s) of element
- List narrows to relevant elements
- Quick selection

### 2. Reference Common Elements
Check the "Common elements" bar for frequently used elements:
- Most detector materials use these
- Saves time searching through periodic table

### 3. Double-Check Fractions
The dropdown handles element selection, but you still need to:
- Ensure fractions sum to 1.0
- Enter accurate mass fractions
- Match your material specification

### 4. Add Multiple Elements Efficiently
For complex mixtures:
1. Click "Add Element" for each component
2. Use dropdown to quickly select element
3. Tab to fraction field
4. Enter value
5. Tab to next row (auto-adds if needed)

## Troubleshooting

### Dropdown Not Showing Elements?
- Make sure you selected "Mixture (Elements)" type
- Compound materials use formula entry (H2O, SiO2, etc.)

### Element Not in List?
- All 118 elements are included
- Check spelling (case doesn't matter)
- Synthetic elements (Np-Og) are available

### Can't Type in Field?
- Dropdown is editable (`state='normal'`)
- Click in field to type
- If locked, restart dialog

### Filter Not Working?
- Type in the element field (not separate search box)
- Filter activates on KeyRelease event
- Clear field and try again

## Examples

### Example 1: Aluminum Oxide (Mixture Method)
```
Material: AluminumOxide
Type: Mixture
Density: 3.95 g/cm³

Elements:
  Al: 0.529  (Aluminum)
  O:  0.471  (Oxygen)
```

### Example 2: Brass Alloy
```
Material: Brass
Type: Mixture
Density: 8.4 g/cm³

Elements:
  Cu: 0.65  (Copper)
  Zn: 0.35  (Zinc)
```

### Example 3: Borosilicate Glass
```
Material: BorosilicateGlass
Type: Mixture
Density: 2.23 g/cm³

Elements:
  B:  0.040  (Boron)
  O:  0.539  (Oxygen)
  Na: 0.028  (Sodium)
  Al: 0.012  (Aluminum)
  Si: 0.377  (Silicon)
  K:  0.003  (Potassium)
```

## Benefits

### For Users
- ✅ **Faster** material definition
- ✅ **Fewer errors** from typos
- ✅ **Professional** interface
- ✅ **Easier** to learn
- ✅ **Visual** element reference

### For Projects
- ✅ **Consistency** in element naming
- ✅ **Reliability** - no invalid elements
- ✅ **Efficiency** - less time debugging
- ✅ **Quality** - professional tool
- ✅ **Standards** - IUPAC compliant

## Future Enhancements

Potential additions:
- Element full names in tooltip
- Atomic numbers displayed
- Group/period highlighting
- Element properties lookup
- Recently used elements
- Material templates

---

**Version:** 1.0  
**Feature Added:** January 2026  
**Compatible With:** pyg4ometry NIST database  
**Elements Included:** All 118 (H through Og)
