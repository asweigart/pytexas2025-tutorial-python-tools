import turtle, time, re

# SC TODO - some kind of live replay sort of thing?
# SC TODO - some kind of chart maker that records the screen after every movement?


ALL_SHORTCUTS = '# f b l r h c g tele x y st u pd pu ps pc fc bc sh cir undo bf ef sleep n s e w nw ne sw se u t cs css spd eoc' + \
    'forward backward left right home clear goto setx sety stamp update pendown penup pensize pencolor fillcolor bgcolor setheading' + \
    'circle undo begin_fill end_fill north south east west northwest northeast southwest southeast reset bye done exitonclick update' + \
    'tracer hide show dot clearstamp clearstamps degrees radians speed'

CARDINAL_TO_DEGREES = {'n': '90', 's': '270', 'e': '0', 'w': '180', 'nw': '135', 'ne': '45', 'sw': '225', 'se': '315'}

_MAP_FULL_TO_SHORT_NAMES = {'forward': 'f', 'backward': 'b', 'right': 'r', 'left': 'l', 'home': 'h', 'clear': 'c', 
        'goto': 'g', 'teleport': 'tele', 'setx': 'x', 'sety': 'y', 'stamp': 'st', 'update': 'u', 'pendown': 'pd', 'penup': 'pu', 
        'pensize': 'ps', 'pencolor': 'pc', 'fillcolor': 'fc', 'bgcolor': 'bc', 'setheading': 'sh', 'circle': 'cir', 
        'begin_fill': 'bf', 'end_fill': 'ef', 'north': 'n', 'south': 's', 'east': 'e', 'west': 'w',
        'northwest': 'nw', 'northeast': 'ne', 'southwest': 'sw', 'southeast': 'se', 'update': 'u', 'tracer': 't',
        'clearstamp': 'cs', 'clearstamps': 'css', 'speed': 'spd', 'exitonclick': 'eoc'}

RECORDED_SHORTCUTS = []
_NOW_RECORDING = False

class TurtleShortcutException(Exception):
    pass

def sc(*args, turtle_obj=None, _return_turtle_code=False, skip=False): # type: () -> int
    """TODO
    """

    """Supported commands:

    f N - forward(N)
    b N - backward(N)
    l N - left(N)
    r N - right(N)
    h - home()
    c - clear()
    g X Y - goto(X, Y)
    tele X Y - teleport(X, Y)
    x X - setx(X)
    y Y - sety(Y)
    st - stamp()
    pd - pendown()
    pu - penup()
    ps N - pensize(N)
    pc RGB - pencolor(RGB) (RGB value can either be a single string like `red` or three dec/hex numbers `1.0 0.0 0.5` or `FF FF 00`
    fc RGB - fillcolor(RGB)
    bc RGB - bgcolor(RGB)
    sh N - setheading(N)
    cir N - circle(N)
    undo - undo()
    bf - begin_fill()
    ef - end_fill()
    reset - reset()

    sleep N - time.sleep(N)

    n N - setheading(90);forward(N)
    s N - setheading(270);forward(N)
    w N - setheading(180);forward(N)
    e N - setheading(0);forward(N)
    nw N - setheading(135);forward(N)
    ne N - setheading(45);forward(N)
    sw N - setheading(225);forward(N)
    se N - setheading(315);forward(N)
    north N - setheading(90);forward(N)
    south N - setheading(270);forward(N)
    west N - setheading(180);forward(N)
    east N - setheading(0);forward(N)
    northwest N - setheading(135);forward(N)
    northeast N - setheading(45);forward(N)
    southwest N - setheading(225);forward(N)
    southeast N - setheading(315);forward(N)

    done - done()
    bye - bye()
    exitonclick - exitonclick()

    t N1 N2 - tracer(N1, N2)
    u - update()

    hide - hide()
    show - show()

    dot N - dot(N)
    cs N - clearstamp(N)
    css N - clearstamps(N)
    degrees - degrees()
    radians - radians()
    
    spd N - speed(N) but N can also be 'fastest', 'fast', 'normal', 'slow', 'slowest'
    !!shape N - shape(N) where N can be “arrow”, “turtle”, “circle”, “square”, “triangle”, “classic”
    !!resizemode N - resizemode(N) where N can be “auto”, “user”, or "noresize"
    !!bgpic N - bgpic(N) where the N filename cannot have a comma in it.

    !!shapesize N1 N2 N3 - shapesize(N1, N2, N3)
    !!settiltangle N - settiltangle(N)
    !!tilt N - tilt(N)
    !!tiltangle N - tiltangle(N)
    



    Note: 


    Furthermore, you can also use the full names: forward N translates to forward(N).
    Note: None of these functions can take string args that have spaces in them, since spaces are the arg delimiter here.
    Note: You also can't use variables here, only static values. But you can use f-strings.

    Return value is the number of commands executed.
    Whitespace is insignificant. '   f     100   ' is the same as 'f 100'
    """

    if skip:
        if _return_turtle_code:
            return ()
        else:
            return 0

    # Join multiple arg strings into one, separated by commas:
    shortcuts = ','.join(args)

    # Newlines become commas as well:
    shortcuts = shortcuts.replace('\n', ',')

    if shortcuts == '' or len(shortcuts.split(',')) == 0:
        return 0
    
    count_of_shortcuts_run = 0

    # Go through and check that all shortcuts are syntactically correct:
    for shortcut in shortcuts.split(','):
        count_of_shortcuts_run += _run_shortcut(shortcut, turtle_obj=turtle_obj, dry_run=True)

    # Go through and actually run all the shortcuts:
    count_of_shortcuts_run = 0
    turtle_code = tuple()
    for shortcut in shortcuts.split(','):
        if _return_turtle_code:
            turtle_code += _run_shortcut(shortcut, turtle_obj=turtle_obj, _return_turtle_code=True)
        else:
            count_of_shortcuts_run += _run_shortcut(shortcut, turtle_obj=turtle_obj)
    
    if _return_turtle_code:
        # Return a multi-line string of Python code calling turtle functions:
        return '\n'.join(turtle_code) + '\n'
    else:
        return count_of_shortcuts_run


def _run_shortcut(shortcut, turtle_obj=None, dry_run=False, _return_turtle_code=False):
    '''Runs a single shortcut'''

    if turtle_obj is None:
        turtle_obj = turtle  # Use the main turtle given by the module.

    # Clean up shortcut name from "  FOrWARD " to "f", for example.
    shortcut_parts = shortcut.strip().split()
    if len(shortcut_parts) == 0:
        if _return_turtle_code:
            return ('',)
        else:
            return 0  # Return 0 because blank strings have zero shortcuts.
    _sc = shortcut_parts[0].lower()
    _sc = _MAP_FULL_TO_SHORT_NAMES.get(_sc, _sc)

    # Check that the shortcut's syntax is valid:

    if _sc not in ALL_SHORTCUTS:
        raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[0] + '` is not a turtle shortcut.')

    raise_exception = False
    count_of_shortcuts_run = 0
    

    # SHORTCUTS THAT TAKE A VARIABLE NUMBER OF ARGUMENTS:
    if _sc in ('#',):
        if _sc == '#':
            if _return_turtle_code:
                return (shortcut.lstrip(),)  # Return the comment as is (but with leading whitespace removed).
            pass  # Comments do nothing.
        else:  # pragma: no cover
            assert False, 'Unhandled shortcut: ' + _sc


    # SHORTCUTS THAT TAKE A SINGLE NUMERIC ARGUMENT:
    elif _sc in ('f', 'b', 'r', 'l', 'x', 'y', 'ps', 'sh', 'cir', 'sleep', 'n', 's', 'e', 'w', 'nw', 'ne', 'sw', 'se', 'dot', 'cs', 'spd'):
        if len(shortcut_parts) < 2:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: Missing the required numeric argument.')
        if len(shortcut_parts) > 2:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: Too many arguments.')

        # Convert the string arguments for the `speed` shortcut to their numeric equivalents.
        if _sc == 'spd':
            shortcut_parts[1] = {'fastest': 0, 'fast': 10, 'normal': 6, 'slow': 3, 'slowest': 1}.get(shortcut_parts[1].lower(), shortcut_parts[1].lower())
        
        try:
            float(shortcut_parts[1])
        except ValueError:
            raise_exception = True  # We don't raise here so we can hide the original ValueError and make the stack trace a bit neater.
        if raise_exception:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[1] + '` is not a number.')

        # `dot` shortcut doesn't allow negative values:
        if _sc == 'dot' and float(shortcut_parts[1]) < 0:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `dot` argument cannot be a negative number.')

        if not dry_run:
            # Run the shortcut that has exactly one numeric argument:
            if _sc == 'f':
                if _return_turtle_code:
                    return ('forward(' + shortcut_parts[1] + ')',)
                turtle_obj.forward(float(shortcut_parts[1]))
            elif _sc == 'b':
                if _return_turtle_code:
                    return ('backward(' + shortcut_parts[1] + ')',)
                turtle_obj.backward(float(shortcut_parts[1]))    
            elif _sc == 'r':
                if _return_turtle_code:
                    return ('right(' + shortcut_parts[1] + ')',)
                turtle_obj.right(float(shortcut_parts[1]))    
            elif _sc == 'l':
                if _return_turtle_code:
                    return ('left(' + shortcut_parts[1] + ')',)
                turtle_obj.left(float(shortcut_parts[1]))    
            elif _sc == 'x':
                if _return_turtle_code:
                    return ('setx(' + shortcut_parts[1] + ')',)
                turtle_obj.setx(float(shortcut_parts[1]))    
            elif _sc == 'y':
                if _return_turtle_code:
                    return ('sety(' + shortcut_parts[1] + ')',)
                turtle_obj.sety(float(shortcut_parts[1]))    
            elif _sc == 'ps':
                if _return_turtle_code:
                    return ('pensize(' + shortcut_parts[1] + ')',)
                turtle_obj.pensize(float(shortcut_parts[1]))    
            elif _sc == 'sh':
                if _return_turtle_code:
                    return ('setheading(' + shortcut_parts[1] + ')',)
                turtle_obj.setheading(float(shortcut_parts[1]))
            elif _sc == 'cir':
                if _return_turtle_code:
                    return ('circle(' + shortcut_parts[1] + ')',)
                turtle_obj.circle(float(shortcut_parts[1]))    
            elif _sc == 'sleep':
                if _return_turtle_code:
                    return ('sleep(' + shortcut_parts[1] + ')', )
                time.sleep(float(shortcut_parts[1]))
            elif _sc in ('n', 's', 'e', 'w', 'nw', 'ne', 'sw', 'se'):
                originally_in_radians_mode = in_radians_mode()

                if _return_turtle_code:
                    if originally_in_radians_mode:
                        return ('degrees()', 'setheading(' + CARDINAL_TO_DEGREES[_sc] + ')', 'forward(' + shortcut_parts[1] + ')', 'radians()')
                    else:
                        return ('setheading(' + CARDINAL_TO_DEGREES[_sc] + ')', 'forward(' + shortcut_parts[1] + ')')                
                turtle.degrees()
                if _sc == 'n':
                    turtle.setheading(90)
                elif _sc == 's':
                    turtle.setheading(270)
                elif _sc == 'e':
                    turtle.setheading(0)
                elif _sc == 'w':
                    turtle.setheading(180)
                elif _sc == 'nw':
                    turtle.setheading(135)
                elif _sc == 'ne':
                    turtle.setheading(45)
                elif _sc == 'sw':
                    turtle.setheading(225)
                elif _sc == 'se':
                    turtle.setheading(315)
                else:  # pragma: no cover
                    assert False, 'Unhandled shortcut: ' + _sc
                turtle_obj.forward(float(shortcut_parts[1]))
                if originally_in_radians_mode:
                    turtle.radians()
            elif _sc == 'dot':
                if _return_turtle_code:
                    return ('dot(' + shortcut_parts[1] + ')',)
                turtle_obj.dot(float(shortcut_parts[1]))
            elif _sc == 'cs':
                if _return_turtle_code:
                    return ('clearstamp(' + shortcut_parts[1] + ')',)
                turtle_obj.clearstamp(float(shortcut_parts[1]))
            elif _sc == 'spd':
                if _return_turtle_code:
                    return ('speed(' + str(shortcut_parts[1]) + ')',)
                turtle_obj.speed(float(shortcut_parts[1]))
            else:  # pragma: no cover
                assert False, 'Unhandled shortcut: ' + _sc
            count_of_shortcuts_run += 1





    # SHORTCUTS THAT TAKE A SINGLE INTEGER ARGUMENT OR NONE ARGUMENT:
    elif _sc in ('css',):
        if len(shortcut_parts) > 2:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: Too many arguments.')
        
        # Technically, the css shortcut can take a float argument, but it gets passed to int() silently. Not ideal, but not a big deal either.

        if len(shortcut_parts) == 2:
            try:
                int(shortcut_parts[1])
            except ValueError:
                raise_exception = True  # We don't raise here so we can hide the original ValueError and make the stack trace a bit neater.
            if raise_exception:
                raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[1] + '` is not a number.')

        if not dry_run:
            # Run the shortcut:
            if _sc == 'css':
                if len(shortcut_parts) == 1:
                    if _return_turtle_code:
                        return ('clearstamps()',)
                    turtle_obj.clearstamps()
                elif len(shortcut_parts) == 2:
                    if _return_turtle_code:
                        return ('clearstamps(' + shortcut_parts[1] + ')',)
                    turtle_obj.clearstamps(int(shortcut_parts[1]))
                else:  # pragma: no cover
                    assert False, 'Unhandled shortcut: ' + _sc
            else:  # pragma: no cover
                assert False, 'Unhandled shortcut: ' + _sc
            count_of_shortcuts_run += 1






    # SHORTCUTS THAT TAKE EXACTLY TWO NUMERIC ARGUMENTS:
    elif _sc in ('g', 't', 'tele'):
        if len(shortcut_parts) < 3:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: Missing two required numeric argument.')
        elif len(shortcut_parts) > 3:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: Too many arguments.')

        try:
            float(shortcut_parts[1])
        except ValueError:
            raise_exception = True  # We don't raise here so we can hide the original ValueError and make the stack trace a bit neater.
        if raise_exception:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[1] + '` is not a number.')
        try:
            float(shortcut_parts[2])
        except ValueError:
            raise_exception = True  # We don't raise here so we can hide the original ValueError and make the stack trace a bit neater.
        if raise_exception:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[2] + '` is not a number.')

        if not dry_run:
            # Run the shortcut that has exactly two numeric arguments:
            x = float(shortcut_parts[1])
            y = float(shortcut_parts[2])

            # Run the shortcut:
            if _sc == 'g':
                if _return_turtle_code:
                    return ('goto(' + shortcut_parts[1] + ', ' + shortcut_parts[2] + ')',)
                turtle_obj.goto(x, y)
            elif _sc == 't':
                if _return_turtle_code:
                    return ('tracer(' + shortcut_parts[1] + ', ' + shortcut_parts[2] + ')',)
                turtle.tracer(x, y)  # Note: tracer() is not a Turtle method, there's only the global tracer() function.
            elif _sc == 'tele':
                if _return_turtle_code:
                    return ('teleport(' + shortcut_parts[1] + ', ' + shortcut_parts[2] + ')',)
                turtle_obj.teleport(x, y)
            else:  # pragma: no cover
                assert False, 'Unhandled shortcut: ' + _sc 
            count_of_shortcuts_run += 1





    # SHORTCUTS THAT TAKE EXACTLY ZERO ARGUMENTS:
    elif _sc in ('h', 'c', 'st', 'pd', 'pu', 'undo', 'bf', 'ef', 'reset', 'bye', 'done', 'eoc', 'u', 'show', 'hide'):
        if len(shortcut_parts) > 1:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: This shortcut does not have arguments.')

        if not dry_run:
            # Run the shortcut that has exactly zero arguments:
            if _sc == 'h':
                if _return_turtle_code:
                    return ('home()',)
                turtle_obj.home()
            elif _sc == 'c':
                if _return_turtle_code:
                    return ('clear()',)
                turtle_obj.clear()
            elif _sc == 'st':
                if _return_turtle_code: 
                    return ('stamp()',)
                turtle_obj.stamp()
            elif _sc == 'pd':
                if _return_turtle_code:
                    return ('pendown()',)
                turtle_obj.pendown()
            elif _sc == 'pu':
                if _return_turtle_code:
                    return ('penup()',)
                turtle_obj.penup()
            elif _sc == 'undo':
                if _return_turtle_code:
                    return ('undo()',)
                turtle_obj.undo()
            elif _sc == 'bf':
                if _return_turtle_code:
                    return ('begin_fill()',)
                turtle_obj.begin_fill()
            elif _sc == 'ef':
                if _return_turtle_code:
                    return ('end_fill()',)
                turtle_obj.end_fill()
            elif _sc == 'reset':
                if _return_turtle_code:
                    return ('reset()',)
                turtle_obj.reset()
            elif _sc == 'bye':  # pragma: no cover
                if _return_turtle_code:
                    return ('bye()',)
                turtle_obj.bye()
            elif _sc == 'done':  # pragma: no cover
                if _return_turtle_code:
                    return ('done()',)
                turtle_obj.done()
            elif _sc == 'eoc':  # pragma: no cover
                if _return_turtle_code:
                    return ('exitonclick()',)
                turtle_obj.exitonclick()
            elif _sc == 'u':
                if _return_turtle_code:
                    return ('update()',)
                turtle_obj.update()
            elif _sc == 'show':
                if _return_turtle_code:
                    return ('showturtle()',)
                turtle_obj.showturtle()
            elif _sc == 'hide':
                if _return_turtle_code:
                    return ('hideturtle()',)
                turtle_obj.hideturtle()
            else:  # pragma: no cover
                assert False, 'Unhandled shortcut: ' + _sc
            count_of_shortcuts_run += 1



    # SHORTCUTS THAT TAKE AN RGB OR COLOR ARGUMENT:
    elif _sc in ('pc', 'fc', 'bc'):
        color_arg_is_color_name = False  # Start as False. If it's a color name, we'll set this to True.

        if len(shortcut_parts) < 2:
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: Missing required RGB argument.')
        elif len(shortcut_parts) not in (2, 4):
            raise TurtleShortcutException('Syntax error in `' + shortcut + '`: Invalid RGB argument. It must either be a color name like `red` or three numbers like `1.0 0.5 0.0` or `255 0 255` or `FF 00 FF`.')

        if len(shortcut_parts) == 4:
            # We expect the color arg to either be something like (255, 0, 0) or (1.0, 0.0, 0.0):
            raise_exception = False

            try:
                float(shortcut_parts[1])
            except ValueError:
                raise_exception = True  # We don't raise here so we can hide the original ValueError and make the stack trace a bit neater.
            if raise_exception:
                raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[1] + '` is not a number.')

            try:
                float(shortcut_parts[2])
            except ValueError:
                raise_exception = True  # We don't raise here so we can hide the original ValueError and make the stack trace a bit neater.
            if raise_exception:
                raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[2] + '` is not a number.')

            try:
                float(shortcut_parts[3])
            except ValueError:
                raise_exception = True  # We don't raise here so we can hide the original ValueError and make the stack trace a bit neater.
            if raise_exception:
                raise TurtleShortcutException('Syntax error in `' + shortcut + '`: `' + shortcut_parts[3] + '` is not a number.')

            if turtle_obj.colormode() == 1.0:
                color_arg = (float(shortcut_parts[1]), float(shortcut_parts[2]), float(shortcut_parts[3]))
            elif turtle_obj.colormode() == 255:
                # Convert strings like '1.0' to floats first, then to int. (Calling int('1.0') would raise a ValueError.)
                color_arg = (int(float(shortcut_parts[1])), int(float(shortcut_parts[2])), int(float(shortcut_parts[3])))
            else:  # pragma: no cover
                assert False, 'Unhandled colormode: ' + str(turtle_obj.colormode())

            if turtle_obj.colormode() == 1.0 and (color_arg[0] > 1.0 or color_arg[1] > 1.0 or color_arg[2] > 1.0):
                raise TurtleShortcutException(shortcut + ' is invalid because colormode is 1.0 and one or more RGB color values are greater than 1.0.')
            
        elif len(shortcut_parts) == 2:
            # We expect the color arg to be a string like 'blue' or '#FF0000':
            raise_exception = False

            if re.match(r'^#[0-9A-Fa-f]{6}$', shortcut_parts[1]):
                # Color arg is a hex code like '#FF0000', and not a name like 'blue'.
                color_arg_is_color_name = False  # It's already False, but I put this here to be explicit.
            else:
                # shortcut_parts[1] must be a color name like 'blue'
                color_arg_is_color_name = True
            color_arg = shortcut_parts[1]

            # Test the color name by actually calling pencolor():
            original_pen_color = turtle_obj.pencolor()
            try:
                turtle_obj.pencolor(color_arg)
            except turtle.TurtleGraphicsError:
                raise_exception = True  # We don't raise here so we can hide the original TurtleGraphicsError and make the stack trace a bit neater.
            if raise_exception:
                if re.match(r'^[0-9A-Fa-f]{6}$', shortcut_parts[1]):
                    raise TurtleShortcutException('Syntax error in `' + shortcut + "`: '" + shortcut_parts[1] + "' is not a valid color. Did you mean '# " + shortcut_parts[1] + "'?")
                else:
                    raise TurtleShortcutException('Syntax error in `' + shortcut + "`: '" + shortcut_parts[1] + "' is not a valid color.")
            
            # NOTE: This code here is to handle an unfixed bug in turtle.py. If the color mode is 1.0 and you set
            # the color to (1.0, 0.0, 0.0) and then change the color mode to 255, the color will be (255.0, 0.0, 0.0)
            # but these float values are not a valid setting for a color while in mode 255. So we have to convert them
            # to integers here.
            if isinstance(original_pen_color, tuple) and turtle_obj.colormode() == 255:
                turtle_obj.pencolor(int(original_pen_color[0]), int(original_pen_color[1]), int(original_pen_color[2]))
            else:
                turtle_obj.pencolor(original_pen_color)

        if not dry_run:
            # Return the turtle code, if that was asked:
            if _return_turtle_code:
                if _sc == 'pc':
                    func_name_prefix = 'pen'
                elif _sc == 'fc':
                    func_name_prefix = 'fill'
                elif _sc == 'bc':
                    func_name_prefix = 'bg'

                if color_arg_is_color_name:
                    return (func_name_prefix + "color('" + str(color_arg) + "')",)
                else:
                    return (func_name_prefix + 'color(' + str(color_arg) + ')',)
            
            # Run the shortcut that has an RGB color argument:
            if _sc == 'pc':
                turtle_obj.pencolor(color_arg)
            elif _sc == 'fc':
                turtle_obj.fillcolor(color_arg)
            elif _sc == 'bc':
                turtle_obj.bgcolor(color_arg)
            else:  # pragma: no cover
                assert False, 'Unhandled shortcut: ' + _sc  
            count_of_shortcuts_run += 1

    # If begin_recording() has been called, log the shortcut.
    if _NOW_RECORDING and not dry_run:
        RECORDED_SHORTCUTS.append(shortcut)

    return count_of_shortcuts_run


def in_radians_mode():
    """Returns True if turtle is in radians mode, False if in degrees mode."""
    original_heading = turtle.heading()
    turtle.left(1)
    turtle.radians()  # Switch to radians mode.
    turtle.right(1)
    if turtle.heading() == original_heading:
        return True
    else:
        turtle.degrees()  # Switch back to degrees mode.
        return False


def in_degrees_mode():
    """Returns True if turtle is in degrees mode, False if in radians mode."""
    return not in_radians_mode()


def scs(*args):
    """Returns the shortcut string of Python code that would be executed by the sc() function, suitable for printing to the screen."""
    return sc(*args, _return_turtle_code=True)

def psc(*args):
    """Prints the Python code that would be executed by the sc() function."""

    # end='' because sc() already adds a newline to the last line.
    print(sc(*args, _return_turtle_code=True), end='')


def begin_recording(shortcut_list=None):
    global RECORDED_SHORTCUTS, _NOW_RECORDING
    RECORDED_SHORTCUTS = []

    _NOW_RECORDING = True
    
def end_recording():
    global RECORDED_SHORTCUTS, _NOW_RECORDING

    _NOW_RECORDING = False
    return RECORDED_SHORTCUTS
