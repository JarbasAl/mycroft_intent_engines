# IntentEngine

base class to add new intent engines to mycroft, check the [examples folder](./examples)

## creating your intent engine

the IntentEngine class exposes add_intent, remove_intent, add_entity, 
remove_entity methods, these will store your samples for training

in the minimal example you should override the following methods and 
implement engine specific training


    class MyEngine(IntentEngine):
        def __init__(self):
            self.name = "MyEngine"
            IntentEngine.__init__(self, self.name)
            
        def train(self, single_thread=False):
            """ train all registered intents and entities"""
            
            for intent_name in self.intent_samples:
                samples = self.intent_samples[name]
                # implement your training here
            
            for entity_name in self.entity_samples:
                samples = self.entity_samples[name]
                # implement your training here
    
        def calc_intent(self, query):
            """ return best intent for this query  """
            data = {"conf": 0,
                    "utterance": query,
                    "name": None}
            # calculate the intent here
            return data


# Intent Engine Skill

IntentEngine skill is a Mycroft skill baseclass that registers and triggers intents using your own intent engine

- edits user configuration to make self a priority skill
- listens for messages to register intents/entities
- on fallback trigger uses engine to determine intent
- registers self as a fallback skill, priority configurable (default is 4)

## Creating a EngineSkill class

all you need to do is subclass the IntentEngineSkill and initialize your engine
 

    from mycroft_intent_engines.skills import IntentEngineSkill
    
    # engine skill for mycroft
    class MyEngineSkill(IntentEngineSkill):
        def initialize(self):
            priority = 4
            engine = MyEngine()
            self.bind_engine(engine, priority)
  
install this as a normal mycroft skill and your new kind of intent will become available in regular mycroft skills


## Creating a MySpecialSkill class

in other skills you can now register intents, create two handlers to make 
your life easy
          
    def register_my_engine_intent(name, samples, handler):
        message = "my_engine:register_intent"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}                
        self.emitter.emit(Message(message, data))
        self.add_event(name, handler, 'mycroft.skill.handler')
    
    
    def register_my_engine_entity(name, samples):
        message = "my_engine:register_entity"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}
        self.emitter.emit(Message(message, data))

You can also subclass MycroftSkill and import it to avoid copy pasting the 
above methods in all skills

    class MySpecialSkill(MycroftSkill):
    
        def register_my_engine_intent(name, samples, handler):
            # same as above
        
        
        def register_my_engine_entity(name, samples):
             # same as above


## Creating actual Mycroft Skills

now just get to work!

    from X import MySpecialSkill
    
    class HelloSkill(MySpecialSkill):
    
        def initialize(self):
            self.register_my_engine_intent("hello", 
                                           ["hi", "hello"], 
                                           self.handle_hello)
            
        def handle_hello(self, message):
            self.speak("hello")
    
in the above X is wherever you have your MySpecialSkill class, assuming all 
of the above in an installed skill

    # make skills dir folder available for import
    
    from os.path import dirname
    skills_dir = dirname(dirname(__file__))
    import sys
    sys.path.append(skills_dir)
    from my_engine import MySpecialSkill