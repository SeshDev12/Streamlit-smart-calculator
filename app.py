import streamlit as st
from sympy import sympify, log, Eq, solve, symbols
from datetime import datetime
import calendar

# ─── STREAMLIT CONFIGURATION ──────────────────────────────────────────────
st.set_page_config(page_title="Smart Calculator", page_icon="🔢", layout="centered")
st.markdown("""
    <style>
    /* Force Streamlit columns to stay side-by-side on mobile */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ─── STATE INITIALIZATION (The App's "Memory") ────────────────────────────
if 'expression' not in st.session_state: st.session_state.expression = ""
if 'just_calculated' not in st.session_state: st.session_state.just_calculated = False
if 'history' not in st.session_state: st.session_state.history = []
if 'sci_mode' not in st.session_state: st.session_state.sci_mode = False
if 'rad_mode' not in st.session_state: st.session_state.rad_mode = True
if 'alt_mode' not in st.session_state: st.session_state.alt_mode = False

# ─── CORE CALCULATION LOGIC ───────────────────────────────────────────────
def press(val):
    if st.session_state.just_calculated:
        if val in ["+", "-", "*", "/", "**", "%"]:
            st.session_state.expression += val
        else:
            st.session_state.expression = str(val)
        st.session_state.just_calculated = False
    else:
        st.session_state.expression += str(val)

def clear():
    st.session_state.expression = ""
    st.session_state.just_calculated = False

def backspace():
    if st.session_state.just_calculated:
        st.session_state.expression = ""
        st.session_state.just_calculated = False
    else:
        st.session_state.expression = st.session_state.expression[:-1]

def press_pm():
    if st.session_state.just_calculated or not st.session_state.expression:
        st.session_state.expression = f"-({st.session_state.expression})"
        st.session_state.just_calculated = False
    elif st.session_state.expression:
        st.session_state.expression = f"-({st.session_state.expression})"

def press_paren():
    if st.session_state.just_calculated:
        st.session_state.just_calculated = False
    opens = st.session_state.expression.count("(")
    closes = st.session_state.expression.count(")")
    st.session_state.expression += "(" if opens == closes else ")"

def calculate():
    expr = st.session_state.expression.strip()
    if not expr: return
    try:
        proc = expr.replace("ln(", "log(")
        if not st.session_state.rad_mode:
            for fn in ("sin", "cos", "tan"):
                proc = proc.replace(f"{fn}(", f"{fn}(pi/180*")
        
        from sympy import cbrt as _cbrt
        L = {"log10": lambda x: log(x, 10), "cbrt": _cbrt}
        
        evaluated = sympify(proc, locals=L).evalf()
        f = float(evaluated)
        result = int(f) if f == int(f) else round(f, 8)
        
        # Save to history
        timestamp = datetime.now().strftime("%d %b %Y %H:%M:%S")
        st.session_state.history.insert(0, f"[{timestamp}] {expr} = {result}")
        
        st.session_state.expression = str(result)
        st.session_state.just_calculated = True
    except Exception:
        st.session_state.expression = "Error"
        st.session_state.just_calculated = True

# ─── UI LAYOUT ────────────────────────────────────────────────────────────
st.title("Smart Calculator")

# App Navigation using Tabs
tab_calc, tab_unit, tab_date, tab_hist = st.tabs(["Calculator", "Units", "Dates", "History"])

# ─── TAB 1: CALCULATOR ────────────────────────────────────────────────────
with tab_calc:
    # Display Screen
    st.text_input("Display", value=st.session_state.expression, disabled=True, label_visibility="collapsed")
    
    # Top Control Bar
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
    with ctrl1:
        if st.button("Sci Mode" if not st.session_state.sci_mode else "Std Mode", use_container_width=True):
            st.session_state.sci_mode = not st.session_state.sci_mode
            st.rerun()
    with ctrl2:
        if st.session_state.sci_mode:
            if st.button("RAD" if st.session_state.rad_mode else "DEG", use_container_width=True):
                st.session_state.rad_mode = not st.session_state.rad_mode
                st.rerun()
    with ctrl3:
        if st.session_state.sci_mode:
            if st.button("ALT", use_container_width=True):
                st.session_state.alt_mode = not st.session_state.alt_mode
                st.rerun()
    with ctrl4:
        if st.button("⌫", use_container_width=True): backspace(); st.rerun()

    st.divider()

    # Scientific Grid (Only visible if Sci Mode is ON)
    if st.session_state.sci_mode:
        s1, s2, s3, s4 = st.columns(4)
        if not st.session_state.alt_mode:
            if s1.button("sin", use_container_width=True): press("sin("); st.rerun()
            if s2.button("cos", use_container_width=True): press("cos("); st.rerun()
            if s3.button("tan", use_container_width=True): press("tan("); st.rerun()
            if s4.button("π", use_container_width=True): press("pi"); st.rerun()
            
            if s1.button("ln", use_container_width=True): press("ln("); st.rerun()
            if s2.button("log", use_container_width=True): press("log10("); st.rerun()
            if s3.button("e", use_container_width=True): press("E"); st.rerun()
            if s4.button("√", use_container_width=True): press("sqrt("); st.rerun()

            if s1.button("eˣ", use_container_width=True): press("exp("); st.rerun()
            if s2.button("x²", use_container_width=True): press("**2"); st.rerun()
            if s3.button("xʸ", use_container_width=True): press("**"); st.rerun()
            if s4.button("|x|", use_container_width=True): press("abs("); st.rerun()
        else:
            if s1.button("sin⁻¹", use_container_width=True): press("asin("); st.rerun()
            if s2.button("cos⁻¹", use_container_width=True): press("acos("); st.rerun()
            if s3.button("tan⁻¹", use_container_width=True): press("atan("); st.rerun()
            if s4.button("π", use_container_width=True): press("pi"); st.rerun()

            if s1.button("10ˣ", use_container_width=True): press("10**("); st.rerun()
            if s2.button("∛", use_container_width=True): press("cbrt("); st.rerun()
            if s3.button("e", use_container_width=True): press("E"); st.rerun()
            if s4.button("n!", use_container_width=True): press("factorial("); st.rerun()

        st.divider()

    # Standard Grid (Always visible)
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    if r1c1.button("C", use_container_width=True, type="primary"): clear(); st.rerun()
    if r1c2.button("( )", use_container_width=True): press_paren(); st.rerun()
    if r1c3.button("%", use_container_width=True): press("%"); st.rerun()
    if r1c4.button("÷", use_container_width=True, type="primary"): press("/"); st.rerun()

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    if r2c1.button("7", use_container_width=True): press("7"); st.rerun()
    if r2c2.button("8", use_container_width=True): press("8"); st.rerun()
    if r2c3.button("9", use_container_width=True): press("9"); st.rerun()
    if r2c4.button("×", use_container_width=True, type="primary"): press("*"); st.rerun()

    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    if r3c1.button("4", use_container_width=True): press("4"); st.rerun()
    if r3c2.button("5", use_container_width=True): press("5"); st.rerun()
    if r3c3.button("6", use_container_width=True): press("6"); st.rerun()
    if r3c4.button("−", use_container_width=True, type="primary"): press("-"); st.rerun()

    r4c1, r4c2, r4c3, r4c4 = st.columns(4)
    if r4c1.button("1", use_container_width=True): press("1"); st.rerun()
    if r4c2.button("2", use_container_width=True): press("2"); st.rerun()
    if r4c3.button("3", use_container_width=True): press("3"); st.rerun()
    if r4c4.button("+", use_container_width=True, type="primary"): press("+"); st.rerun()

    r5c1, r5c2, r5c3, r5c4 = st.columns(4)
    if r5c1.button("±", use_container_width=True): press_pm(); st.rerun()
    if r5c2.button("0", use_container_width=True): press("0"); st.rerun()
    if r5c3.button(".", use_container_width=True): press("."); st.rerun()
    if r5c4.button("=", use_container_width=True, type="primary"): calculate(); st.rerun()


# ─── UNIT DATA DICTIONARY ─────────────────────────────────────────────────
UNIT_CATEGORIES = {
    "Length":      {"Metre":1.0,"Kilometre":1e3,"Centimetre":1e-2,"Millimetre":1e-3,"Mile":1609.344,"Yard":0.9144,"Foot":0.3048,"Inch":0.0254,"Nautical mi":1852.0},
    "Weight":      {"Kilogram":1.0,"Gram":1e-3,"Milligram":1e-6,"Tonne":1e3,"Pound":0.45359237,"Ounce":0.028349523,"Stone":6.35029318},
    "Temperature": {"Celsius":"C","Fahrenheit":"F","Kelvin":"K"},
    "Area":        {"Sq Metre":1.0,"Sq Km":1e6,"Sq Mile":2589988.11,"Hectare":1e4,"Acre":4046.856,"Sq Foot":0.092903,"Sq Inch":6.4516e-4},
    "Volume":      {"Litre":1.0,"Millilitre":1e-3,"Cubic m":1e3,"Gallon (US)":3.785411784,"Gallon (UK)":4.54609,"Pint (US)":0.473176473,"Pint (UK)":0.56826125,"Cup":0.2365882365,"Fluid oz":0.0295735296},
    "Speed":       {"m/s":1.0,"km/h":1/3.6,"mph":0.44704,"knots":0.514444},
    "Data":        {"Byte":1.0,"Kilobyte":1024.0,"Megabyte":1024.0**2,"Gigabyte":1024.0**3,"Terabyte":1024.0**4,"Bit":0.125},
    "Energy":      {"Joule":1.0,"Kilojoule":1e3,"Calorie":4.184,"kcal":4184.0,"kWh":3.6e6,"eV":1.602176634e-19},
    "Pressure":    {"Pascal":1.0,"kPa":1e3,"Bar":1e5,"PSI":6894.757,"Atm":101325.0,"mmHg":133.322},
}

# ─── TAB 2: UNIT CONVERTER ────────────────────────────────────────────────
with tab_unit:
    category = st.selectbox("Category", list(UNIT_CATEGORIES.keys()))
    units = list(UNIT_CATEGORIES[category].keys())
    
    col1, col2 = st.columns(2)
    from_unit = col1.selectbox("From", units, index=0)
    to_unit = col2.selectbox("To", units, index=1 if len(units)>1 else 0)
    
    val = st.number_input("Value to Convert", value=1.0)
    
    if category == "Temperature":
        c = (val-32)*5/9 if from_unit=="Fahrenheit" else (val-273.15 if from_unit=="Kelvin" else val)
        if to_unit == "Fahrenheit": result = c*9/5+32
        elif to_unit == "Kelvin": result = c+273.15
        else: result = c
    else:
        u_dict = UNIT_CATEGORIES[category]
        result = val * u_dict[from_unit] / u_dict[to_unit]
    
    st.success(f"**Result:** {result:.8g} {to_unit}")
    if st.button("Use Result in Calculator"):
        st.session_state.expression = str(result)
        st.session_state.just_calculated = False
        st.toast("Added to calculator!")


# ─── TAB 3: DATE CALCULATOR ───────────────────────────────────────────────
with tab_date:
    d1 = st.date_input("From Date", value="today")
    d2 = st.date_input("To Date", value="today")
    
    if d1 and d2:
        delta = d2 - d1
        days = abs(delta.days)
        if days == 0:
            st.info("Same dates")
        else:
            st.success(f"**Difference:** {days} days")
            if st.button("Use Days in Calculator"):
                st.session_state.expression = str(days)
                st.session_state.just_calculated = False
                st.toast("Added to calculator!")


# ─── TAB 4: HISTORY ───────────────────────────────────────────────────────
with tab_hist:
    if not st.session_state.history:
        st.write("No calculations yet.")
    else:
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
        for item in st.session_state.history:
            st.code(item)
