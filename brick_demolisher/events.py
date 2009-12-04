"""
An event based architecture.
Works by adding callbacks to certain events, which are called when the event
occurs. An Event object is passed as a parameter to each callback, providing
usefull information to the listening object.

Examples:

    import events
    class HelloDispatcher(events.Dispatcher):
        def __init__(self):
            events.Dispatcher.__init__(self)

        def getHelloMessage(self):
            return "Hello World!"

        def sayHello(self):
            self.dispatch(events.Event("hello-event", self))

    def onHelloEvent(evt):
        print evt.target.getHelloMessage()

    if __name__ == "__main__":
        hello = HelloDispatcher()
        hello.addEvent("hello-event", onHelloEvent)
        hello.sayHello() # prints "Hello World!"
"""

class Event(object):
    """
    An object to be dispatched by Dispatcher. Extend this object to create
    other kinds of events.

    Custom events:
    You may extend this class to create custom events, with more attributes
    and/or operations. Here is an example:
        
        import events
        class KeyboardEvent(events.Event):
            def __init__(self, target, key, shift=False, ctrl=False, alt=False):
                events.Event.__init__("keyboard-event", target, None)
                self.key = key
                self.shift = shift
                self.ctrl = ctrl
                self.alt = alt

        class ScreenDraw(events.Event):
            def __init__(self, target, screen):
                events.Event.__init__("screen-draw", target, None)
                self.screen = screen

            def clear(self):
                self.screen.clear()
    
    Attributes:
        Event.type: the unique event identifier for a Dispatcher. Note that
            this may be almost any kind of object (strings, ints, etc). This
            is actually implemented as a python dictionary, so any valid key
            may be used here.
        Event.target: the object which is dispatching this Event.
        Event.data: extra field for passing data.
    """
    def __init__(self, type, target, data = None):
        """
        Creates a new Event object.
        @type:      Unique event type identifier.
        @target:    Object that dispatched the event.
        @data:      Conviniece attribute to pass objects.
        """
        self.type = type
        self.target = target
        self.data = data

class Dispatcher(object):
    """
    Extend this class to gain event dispatching capabilities.

    Example:
        import events
        import random
        class GreaterThanN(events.Dispatcher):
            def __init__(self, N):
                events.Dispatcher.__init__(self)
                self.i = 0
                self.N = N

            def add(self):
                self.i += random.randint(1, 10)
                if self.i > self.N:
                    self.dispatch(events.Event("greater-than-n", self))

        run = True
        def onGreaterThanN(evt):
            global run
            run = False

        if __name__ == "__main__":
            gtn = GreaterThanN(10)
            gtn.addEvent("greater-than-n", onGreaterThanN)
            while run:
                print gtn.i
                gtn.add()
            print gtn.i, "is greater than", gtn.N
    """
    def __init__(self):
        self._hash = {}

    def addEvent(self, evt, callback):
        """
        Adds an event to this Dispatcher.
        @evt:       Unique event type identifier.
        @callback:  Function to be called when 'evt' is triggered.
        """
        if not self.hasEvent(evt):
            self._hash[evt] = []
        self._hash[evt].append(callback)

    def delEvent(self, evt, callback):
        """
        Deletes an event callback given by @evt and @callback.
        @evt:       Unique event type identifier.
        @callback:  Function to be searched for deletion.
        """
        if not self.hasEvent(evt):
            return False
        for i in range(len(self._hash[evt])):
            if self._hash[evt][i][0] is callback:
                del self._hash[evt][i]
                return True
        return False

    def hasEvent(self, evt, callback = None):
        """
        Tells if there is at least one callback listening for @evt.
        If @callback is passed, tells if @callback is listening for @evt.
        """
        if not self._hash.has_key(evt):
            return False
        if not callback:
            return True
        for cb in self._hash[evt]:
            if cb is callback:
                return True
        return False

    def dispatch(self, evt):
        """
        Triggers @evt by calling all callbacks that are listening for @evt.
        """
        if self.hasEvent(evt.type):
            for callback in self._hash[evt.type]:
                callback(evt)

class GameQuit(Exception):
    pass

