# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from rasa.core.agent import Agent
import asyncio
from fpdf import FPDF


# class ActionSelectFilingType(Action):

#     def name(self) -> Text:
#         return "action_select_filing_type"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         buttons = [
#             {"payload":'/individual{"filing_type":"individual"}', "title":"Individual"},
#             {"payload":'/corporate{"filing_type":"corporate"}', "title":"Corporate"}
#         ]

#         dispatcher.utter_message(text="Please select your filing type:", buttons=buttons)

#         return []

class ActionGetUserInfo(Action):

    def name(self) -> Text:
        return "action_get_user_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        filing_type = tracker.get_slot("filing_type")
        print(tracker.slots)
        # if any slot exists, and print filing type
        if filing_type is not None:
            dispatcher.utter_message(text="Here is the information we have gathered thus far:")
        #Return info about each slot
            for (key, value) in tracker.slots.items():
                if key != "session_started_metadata" and value is not None:
                    if type(value) == str:
                        dispatcher.utter_message(text=f"{key.upper()}: {value.upper()}")    
                    else:
                        dispatcher.utter_message(text=f"{key.upper()}: {value}")    
        else:
            dispatcher.utter_message(text="Sorry, I don't have any information about you stored at this time.")

        return []
    
class ActionConfirmDefendantName(Action):
    def name(self) -> Text:
        return "action_confirm_defendant_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        name = tracker.get_slot('name')
        message = f"The name of the defendant you are suing is {name}, is that correct?"
        buttons = [{"payload": "/affirm", "title": "Yes"}, {"payload": "/deny", "title": "No, let me try again"}]
        dispatcher.utter_button_message(message, buttons)

        return []

# class ActionAskDefendantCountyOrZip(Action):
#     def name(self) -> Text:
#         return "action_ask_defendant_county_or_zip"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
#         q1 = tracker.get_slot('defendant_county_zip_question1')
#         location_type = "zip code" if q1==False else "county"
#         message = f"Please enter the defendant's {location_type}."
#         dispatcher.utter_message(text=message)

#         return []

class ValidateFilingTypeForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_filing_type_form"

    def validate_filing_type(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:
        #Validate filing type of user
        allowedIndividualTypes = ["individual", "independent"]
        
        slot_value = slot_value.lower()
        if slot_value in allowedIndividualTypes:
            return {"filing_type": "individual"}
        elif slot_value in ["corporation", "agency", "parternship"]:
            return {"filing_type": slot_value}
        else:
            dispatcher.utter_message(text=f"\"{slot_value}\" is not a valid filing type, please choose from the options given to you.")
            return {"filing_type": None}
    
class ValidateDefendantNameForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_defendant_name_form"

    def validate_defendant_name(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:

        #Validate defendant name
        return {"defendant_name":slot_value}

    def validate_confirm_defendant_name(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:
        
        #Check if we need to ask for defendant name again
        confirm_defendant_name = slot_value
        defendant_name = tracker.get_slot('defendant_name')
        print(f"requested_slot: {tracker.get_slot('requested_slot')}")
        if confirm_defendant_name == False:
            return {"defendant_name":None, "confirm_defendant_name":None}
        else:
            ####
            return {"defendant_name":defendant_name, "confirm_defendant_name":confirm_defendant_name}
        
class ValidateDefendantLocationQuestionForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_defendant_location_question_form"

    def validate_defendant_location_question1(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:

        #If answer is no, check to see if the defendant is a business
        if slot_value == False and tracker.get_slot('defendant_type') == "business":
            return {"requested_slot":None, "defendant_location_question1":slot_value}
        return {"defendant_location_question1":slot_value}


class ValidateDefendantCountyZipForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_defendant_county_zip_form"
    
    def validate_defendant_county_zip(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:
        return {"defendant_county_zip": slot_value}

    def validate_confirm_defendant_county_zip(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:
        #Check if we need to ask for defendant county zip again
        confirm_defendant_county_zip = slot_value
        defendant_county_zip = tracker.get_slot('defendant_county_zip')
        print(f"requested_slot: {tracker.get_slot('requested_slot')}")
        if confirm_defendant_county_zip == False:
            return {"defendant_county_zip":None, "confirm_defendant_county_zip":None}
        else:
            ####
            return {"defendant_county_zip":defendant_county_zip, "confirm_defendant_county_zip":confirm_defendant_county_zip}


class ValidateControversyForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_controversy_form"

    def validate_controversy_range(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:

        #Validate controversy range
        print(slot_value)
        return {"controversy_range": slot_value, "requested_slot": None}
    
class ValidateDamagesForm(FormValidationAction):

    def __init__(self):
        self.interpreter = Agent.load("models/20230528-192920-chewy-object.tar.gz")

    def name(self) -> Text:
        return "validate_damages_form"
    
    async def parse_damage_type(self, damage_type):
        return await self.interpreter.parse_message(message_data=damage_type)

    def validate_damage_type(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:

        #Validate defendant county zip
        return {"damage_type":slot_value}

    async def validate_confirm_damage_type(
            self, 
            slot_value: Any, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
            ) -> Dict[Text, Any]:
        
        confirm_damage_type = slot_value
        damage_type = tracker.get_slot('damage_type')

        loop = asyncio.get_event_loop()
        parsed_data = await loop.create_task(self.parse_damage_type(damage_type))
        print(parsed_data)
        print(f"Intent predicted: {parsed_data['intent']['name']}\nConfidence: {parsed_data['intent']['confidence']}\n")
        print("\n-----\n")
        
        if confirm_damage_type == False:
            return {"damage_type":None, "confirm_damage_type":None}
        else:
            ####
            return {"damage_type":damage_type, "confirm_damage_type":confirm_damage_type}


class ActionGeneratePDF(Action):

    def name(self) -> Text:
        return "action_generate_pdf"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #  slots
        todays_date = tracker.get_slot("todays_date")
        defendant_name = tracker.get_slot("defendant_name")
        defendant_address = tracker.get_slot("defendant_address")
        file_to_court = tracker.get_slot("file_to_court")
        court_address = tracker.get_slot("court_address")
        county_clerk_phone_number = tracker.get_slot("county_clerk_phone_number")

        #####
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "", ln=True)  # Add some space

        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, f"As of {todays_date}", ln=True, align="R")
        pdf.set_font("Arial", size=12)  # setting the font back to normal

        pdf.cell(0, 10, "", ln=True)  # Add some space
        pdf.set_font("Arial", style='B', size=18)
        pdf.cell(0, 10, "Claim Bot Summary Page", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "", ln=True)  # Add some space

        pdf.set_font("Arial", style='B', size=12)

        # BOLDING 1
        pdf.set_font("Arial", style='B', size=12)
        label_text = "Defendant's Name:"
        pdf.cell(pdf.get_string_width(label_text), 10, label_text, ln=0)  # ln=0 means the cursor won't go to the next line

        # Set font to normal for actual name
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "\t" + defendant_name, ln=True)  # ln=True means the cursor will go to the next line after this
        #------

        # BOLDING 2
        pdf.set_font("Arial", style='B', size=12)
        label_text2 = "Defendant's Address:"
        pdf.cell(pdf.get_string_width(label_text2), 10, label_text2, ln=0)  # ln=0 means the cursor won't go to the next line

        # Set font to normal for actual name
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "\t" + defendant_address, ln=True)  # ln=True means the cursor will go to the next line after this
        #------
        pdf.cell(0, 10, "", ln=True)  # Add some space

        # BOLDING 3
        pdf.set_font("Arial", style='B', size=12)
        label_text3 = "File to this Court:"
        pdf.cell(pdf.get_string_width(label_text3), 10, label_text3, ln=0)  # ln=0 means the cursor won't go to the next line

        # Set font to normal for actual name
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "\t" + file_to_court, ln=True)  # ln=True means the cursor will go to the next line after this
        #------
        # BOLDING 4
        pdf.set_font("Arial", style='B', size=12)
        label_text4 = "Court's Address:"
        pdf.cell(pdf.get_string_width(label_text4), 10, label_text4, ln=0)  # ln=0 means the cursor won't go to the next line

        # Set font to normal for actual name
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "\t" + court_address, ln=True)  # ln=True means the cursor will go to the next line after this
        #------
        pdf.cell(0, 10, "", ln=True)  # Add some space

        pdf.set_font("Arial", style='B', size=12)
        text = """Keep in mind you must pay a court fee (cash or money order). 
        Nassau and Western Suffolk County accept credit cards in the courthouse. 
        Western Suffolk County accepts personal checks. Checks and money orders should be made payable to "The Clerk of the Court."
        """

        pdf.multi_cell(0, 10, text, align='C')
        pdf.set_font("Arial", size=12)


        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, "The fee to sue in Small Claims Court is:", ln=True)
        pdf.set_font("Arial", size=12)

        # Indent by 20mm
        pdf.set_x(20)
        pdf.cell(0, 10, "- $15 for claims up to $1000, and", ln=True)
        pdf.set_x(20)
        pdf.cell(0, 10, "- $20 for claims over $100", ln=True)
        pdf.set_x(10)


        # LINE
        start_y = pdf.get_y()
        start_x = 10  # Adjust this value as needed
        end_x = pdf.w - 10  # Adjust this value as needed
        pdf.line(start_x, start_y, end_x, start_y)


        text2 = """There is another way to solve your problem without going to Court. Every county in the state of New York has a community dispute resolution center that offers mediation for free.
        """
        pdf.multi_cell(0, 10, text2)

        pdf.cell(0, 5, "", ln=True)  # Add small space

        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, "You can find the location of a community dispute resolution center near you at:", ln=True)
        pdf.set_font("Arial", size=12)


        # Indent by 20mm
        pdf.set_x(20)
        pdf.cell(0, 10, "- At the Small Claims Court Clerk's Office, or", ln=True)
        pdf.set_x(20)

        #HYPERLINK
        url = "http://www.nycourts.gov/ip/adr/ProgramList.shtml"

        # Change text color to blue
        pdf.set_text_color(0, 0, 255)  # RGB for blue

        # Output the text
        pdf.cell(0, 10, "- At: " + url, ln=True)

        # Change text color back to black
        pdf.set_text_color(0, 0, 0)  # RGB for black

        # Get current position
        x = pdf.get_x()
        y = pdf.get_y()

        # Set the link
        link_width = pdf.get_string_width(url)
        link_height = 10  # Adjust as needed
        pdf.link(x, y - link_height, link_width, link_height, url)

        #/HYPERLINK
        pdf.cell(0, 10, "", ln=True)  # Add some space

        # Reset X position to left margin (if necessary)
        pdf.set_x(10)


        # BOLDING 2
        pdf.set_font("Arial", style='B', size=12)
        label_text5 = "County Clerk Phone Number:"
        pdf.cell(pdf.get_string_width(label_text5), 10, label_text5, ln=0)  # ln=0 means the cursor won't go to the next line

        # Set font to normal for actual name
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "\t" + county_clerk_phone_number, ln=True)  # ln=True means the cursor will go to the next line after this
        #------


        # LINE
        start_y = pdf.get_y()
        start_x = 10  # Adjust this value as needed
        end_x = pdf.w - 10  # Adjust this value as needed
        pdf.line(start_x, start_y, end_x, start_y)


        pdf.output("claimbot333333.pdf")
        ####
        return []