# -*- coding: utf-8 -*-

# This Alexa skill allows users to check Georgia Tech dining options for the Today
# @author Jin Park, Ben Rochford, Luke Dague
# @version 1.0.0
# This script is built using the handler classes approach in skill builder.
import logging
import requests
import ask_sdk_core.utils as ask_utils
import random

from bs4 import BeautifulSoup
from time import sleep

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Which Georgia Tech dining hall menu would you like to check today?"
        reprompt_text = "North Ave and Brittain are both great choices. Which dining hall are you looking for?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )


class HallIntentHandler(AbstractRequestHandler):
    """Handler for Hall Intent"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HallIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        hall = slots["Hall"].value

        print('## the thing found: ', handler_input.request_envelope.request.intent.slots)

        linkEnd = ""
        if hall == "Brittain" or hall == "Brittain hall" or hall == "Brittain dining hall" or hall == "Brittain dining":
            linkEnd = "BrittainDiningHall"
        if hall == "nav" or hall == "nav dining" or hall == "north ave" or hall == "north avenue" or hall == "nav dining hall" or hall == "north ave dining" or hall == "north ave dining hall" or hall == "north avenue dining hall":
            linkEnd = "NorthAveDiningHall"


        print("$ Result linkEnd: ", linkEnd)

        link = 'https://georgiatech.campusdish.com/LocationsAndMenus/' + linkEnd
        print("$ Requesting link ", link)
        request = requests.get(link)

        html_soup = BeautifulSoup(request.text, 'html.parser')
        type(html_soup)
        food_containers = html_soup.find_all('span', class_ = 'item__name')
        closed_check = html_soup.find('span', class_ = 'locationstatus closed')
        print("closed or nah: ", closed_check)
        #print("$ All food content: ", food_containers)
        print("$ Type of food_containers: ", type(food_containers))
        print("$ Length of food_containers: ", len(food_containers))

        print("$ Printing foods: ")
        for x in food_containers:
            print("\t- ", x.a.text)

        net_menu = ""
        for x in range (0, 5):
            net_menu += food_containers[x].a.text.replace('&',' and ') + ", "

        #handler_input.request_envelope.request.intent.slots['Hall'].value

        funny_adj = ["yummy","tastalicious","bolognese","edible at best","tasty","crunchy","creamy","finger lickin good","slammin","delectable","cash money","wonderful","alright","like a real toungue pleaser","yum yum good","like you should bring me some"]

        speak_output = 'Today at {hall}, they are serving {net_menu} and more. Sounds {adj}!'.format(hall=hall, net_menu=net_menu, adj=random.choice(funny_adj))

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, this hall is closed right now."

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HallIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
