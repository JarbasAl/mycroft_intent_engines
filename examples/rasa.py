from mycroft_intent_engines.engines import IntentEngine
from mycroft_intent_engines.skills import IntentEngineSkill

from mycroft.configuration.config import Configuration
from mycroft.skills.core import MycroftSkill, Message

from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config
from rasa_nlu.model import Interpreter

from os.path import dirname, join, expanduser, exists
from os import makedirs
import json


class RASAEngine(IntentEngine):
    def __init__(self):
        self.name = "rasa"
        IntentEngine.__init__(self, self.name)
        self.config = Configuration.get().get(self.name, {})
        self.training_data_path = self.config.get("training_data_path",
                                                  join(dirname(__file__),
                                                       'demo-rasa.json'))
        self.rasa_config = self.config.get("config",
                                           join(dirname(__file__),
                                                'rasa_config.yml'))
        self.model_path = self.config.get("model_path", expanduser("~/.rasa"))
        if not exists(self.model_path):
            makedirs(self.model_path)

        self.interpreter = None
        self.training_data = {
            "rasa_nlu_data": {
                "regex_features": [],
                "entity_synonyms": [],
                "common_examples": []
            }}

    def add_intent(self, name, samples):
        for sample in samples:
            # TODO extract entities
            # {
            #    "start": 31,
            #    "end": 36,
            #    "value": "north",
            #    "entity": "location"
            # }
            sample = {
                         "text": sample,
                         "intent": name,
                         "entities": []
                     },
            self.training_data["rasa_nlu_data"]["common_examples"].append(sample)

    def remove_intent(self, name):
        # TODO
        pass

    def add_entity(self, name, samples):
        sample = {
            "value": name,
            "synonyms": samples
        }
        self.training_data["rasa_nlu_data"]["entity_synonyms"].append(sample)

    def remove_entity(self, name):
        # TODO
        pass

    def add_regex(self, name, pattern):
        sample = {"name": name, "pattern": pattern}
        self.training_data["rasa_nlu_data"]["regex_features"].append(sample)

    def remove_regex(self, name):
        # TODO
        pass

    def update_training_data(self):
        # update disk training data file with in memory training data
        with open(self.training_data_path, "r") as f:
            data = json.loads(f.read())
        data.update(self.training_data_path)
        with open(self.training_data_path, "w") as f:
            f.write(json.dumps(data, indent=4))

    def train(self, single_thread=False):
        """ train all registered intents and entities"""
        self.update_training_data()

        training_data = load_data(self.training_data_path)
        trainer = Trainer(config.load(self.rasa_config))
        trainer.train(training_data)
        model_directory = trainer.persist(
            self.model_path)  # Returns the directory the  model is stored in

        # where model_directory points to the model folder
        self.interpreter = Interpreter.load(model_directory)

    def calc_intent(self, query):
        """ return best intent for this query  """
        data = {"conf": 0,
                "utterance": query,
                "name": None}
        if self.interpreter is not None:
            data.update(self.interpreter.parse(query))
        return data


# engine skill for mycroft
class RASAEngineSkill(IntentEngineSkill):
    def initialize(self):
        priority = 4
        engine = RASAEngine()
        self.bind_engine(engine, priority)


class RASASkill(MycroftSkill):
    def register_rasa_intent(self, name, samples, handler):
        message = "rasa:register_intent"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}

        self.emitter.emit(Message(message, data))
        self.add_event(name, handler, 'mycroft.skill.handler')

    def register_rasa_entity(self, name, samples):
        message = "rasa:register_entity"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}
        self.emitter.emit(Message(message, data))

    def register_rasa_regex(self, name, pattern):
        message = "rasa:register_regex"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "pattern": pattern}
        self.emitter.emit(Message(message, data))


def create_skill():
    return RASAEngineSkill()
